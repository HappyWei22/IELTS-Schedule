<template>
  <section>
    <div class="page-header">
      <div>
        <h1>老师月度统计</h1>
        <p>选择老师和月份，查看当月课程与课时统计。</p>
      </div>
    </div>

    <div v-if="message" class="alert alert-success">{{ message }}</div>
    <div v-if="error" class="alert alert-error">{{ error }}</div>

    <div class="panel">
      <div class="toolbar filters">
        <select v-model="selectedTeacherId">
          <option value="">请选择老师</option>
          <option v-for="teacher in teachers" :key="teacher.id" :value="teacher.id">
            {{ teacher.name }}（{{ teacher.subject }}）
          </option>
        </select>
        <input v-model="selectedMonth" type="month" />
        <button class="button button-primary" @click="loadSchedule">查看统计</button>
        <button class="button" @click="downloadCsv">导出 CSV</button>
      </div>

      <div class="stats-grid compact">
        <div class="stat-card">
          <span>当月总课程数</span>
          <strong>{{ summary.total_courses }}</strong>
        </div>
        <div class="stat-card">
          <span>当月总课时数</span>
          <strong>{{ summary.total_hours }}</strong>
        </div>
        <div class="stat-card">
          <span>老师</span>
          <strong>{{ summary.teacher_name || '-' }}</strong>
        </div>
      </div>

      <div v-if="summary.type_hours.length" class="type-summary">
        <span v-for="item in summary.type_hours" :key="item.course_type" class="tag">
          {{ item.course_type }}：{{ item.hours }} 小时
        </span>
      </div>
      <div v-else class="empty-state compact-empty">
        <strong>暂无课程类型统计</strong>
        <span>选择老师并查看统计后，这里会显示各课程类型课时。</span>
      </div>

      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>日期</th>
              <th>开始时间</th>
              <th>结束时间</th>
              <th>学生</th>
              <th>课程类型</th>
              <th>时长</th>
              <th>线上链接/地点</th>
              <th>备注</th>
            </tr>
            </thead>
            <tbody>
            <tr v-for="course in courses" :key="course.id">
              <td data-label="日期">{{ course.course_date }}</td>
              <td data-label="开始时间">{{ formatTime(course.start_time) }}</td>
              <td data-label="结束时间">{{ formatTime(course.end_time) }}</td>
              <td data-label="学生">{{ course.student_name }}</td>
              <td data-label="课程类型"><span class="tag">{{ course.course_type }}</span></td>
              <td data-label="时长">{{ course.duration_hours }} 小时</td>
              <td data-label="线上链接/地点">
                <a v-if="isLink(course.location)" :href="course.location" target="_blank" rel="noreferrer">打开</a>
                <span v-else>{{ course.location || '-' }}</span>
              </td>
              <td data-label="备注">{{ course.note || '-' }}</td>
            </tr>
            <tr v-if="courses.length === 0">
              <td colspan="8" class="empty">暂无课程</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </section>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { exportTeacherMonthlySchedule } from '../api/exports'
import { getErrorMessage } from '../api/http'
import { fetchTeacherMonthlySchedule } from '../api/schedules'
import { fetchTeachers } from '../api/teachers'

const teachers = ref([])
const courses = ref([])
const selectedTeacherId = ref('')
const error = ref('')
const message = ref('')
const summary = reactive({
  teacher_name: '',
  total_courses: 0,
  total_hours: 0,
  type_hours: []
})

function toMonthInput(date) {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  return `${year}-${month}`
}

const selectedMonth = ref(toMonthInput(new Date()))

function formatTime(value) {
  return value ? value.slice(0, 5) : ''
}

function isLink(value) {
  return /^https?:\/\//i.test(value || '')
}

function resetSummary() {
  Object.assign(summary, {
    teacher_name: '',
    total_courses: 0,
    total_hours: 0,
    type_hours: []
  })
}

async function loadTeachers() {
  const res = await fetchTeachers()
  teachers.value = res.data
}

async function loadSchedule() {
  error.value = ''
  message.value = ''
  courses.value = []
  resetSummary()

  if (!selectedTeacherId.value) {
    error.value = '请先选择老师。'
    return
  }
  if (!selectedMonth.value) {
    error.value = '请选择月份。'
    return
  }

  try {
    const res = await fetchTeacherMonthlySchedule(selectedTeacherId.value, selectedMonth.value)
    courses.value = res.data.courses
    Object.assign(summary, {
      teacher_name: res.data.teacher_name,
      total_courses: res.data.total_courses,
      total_hours: res.data.total_hours,
      type_hours: res.data.type_hours
    })
  } catch (err) {
    error.value = getErrorMessage(err, '老师月度课表加载失败。')
  }
}

async function downloadCsv() {
  error.value = ''
  message.value = ''
  if (!selectedTeacherId.value) {
    error.value = '请先选择老师。'
    return
  }
  if (!selectedMonth.value) {
    error.value = '请选择月份。'
    return
  }

  try {
    await exportTeacherMonthlySchedule(selectedTeacherId.value, selectedMonth.value)
    message.value = 'CSV 文件已开始下载。'
  } catch (err) {
    error.value = getErrorMessage(err, '老师月度课表导出失败。')
  }
}

onMounted(async () => {
  try {
    await loadTeachers()
  } catch (err) {
    error.value = getErrorMessage(err, '老师列表加载失败。')
  }
})
</script>

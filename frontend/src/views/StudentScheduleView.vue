<template>
  <section>
    <div class="page-header">
      <div>
        <h1>学生个人课表</h1>
        <p>选择学生和日期范围，查看该学生的课程安排。</p>
      </div>
    </div>

    <div v-if="error" class="alert alert-error">{{ error }}</div>

    <div class="panel">
      <div class="toolbar filters">
        <select v-model="selectedStudentId">
          <option value="">请选择学生</option>
          <option v-for="student in students" :key="student.id" :value="student.id">{{ student.name }}</option>
        </select>
        <input v-model="startDate" type="date" />
        <input v-model="endDate" type="date" />
        <button class="button button-primary" @click="loadSchedule">查看课表</button>
        <button class="button" @click="setThisWeek">本周</button>
        <button class="button" @click="setThisMonth">本月</button>
      </div>

      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>日期</th>
              <th>上课时间</th>
              <th>课程类型</th>
              <th>老师</th>
              <th>线上链接/地点</th>
              <th>备注</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="course in courses" :key="course.id">
              <td>{{ course.course_date }}</td>
              <td>{{ formatTime(course.start_time) }}-{{ formatTime(course.end_time) }}</td>
              <td><span class="tag">{{ course.course_type }}</span></td>
              <td>{{ course.teacher_name }}</td>
              <td>
                <a v-if="isLink(course.location)" :href="course.location" target="_blank" rel="noreferrer">打开</a>
                <span v-else>{{ course.location || '-' }}</span>
              </td>
              <td>{{ course.note || '-' }}</td>
            </tr>
            <tr v-if="courses.length === 0">
              <td colspan="6" class="empty">暂无课程</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </section>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { getErrorMessage } from '../api/http'
import { fetchStudentSchedule } from '../api/schedules'
import { fetchStudents } from '../api/students'

const students = ref([])
const courses = ref([])
const selectedStudentId = ref('')
const startDate = ref('')
const endDate = ref('')
const error = ref('')

function toDateInput(date) {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

function setThisWeek() {
  const today = new Date()
  const day = today.getDay() || 7
  const monday = new Date(today)
  monday.setDate(today.getDate() - day + 1)
  const sunday = new Date(monday)
  sunday.setDate(monday.getDate() + 6)
  startDate.value = toDateInput(monday)
  endDate.value = toDateInput(sunday)
}

function setThisMonth() {
  const today = new Date()
  const firstDay = new Date(today.getFullYear(), today.getMonth(), 1)
  const lastDay = new Date(today.getFullYear(), today.getMonth() + 1, 0)
  startDate.value = toDateInput(firstDay)
  endDate.value = toDateInput(lastDay)
}

function formatTime(value) {
  return value ? value.slice(0, 5) : ''
}

function isLink(value) {
  return /^https?:\/\//i.test(value || '')
}

async function loadStudents() {
  const res = await fetchStudents()
  students.value = res.data
}

async function loadSchedule() {
  error.value = ''
  courses.value = []
  if (!selectedStudentId.value) {
    error.value = '请先选择学生。'
    return
  }
  if (!startDate.value || !endDate.value) {
    error.value = '请选择开始日期和结束日期。'
    return
  }

  try {
    const res = await fetchStudentSchedule(selectedStudentId.value, startDate.value, endDate.value)
    courses.value = res.data
  } catch (err) {
    error.value = getErrorMessage(err, '学生课表加载失败。')
  }
}

onMounted(async () => {
  setThisWeek()
  try {
    await loadStudents()
  } catch (err) {
    error.value = getErrorMessage(err, '学生列表加载失败。')
  }
})
</script>

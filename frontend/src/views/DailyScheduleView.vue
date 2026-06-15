<template>
  <section>
    <div class="page-header">
      <div>
        <h1>每日总课表</h1>
        <p>选择日期，查看当天全部课程，并复制提醒消息。</p>
      </div>
    </div>

    <div v-if="message" class="alert alert-success">{{ message }}</div>
    <div v-if="error" class="alert alert-error">{{ error }}</div>

    <div class="panel">
      <div class="toolbar filters">
        <input v-model="selectedDate" type="date" />
        <button class="button button-primary" @click="loadSchedule">查看课表</button>
        <button class="button" @click="copyAllReminders" :disabled="courses.length === 0">复制全部提醒</button>
        <button class="button" @click="downloadCsv">导出 CSV</button>
      </div>

      <div class="summary-strip">
        <div class="summary-item">
          <span>当天课程数</span>
          <strong>{{ courses.length }} 节</strong>
        </div>
        <div class="summary-item">
          <span>总时长</span>
          <strong>{{ totalHours }} 小时</strong>
        </div>
      </div>

      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>上课时间</th>
              <th>学生</th>
              <th>老师</th>
              <th>课程类型</th>
              <th>时长</th>
              <th>备注</th>
              <th>提醒</th>
            </tr>
            </thead>
            <tbody>
              <tr v-for="course in courses" :key="course.id">
              <td data-label="上课时间">{{ formatTime(course.start_time) }}-{{ formatTime(course.end_time) }}</td>
              <td data-label="学生">{{ course.student_name }}</td>
              <td data-label="老师">{{ course.teacher_name }}</td>
              <td data-label="课程类型"><span class="tag">{{ course.course_type }}</span></td>
              <td data-label="时长">{{ course.duration_hours }} 小时</td>
              <td data-label="备注">{{ course.note || '-' }}</td>
              <td data-label="提醒">
                <button class="link-button" @click="copyReminder(course)">复制</button>
              </td>
            </tr>
            <tr v-if="courses.length === 0">
              <td colspan="7" class="empty">当天暂无课程</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { exportDailySchedule } from '../api/exports'
import { getErrorMessage } from '../api/http'
import { fetchDailySchedule } from '../api/schedules'

function toDateInput(date) {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

const selectedDate = ref(toDateInput(new Date()))
const courses = ref([])
const error = ref('')
const message = ref('')
const totalHours = computed(() => courses.value.reduce((sum, course) => sum + Number(course.duration_hours || 0), 0).toFixed(2))

function resetNotice() {
  error.value = ''
  message.value = ''
}

function formatTime(value) {
  return value ? value.slice(0, 5) : ''
}

function formatChineseDate(dateValue) {
  const [, month, day] = dateValue.split('-').map(Number)
  return `${month} 月 ${day} 号`
}

function buildReminder(course) {
  return `亲们，咱们明天${course.course_type}上课时间为 ${formatChineseDate(course.course_date)} ${formatTime(course.start_time)}-${formatTime(course.end_time)} 哈～`
}

async function copyText(text, successText) {
  resetNotice()
  try {
    await navigator.clipboard.writeText(text)
    message.value = successText
  } catch {
    error.value = '复制失败，请检查浏览器剪贴板权限。'
  }
}

function copyReminder(course) {
  copyText(buildReminder(course), '提醒消息已复制。')
}

function copyAllReminders() {
  const text = courses.value.map(buildReminder).join('\n')
  copyText(text, '全部提醒消息已复制。')
}

async function loadSchedule() {
  resetNotice()
  try {
    const res = await fetchDailySchedule(selectedDate.value)
    courses.value = res.data
  } catch (err) {
    error.value = getErrorMessage(err, '每日课表加载失败。')
  }
}

async function downloadCsv() {
  resetNotice()
  if (!selectedDate.value) {
    error.value = '请先选择日期。'
    return
  }

  try {
    await exportDailySchedule(selectedDate.value)
    message.value = 'CSV 文件已开始下载。'
  } catch (err) {
    error.value = getErrorMessage(err, '每日课表导出失败。')
  }
}

onMounted(loadSchedule)
</script>

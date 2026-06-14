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
              <th>线上链接/地点</th>
              <th>备注</th>
              <th>提醒</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="course in courses" :key="course.id">
              <td>{{ formatTime(course.start_time) }}-{{ formatTime(course.end_time) }}</td>
              <td>{{ course.student_name }}</td>
              <td>{{ course.teacher_name }}</td>
              <td><span class="tag">{{ course.course_type }}</span></td>
              <td>{{ course.duration_hours }} 小时</td>
              <td>
                <a v-if="isLink(course.location)" :href="course.location" target="_blank" rel="noreferrer">打开</a>
                <span v-else>{{ course.location || '-' }}</span>
              </td>
              <td>{{ course.note || '-' }}</td>
              <td>
                <button class="link-button" @click="copyReminder(course)">复制</button>
              </td>
            </tr>
            <tr v-if="courses.length === 0">
              <td colspan="8" class="empty">当天暂无课程</td>
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

function resetNotice() {
  error.value = ''
  message.value = ''
}

function formatTime(value) {
  return value ? value.slice(0, 5) : ''
}

function isLink(value) {
  return /^https?:\/\//i.test(value || '')
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

onMounted(loadSchedule)
</script>

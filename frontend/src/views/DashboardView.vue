<template>
  <section>
    <div class="page-header">
      <div>
        <h1>首页仪表盘</h1>
        <p>第一阶段已实现学生、老师、课程和冲突检测。</p>
      </div>
    </div>

    <div v-if="error" class="alert alert-error">{{ error }}</div>

    <div class="stats-grid">
      <div class="stat-card">
        <span>今日课程</span>
        <strong>{{ todayCourses }}</strong>
      </div>
      <div class="stat-card">
        <span>本月课程</span>
        <strong>{{ monthCourses }}</strong>
      </div>
      <div class="stat-card">
        <span>学生数量</span>
        <strong>{{ students.length }}</strong>
      </div>
      <div class="stat-card">
        <span>老师数量</span>
        <strong>{{ teachers.length }}</strong>
      </div>
    </div>

    <div class="panel">
      <h2>快速开始</h2>
      <div class="quick-links">
        <RouterLink class="button" to="/students">录入学生</RouterLink>
        <RouterLink class="button" to="/teachers">录入老师</RouterLink>
        <RouterLink class="button button-primary" to="/courses">新增课程</RouterLink>
        <RouterLink class="button" to="/daily-schedule">查看每日课表</RouterLink>
        <RouterLink class="button" to="/student-schedule">查看学生课表</RouterLink>
        <RouterLink class="button" to="/teacher-monthly">老师月度统计</RouterLink>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { fetchCourses } from '../api/courses'
import { fetchStudents } from '../api/students'
import { fetchTeachers } from '../api/teachers'
import { getErrorMessage } from '../api/http'

const students = ref([])
const teachers = ref([])
const courses = ref([])
const error = ref('')

function toDateInput(date) {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

const today = toDateInput(new Date())
const currentMonth = today.slice(0, 7)

const todayCourses = computed(() => courses.value.filter((course) => course.course_date === today).length)
const monthCourses = computed(() => courses.value.filter((course) => course.course_date.startsWith(currentMonth)).length)

async function loadDashboard() {
  error.value = ''
  try {
    const [studentRes, teacherRes, courseRes] = await Promise.all([
      fetchStudents(),
      fetchTeachers(),
      fetchCourses()
    ])
    students.value = studentRes.data
    teachers.value = teacherRes.data
    courses.value = courseRes.data
  } catch (err) {
    error.value = getErrorMessage(err, '仪表盘数据加载失败。')
  }
}

onMounted(loadDashboard)
</script>

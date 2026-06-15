<template>
  <section>
    <div class="page-header">
      <div>
        <h1>今日工作台</h1>
        <p>快速确认今日课程、近期排课和基础资料状态。</p>
      </div>
      <RouterLink class="button button-primary" to="/courses">新增课程</RouterLink>
    </div>

    <div v-if="error" class="alert alert-error">{{ error }}</div>
    <div v-if="loading" class="loading-bar">正在加载工作台数据...</div>

    <div class="stats-grid">
      <div class="stat-card">
        <span>今日课程</span>
        <strong>{{ todayCourses }}</strong>
        <small>{{ today }}</small>
      </div>
      <div class="stat-card">
        <span>本月课程</span>
        <strong>{{ monthCourses }}</strong>
        <small>{{ currentMonth }}</small>
      </div>
      <div class="stat-card">
        <span>学生数量</span>
        <strong>{{ students.length }}</strong>
        <small>在读、暂停、结课</small>
      </div>
      <div class="stat-card">
        <span>老师数量</span>
        <strong>{{ teachers.length }}</strong>
        <small>可参与排课</small>
      </div>
    </div>

    <div class="dashboard-grid">
      <div class="panel">
        <div class="panel-header">
          <div>
            <h2>今日课程</h2>
            <p>{{ todayCourses ? '按上课时间排序' : '今天还没有课程安排' }}</p>
          </div>
          <RouterLink class="link-button" to="/daily-schedule">查看全部</RouterLink>
        </div>

        <div v-if="todayList.length" class="schedule-list">
          <div v-for="course in todayList" :key="course.id" class="schedule-row">
            <time>{{ formatTime(course.start_time) }}-{{ formatTime(course.end_time) }}</time>
            <div>
              <strong>{{ course.student_name }} · {{ course.course_type }}</strong>
              <span>{{ course.teacher_name }}，{{ course.duration_hours }} 小时</span>
            </div>
          </div>
        </div>
        <div v-else class="empty-state">
          <strong>今日暂无课程</strong>
          <span>可以先去排课管理新增课程，或查看每日总课表确认安排。</span>
        </div>
      </div>

      <div class="panel">
        <div class="panel-header">
          <div>
            <h2>近期安排</h2>
            <p>未来 5 节课程</p>
          </div>
        </div>

        <div v-if="upcomingCourses.length" class="schedule-list">
          <div v-for="course in upcomingCourses" :key="course.id" class="schedule-row">
            <time>{{ course.course_date }}</time>
            <div>
              <strong>{{ formatTime(course.start_time) }} {{ course.student_name }}</strong>
              <span>{{ course.teacher_name }} · {{ course.course_type }}</span>
            </div>
          </div>
        </div>
        <div v-else class="empty-state">
          <strong>暂无后续课程</strong>
          <span>完成学生和老师录入后，就可以开始创建排课。</span>
        </div>
      </div>
    </div>

    <div class="panel action-panel">
      <div class="panel-header">
        <div>
          <h2>常用操作</h2>
          <p>按助教日常工作流组织</p>
        </div>
      </div>
      <div class="action-grid">
        <RouterLink class="action-tile" to="/students">
          <strong>录入学生</strong>
          <span>维护状态和备注</span>
        </RouterLink>
        <RouterLink class="action-tile" to="/teachers">
          <strong>录入老师</strong>
          <span>维护授课科目和备注</span>
        </RouterLink>
        <RouterLink class="action-tile primary" to="/courses">
          <strong>安排课程</strong>
          <span>保存前自动检查老师和学生冲突</span>
        </RouterLink>
        <RouterLink class="action-tile" to="/teacher-monthly">
          <strong>月度统计</strong>
          <span>查看老师课时并导出 CSV</span>
        </RouterLink>
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
const loading = ref(false)

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
const todayList = computed(() =>
  courses.value
    .filter((course) => course.course_date === today)
    .sort((a, b) => a.start_time.localeCompare(b.start_time))
)
const upcomingCourses = computed(() =>
  courses.value
    .filter((course) => course.course_date >= today)
    .sort((a, b) => `${a.course_date} ${a.start_time}`.localeCompare(`${b.course_date} ${b.start_time}`))
    .slice(0, 5)
)

function formatTime(value) {
  return value ? value.slice(0, 5) : ''
}

async function loadDashboard() {
  error.value = ''
  loading.value = true
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
  } finally {
    loading.value = false
  }
}

onMounted(loadDashboard)
</script>

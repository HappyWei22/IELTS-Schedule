<template>
  <section>
    <div class="page-header">
      <div>
        <h1>排课管理</h1>
        <p>新增、编辑课程，并自动检测老师和学生时间冲突。</p>
      </div>
    </div>

    <div v-if="message" class="alert alert-success">{{ message }}</div>
    <div v-if="error" class="alert alert-error">{{ error }}</div>

    <div class="layout-grid wide-left">
      <form class="panel form-panel" @submit.prevent="submitForm">
        <h2>{{ editingId ? '编辑课程' : '新增课程' }}</h2>

        <label>
          学生
          <select v-model.number="form.student_id" required>
            <option value="" disabled>请选择学生</option>
            <option v-for="student in students" :key="student.id" :value="student.id">
              {{ student.name }}
            </option>
          </select>
        </label>

        <label>
          老师
          <select v-model.number="form.teacher_id" required>
            <option value="" disabled>请选择老师</option>
            <option v-for="teacher in teachers" :key="teacher.id" :value="teacher.id">
              {{ teacher.name }}（{{ teacher.subject }}）
            </option>
          </select>
        </label>

        <label>
          课程类型
          <input v-model.trim="form.course_type" required placeholder="听力、阅读、写作、口语或自定义" />
        </label>

        <div class="two-columns">
          <label>
            上课日期
            <input v-model="form.course_date" type="date" required />
          </label>
          <label>
            开始时间
            <input v-model="form.start_time" type="time" required @change="fillDefaultEndTime" />
          </label>
        </div>

        <div class="two-columns">
          <label>
            结束时间
            <input v-model="form.end_time" type="time" required />
          </label>
          <label>
            线上链接/地点
            <input v-model.trim="form.location" placeholder="可选" />
          </label>
        </div>

        <label>
          备注
          <textarea v-model.trim="form.note" rows="3" placeholder="可选"></textarea>
        </label>

        <div class="button-row">
          <button class="button button-primary" type="submit">{{ editingId ? '保存修改' : '新增课程' }}</button>
          <button v-if="editingId" class="button" type="button" @click="resetForm">取消编辑</button>
        </div>
      </form>

      <div class="panel">
        <div class="toolbar filters">
          <input v-model="filters.date" type="date" title="按日期筛选" />
          <select v-model="filters.student_id">
            <option value="">全部学生</option>
            <option v-for="student in students" :key="student.id" :value="student.id">{{ student.name }}</option>
          </select>
          <select v-model="filters.teacher_id">
            <option value="">全部老师</option>
            <option v-for="teacher in teachers" :key="teacher.id" :value="teacher.id">{{ teacher.name }}</option>
          </select>
          <button class="button" @click="loadCourses">筛选</button>
          <button class="button" @click="clearFilters">清空</button>
        </div>

        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>日期</th>
                <th>时间</th>
                <th>学生</th>
                <th>老师</th>
                <th>课程</th>
                <th>时长</th>
                <th>线上链接/地点</th>
                <th>备注</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="course in courses" :key="course.id">
                <td>{{ course.course_date }}</td>
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
                <td class="actions">
                  <button class="link-button" @click="editCourse(course)">编辑</button>
                  <button class="link-button danger" @click="removeCourse(course)">删除</button>
                </td>
              </tr>
              <tr v-if="courses.length === 0">
                <td colspan="9" class="empty">暂无课程</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { createCourse, deleteCourse, fetchCourses, updateCourse } from '../api/courses'
import { fetchStudents } from '../api/students'
import { fetchTeachers } from '../api/teachers'
import { getErrorMessage } from '../api/http'

const students = ref([])
const teachers = ref([])
const courses = ref([])
const editingId = ref(null)
const error = ref('')
const message = ref('')

const form = reactive({
  student_id: '',
  teacher_id: '',
  course_type: '',
  course_date: '',
  start_time: '',
  end_time: '',
  location: '',
  note: ''
})

const filters = reactive({
  date: '',
  student_id: '',
  teacher_id: ''
})

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

function addTwoHours(timeValue) {
  if (!timeValue) return ''
  const [hours, minutes] = timeValue.split(':').map(Number)
  const date = new Date()
  date.setHours(hours + 2, minutes, 0, 0)
  return `${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
}

function fillDefaultEndTime() {
  if (form.start_time && !editingId.value) {
    form.end_time = addTwoHours(form.start_time)
  }
}

function resetForm() {
  editingId.value = null
  Object.assign(form, {
    student_id: '',
    teacher_id: '',
    course_type: '',
    course_date: '',
    start_time: '',
    end_time: '',
    location: '',
    note: ''
  })
}

async function loadBaseData() {
  const [studentRes, teacherRes] = await Promise.all([fetchStudents(), fetchTeachers()])
  students.value = studentRes.data
  teachers.value = teacherRes.data
}

async function loadCourses() {
  resetNotice()
  try {
    const res = await fetchCourses(filters)
    courses.value = res.data
  } catch (err) {
    error.value = getErrorMessage(err, '课程列表加载失败。')
  }
}

async function submitForm() {
  resetNotice()
  try {
    const payload = {
      ...form,
      student_id: Number(form.student_id),
      teacher_id: Number(form.teacher_id)
    }

    if (editingId.value) {
      await updateCourse(editingId.value, payload)
      message.value = '课程已更新。'
    } else {
      await createCourse(payload)
      message.value = '课程已新增。'
    }
    resetForm()
    await loadCourses()
  } catch (err) {
    error.value = getErrorMessage(err, '课程保存失败。')
  }
}

function editCourse(course) {
  resetNotice()
  editingId.value = course.id
  Object.assign(form, {
    student_id: course.student_id,
    teacher_id: course.teacher_id,
    course_type: course.course_type,
    course_date: course.course_date,
    start_time: formatTime(course.start_time),
    end_time: formatTime(course.end_time),
    location: course.location || '',
    note: course.note || ''
  })
}

async function removeCourse(course) {
  resetNotice()
  if (!window.confirm(`确定删除 ${course.course_date} ${course.student_name} 的课程吗？`)) return
  try {
    await deleteCourse(course.id)
    message.value = '课程已删除。'
    await loadCourses()
  } catch (err) {
    error.value = getErrorMessage(err, '课程删除失败。')
  }
}

function clearFilters() {
  Object.assign(filters, { date: '', student_id: '', teacher_id: '' })
  loadCourses()
}

onMounted(async () => {
  try {
    await loadBaseData()
    await loadCourses()
  } catch (err) {
    error.value = getErrorMessage(err, '基础数据加载失败，请确认后端已启动。')
  }
})
</script>

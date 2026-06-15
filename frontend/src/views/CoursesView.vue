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

        <div class="field-group">
          <label for="course-student-search">学生</label>
          <div class="search-picker">
            <input
              id="course-student-search"
              v-model.trim="studentSearch"
              autocomplete="off"
              placeholder="输入学生姓名搜索"
              @focus="studentPickerOpen = true"
              @input="studentPickerOpen = true"
            />
            <div v-if="selectedStudent" class="selected-pill">
              <span>已选：{{ selectedStudent.name }}</span>
              <button type="button" class="link-button" @click="clearSelectedStudent">更换</button>
            </div>
            <div v-if="studentPickerOpen" class="search-results">
              <button
                v-for="student in filteredStudents"
                :key="student.id"
                type="button"
                class="search-result"
                @click="selectStudent(student)"
              >
                <strong>{{ student.name }}</strong>
                <span>{{ student.status }}</span>
              </button>
              <div v-if="filteredStudents.length === 0" class="search-empty">
                没有找到匹配学生，请先到学生管理新增。
              </div>
            </div>
          </div>
        </div>

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

        <label>
          结束时间
          <input v-model="form.end_time" type="time" required />
        </label>

        <label>
          备注
          <textarea v-model.trim="form.note" rows="3" placeholder="可选"></textarea>
        </label>

        <div class="button-row">
          <button class="button button-primary" type="submit" :disabled="submitting">
            {{ submitting ? '保存中...' : editingId ? '保存修改' : '新增课程' }}
          </button>
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
                <th>备注</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="course in courses" :key="course.id">
                <td data-label="日期">{{ course.course_date }}</td>
                <td data-label="时间">{{ formatTime(course.start_time) }}-{{ formatTime(course.end_time) }}</td>
                <td data-label="学生">{{ course.student_name }}</td>
                <td data-label="老师">{{ course.teacher_name }}</td>
                <td data-label="课程"><span class="tag">{{ course.course_type }}</span></td>
                <td data-label="时长">{{ course.duration_hours }} 小时</td>
                <td data-label="备注">{{ course.note || '-' }}</td>
                <td data-label="操作" class="actions">
                  <button class="link-button" @click="editCourse(course)">编辑</button>
                  <button class="link-button danger" @click="removeCourse(course)">删除</button>
                </td>
              </tr>
              <tr v-if="courses.length === 0">
                <td colspan="8" class="empty">暂无课程</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
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
const submitting = ref(false)
const studentSearch = ref('')
const studentPickerOpen = ref(false)

const form = reactive({
  student_id: '',
  teacher_id: '',
  course_type: '',
  course_date: '',
  start_time: '',
  end_time: '',
  note: ''
})

const filters = reactive({
  date: '',
  student_id: '',
  teacher_id: ''
})

const selectedStudent = computed(() => students.value.find((student) => student.id === Number(form.student_id)))
const filteredStudents = computed(() => {
  const keyword = studentSearch.value.trim().toLowerCase()
  const list = keyword
    ? students.value.filter((student) =>
        [student.name, student.status].some((value) => String(value || '').toLowerCase().includes(keyword))
      )
    : students.value
  return list.slice(0, 8)
})

function resetNotice() {
  error.value = ''
  message.value = ''
}

function formatTime(value) {
  return value ? value.slice(0, 5) : ''
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

function selectStudent(student) {
  form.student_id = student.id
  studentSearch.value = student.name
  studentPickerOpen.value = false
}

function clearSelectedStudent() {
  form.student_id = ''
  studentSearch.value = ''
  studentPickerOpen.value = true
}

function resetForm() {
  editingId.value = null
  studentSearch.value = ''
  studentPickerOpen.value = false
  Object.assign(form, {
    student_id: '',
    teacher_id: '',
    course_type: '',
    course_date: '',
    start_time: '',
    end_time: '',
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
  if (!form.student_id) {
    error.value = '请先搜索并选择学生。'
    return
  }
  submitting.value = true
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
  } finally {
    submitting.value = false
  }
}

function editCourse(course) {
  resetNotice()
  editingId.value = course.id
  studentSearch.value = course.student_name
  studentPickerOpen.value = false
  Object.assign(form, {
    student_id: course.student_id,
    teacher_id: course.teacher_id,
    course_type: course.course_type,
    course_date: course.course_date,
    start_time: formatTime(course.start_time),
    end_time: formatTime(course.end_time),
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

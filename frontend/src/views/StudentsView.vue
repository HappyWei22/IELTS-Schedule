<template>
  <section>
    <div class="page-header">
      <div>
        <h1>学生管理</h1>
        <p>手动录入学生信息，并按姓名搜索。</p>
      </div>
    </div>

    <div v-if="message" class="alert alert-success">{{ message }}</div>
    <div v-if="error" class="alert alert-error">{{ error }}</div>

    <div class="layout-grid">
      <form class="panel form-panel" @submit.prevent="submitForm">
        <h2>{{ editingId ? '编辑学生' : '新增学生' }}</h2>
        <label>
          学生姓名
          <input v-model.trim="form.name" required placeholder="例如：李同学" />
        </label>
        <label>
          联系方式
          <input v-model.trim="form.phone" placeholder="手机或微信，可选" />
        </label>
        <label>
          当前状态
          <select v-model="form.status">
            <option>在读</option>
            <option>暂停</option>
            <option>结课</option>
          </select>
        </label>
        <label>
          备注
          <textarea v-model.trim="form.note" rows="4" placeholder="可选"></textarea>
        </label>
        <div class="button-row">
          <button class="button button-primary" type="submit">{{ editingId ? '保存修改' : '新增学生' }}</button>
          <button v-if="editingId" class="button" type="button" @click="resetForm">取消编辑</button>
        </div>
      </form>

      <div class="panel">
        <div class="toolbar">
          <input v-model.trim="keyword" placeholder="按姓名搜索学生" @keyup.enter="loadStudents" />
          <button class="button" @click="loadStudents">搜索</button>
        </div>

        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>姓名</th>
                <th>联系方式</th>
                <th>状态</th>
                <th>备注</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="student in students" :key="student.id">
                <td>{{ student.name }}</td>
                <td>{{ student.phone || '-' }}</td>
                <td><span class="tag">{{ student.status }}</span></td>
                <td>{{ student.note || '-' }}</td>
                <td class="actions">
                  <button class="link-button" @click="editStudent(student)">编辑</button>
                  <button class="link-button danger" @click="removeStudent(student)">删除</button>
                </td>
              </tr>
              <tr v-if="students.length === 0">
                <td colspan="5" class="empty">暂无学生</td>
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
import { createStudent, deleteStudent, fetchStudents, updateStudent } from '../api/students'
import { getErrorMessage } from '../api/http'

const students = ref([])
const keyword = ref('')
const editingId = ref(null)
const error = ref('')
const message = ref('')
const form = reactive({
  name: '',
  phone: '',
  status: '在读',
  note: ''
})

function resetNotice() {
  error.value = ''
  message.value = ''
}

function resetForm() {
  editingId.value = null
  Object.assign(form, { name: '', phone: '', status: '在读', note: '' })
}

async function loadStudents() {
  resetNotice()
  try {
    const res = await fetchStudents(keyword.value)
    students.value = res.data
  } catch (err) {
    error.value = getErrorMessage(err, '学生列表加载失败。')
  }
}

async function submitForm() {
  resetNotice()
  try {
    if (editingId.value) {
      await updateStudent(editingId.value, form)
      message.value = '学生信息已更新。'
    } else {
      await createStudent(form)
      message.value = '学生已新增。'
    }
    resetForm()
    await loadStudents()
  } catch (err) {
    error.value = getErrorMessage(err, '学生保存失败。')
  }
}

function editStudent(student) {
  resetNotice()
  editingId.value = student.id
  Object.assign(form, {
    name: student.name,
    phone: student.phone || '',
    status: student.status,
    note: student.note || ''
  })
}

async function removeStudent(student) {
  resetNotice()
  if (!window.confirm(`确定删除学生“${student.name}”吗？`)) return
  try {
    await deleteStudent(student.id)
    message.value = '学生已删除。'
    await loadStudents()
  } catch (err) {
    error.value = getErrorMessage(err, '学生删除失败。')
  }
}

onMounted(loadStudents)
</script>

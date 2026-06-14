<template>
  <section>
    <div class="page-header">
      <div>
        <h1>老师管理</h1>
        <p>维护老师姓名、科目和联系方式。</p>
      </div>
    </div>

    <div v-if="message" class="alert alert-success">{{ message }}</div>
    <div v-if="error" class="alert alert-error">{{ error }}</div>

    <div class="layout-grid">
      <form class="panel form-panel" @submit.prevent="submitForm">
        <h2>{{ editingId ? '编辑老师' : '新增老师' }}</h2>
        <label>
          老师姓名
          <input v-model.trim="form.name" required placeholder="例如：张老师" />
        </label>
        <label>
          教授科目
          <input v-model.trim="form.subject" required placeholder="听力、阅读、写作、口语或自定义" />
        </label>
        <label>
          联系方式
          <input v-model.trim="form.phone" placeholder="手机或微信，可选" />
        </label>
        <label>
          备注
          <textarea v-model.trim="form.note" rows="4" placeholder="可选"></textarea>
        </label>
        <div class="button-row">
          <button class="button button-primary" type="submit">{{ editingId ? '保存修改' : '新增老师' }}</button>
          <button v-if="editingId" class="button" type="button" @click="resetForm">取消编辑</button>
        </div>
      </form>

      <div class="panel">
        <div class="toolbar">
          <input v-model.trim="keyword" placeholder="按姓名搜索老师" @keyup.enter="loadTeachers" />
          <button class="button" @click="loadTeachers">搜索</button>
        </div>

        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>姓名</th>
                <th>科目</th>
                <th>联系方式</th>
                <th>备注</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="teacher in teachers" :key="teacher.id">
                <td>{{ teacher.name }}</td>
                <td><span class="tag">{{ teacher.subject }}</span></td>
                <td>{{ teacher.phone || '-' }}</td>
                <td>{{ teacher.note || '-' }}</td>
                <td class="actions">
                  <button class="link-button" @click="editTeacher(teacher)">编辑</button>
                  <button class="link-button danger" @click="removeTeacher(teacher)">删除</button>
                </td>
              </tr>
              <tr v-if="teachers.length === 0">
                <td colspan="5" class="empty">暂无老师</td>
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
import { createTeacher, deleteTeacher, fetchTeachers, updateTeacher } from '../api/teachers'
import { getErrorMessage } from '../api/http'

const teachers = ref([])
const keyword = ref('')
const editingId = ref(null)
const error = ref('')
const message = ref('')
const form = reactive({
  name: '',
  subject: '',
  phone: '',
  note: ''
})

function resetNotice() {
  error.value = ''
  message.value = ''
}

function resetForm() {
  editingId.value = null
  Object.assign(form, { name: '', subject: '', phone: '', note: '' })
}

async function loadTeachers() {
  resetNotice()
  try {
    const res = await fetchTeachers(keyword.value)
    teachers.value = res.data
  } catch (err) {
    error.value = getErrorMessage(err, '老师列表加载失败。')
  }
}

async function submitForm() {
  resetNotice()
  try {
    if (editingId.value) {
      await updateTeacher(editingId.value, form)
      message.value = '老师信息已更新。'
    } else {
      await createTeacher(form)
      message.value = '老师已新增。'
    }
    resetForm()
    await loadTeachers()
  } catch (err) {
    error.value = getErrorMessage(err, '老师保存失败。')
  }
}

function editTeacher(teacher) {
  resetNotice()
  editingId.value = teacher.id
  Object.assign(form, {
    name: teacher.name,
    subject: teacher.subject,
    phone: teacher.phone || '',
    note: teacher.note || ''
  })
}

async function removeTeacher(teacher) {
  resetNotice()
  if (!window.confirm(`确定删除老师“${teacher.name}”吗？`)) return
  try {
    await deleteTeacher(teacher.id)
    message.value = '老师已删除。'
    await loadTeachers()
  } catch (err) {
    error.value = getErrorMessage(err, '老师删除失败。')
  }
}

onMounted(loadTeachers)
</script>

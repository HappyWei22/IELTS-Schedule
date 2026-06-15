<template>
  <section>
    <div class="page-header">
      <div>
        <h1>老师管理</h1>
        <p>维护老师姓名、科目和备注。</p>
      </div>
    </div>

    <div v-if="message" class="alert alert-success">{{ message }}</div>
    <div v-if="error" class="alert alert-error">{{ error }}</div>

    <div class="layout-grid">
      <div class="side-stack">
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
            备注
            <textarea v-model.trim="form.note" rows="4" placeholder="可选"></textarea>
          </label>
          <div class="button-row">
            <button class="button button-primary" type="submit" :disabled="submitting">
              {{ submitting ? '保存中...' : editingId ? '保存修改' : '新增老师' }}
            </button>
            <button v-if="editingId" class="button" type="button" @click="resetForm">取消编辑</button>
          </div>
        </form>
      </div>

      <div class="panel">
        <div class="toolbar">
          <input v-model.trim="keyword" placeholder="按姓名搜索老师" @keyup.enter="loadTeachers" />
          <button class="button" @click="loadTeachers">搜索</button>
          <button class="button" :class="{ 'button-primary': selectionMode }" @click="toggleSelectionMode">
            {{ selectionMode ? '退出多选' : '多选' }}
          </button>
        </div>

        <div v-if="selectionMode" class="bulk-toolbar">
          <strong>已选择 {{ selectedIds.length }} 位老师</strong>
          <input v-model.trim="bulkSubject" placeholder="批量修改科目" />
          <input v-model.trim="bulkNote" placeholder="批量备注，可选" />
          <button class="button" @click="submitBulkUpdate" :disabled="selectedIds.length === 0 || bulkSubmitting">批量修改</button>
          <button class="button" @click="clearSelection" :disabled="selectedIds.length === 0">取消选择</button>
          <button class="button button-danger" @click="submitBulkDelete" :disabled="selectedIds.length === 0 || bulkSubmitting">批量删除</button>
        </div>

        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th v-if="selectionMode" class="select-cell">
                  <input type="checkbox" :checked="allSelected" @change="toggleAll($event.target.checked)" />
                </th>
                <th>姓名</th>
                <th>科目</th>
                <th>备注</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="teacher in teachers" :key="teacher.id">
                <td v-if="selectionMode" class="select-cell">
                  <input v-model="selectedIds" type="checkbox" :value="teacher.id" />
                </td>
                <td data-label="姓名">{{ teacher.name }}</td>
                <td data-label="科目"><span class="tag">{{ teacher.subject }}</span></td>
                <td data-label="备注">{{ teacher.note || '-' }}</td>
                <td data-label="操作" class="actions">
                  <button class="link-button" @click="editTeacher(teacher)">编辑</button>
                  <button class="link-button danger" @click="removeTeacher(teacher)">删除</button>
                </td>
              </tr>
              <tr v-if="teachers.length === 0">
                <td :colspan="selectionMode ? 5 : 4" class="empty">暂无老师</td>
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
import { bulkDeleteTeachers, bulkUpdateTeachers, createTeacher, deleteTeacher, fetchTeachers, updateTeacher } from '../api/teachers'
import { getErrorMessage } from '../api/http'

const teachers = ref([])
const keyword = ref('')
const editingId = ref(null)
const error = ref('')
const message = ref('')
const submitting = ref(false)
const bulkSubmitting = ref(false)
const selectionMode = ref(false)
const selectedIds = ref([])
const bulkSubject = ref('')
const bulkNote = ref('')
const form = reactive({
  name: '',
  subject: '',
  note: ''
})

function resetNotice() {
  error.value = ''
  message.value = ''
}

function resetForm() {
  editingId.value = null
  Object.assign(form, { name: '', subject: '', note: '' })
}

const allSelected = computed(() => teachers.value.length > 0 && selectedIds.value.length === teachers.value.length)

function toggleAll(checked) {
  selectedIds.value = checked ? teachers.value.map((teacher) => teacher.id) : []
}

function clearSelection() {
  selectedIds.value = []
}

function toggleSelectionMode() {
  selectionMode.value = !selectionMode.value
  if (!selectionMode.value) {
    clearSelection()
    bulkSubject.value = ''
    bulkNote.value = ''
  }
}

async function loadTeachers() {
  resetNotice()
  try {
    const res = await fetchTeachers(keyword.value)
    teachers.value = res.data
    selectedIds.value = selectedIds.value.filter((id) => teachers.value.some((teacher) => teacher.id === id))
  } catch (err) {
    error.value = getErrorMessage(err, '老师列表加载失败。')
  }
}

async function submitForm() {
  resetNotice()
  submitting.value = true
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
  } finally {
    submitting.value = false
  }
}

async function submitBulkUpdate() {
  resetNotice()
  if (selectedIds.value.length === 0) {
    error.value = '请先勾选要修改的老师。'
    return
  }
  if (!bulkSubject.value && !bulkNote.value) {
    error.value = '请填写要批量修改的科目或备注。'
    return
  }

  bulkSubmitting.value = true
  try {
    const payload = { ids: selectedIds.value }
    if (bulkSubject.value) payload.subject = bulkSubject.value
    if (bulkNote.value) payload.note = bulkNote.value
    const res = await bulkUpdateTeachers(payload)
    message.value = `已批量修改 ${res.data.affected_count} 位老师。`
    bulkSubject.value = ''
    bulkNote.value = ''
    selectionMode.value = false
    selectedIds.value = []
    await loadTeachers()
  } catch (err) {
    error.value = getErrorMessage(err, '批量修改老师失败。')
  } finally {
    bulkSubmitting.value = false
  }
}

async function submitBulkDelete() {
  resetNotice()
  if (selectedIds.value.length === 0) {
    error.value = '请先勾选要删除的老师。'
    return
  }
  if (!window.confirm(`确定删除选中的 ${selectedIds.value.length} 位老师吗？`)) return

  bulkSubmitting.value = true
  try {
    const res = await bulkDeleteTeachers(selectedIds.value)
    message.value = `已批量删除 ${res.data.affected_count} 位老师。`
    selectedIds.value = []
    selectionMode.value = false
    await loadTeachers()
  } catch (err) {
    error.value = getErrorMessage(err, '批量删除老师失败。')
  } finally {
    bulkSubmitting.value = false
  }
}

function editTeacher(teacher) {
  resetNotice()
  editingId.value = teacher.id
  Object.assign(form, {
    name: teacher.name,
    subject: teacher.subject,
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

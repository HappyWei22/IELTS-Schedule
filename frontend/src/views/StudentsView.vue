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
      <div class="side-stack">
        <form class="panel form-panel" @submit.prevent="submitForm">
          <h2>{{ editingId ? '编辑学生' : '新增学生' }}</h2>
          <label>
            学生姓名
            <input v-model.trim="form.name" required placeholder="例如：李同学" />
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
            <button class="button button-primary" type="submit" :disabled="submitting">
              {{ submitting ? '保存中...' : editingId ? '保存修改' : '新增学生' }}
            </button>
            <button v-if="editingId" class="button" type="button" @click="resetForm">取消编辑</button>
          </div>
        </form>
      </div>

      <div class="panel">
        <div class="toolbar">
          <input v-model.trim="keyword" placeholder="按姓名搜索学生" @keyup.enter="loadStudents" />
          <button class="button" @click="loadStudents">搜索</button>
          <button class="button" :class="{ 'button-primary': selectionMode }" @click="toggleSelectionMode">
            {{ selectionMode ? '退出多选' : '多选' }}
          </button>
        </div>

        <div v-if="selectionMode" class="bulk-toolbar">
          <strong>已选择 {{ selectedIds.length }} 名学生</strong>
          <select v-model="bulkStatus">
            <option value="">批量修改状态</option>
            <option>在读</option>
            <option>暂停</option>
            <option>结课</option>
          </select>
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
                <th>状态</th>
                <th>备注</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="student in students" :key="student.id">
                <td v-if="selectionMode" class="select-cell">
                  <input v-model="selectedIds" type="checkbox" :value="student.id" />
                </td>
                <td data-label="姓名">{{ student.name }}</td>
                <td data-label="状态"><span class="tag" :class="statusClass(student.status)">{{ student.status }}</span></td>
                <td data-label="备注">{{ student.note || '-' }}</td>
                <td data-label="操作" class="actions">
                  <button class="link-button" @click="editStudent(student)">编辑</button>
                  <button class="link-button danger" @click="removeStudent(student)">删除</button>
                </td>
              </tr>
              <tr v-if="students.length === 0">
                <td :colspan="selectionMode ? 5 : 4" class="empty">暂无学生</td>
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
import { bulkDeleteStudents, bulkUpdateStudents, createStudent, deleteStudent, fetchStudents, updateStudent } from '../api/students'
import { getErrorMessage } from '../api/http'

const students = ref([])
const keyword = ref('')
const editingId = ref(null)
const error = ref('')
const message = ref('')
const submitting = ref(false)
const bulkSubmitting = ref(false)
const selectionMode = ref(false)
const selectedIds = ref([])
const bulkStatus = ref('')
const bulkNote = ref('')
const form = reactive({
  name: '',
  status: '在读',
  note: ''
})

function resetNotice() {
  error.value = ''
  message.value = ''
}

function resetForm() {
  editingId.value = null
  Object.assign(form, { name: '', status: '在读', note: '' })
}

function statusClass(status) {
  return {
    'tag-success': status === '在读',
    'tag-warning': status === '暂停',
    'tag-danger': status === '结课'
  }
}

const allSelected = computed(() => students.value.length > 0 && selectedIds.value.length === students.value.length)

function toggleAll(checked) {
  selectedIds.value = checked ? students.value.map((student) => student.id) : []
}

function clearSelection() {
  selectedIds.value = []
}

function toggleSelectionMode() {
  selectionMode.value = !selectionMode.value
  if (!selectionMode.value) {
    clearSelection()
    bulkStatus.value = ''
    bulkNote.value = ''
  }
}

async function loadStudents() {
  resetNotice()
  try {
    const res = await fetchStudents(keyword.value)
    students.value = res.data
    selectedIds.value = selectedIds.value.filter((id) => students.value.some((student) => student.id === id))
  } catch (err) {
    error.value = getErrorMessage(err, '学生列表加载失败。')
  }
}

async function submitForm() {
  resetNotice()
  submitting.value = true
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
  } finally {
    submitting.value = false
  }
}

async function submitBulkUpdate() {
  resetNotice()
  if (selectedIds.value.length === 0) {
    error.value = '请先勾选要修改的学生。'
    return
  }
  if (!bulkStatus.value && !bulkNote.value) {
    error.value = '请选择要修改的状态，或填写批量备注。'
    return
  }

  bulkSubmitting.value = true
  try {
    const payload = { ids: selectedIds.value }
    if (bulkStatus.value) payload.status = bulkStatus.value
    if (bulkNote.value) payload.note = bulkNote.value
    const res = await bulkUpdateStudents(payload)
    message.value = `已批量修改 ${res.data.affected_count} 名学生。`
    bulkStatus.value = ''
    bulkNote.value = ''
    selectionMode.value = false
    selectedIds.value = []
    await loadStudents()
  } catch (err) {
    error.value = getErrorMessage(err, '批量修改学生失败。')
  } finally {
    bulkSubmitting.value = false
  }
}

async function submitBulkDelete() {
  resetNotice()
  if (selectedIds.value.length === 0) {
    error.value = '请先勾选要删除的学生。'
    return
  }
  if (!window.confirm(`确定删除选中的 ${selectedIds.value.length} 名学生吗？`)) return

  bulkSubmitting.value = true
  try {
    const res = await bulkDeleteStudents(selectedIds.value)
    message.value = `已批量删除 ${res.data.affected_count} 名学生。`
    selectedIds.value = []
    selectionMode.value = false
    await loadStudents()
  } catch (err) {
    error.value = getErrorMessage(err, '批量删除学生失败。')
  } finally {
    bulkSubmitting.value = false
  }
}

function editStudent(student) {
  resetNotice()
  editingId.value = student.id
  Object.assign(form, {
    name: student.name,
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

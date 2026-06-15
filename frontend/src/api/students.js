import http from './http'

export function fetchStudents(keyword = '') {
  return http.get('/students', { params: { keyword: keyword || undefined } })
}

export function createStudent(data) {
  return http.post('/students', data)
}

export function bulkUpdateStudents(data) {
  return http.put('/students/bulk', data)
}

export function bulkDeleteStudents(ids) {
  return http.post('/students/bulk-delete', { ids })
}

export function updateStudent(id, data) {
  return http.put(`/students/${id}`, data)
}

export function deleteStudent(id) {
  return http.delete(`/students/${id}`)
}

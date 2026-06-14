import http from './http'

export function fetchTeachers(keyword = '') {
  return http.get('/teachers', { params: { keyword: keyword || undefined } })
}

export function createTeacher(data) {
  return http.post('/teachers', data)
}

export function updateTeacher(id, data) {
  return http.put(`/teachers/${id}`, data)
}

export function deleteTeacher(id) {
  return http.delete(`/teachers/${id}`)
}

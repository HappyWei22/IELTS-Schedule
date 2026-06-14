import http from './http'

export function fetchCourses(filters = {}) {
  return http.get('/courses', {
    params: {
      date: filters.date || undefined,
      student_id: filters.student_id || undefined,
      teacher_id: filters.teacher_id || undefined
    }
  })
}

export function createCourse(data) {
  return http.post('/courses', data)
}

export function updateCourse(id, data) {
  return http.put(`/courses/${id}`, data)
}

export function deleteCourse(id) {
  return http.delete(`/courses/${id}`)
}

export function checkCourseConflict(data) {
  return http.post('/courses/check-conflict', data)
}

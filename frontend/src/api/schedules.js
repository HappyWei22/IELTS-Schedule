import http from './http'

export function fetchDailySchedule(date) {
  return http.get('/schedules/daily', { params: { date } })
}

export function fetchStudentSchedule(studentId, startDate, endDate) {
  return http.get(`/schedules/student/${studentId}`, {
    params: {
      start_date: startDate,
      end_date: endDate
    }
  })
}

export function fetchTeacherMonthlySchedule(teacherId, month) {
  return http.get(`/schedules/teacher/${teacherId}/monthly`, {
    params: { month }
  })
}

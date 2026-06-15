import http from './http'

function getFilename(disposition, fallback) {
  const utf8Match = /filename\*=UTF-8''([^;]+)/i.exec(disposition || '')
  if (utf8Match) {
    return decodeURIComponent(utf8Match[1])
  }

  const plainMatch = /filename="?([^"]+)"?/i.exec(disposition || '')
  return plainMatch ? plainMatch[1] : fallback
}

function downloadBlob(blob, filename) {
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.URL.revokeObjectURL(url)
}

async function downloadCsv(url, params, fallbackFilename) {
  const res = await http.get(url, {
    params,
    responseType: 'blob'
  })
  const filename = getFilename(res.headers['content-disposition'], fallbackFilename)
  downloadBlob(res.data, filename)
}

export function exportDailySchedule(date) {
  return downloadCsv('/export/daily', { date }, `每日总课表-${date}.csv`)
}

export function exportStudentSchedule(studentId, startDate, endDate) {
  return downloadCsv(
    `/export/student/${studentId}`,
    {
      start_date: startDate,
      end_date: endDate
    },
    `学生课表-${startDate}_至_${endDate}.csv`
  )
}

export function exportTeacherMonthlySchedule(teacherId, month) {
  return downloadCsv(`/export/teacher/${teacherId}/monthly`, { month }, `老师月度课表-${month}.csv`)
}

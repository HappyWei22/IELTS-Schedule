import axios from 'axios'

const http = axios.create({
  baseURL: '/api',
  timeout: 10000
})

export function getErrorMessage(error, fallback = '操作失败，请稍后重试。') {
  return error?.response?.data?.detail || error?.message || fallback
}

export default http

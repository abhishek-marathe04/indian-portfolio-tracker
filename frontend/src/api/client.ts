import axios from 'axios'

export const apiClient = axios.create({
  baseURL: '/api',
  withCredentials: true,
})

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error?.response?.status === 401) {
      const onLoginPage = window.location.pathname === '/login'
      if (!onLoginPage) {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  },
)

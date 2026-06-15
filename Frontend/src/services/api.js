import axios from 'axios'
import router from '../router/index'

const api = axios.create({
  baseURL: 'http://127.0.0.1:5000' // your Flask backend
})

api.interceptors.request.use(config => {  //This is global token injection, we don't have to manually send in the token with every request now, this automatically handles it for us.
  const token = localStorage.getItem('token')

  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }

  return config
})

api.interceptors.response.use(
  //success response
  (response) => response,
  //error response
  (error) => {
    if (error.response?.status === 403) {
      localStorage.removeItem('token')
      localStorage.removeItem('role')

      alert('Your account has been blacklisted')
      router.push('/login')
    }
    return Promise.reject(error)
  }
)

export default api

//why this matters??
//instead of doing axios.get('http://...'), we can do api.get('/api/...') 

//Now the second block of code helps with the blacklist of users. ie, if the user is say looking at the doctor
//page, and the admin blacklists him/her then the next thing the user clicks, there will be an alert message
//and also they will be sent to the login page, where they won't be able to login and displayed an error message saying "you've been blacklisted"
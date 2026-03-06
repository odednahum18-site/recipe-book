import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || ''

const client = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  timeout: 30000
})

// Auth interceptor
client.interceptors.request.use((config) => {
  const token = localStorage.getItem('recipe-book-token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response interceptor
client.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const detail = error.response?.data?.detail
    return Promise.reject({
      message: detail || error.message,
      statusCode: error.response?.status
    })
  }
)

export default {
  // Auth
  login(username, password) {
    return client.post('/auth/login', { username, password })
  },
  firebaseLogin() {
    return client.post('/auth/firebase-login')
  },
  getMe() {
    return client.get('/auth/me')
  },

  // Public - Recipes
  getRecipes(params = {}) {
    return client.get('/recipes', { params })
  },
  getRecipe(slug) {
    return client.get(`/recipes/${slug}`)
  },

  // Public - Categories
  getCategories() {
    return client.get('/categories')
  },

  // Public - Stars
  starRecipe(recipeId, visitorId) {
    return client.post(`/recipes/${recipeId}/star`, { visitor_id: visitorId })
  },
  unstarRecipe(recipeId, visitorId) {
    return client.delete(`/recipes/${recipeId}/star`, { data: { visitor_id: visitorId } })
  },
  checkStarred(recipeId, visitorId) {
    return client.get(`/recipes/${recipeId}/starred`, { params: { visitor_id: visitorId } })
  },

  // Admin - Recipes
  getAdminRecipes() {
    return client.get('/admin/recipes')
  },
  createRecipe(data) {
    return client.post('/admin/recipes', data)
  },
  updateRecipe(id, data) {
    return client.put(`/admin/recipes/${id}`, data)
  },
  deleteRecipe(id) {
    return client.delete(`/admin/recipes/${id}`)
  },

  // Admin - Image Upload
  uploadImage(file, recipeId = 'temp') {
    const formData = new FormData()
    formData.append('file', file)
    return client.post(`/admin/upload-image?recipe_id=${recipeId}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  // Admin - Categories
  createCategory(data) {
    return client.post('/admin/categories', data)
  },
  updateCategory(id, data) {
    return client.put(`/admin/categories/${id}`, data)
  },
  deleteCategory(id) {
    return client.delete(`/admin/categories/${id}`)
  },

  // Admin - Users
  getUsers() {
    return client.get('/admin/users')
  },
  inviteUser(email, displayName) {
    return client.post('/admin/invite', { email, display_name: displayName })
  },
  deleteUser(id) {
    return client.delete(`/admin/users/${id}`)
  }
}

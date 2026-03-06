<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')
const googleBtnRef = ref(null)

const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID

function redirectAfterLogin() {
  const redirect = route.query.redirect || '/admin'
  router.push(redirect)
}

async function handleLogin() {
  const success = await authStore.login(username.value, password.value)
  if (success) {
    ElMessage.success('Login successful')
    redirectAfterLogin()
  } else {
    ElMessage.error(authStore.error || 'Login failed')
  }
}

async function handleGoogleCallback(response) {
  const success = await authStore.googleLogin(response.credential)
  if (success) {
    ElMessage.success('Login successful')
    redirectAfterLogin()
  } else {
    ElMessage.error(authStore.error || 'Google login failed')
  }
}

onMounted(() => {
  if (GOOGLE_CLIENT_ID && window.google?.accounts) {
    initGoogleBtn()
  } else if (GOOGLE_CLIENT_ID) {
    // Script may still be loading
    const check = setInterval(() => {
      if (window.google?.accounts) {
        clearInterval(check)
        initGoogleBtn()
      }
    }, 200)
    setTimeout(() => clearInterval(check), 5000)
  }
})

function initGoogleBtn() {
  window.google.accounts.id.initialize({
    client_id: GOOGLE_CLIENT_ID,
    callback: handleGoogleCallback,
  })
  if (googleBtnRef.value) {
    window.google.accounts.id.renderButton(googleBtnRef.value, {
      theme: 'outline',
      size: 'large',
      width: googleBtnRef.value.offsetWidth,
      text: 'signin_with',
    })
  }
}
</script>

<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-icon">&#128274;</div>
      <h2>{{ $t('auth.login') }}</h2>

      <!-- Google Sign-In -->
      <div v-if="GOOGLE_CLIENT_ID" class="google-login-section">
        <div ref="googleBtnRef" class="google-btn-wrapper"></div>
        <div class="divider">
          <span>{{ $t('auth.or') }}</span>
        </div>
      </div>

      <el-form @submit.prevent="handleLogin">
        <el-form-item>
          <el-input
            v-model="username"
            :placeholder="authStore.isFirebaseAuth ? $t('auth.email') : $t('auth.username')"
            prefix-icon="User"
            size="large"
          />
        </el-form-item>
        <el-form-item>
          <el-input
            v-model="password"
            type="password"
            :placeholder="$t('auth.password')"
            prefix-icon="Lock"
            size="large"
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        <el-button
          type="primary"
          size="large"
          :loading="authStore.loading"
          style="width: 100%"
          @click="handleLogin"
        >
          {{ $t('auth.login') }}
        </el-button>
      </el-form>
    </div>
  </div>
</template>

<style scoped>
.login-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  padding: 20px;
}

.login-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 40px;
  max-width: 400px;
  width: 100%;
  text-align: center;
}

.login-icon {
  font-size: 3rem;
  margin-bottom: 16px;
}

.login-card h2 {
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 24px;
}

.el-form-item {
  margin-bottom: 16px;
}

.google-login-section {
  margin-bottom: 8px;
}

.google-btn-wrapper {
  display: flex;
  justify-content: center;
  min-height: 44px;
}

.divider {
  display: flex;
  align-items: center;
  margin: 16px 0;
  color: var(--text-secondary);
  font-size: 0.85rem;
}

.divider::before,
.divider::after {
  content: '';
  flex: 1;
  border-bottom: 1px solid var(--border);
}

.divider span {
  padding: 0 12px;
}
</style>

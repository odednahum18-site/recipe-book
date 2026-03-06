<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')

async function handleLogin() {
  const success = await authStore.login(username.value, password.value)
  if (success) {
    ElMessage.success('Login successful')
    const redirect = route.query.redirect || '/admin'
    router.push(redirect)
  } else {
    ElMessage.error(authStore.error || 'Login failed')
  }
}
</script>

<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-icon">&#128274;</div>
      <h2>{{ $t('auth.login') }}</h2>

      <el-form @submit.prevent="handleLogin">
        <el-form-item>
          <el-input
            v-model="username"
            :placeholder="$t('auth.username')"
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

</style>

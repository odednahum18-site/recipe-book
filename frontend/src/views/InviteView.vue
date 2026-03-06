<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '@/api'

const router = useRouter()
const users = ref([])
const email = ref('')
const displayName = ref('')
const loading = ref(true)

onMounted(async () => {
  try {
    users.value = await api.getUsers()
  } catch (e) {
    ElMessage.error(e.message)
  } finally {
    loading.value = false
  }
})

async function inviteUser() {
  if (!email.value) {
    ElMessage.warning('Email is required')
    return
  }
  try {
    const newUser = await api.inviteUser(email.value, displayName.value)
    users.value.push(newUser)
    email.value = ''
    displayName.value = ''
    ElMessage.success('User invited')
  } catch (e) {
    ElMessage.error(e.message || 'Invite failed')
  }
}
</script>

<template>
  <div class="invite-container">
    <div class="invite-header">
      <h2>{{ $t('admin.users') }}</h2>
      <el-button @click="router.push('/admin')">{{ $t('admin.back') }}</el-button>
    </div>

    <el-card class="invite-form">
      <h3>{{ $t('admin.inviteUser') }}</h3>
      <div style="display: flex; gap: 8px; margin-top: 12px; flex-wrap: wrap">
        <el-input v-model="email" placeholder="Email" style="flex: 1; min-width: 200px" />
        <el-input v-model="displayName" placeholder="Display name (optional)" style="width: 200px" />
        <el-button type="primary" @click="inviteUser">{{ $t('admin.inviteUser') }}</el-button>
      </div>
    </el-card>

    <el-table :data="users" v-loading="loading" style="margin-top: 20px">
      <el-table-column prop="display_name" label="Name" />
      <el-table-column prop="email" label="Email" />
      <el-table-column prop="role" label="Role" width="100">
        <template #default="{ row }">
          <el-tag :type="row.role === 'admin' ? 'danger' : 'info'" size="small">
            {{ row.role }}
          </el-tag>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<style scoped>
.invite-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 24px 20px;
}

.invite-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}

.invite-header h2 {
  font-size: 1.5rem;
  font-weight: 700;
}

.invite-form h3 {
  font-size: 1rem;
  font-weight: 600;
}

</style>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useLocaleStore } from '@/stores/locale'
import { useCategoriesStore } from '@/stores/categories'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/api'

const router = useRouter()
const localeStore = useLocaleStore()
const categoriesStore = useCategoriesStore()

const recipes = ref([])
const loading = ref(true)

onMounted(async () => {
  try {
    recipes.value = await api.getAdminRecipes()
  } catch (e) {
    ElMessage.error(e.message)
  } finally {
    loading.value = false
  }
})

function getRecipeName(recipe) {
  return recipe.name?.[localeStore.locale] || recipe.name?.en || ''
}

function getCategoryName(categoryId) {
  const cat = categoriesStore.getCategoryById(categoryId)
  return cat?.name?.[localeStore.locale] || cat?.name?.en || ''
}

async function deleteRecipe(recipe) {
  try {
    await ElMessageBox.confirm(
      `Delete "${getRecipeName(recipe)}"?`,
      { confirmButtonText: 'Delete', cancelButtonText: 'Cancel', type: 'warning' }
    )
    await api.deleteRecipe(recipe.id)
    recipes.value = recipes.value.filter(r => r.id !== recipe.id)
    ElMessage.success('Recipe deleted')
  } catch (e) {
    if (e !== 'cancel') ElMessage.error(e.message || 'Failed to delete')
  }
}
</script>

<template>
  <div class="admin-container">
    <div class="admin-header">
      <h2>{{ $t('admin.dashboard') }}</h2>
      <div style="display: flex; gap: 8px">
        <el-button @click="router.push('/')">
          &#8592; {{ $t('admin.back') }}
        </el-button>
        <el-button type="primary" @click="router.push('/admin/recipe/new')">
          + {{ $t('admin.addRecipe') }}
        </el-button>
      </div>
    </div>

    <div class="admin-links">
      <el-button @click="router.push('/admin/invite')">{{ $t('admin.users') }}</el-button>
    </div>

    <div v-if="loading" class="skeleton-table">
      <el-skeleton v-for="n in 5" :key="n" animated>
        <template #template>
          <div class="skeleton-row">
            <el-skeleton-item variant="text" style="width: 40%" />
            <el-skeleton-item variant="text" style="width: 15%" />
            <el-skeleton-item variant="text" style="width: 10%" />
            <el-skeleton-item variant="text" style="width: 8%" />
            <el-skeleton-item variant="text" style="width: 20%" />
          </div>
        </template>
      </el-skeleton>
    </div>

    <el-table v-else :data="recipes" stripe>
      <el-table-column :label="$t('admin.recipeName')" min-width="200">
        <template #default="{ row }">
          <strong>{{ getRecipeName(row) }}</strong>
        </template>
      </el-table-column>
      <el-table-column :label="$t('admin.category')" width="150">
        <template #default="{ row }">
          {{ getCategoryName(row.category_id) }}
        </template>
      </el-table-column>
      <el-table-column label="Status" width="120">
        <template #default="{ row }">
          <el-tag :type="row.published ? 'success' : 'warning'" size="small">
            {{ row.published ? $t('admin.published') : $t('admin.draft') }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="&#9733;" width="80">
        <template #default="{ row }">
          <span style="color: var(--star)">&#9733;</span> {{ row.star_count || 0 }}
        </template>
      </el-table-column>
      <el-table-column label="" width="180">
        <template #default="{ row }">
          <el-button size="small" @click="router.push(`/admin/recipe/${row.id}/edit`)">
            {{ $t('admin.edit') }}
          </el-button>
          <el-button size="small" type="danger" @click="deleteRecipe(row)">
            {{ $t('admin.delete') }}
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<style scoped>
.admin-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px 20px;
}

.admin-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 12px;
}

.admin-header h2 {
  font-size: 1.5rem;
  font-weight: 700;
}

.admin-links {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.skeleton-table {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.skeleton-row {
  display: flex;
  gap: 16px;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid var(--border);
}

</style>

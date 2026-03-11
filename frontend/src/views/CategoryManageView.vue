<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useLocaleStore } from '@/stores/locale'
import { useCategoriesStore } from '@/stores/categories'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const { t } = useI18n()
const localeStore = useLocaleStore()
const categoriesStore = useCategoriesStore()

const dialogVisible = ref(false)
const editingId = ref(null)
const categoryForm = ref({ name: { en: '', he: '' }, icon: '', order: 0 })

onMounted(() => {
  categoriesStore.fetchCategories()
})

function getCategoryName(cat) {
  return cat.name?.[localeStore.locale] || cat.name?.en || ''
}

function openAdd() {
  editingId.value = null
  categoryForm.value = { name: { en: '', he: '' }, icon: '', order: categoriesStore.categories.length + 1 }
  dialogVisible.value = true
}

function openEdit(cat) {
  editingId.value = cat.id
  categoryForm.value = {
    name: { en: cat.name?.en || '', he: cat.name?.he || '' },
    icon: cat.icon || '',
    order: cat.order || 0
  }
  dialogVisible.value = true
}

async function saveCategory() {
  if (!categoryForm.value.name.en || !categoryForm.value.name.he) {
    ElMessage.warning(t('admin.requiredBothLangs'))
    return
  }
  try {
    if (editingId.value) {
      await categoriesStore.updateCategory(editingId.value, categoryForm.value)
    } else {
      await categoriesStore.createCategory(categoryForm.value)
    }
    dialogVisible.value = false
    ElMessage.success(t('admin.categorySaved'))
  } catch (e) {
    ElMessage.error(e.message || 'Failed to save category')
  }
}

async function deleteCategory(cat) {
  if (cat.recipe_count > 0) {
    ElMessage.warning(t('admin.cantDeleteWithRecipes'))
    return
  }
  try {
    await ElMessageBox.confirm(
      t('admin.deleteConfirm', { name: getCategoryName(cat) }),
      { confirmButtonText: t('admin.delete'), cancelButtonText: t('admin.cancel'), type: 'warning' }
    )
    await categoriesStore.deleteCategory(cat.id)
    ElMessage.success(t('admin.categoryDeleted'))
  } catch (e) {
    if (e !== 'cancel') ElMessage.error(e.message || 'Failed to delete')
  }
}

async function moveUp(index) {
  if (index === 0) return
  const cats = [...categoriesStore.categories]
  const order = cats.map((c, i) => ({
    id: c.id,
    order: i === index ? cats[index - 1].order : i === index - 1 ? cats[index].order : c.order
  }))
  try {
    await categoriesStore.reorderCategories(order)
  } catch (e) {
    ElMessage.error(e.message || 'Failed to reorder')
  }
}

async function moveDown(index) {
  if (index >= categoriesStore.categories.length - 1) return
  const cats = [...categoriesStore.categories]
  const order = cats.map((c, i) => ({
    id: c.id,
    order: i === index ? cats[index + 1].order : i === index + 1 ? cats[index].order : c.order
  }))
  try {
    await categoriesStore.reorderCategories(order)
  } catch (e) {
    ElMessage.error(e.message || 'Failed to reorder')
  }
}
</script>

<template>
  <div class="admin-container">
    <div class="admin-header">
      <h2>{{ $t('admin.manageCategories') }}</h2>
      <div style="display: flex; gap: 8px">
        <el-button @click="router.push('/admin')">&#8592; {{ $t('admin.back') }}</el-button>
        <el-button type="primary" @click="openAdd">+ {{ $t('admin.addCategory') }}</el-button>
      </div>
    </div>

    <el-table :data="categoriesStore.categories" stripe v-loading="categoriesStore.loading">
      <el-table-column :label="$t('admin.categoryOrder')" width="80">
        <template #default="{ row }">
          {{ row.order }}
        </template>
      </el-table-column>
      <el-table-column :label="$t('admin.categoryName') + ' (EN)'" min-width="150">
        <template #default="{ row }">
          {{ row.name?.en || '' }}
        </template>
      </el-table-column>
      <el-table-column :label="$t('admin.categoryName') + ' (HE)'" min-width="150">
        <template #default="{ row }">
          <span dir="rtl">{{ row.name?.he || '' }}</span>
        </template>
      </el-table-column>
      <el-table-column :label="$t('admin.categoryIcon')" width="80">
        <template #default="{ row }">
          {{ row.icon }}
        </template>
      </el-table-column>
      <el-table-column label="#" width="80">
        <template #default="{ row }">
          {{ row.recipe_count || 0 }}
        </template>
      </el-table-column>
      <el-table-column label="" width="240">
        <template #default="{ row, $index }">
          <el-button size="small" @click="moveUp($index)" :disabled="$index === 0">&#9650;</el-button>
          <el-button size="small" @click="moveDown($index)" :disabled="$index >= categoriesStore.categories.length - 1">&#9660;</el-button>
          <el-button size="small" @click="openEdit(row)">{{ $t('admin.edit') }}</el-button>
          <el-button size="small" type="danger" @click="deleteCategory(row)" :disabled="row.recipe_count > 0">
            {{ $t('admin.delete') }}
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- Add/Edit Dialog -->
    <el-dialog v-model="dialogVisible" :title="editingId ? $t('admin.editCategory') : $t('admin.addCategory')" width="480px">
      <div class="dialog-form">
        <div class="form-group">
          <label class="form-label">{{ $t('admin.categoryName') }} (EN)</label>
          <el-input v-model="categoryForm.name.en" placeholder="Category name in English" />
        </div>
        <div class="form-group">
          <label class="form-label">{{ $t('admin.categoryName') }} (HE)</label>
          <el-input v-model="categoryForm.name.he" placeholder="\u05e9\u05dd \u05e7\u05d8\u05d2\u05d5\u05e8\u05d9\u05d4 \u05d1\u05e2\u05d1\u05e8\u05d9\u05ea" dir="rtl" />
        </div>
        <div class="form-group">
          <label class="form-label">{{ $t('admin.categoryIcon') }}</label>
          <el-input v-model="categoryForm.icon" placeholder="e.g. dish, cake, salad" />
        </div>
        <div class="form-group">
          <label class="form-label">{{ $t('admin.categoryOrder') }}</label>
          <el-input-number v-model="categoryForm.order" :min="0" />
        </div>
      </div>
      <template #footer>
        <el-button @click="dialogVisible = false">{{ $t('admin.cancel') }}</el-button>
        <el-button type="primary" @click="saveCategory">{{ $t('admin.savePublish') }}</el-button>
      </template>
    </el-dialog>
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

.dialog-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.form-label {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-secondary);
}
</style>

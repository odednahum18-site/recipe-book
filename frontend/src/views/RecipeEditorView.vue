<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useCategoriesStore } from '@/stores/categories'
import { useLocaleStore } from '@/stores/locale'
import { ElMessage } from 'element-plus'
import api from '@/api'
import RichTextEditor from '@/components/recipe/RichTextEditor.vue'
import { Loading } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const categoriesStore = useCategoriesStore()
const localeStore = useLocaleStore()

const isEditing = computed(() => !!route.params.id)
const loading = ref(false)
const saving = ref(false)
const activeLangTab = ref('en')

const form = ref({
  name: { en: '', he: '' },
  category_id: '',
  ingredients: [{ text: { en: '', he: '' }, amount: '', unit: '' }],
  steps: { en: '', he: '' },
  images: [],
  published: false
})

onMounted(async () => {
  if (isEditing.value) {
    loading.value = true
    try {
      const recipes = await api.getAdminRecipes()
      const recipe = recipes.find(r => r.id === route.params.id)
      if (recipe) {
        form.value = {
          name: recipe.name || { en: '', he: '' },
          category_id: recipe.category_id || '',
          ingredients: recipe.ingredients?.length
            ? recipe.ingredients
            : [{ text: { en: '', he: '' }, amount: '', unit: '' }],
          steps: recipe.steps || { en: '', he: '' },
          images: recipe.images || [],
          published: recipe.published || false
        }
      }
    } catch (e) {
      ElMessage.error(e.message)
    } finally {
      loading.value = false
    }
  }
})

function addIngredient() {
  form.value.ingredients.push({ text: { en: '', he: '' }, amount: '', unit: '' })
}

function removeIngredient(index) {
  form.value.ingredients.splice(index, 1)
}

const uploading = ref(false)
const dragOver = ref(false)

async function uploadFiles(files) {
  if (!files || !files.length) return
  uploading.value = true
  for (const file of files) {
    if (form.value.images.length >= 5) {
      ElMessage.warning('Maximum 5 images')
      break
    }
    try {
      const result = await api.uploadImage(file)
      form.value.images.push({ url: result.url, thumbnail_url: result.thumbnail_url, order: form.value.images.length })
    } catch (e) {
      ElMessage.error(e.message || 'Upload failed')
    }
  }
  uploading.value = false
}

function handleUpload(event) {
  uploadFiles(event.target.files)
  event.target.value = ''
}

function handleDrop(event) {
  event.preventDefault()
  dragOver.value = false
  const files = Array.from(event.dataTransfer.files).filter(f => f.type.startsWith('image/'))
  uploadFiles(files)
}

function removeImage(index) {
  form.value.images.splice(index, 1)
}

async function save(publish = false) {
  if (!form.value.name.en || !form.value.name.he) {
    ElMessage.warning('Recipe name is required in both languages')
    return
  }
  if (!form.value.category_id) {
    ElMessage.warning('Please select a category')
    return
  }

  saving.value = true
  form.value.published = publish

  try {
    if (isEditing.value) {
      await api.updateRecipe(route.params.id, form.value)
      ElMessage.success('Recipe updated')
    } else {
      await api.createRecipe(form.value)
      ElMessage.success('Recipe created')
    }
    router.push('/admin')
  } catch (e) {
    ElMessage.error(e.message || 'Save failed')
  } finally {
    saving.value = false
  }
}

function getCategoryName(cat) {
  return cat.name?.[localeStore.locale] || cat.name?.en || ''
}
</script>

<template>
  <div class="editor-container" v-loading="loading">
    <div class="editor-header">
      <h2>{{ isEditing ? $t('admin.editRecipe') : $t('admin.createRecipe') }}</h2>
      <div style="display: flex; gap: 8px">
        <el-button @click="router.push('/admin')">{{ $t('admin.cancel') }}</el-button>
        <el-button @click="save(false)" :loading="saving">{{ $t('admin.saveDraft') }}</el-button>
        <el-button type="primary" @click="save(true)" :loading="saving">
          {{ $t('admin.savePublish') }}
        </el-button>
      </div>
    </div>

    <!-- Language tabs -->
    <el-tabs v-model="activeLangTab" class="lang-tabs">
      <el-tab-pane label="English" name="en" />
      <el-tab-pane label="Hebrew" name="he" />
    </el-tabs>

    <!-- Recipe Name -->
    <div class="form-group">
      <label class="form-label">{{ $t('admin.recipeName') }} ({{ $t('admin.requiredBothLangs') }})</label>
      <el-input
        v-model="form.name[activeLangTab]"
        :placeholder="activeLangTab === 'en' ? 'Recipe name in English' : '\u05e9\u05dd \u05d4\u05de\u05ea\u05db\u05d5\u05df \u05d1\u05e2\u05d1\u05e8\u05d9\u05ea'"
        size="large"
        :dir="activeLangTab === 'he' ? 'rtl' : 'ltr'"
      />
    </div>

    <!-- Category -->
    <div class="form-group">
      <label class="form-label">{{ $t('admin.category') }}</label>
      <el-select v-model="form.category_id" :placeholder="$t('admin.category')" size="large" style="width: 100%">
        <el-option
          v-for="cat in categoriesStore.categories"
          :key="cat.id"
          :label="getCategoryName(cat)"
          :value="cat.id"
        />
      </el-select>
    </div>

    <!-- Ingredients -->
    <div class="form-group">
      <label class="form-label">{{ $t('admin.ingredients') }}</label>
      <div v-for="(ing, idx) in form.ingredients" :key="idx" class="ingredient-row">
        <el-input v-model="ing.amount" placeholder="Amount" style="width: 100px" />
        <el-input v-model="ing.unit" placeholder="Unit" style="width: 80px" />
        <el-input
          v-model="ing.text[activeLangTab]"
          :placeholder="activeLangTab === 'en' ? 'Ingredient' : '\u05de\u05e6\u05e8\u05da'"
          :dir="activeLangTab === 'he' ? 'rtl' : 'ltr'"
          style="flex: 1"
        />
        <el-button @click="removeIngredient(idx)" :disabled="form.ingredients.length <= 1">
          &#128465;
        </el-button>
      </div>
      <el-button @click="addIngredient" style="margin-top: 8px">
        + {{ $t('admin.addIngredient') }}
      </el-button>
    </div>

    <!-- Steps -->
    <div class="form-group">
      <label class="form-label">{{ $t('admin.prepSteps') }}</label>
      <RichTextEditor
        v-model="form.steps[activeLangTab]"
        :placeholder="activeLangTab === 'en' ? 'Preparation steps...' : '\u05e9\u05dc\u05d1\u05d9 \u05d4\u05db\u05e0\u05d4...'"
        :dir="activeLangTab === 'he' ? 'rtl' : 'ltr'"
      />
    </div>

    <!-- Images -->
    <div class="form-group">
      <label class="form-label">{{ $t('admin.images') }} ({{ form.images.length }}/5)</label>
      <div
        class="image-upload-zone"
        :class="{ 'drag-over': dragOver, uploading }"
        @click="$refs.fileInput.click()"
        @dragover.prevent="dragOver = true"
        @dragleave="dragOver = false"
        @drop="handleDrop"
      >
        <div v-if="uploading" class="upload-spinner">
          <el-icon class="is-loading" :size="32"><Loading /></el-icon>
          <div>{{ $t('common.loading') }}...</div>
        </div>
        <template v-else>
          <div class="upload-icon">&#128247;</div>
          <div>{{ $t('admin.dragDrop') }}</div>
          <div class="upload-buttons">
            <span class="upload-btn" @click.stop="$refs.fileInput.click()">&#128193; {{ $t('admin.browseFiles') }}</span>
            <span class="upload-btn" @click.stop="$refs.cameraInput.click()">&#128247; {{ $t('admin.takePhoto') }}</span>
          </div>
        </template>
      </div>
      <input
        ref="fileInput"
        type="file"
        accept="image/*"
        multiple
        style="display: none"
        @change="handleUpload"
      />
      <input
        ref="cameraInput"
        type="file"
        accept="image/*"
        capture="environment"
        style="display: none"
        @change="handleUpload"
      />
      <div v-if="form.images.length" class="uploaded-images">
        <div v-for="(img, idx) in form.images" :key="idx" class="uploaded-thumb">
          <img :src="img.thumbnail_url || img.url" />
          <button class="remove-btn" @click="removeImage(idx)">x</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.editor-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 24px 20px;
}

.editor-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 12px;
}

.editor-header h2 {
  font-size: 1.5rem;
  font-weight: 700;
}

.form-group {
  margin-bottom: 20px;
}

.form-label {
  display: block;
  font-size: 0.85rem;
  font-weight: 600;
  margin-bottom: 6px;
  color: var(--text-secondary);
}

.ingredient-row {
  display: flex;
  gap: 8px;
  align-items: center;
  margin-bottom: 8px;
}

.image-upload-zone {
  border: 2px dashed var(--border);
  border-radius: var(--radius);
  padding: 32px;
  text-align: center;
  color: var(--text-muted);
  cursor: pointer;
  transition: all var(--transition);
}

.image-upload-zone:hover,
.image-upload-zone.drag-over {
  border-color: var(--accent);
  color: var(--accent);
  background: var(--accent-light);
}

.image-upload-zone.uploading {
  pointer-events: none;
  opacity: 0.7;
}

.upload-spinner {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.upload-icon { font-size: 2.5rem; margin-bottom: 8px; }

.upload-buttons {
  display: flex;
  gap: 12px;
  justify-content: center;
  margin-top: 12px;
}

.upload-btn {
  padding: 6px 14px;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  font-size: 0.85rem;
}

.uploaded-images {
  display: flex;
  gap: 12px;
  margin-top: 12px;
  flex-wrap: wrap;
}

.uploaded-thumb {
  width: 80px;
  height: 80px;
  border-radius: var(--radius-sm);
  overflow: hidden;
  position: relative;
}

.uploaded-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.remove-btn {
  position: absolute;
  top: -4px;
  right: -4px;
  width: 20px;
  height: 20px;
  background: #ef4444;
  color: white;
  border: none;
  border-radius: 50%;
  font-size: 0.7rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

:deep(.el-button--primary) {
  background-color: var(--accent);
  border-color: var(--accent);
}

:deep(.el-tabs__active-bar) {
  background-color: var(--accent);
}

@media (max-width: 768px) {
  .ingredient-row { flex-wrap: wrap; }
}
</style>

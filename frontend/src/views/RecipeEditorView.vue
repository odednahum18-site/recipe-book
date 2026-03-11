<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useCategoriesStore } from '@/stores/categories'
import { useLocaleStore } from '@/stores/locale'
import { ElMessage, ElMessageBox } from 'element-plus'
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
const tags = ref([])

const form = ref({
  name: { en: '', he: '' },
  recipe_of: { en: '', he: '' },
  category_ids: [],
  tags: [],
  ingredients: [{ text: { en: '', he: '' }, amount: '', unit: '' }],
  steps: { en: '', he: '' },
  images: [],
  published: false
})

onMounted(async () => {
  try {
    tags.value = await api.getTags()
  } catch (e) {
    // Tags are non-critical
  }

  if (isEditing.value) {
    loading.value = true
    try {
      const recipe = await api.getAdminRecipe(route.params.id)
      if (recipe) {
        form.value = {
          name: recipe.name || { en: '', he: '' },
          recipe_of: recipe.recipe_of || { en: '', he: '' },
          category_ids: recipe.category_ids || (recipe.category_id ? [recipe.category_id] : []),
          tags: recipe.tags || [],
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

const translating = ref(false)
const scanning = ref(false)

async function translateAll() {
  const sourceLang = activeLangTab.value
  const targetLang = sourceLang === 'en' ? 'he' : 'en'
  const targetLabel = targetLang === 'en' ? 'English' : 'Hebrew'

  // Check if target already has content
  const hasTarget = form.value.name[targetLang] ||
    form.value.recipe_of[targetLang] ||
    form.value.ingredients.some(i => i.text[targetLang]) ||
    form.value.steps[targetLang]

  if (hasTarget) {
    try {
      await ElMessageBox.confirm(
        `This will overwrite existing ${targetLabel} content. Continue?`,
        'Translate',
        { type: 'warning' }
      )
    } catch { return }
  }

  // Build batch request
  const texts = [
    { field: 'name', value: form.value.name[sourceLang], format: 'text' },
    { field: 'recipe_of', value: form.value.recipe_of[sourceLang], format: 'text' },
    { field: 'steps', value: form.value.steps[sourceLang], format: 'html' },
  ]
  form.value.ingredients.forEach((ing, idx) => {
    if (ing.text[sourceLang]) {
      texts.push({ field: `ingredient_${idx}`, value: ing.text[sourceLang], format: 'text' })
    }
  })

  translating.value = true
  try {
    const result = await api.translateFields(texts, sourceLang, targetLang)
    const t = result.translations
    if (t.name) form.value.name[targetLang] = t.name
    if (t.recipe_of) form.value.recipe_of[targetLang] = t.recipe_of
    if (t.steps) form.value.steps[targetLang] = t.steps
    form.value.ingredients.forEach((ing, idx) => {
      const key = `ingredient_${idx}`
      if (t[key]) ing.text[targetLang] = t[key]
    })
    ElMessage.success(targetLang === 'he' ? '\u05d4\u05ea\u05e8\u05d2\u05d5\u05dd \u05d4\u05d5\u05e9\u05dc\u05dd!' : 'Translation complete!')
    activeLangTab.value = targetLang
  } catch (e) {
    ElMessage.error(e.message || 'Translation failed')
  } finally {
    translating.value = false
  }
}

async function handleScan(event) {
  const file = event.target.files?.[0]
  if (!file) return
  event.target.value = ''

  // Check if form has content
  const hasContent = form.value.name.en || form.value.name.he ||
    form.value.ingredients.some(i => i.text.en || i.text.he) ||
    form.value.steps.en || form.value.steps.he

  if (hasContent) {
    try {
      await ElMessageBox.confirm(
        'This will overwrite existing recipe content. Continue?',
        'Scan Recipe',
        { type: 'warning' }
      )
    } catch { return }
  }

  scanning.value = true
  try {
    const result = await api.scanRecipe(file)
    const lang = result.detected_language || 'he'

    if (result.name) form.value.name[lang] = result.name
    if (result.ingredients?.length) {
      form.value.ingredients = result.ingredients.map(ing => ({
        text: { en: '', he: '', [lang]: ing.text || '' },
        amount: ing.amount || '',
        unit: ing.unit || ''
      }))
    }
    if (result.steps) form.value.steps[lang] = result.steps

    activeLangTab.value = lang
    ElMessage.success(lang === 'he' ? '\u05d4\u05de\u05ea\u05db\u05d5\u05df \u05e0\u05e1\u05e8\u05e7 \u05d1\u05d4\u05e6\u05dc\u05d7\u05d4!' : 'Recipe scanned successfully!')
  } catch (e) {
    ElMessage.error(e.message || 'Scan failed')
  } finally {
    scanning.value = false
  }
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

function getTagName(slug) {
  const tag = tags.value.find(t => t.slug === slug)
  if (!tag) return slug
  return tag.name?.[localeStore.locale] || tag.name?.en || slug
}

async function save(publish = false) {
  if (!form.value.name.en || !form.value.name.he) {
    ElMessage.warning('Recipe name is required in both languages')
    return
  }
  if (!form.value.category_ids.length) {
    ElMessage.warning('Please select at least one category')
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

    <!-- Scan Recipe -->
    <div class="scan-zone">
      <el-button type="success" @click="$refs.scanInput.click()" :loading="scanning" size="large">
        {{ scanning ? $t('admin.scanning') : $t('admin.scanRecipe') }}
      </el-button>
      <input
        ref="scanInput"
        type="file"
        accept="image/*"
        capture="environment"
        style="display: none"
        @change="handleScan"
      />
    </div>

    <!-- Language tabs -->
    <div class="lang-bar">
      <el-tabs v-model="activeLangTab" class="lang-tabs">
        <el-tab-pane label="English" name="en" />
        <el-tab-pane label="Hebrew" name="he" />
      </el-tabs>
      <el-button
        size="small"
        type="info"
        plain
        @click="translateAll"
        :loading="translating"
        class="translate-btn"
      >
        {{ activeLangTab === 'en' ? $t('admin.translateToHe') : $t('admin.translateToEn') }}
      </el-button>
    </div>

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

    <!-- Recipe Of -->
    <div class="form-group">
      <label class="form-label">{{ $t('admin.recipeOf') }}</label>
      <el-input
        v-model="form.recipe_of[activeLangTab]"
        :placeholder="activeLangTab === 'en' ? 'e.g. Grandma Sarah' : '\u05dc\u05de\u05e9\u05dc \u05e1\u05d1\u05ea\u05d0 \u05e9\u05e8\u05d4'"
        :dir="activeLangTab === 'he' ? 'rtl' : 'ltr'"
      />
    </div>

    <!-- Categories (multi-select) -->
    <div class="form-group">
      <label class="form-label">{{ $t('admin.categories') }}</label>
      <el-select v-model="form.category_ids" multiple :placeholder="$t('admin.category')" size="large" style="width: 100%">
        <el-option
          v-for="cat in categoriesStore.categories"
          :key="cat.id"
          :label="getCategoryName(cat)"
          :value="cat.id"
        />
      </el-select>
    </div>

    <!-- Tags -->
    <div class="form-group" v-if="tags.length">
      <label class="form-label">{{ $t('admin.tags') }}</label>
      <el-checkbox-group v-model="form.tags">
        <el-checkbox
          v-for="tag in tags"
          :key="tag.slug"
          :value="tag.slug"
        >
          {{ getTagName(tag.slug) }}
        </el-checkbox>
      </el-checkbox-group>
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

.scan-zone {
  margin-bottom: 16px;
  text-align: center;
  padding: 16px;
  border: 2px dashed var(--border);
  border-radius: var(--radius);
  background: var(--bg-card);
}

.lang-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 4px;
}

.lang-bar .lang-tabs {
  flex: 1;
}

.translate-btn {
  white-space: nowrap;
  flex-shrink: 0;
}

:deep(.el-tabs__active-bar) {
  background-color: var(--accent);
}

@media (max-width: 768px) {
  .ingredient-row { flex-wrap: wrap; }
}
</style>

<script setup>
import { useEditor, EditorContent } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'
import Placeholder from '@tiptap/extension-placeholder'
import { watch } from 'vue'

const props = defineProps({
  modelValue: { type: String, default: '' },
  placeholder: { type: String, default: '' },
  dir: { type: String, default: 'ltr' }
})

const emit = defineEmits(['update:modelValue'])

const editor = useEditor({
  content: props.modelValue,
  extensions: [
    StarterKit,
    Placeholder.configure({ placeholder: props.placeholder })
  ],
  onUpdate({ editor }) {
    emit('update:modelValue', editor.getHTML())
  }
})

watch(() => props.modelValue, (val) => {
  if (editor.value && editor.value.getHTML() !== val) {
    editor.value.commands.setContent(val || '', false)
  }
})
</script>

<template>
  <div class="rich-editor" :dir="dir">
    <div v-if="editor" class="toolbar">
      <button type="button" @click="editor.chain().focus().toggleBold().run()" :class="{ active: editor.isActive('bold') }">B</button>
      <button type="button" @click="editor.chain().focus().toggleItalic().run()" :class="{ active: editor.isActive('italic') }">I</button>
      <span class="divider" />
      <button type="button" @click="editor.chain().focus().toggleHeading({ level: 3 }).run()" :class="{ active: editor.isActive('heading', { level: 3 }) }">H</button>
      <button type="button" @click="editor.chain().focus().toggleBulletList().run()" :class="{ active: editor.isActive('bulletList') }">&#8226;</button>
      <button type="button" @click="editor.chain().focus().toggleOrderedList().run()" :class="{ active: editor.isActive('orderedList') }">1.</button>
      <span class="divider" />
      <button type="button" @click="editor.chain().focus().setHorizontalRule().run()">&#8213;</button>
      <button type="button" @click="editor.chain().focus().undo().run()">&#8617;</button>
      <button type="button" @click="editor.chain().focus().redo().run()">&#8618;</button>
    </div>
    <EditorContent :editor="editor" class="editor-content" />
  </div>
</template>

<style scoped>
.rich-editor {
  border: 1px solid var(--border);
  border-radius: var(--radius);
  overflow: hidden;
  background: var(--bg-card);
}

.toolbar {
  display: flex;
  gap: 2px;
  padding: 6px 8px;
  border-bottom: 1px solid var(--border);
  background: var(--category-bg);
  flex-wrap: wrap;
}

.toolbar button {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: var(--radius-sm);
  background: transparent;
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition);
  font-family: inherit;
}

.toolbar button:hover {
  background: var(--border);
  color: var(--text);
}

.toolbar button.active {
  background: var(--accent);
  color: white;
}

.divider {
  width: 1px;
  height: 24px;
  background: var(--border);
  margin: 4px 4px;
}

.editor-content {
  min-height: 200px;
  padding: 12px 16px;
}

.editor-content :deep(.tiptap) {
  outline: none;
  min-height: 180px;
  font-size: 0.95rem;
  line-height: 1.7;
  color: var(--text);
}

.editor-content :deep(.tiptap p) {
  margin-bottom: 8px;
}

.editor-content :deep(.tiptap h3) {
  font-size: 1.1rem;
  font-weight: 700;
  margin: 16px 0 8px;
}

.editor-content :deep(.tiptap ul),
.editor-content :deep(.tiptap ol) {
  padding-inline-start: 24px;
  margin-bottom: 8px;
}

.editor-content :deep(.tiptap li) {
  margin-bottom: 4px;
}

.editor-content :deep(.tiptap hr) {
  border: none;
  border-top: 1px solid var(--border);
  margin: 16px 0;
}

.editor-content :deep(.tiptap p.is-editor-empty:first-child::before) {
  content: attr(data-placeholder);
  float: left;
  color: var(--text-muted);
  pointer-events: none;
  height: 0;
}

[dir="rtl"] .editor-content :deep(.tiptap p.is-editor-empty:first-child::before) {
  float: right;
}
</style>

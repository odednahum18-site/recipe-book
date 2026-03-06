import { createI18n } from 'vue-i18n'
import en from './en.json'
import he from './he.json'

const i18n = createI18n({
  legacy: false,
  locale: localStorage.getItem('recipe-book-locale') || 'he',
  fallbackLocale: 'en',
  messages: { en, he }
})

export default i18n

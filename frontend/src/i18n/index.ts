import { createI18n } from 'vue-i18n'
import zh from './locales/zh-CN'
import en from './locales/en-US'

export type Locale = 'zh-CN' | 'en-US'

const i18n = createI18n({
  legacy: false, // Use Composition API mode
  locale: 'zh-CN' as Locale, // Default language
  fallbackLocale: 'en-US' as Locale, // Fallback language
  messages: {
    'zh-CN': zh,
    'en-US': en
  },
  globalInjection: true, // Globally inject $t and other functions
  silentTranslationWarn: true, // Silent translation warnings
  missingWarn: false, // Disable missing translation warnings
  fallbackWarn: false // Disable fallback translation warnings
})

export default i18n 
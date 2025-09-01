import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { Locale } from '../i18n'
import { detectUserLanguage, isLanguageSupported } from './languageDetector'

const STORAGE_KEY = 'agentmesh-locale'

export function useLanguage() {
  const { locale } = useI18n()
  
  // 从本地存储获取语言设置
  const getStoredLocale = (): Locale | null => {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (stored && isLanguageSupported(stored)) {
      return stored as Locale
    }
    return null
  }
  
  // 保存语言设置到本地存储
  const setStoredLocale = (newLocale: Locale) => {
    localStorage.setItem(STORAGE_KEY, newLocale)
  }
  
  // 切换语言
  const switchLanguage = (newLocale: Locale) => {
    if (isLanguageSupported(newLocale)) {
      locale.value = newLocale
      setStoredLocale(newLocale)
    }
  }
  
  // 初始化语言设置
  const initLanguage = () => {
    // 优先使用存储的语言设置
    const storedLocale = getStoredLocale()
    if (storedLocale) {
      locale.value = storedLocale
      return
    }
    
    // 其次使用浏览器检测的语言
    const detectedLocale = detectUserLanguage()
    locale.value = detectedLocale
    setStoredLocale(detectedLocale)
  }
  
  // 重置为默认语言
  const resetToDefault = () => {
    const defaultLocale: Locale = 'zh-CN'
    locale.value = defaultLocale
    setStoredLocale(defaultLocale)
  }
  
  return {
    locale: computed(() => locale.value),
    switchLanguage,
    initLanguage,
    resetToDefault,
    getStoredLocale
  }
}

export function getSupportedLocales(): { code: Locale; name: string; flag: string }[] {
  return [
    { code: 'zh-CN', name: '简体中文', flag: '🇨🇳' },
    { code: 'en-US', name: 'English', flag: '🇺🇸' }
  ]
}

// 语言切换事件
export const LANGUAGE_CHANGE_EVENT = 'language-change'

export function emitLanguageChange(newLocale: Locale) {
  window.dispatchEvent(new CustomEvent(LANGUAGE_CHANGE_EVENT, {
    detail: { locale: newLocale }
  }))
} 
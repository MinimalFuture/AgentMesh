import type { Locale } from '../i18n'

export function detectUserLanguage(): Locale {
  // Get browser language
  const browserLanguage = navigator.language || navigator.languages?.[0] || 'en-US'
  
  // Supported language list
  const supportedLocales: Locale[] = ['zh-CN', 'en-US']
  
  // Language mapping
  const languageMap: Record<string, Locale> = {
    'zh': 'zh-CN',
    'zh-CN': 'zh-CN',
    'zh-TW': 'zh-CN',
    'zh-HK': 'zh-CN',
    'en': 'en-US',
    'en-US': 'en-US',
    'en-GB': 'en-US',
    'en-CA': 'en-US',
    'en-AU': 'en-US'
  }
  
  // Try exact match
  if (languageMap[browserLanguage]) {
    return languageMap[browserLanguage]
  }
  
  // Try language code match
  const languageCode = browserLanguage.split('-')[0]
  if (languageMap[languageCode]) {
    return languageMap[languageCode]
  }
  
  // Default to English
  return 'en-US'
}

export function isLanguageSupported(locale: string): locale is Locale {
  const supportedLocales: Locale[] = ['zh-CN', 'en-US']
  return supportedLocales.includes(locale as Locale)
}

export function getLanguageDisplayName(locale: Locale): string {
  const displayNames: Record<Locale, string> = {
    'zh-CN': '简体中文',
    'en-US': 'English'
  }
  return displayNames[locale]
}

export function getLanguageFlag(locale: Locale): string {
  const flags: Record<Locale, string> = {
    'zh-CN': '🇨🇳',
    'en-US': '🇺🇸'
  }
  return flags[locale]
} 
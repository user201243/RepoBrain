import { docsLibrary, type Locale } from '../content'
import { defaultDocId, defaultLocale, defaultTheme, type Theme } from './docsConfig'

export function normalizeTheme(value: string | null): Theme | null {
  return value === 'light' || value === 'dark' ? value : null
}

export function normalizeLocale(value: string | null): Locale | null {
  return value === 'en' || value === 'vi' || value === 'zh' ? value : null
}

export function getInitialTheme(): Theme {
  if (typeof window === 'undefined') {
    return defaultTheme
  }

  const urlTheme = normalizeTheme(
    window.location.search ? new URLSearchParams(window.location.search).get('theme') : null,
  )
  if (urlTheme) {
    return urlTheme
  }

  const savedTheme = window.localStorage.getItem('repobrain-docs-theme')
  if (savedTheme === 'light' || savedTheme === 'dark') {
    return savedTheme
  }

  return defaultTheme
}

export function getInitialLocale(): Locale {
  if (typeof window === 'undefined') {
    return defaultLocale
  }

  const urlLocale = normalizeLocale(
    window.location.search ? new URLSearchParams(window.location.search).get('lang') : null,
  )
  if (urlLocale) {
    return urlLocale
  }

  const savedLocale = normalizeLocale(window.localStorage.getItem('repobrain-docs-locale'))
  if (savedLocale) {
    return savedLocale
  }

  const browserLocales =
    window.navigator.languages.length > 0 ? window.navigator.languages : [window.navigator.language]

  for (const browserLocale of browserLocales) {
    const normalizedLocale = browserLocale.toLowerCase()

    if (normalizedLocale.startsWith('vi')) {
      return 'vi'
    }

    if (normalizedLocale.startsWith('zh')) {
      return 'zh'
    }

    if (normalizedLocale.startsWith('en')) {
      return 'en'
    }
  }

  return defaultLocale
}

export function getInitialQuery() {
  if (typeof window === 'undefined') {
    return ''
  }

  return new URLSearchParams(window.location.search).get('q') ?? ''
}

export function getInitialSelectedDocId() {
  if (typeof window === 'undefined') {
    return defaultDocId
  }

  const docId = new URLSearchParams(window.location.search).get('doc')
  if (docId && docsLibrary.some((entry) => entry.id === docId)) {
    return docId
  }

  return defaultDocId
}

export function buildViewUrl({
  docId,
  locale,
  query,
  theme,
}: {
  docId: string
  locale: Locale
  query: string
  theme: Theme
}) {
  if (typeof window === 'undefined') {
    return ''
  }

  const url = new URL(window.location.href)
  const normalizedQuery = query.trim()

  if (docId && docId !== defaultDocId) {
    url.searchParams.set('doc', docId)
  } else {
    url.searchParams.delete('doc')
  }

  if (locale !== defaultLocale) {
    url.searchParams.set('lang', locale)
  } else {
    url.searchParams.delete('lang')
  }

  if (theme !== defaultTheme) {
    url.searchParams.set('theme', theme)
  } else {
    url.searchParams.delete('theme')
  }

  if (normalizedQuery) {
    url.searchParams.set('q', normalizedQuery)
  } else {
    url.searchParams.delete('q')
  }

  return url.toString()
}

export function isTypingTarget(target: EventTarget | null) {
  if (!(target instanceof HTMLElement)) {
    return false
  }

  return (
    target.isContentEditable ||
    target.tagName === 'INPUT' ||
    target.tagName === 'TEXTAREA' ||
    target.tagName === 'SELECT'
  )
}

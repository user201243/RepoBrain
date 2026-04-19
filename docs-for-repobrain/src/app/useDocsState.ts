import {
  type ChangeEvent,
  startTransition,
  useCallback,
  useDeferredValue,
  useEffect,
  useRef,
  useState,
} from 'react'
import type { Locale } from '../content'
import { normalizeSearchText } from '../i18n/localize'
import type { Theme } from './docsConfig'
import {
  getInitialLocale,
  getInitialQuery,
  getInitialSelectedDocId,
  getInitialTheme,
  isTypingTarget,
} from './urlState'

export function useDocsState() {
  const [theme, setTheme] = useState<Theme>(getInitialTheme)
  const [locale, setLocale] = useState<Locale>(getInitialLocale)
  const [query, setQuery] = useState(getInitialQuery)
  const [selectedDocId, setSelectedDocId] = useState(getInitialSelectedDocId)
  const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState(false)
  const desktopSearchRef = useRef<HTMLInputElement>(null)
  const mobileSearchRef = useRef<HTMLInputElement>(null)
  const shouldFocusMobileSearchRef = useRef(false)
  const deferredQuery = useDeferredValue(normalizeSearchText(query))

  function handleSearchChange(event: ChangeEvent<HTMLInputElement>) {
    const nextValue = event.target.value
    startTransition(() => {
      setQuery(nextValue)
    })
  }

  const handleClearSearch = useCallback(() => {
    startTransition(() => {
      setQuery('')
    })
  }, [])

  function toggleTheme() {
    setTheme((current) => (current === 'light' ? 'dark' : 'light'))
  }

  function closeMobileSidebar() {
    shouldFocusMobileSearchRef.current = false
    setIsMobileSidebarOpen(false)
  }

  const focusSearchInput = useCallback(() => {
    if (typeof window !== 'undefined' && window.matchMedia('(max-width: 980px)').matches) {
      shouldFocusMobileSearchRef.current = true
      setIsMobileSidebarOpen(true)
      return
    }

    desktopSearchRef.current?.focus()
    desktopSearchRef.current?.select()
  }, [])

  useEffect(() => {
    document.documentElement.dataset.theme = theme
    document.documentElement.style.colorScheme = theme
    window.localStorage.setItem('repobrain-docs-theme', theme)
  }, [theme])

  useEffect(() => {
    document.documentElement.lang = locale
    document.documentElement.dataset.locale = locale
    window.localStorage.setItem('repobrain-docs-locale', locale)
  }, [locale])

  useEffect(() => {
    document.body.style.overflow = isMobileSidebarOpen ? 'hidden' : ''

    return () => {
      document.body.style.overflow = ''
    }
  }, [isMobileSidebarOpen])

  useEffect(() => {
    if (typeof window === 'undefined') {
      return undefined
    }

    const mediaQuery = window.matchMedia('(min-width: 981px)')
    const handleChange = (event: MediaQueryListEvent) => {
      if (event.matches) {
        shouldFocusMobileSearchRef.current = false
        setIsMobileSidebarOpen(false)
      }
    }

    mediaQuery.addEventListener('change', handleChange)

    return () => {
      mediaQuery.removeEventListener('change', handleChange)
    }
  }, [])

  useEffect(() => {
    if (!isMobileSidebarOpen || !shouldFocusMobileSearchRef.current) {
      return
    }

    mobileSearchRef.current?.focus()
    mobileSearchRef.current?.select()
    shouldFocusMobileSearchRef.current = false
  }, [isMobileSidebarOpen])

  useEffect(() => {
    if (typeof window === 'undefined') {
      return undefined
    }

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.defaultPrevented) {
        return
      }

      const isSearchShortcut =
        (event.key === 'k' || event.key === 'K') && (event.ctrlKey || event.metaKey)

      if ((event.key === '/' && !isTypingTarget(event.target)) || isSearchShortcut) {
        event.preventDefault()
        focusSearchInput()
        return
      }

      if (event.key === 'Escape') {
        if (isMobileSidebarOpen) {
          event.preventDefault()
          shouldFocusMobileSearchRef.current = false
          setIsMobileSidebarOpen(false)
          return
        }

        if (query) {
          event.preventDefault()
          handleClearSearch()
        }
      }
    }

    window.addEventListener('keydown', handleKeyDown)

    return () => {
      window.removeEventListener('keydown', handleKeyDown)
    }
  }, [focusSearchInput, handleClearSearch, isMobileSidebarOpen, query])

  return {
    theme,
    setTheme,
    locale,
    setLocale,
    query,
    setQuery,
    deferredQuery,
    selectedDocId,
    setSelectedDocId,
    isMobileSidebarOpen,
    setIsMobileSidebarOpen,
    desktopSearchRef,
    mobileSearchRef,
    handleSearchChange,
    handleClearSearch,
    toggleTheme,
    closeMobileSidebar,
  }
}

import { MoonStar, SunMedium } from 'lucide-react'
import { uiCopy, type Locale } from '../../content'
import { localizeText } from '../../i18n/localize'
import type { Theme } from '../../app/docsConfig'

type ThemeToggleProps = {
  locale: Locale
  theme: Theme
  onToggleTheme: () => void
}

export function ThemeToggle({ locale, theme, onToggleTheme }: ThemeToggleProps) {
  const themeLabel = localizeText(uiCopy.themeLabel, locale)
  const currentThemeLabel =
    theme === 'light' ? localizeText(uiCopy.lightMode, locale) : localizeText(uiCopy.darkMode, locale)

  return (
    <button
      className="docs-theme-button"
      type="button"
      aria-label={`${themeLabel}: ${currentThemeLabel}`}
      aria-pressed={theme === 'dark'}
      onClick={onToggleTheme}
    >
      {theme === 'light' ? <SunMedium size={16} /> : <MoonStar size={16} />}
      <span>{currentThemeLabel}</span>
    </button>
  )
}

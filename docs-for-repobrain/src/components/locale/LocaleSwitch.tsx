import { localeOptions, type Locale } from '../../content'
import { localizeText } from '../../i18n/localize'
import { uiCopy } from '../../content'

type LocaleSwitchProps = {
  locale: Locale
  className?: string
  onLocaleChange: (locale: Locale) => void
}

export function LocaleSwitch({ locale, className = '', onLocaleChange }: LocaleSwitchProps) {
  return (
    <div
      className={`docs-locale-switch ${className}`.trim()}
      role="group"
      aria-label={localizeText(uiCopy.languageLabel, locale)}
    >
      {localeOptions.map((option) => (
        <button
          className={`docs-locale-button${locale === option.code ? ' active' : ''}`}
          key={option.code}
          type="button"
          aria-pressed={locale === option.code}
          onClick={() => onLocaleChange(option.code)}
        >
          {option.short}
        </button>
      ))}
    </div>
  )
}

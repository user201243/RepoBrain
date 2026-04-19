import { type Locale } from '../../content'
import { chromeUi } from '../../app/docsConfig'
import { localizeText } from '../../i18n/localize'

type EmptyStateProps = {
  locale: Locale
  onClearSearch: () => void
}

export function EmptyState({ locale, onClearSearch }: EmptyStateProps) {
  const text = (value: Parameters<typeof localizeText>[0]) => localizeText(value, locale)

  return (
    <div className="docs-empty">
      <h2>{text(chromeUi.noResultsTitle)}</h2>
      <p>{text(chromeUi.noResultsBody)}</p>
      <button className="doc-action-button" type="button" onClick={onClearSearch}>
        {text(chromeUi.clearSearch)}
      </button>
    </div>
  )
}

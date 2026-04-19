import { type DocEntry, type Locale } from '../../content'
import { chromeUi } from '../../app/docsConfig'
import { localizeText } from '../../i18n/localize'

type RelatedDocsProps = {
  docs: DocEntry[]
  locale: Locale
  onSelectDoc: (docId: string) => void
}

export function RelatedDocs({ docs, locale, onSelectDoc }: RelatedDocsProps) {
  if (docs.length === 0) {
    return null
  }

  const text = (value: Parameters<typeof localizeText>[0]) => localizeText(value, locale)

  return (
    <section className="doc-related">
      <div className="doc-related-head">
        <span className="doc-kicker">{text(chromeUi.relatedDocs)}</span>
        <p>{text(chromeUi.relatedDocsBody)}</p>
      </div>

      <div className="doc-related-grid">
        {docs.map((doc) => (
          <button className="doc-related-card" key={doc.id} type="button" onClick={() => onSelectDoc(doc.id)}>
            <span>{text(doc.eyebrow)}</span>
            <strong>{text(doc.title)}</strong>
            <small>{text(doc.summary)}</small>
          </button>
        ))}
      </div>
    </section>
  )
}

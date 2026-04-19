import { docsLibrary, quickstartSteps, type DocEntry, type Locale, uiCopy } from '../../content'
import { quickstartDocIds } from '../../app/docsConfig'
import { localizeText } from '../../i18n/localize'

type QuickstartSectionProps = {
  locale: Locale
  onSelectDoc: (docId: string) => void
}

export function QuickstartSection({ locale, onSelectDoc }: QuickstartSectionProps) {
  const text = (value: Parameters<typeof localizeText>[0]) => localizeText(value, locale)
  const linkedDocs = quickstartDocIds
    .map((docId) => docsLibrary.find((doc) => doc.id === docId))
    .filter((doc): doc is DocEntry => doc !== undefined)

  return (
    <section className="quickstart-section" id="quickstart">
      <div className="quickstart-header">
        <span className="doc-kicker">{text(uiCopy.quickstartEyebrow)}</span>
        <h2>{text(uiCopy.quickstartTitle)}</h2>
        <p>{text(uiCopy.quickstartBody)}</p>
      </div>

      <div className="quickstart-grid">
        {quickstartSteps.map((step, index) => (
          <article className="quickstart-card" key={step.command}>
            <span className="quickstart-step-number">{String(index + 1).padStart(2, '0')}</span>
            <div className="quickstart-card-copy">
              <h3>{text(step.title)}</h3>
              <p>{text(step.body)}</p>
            </div>
            <pre>
              <code>{step.command}</code>
            </pre>
          </article>
        ))}
      </div>

      <div className="quickstart-doc-links" aria-label={text(uiCopy.readingOrderTitle)}>
        {linkedDocs.map((doc) => (
          <button className="quickstart-doc-link" key={doc.id} type="button" onClick={() => onSelectDoc(doc.id)}>
            <span>{text(doc.eyebrow)}</span>
            <strong>{text(doc.title)}</strong>
          </button>
        ))}
      </div>
    </section>
  )
}

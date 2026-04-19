import { ExternalLink } from 'lucide-react'
import { type DocEntry, type Locale, uiCopy } from '../../content'
import { chromeUi } from '../../app/docsConfig'
import { localizeText } from '../../i18n/localize'
import { MarkdownRenderer } from './MarkdownRenderer'
import { RelatedDocs } from './RelatedDocs'
import { TerminalCliPreview } from './TerminalCliPreview'

type SelectDocOptions = {
  clearSearch?: boolean
  scrollTarget?: string
}

type DocPageProps = {
  doc: DocEntry
  readerContent: string
  githubUrl: string
  sourcePath: string
  relatedDocs: DocEntry[]
  locale: Locale
  onSelectDoc: (docId: string, options?: SelectDocOptions) => void
}

export function DocPage({
  doc,
  readerContent,
  githubUrl,
  sourcePath,
  relatedDocs,
  locale,
  onSelectDoc,
}: DocPageProps) {
  const text = (value: Parameters<typeof localizeText>[0]) => localizeText(value, locale)

  return (
    <div className="doc-page" id="doc-top">
      <section className="doc-header">
        <span className="doc-kicker">{text(doc.eyebrow)}</span>
        <h1>{text(doc.title)}</h1>

        <div className="doc-header-actions">
          <a className="doc-action-button" href={githubUrl} target="_blank" rel="noreferrer">
            <ExternalLink size={16} />
            <span>{text(chromeUi.openGithub)}</span>
          </a>
        </div>

        <p className="doc-summary">{text(doc.summary)}</p>

        <div className="doc-meta-row">
          <article className="doc-meta-card">
            <span>{text(chromeUi.source)}</span>
            <code>{sourcePath}</code>
          </article>

          <article className="doc-meta-card">
            <span>{text(uiCopy.bestFor)}</span>
            <strong>{text(doc.audience)}</strong>
          </article>
        </div>

        <div className="doc-tags">
          {doc.tags.map((tag) => (
            <span key={tag}>{tag}</span>
          ))}
        </div>
      </section>

      {doc.id === 'vision' ? <TerminalCliPreview locale={locale} /> : null}

      <article className="doc-article">
        <MarkdownRenderer content={readerContent} onSelectDoc={onSelectDoc} />
      </article>

      <RelatedDocs docs={relatedDocs} locale={locale} onSelectDoc={(docId) => onSelectDoc(docId)} />
    </div>
  )
}

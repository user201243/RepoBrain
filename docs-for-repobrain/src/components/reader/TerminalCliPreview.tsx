import cliTerminalUrl from '../../assets/repobrain-cli-terminal.svg'
import { type Locale } from '../../content'
import { chromeUi } from '../../app/docsConfig'
import { localizeText } from '../../i18n/localize'

type TerminalCliPreviewProps = {
  locale: Locale
}

export function TerminalCliPreview({ locale }: TerminalCliPreviewProps) {
  const text = (value: Parameters<typeof localizeText>[0]) => localizeText(value, locale)

  return (
    <section className="terminal-preview" aria-labelledby="terminal-preview-title">
      <div className="terminal-preview-copy">
        <span className="doc-kicker">CLI</span>
        <h2 id="terminal-preview-title">{text(chromeUi.terminalPreviewTitle)}</h2>
        <p>{text(chromeUi.terminalPreviewBody)}</p>
      </div>
      <figure className="terminal-preview-frame">
        <img src={cliTerminalUrl} alt={text(chromeUi.terminalPreviewAlt)} />
      </figure>
    </section>
  )
}

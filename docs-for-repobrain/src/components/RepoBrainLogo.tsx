import markUrl from '../assets/repobrain-mark.svg'

type RepoBrainLogoProps = {
  compact?: boolean
  showTagline?: boolean
  tagline?: string
}

export function RepoBrainLogo({
  compact = false,
  showTagline = true,
  tagline = 'local-first codebase memory engine for AI coding assistants',
}: RepoBrainLogoProps) {
  return (
    <div className={`brand-lockup${compact ? ' compact' : ''}`}>
      <img className="brand-mark" src={markUrl} alt="RepoBrain brand mark" />
      <div className="brand-copy">
        <div className="brand-wordmark" aria-label="RepoBrain">
          <span className="brand-word brand-word-repo">Repo</span>
          <span className="brand-word brand-word-brain">Brain</span>
        </div>
        {showTagline ? (
          <p className="brand-tagline">{tagline}</p>
        ) : null}
      </div>
    </div>
  )
}

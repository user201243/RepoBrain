import type { ChangeEvent, RefObject } from 'react'
import { GitBranch, Menu, X } from 'lucide-react'
import type { DocEntry, Locale } from '../../content'
import { uiCopy } from '../../content'
import { chromeUi, docsNavItems, githubRepoUrl, type DocsNavItem, type Theme } from '../../app/docsConfig'
import { localizeText } from '../../i18n/localize'
import { LocaleSwitch } from '../locale/LocaleSwitch'
import { ThemeToggle } from '../locale/ThemeToggle'
import { RepoBrainLogo } from '../RepoBrainLogo'
import { DocsSearch } from '../search/DocsSearch'

type DocsHeaderProps = {
  selectedDoc: DocEntry | undefined
  locale: Locale
  theme: Theme
  query: string
  isMobileSidebarOpen: boolean
  desktopSearchRef: RefObject<HTMLInputElement | null>
  onToggleMobileSidebar: () => void
  onBrandSelect: () => void
  onNavSelect: (item: DocsNavItem) => void
  onLocaleChange: (locale: Locale) => void
  onToggleTheme: () => void
  onSearchChange: (event: ChangeEvent<HTMLInputElement>) => void
  onClearSearch: () => void
}

export function DocsHeader({
  selectedDoc,
  locale,
  theme,
  query,
  isMobileSidebarOpen,
  desktopSearchRef,
  onToggleMobileSidebar,
  onBrandSelect,
  onNavSelect,
  onLocaleChange,
  onToggleTheme,
  onSearchChange,
  onClearSearch,
}: DocsHeaderProps) {
  const text = (value: Parameters<typeof localizeText>[0]) => localizeText(value, locale)

  return (
    <header className="docs-header">
      <div className="docs-header-inner">
        <div className="docs-header-left">
          <button
            className="docs-menu-button mobile-only"
            type="button"
            aria-expanded={isMobileSidebarOpen}
            aria-label={isMobileSidebarOpen ? text(chromeUi.menuClose) : text(chromeUi.menuOpen)}
            onClick={onToggleMobileSidebar}
          >
            {isMobileSidebarOpen ? <X size={18} /> : <Menu size={18} />}
          </button>

          <a
            className="docs-brand-link"
            href="#doc-top"
            onClick={(event) => {
              event.preventDefault()
              onBrandSelect()
            }}
          >
            <RepoBrainLogo compact showTagline={false} />
          </a>

          <nav className="docs-primary-nav desktop-only" aria-label={text(chromeUi.navigation)}>
            {docsNavItems.map((item) => {
              if (item.href) {
                return (
                  <a
                    className="docs-nav-button"
                    key={item.id}
                    href={item.href}
                    target="_blank"
                    rel="noreferrer"
                  >
                    {text(item.label)}
                  </a>
                )
              }

              const isActive = selectedDoc ? item.docIds?.includes(selectedDoc.id) ?? false : false

              return (
                <button
                  className={`docs-nav-button${isActive ? ' active' : ''}`}
                  key={item.id}
                  type="button"
                  onClick={() => onNavSelect(item)}
                >
                  {text(item.label)}
                </button>
              )
            })}
          </nav>
        </div>

        <div className="docs-header-actions">
          <DocsSearch
            className="desktop-only"
            inputRef={desktopSearchRef}
            value={query}
            onChange={onSearchChange}
            onClear={onClearSearch}
            placeholder={text(uiCopy.searchPlaceholder)}
            clearLabel={text(chromeUi.clearSearch)}
            shortcutLabel={text(chromeUi.searchShortcut)}
          />

          <a className="docs-link-button desktop-only" href={githubRepoUrl} target="_blank" rel="noreferrer">
            <GitBranch size={16} />
            <span>{text(chromeUi.repoLink)}</span>
          </a>

          <LocaleSwitch locale={locale} onLocaleChange={onLocaleChange} className="desktop-only" />
          <ThemeToggle locale={locale} theme={theme} onToggleTheme={onToggleTheme} />
        </div>
      </div>
    </header>
  )
}

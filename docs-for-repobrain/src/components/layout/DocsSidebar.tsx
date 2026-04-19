import type { ChangeEvent, RefObject } from 'react'
import { GitBranch } from 'lucide-react'
import { type DocEntry, type Locale, uiCopy } from '../../content'
import { chromeUi, githubRepoUrl, type DocsSidebarGroup } from '../../app/docsConfig'
import { localizeText } from '../../i18n/localize'
import { LocaleSwitch } from '../locale/LocaleSwitch'
import { DocsSearch } from '../search/DocsSearch'

type SidebarGroupWithDocs = DocsSidebarGroup & {
  docs: DocEntry[]
}

type DocsSidebarProps = {
  locale: Locale
  query: string
  visibleDocsCount: number
  selectedDoc: DocEntry | undefined
  isOpen: boolean
  sidebarGroups: SidebarGroupWithDocs[]
  remainingDocs: DocEntry[]
  mobileSearchRef: RefObject<HTMLInputElement | null>
  onSearchChange: (event: ChangeEvent<HTMLInputElement>) => void
  onClearSearch: () => void
  onSelectDoc: (docId: string) => void
  onLocaleChange: (locale: Locale) => void
}

export function DocsSidebar({
  locale,
  query,
  visibleDocsCount,
  selectedDoc,
  isOpen,
  sidebarGroups,
  remainingDocs,
  mobileSearchRef,
  onSearchChange,
  onClearSearch,
  onSelectDoc,
  onLocaleChange,
}: DocsSidebarProps) {
  const text = (value: Parameters<typeof localizeText>[0]) => localizeText(value, locale)

  return (
    <aside className={`docs-sidebar${isOpen ? ' open' : ''}`}>
      <div className="docs-sidebar-inner">
        <div className="docs-sidebar-top">
          <div>
            <span className="docs-sidebar-label">{text(chromeUi.docsIndex)}</span>
            <strong>
              {visibleDocsCount} {text(uiCopy.docsUnit)}
            </strong>
          </div>
          <a className="docs-sidebar-repo" href={githubRepoUrl} target="_blank" rel="noreferrer">
            <GitBranch size={15} />
            <span>{text(chromeUi.repoBrowse)}</span>
          </a>
        </div>

        <LocaleSwitch locale={locale} onLocaleChange={onLocaleChange} className="mobile-only docs-sidebar-locale" />

        <DocsSearch
          className="mobile-only"
          inputRef={mobileSearchRef}
          value={query}
          onChange={onSearchChange}
          onClear={onClearSearch}
          placeholder={text(uiCopy.searchPlaceholder)}
          clearLabel={text(chromeUi.clearSearch)}
          shortcutLabel={text(chromeUi.searchShortcut)}
        />

        {query ? (
          <p className="docs-sidebar-filter">
            {text(chromeUi.sidebarFiltered)}: <strong>{query}</strong>
          </p>
        ) : null}

        <nav className="docs-sidebar-nav" aria-label={text(chromeUi.navigation)}>
          {sidebarGroups.map((group) => (
            <details className="docs-sidebar-group" key={group.id} open>
              <summary>{text(group.label)}</summary>
              <div className="docs-sidebar-list">
                {group.docs.map((doc) => (
                  <button
                    className={`docs-sidebar-item${selectedDoc?.id === doc.id ? ' active' : ''}`}
                    key={doc.id}
                    type="button"
                    onClick={() => onSelectDoc(doc.id)}
                  >
                    <span>{text(doc.title)}</span>
                  </button>
                ))}
              </div>
            </details>
          ))}

          {remainingDocs.length > 0 ? (
            <details className="docs-sidebar-group" open>
              <summary>{text(chromeUi.moreNotes)}</summary>
              <div className="docs-sidebar-list">
                {remainingDocs.map((doc) => (
                  <button
                    className={`docs-sidebar-item${selectedDoc?.id === doc.id ? ' active' : ''}`}
                    key={doc.id}
                    type="button"
                    onClick={() => onSelectDoc(doc.id)}
                  >
                    <span>{text(doc.title)}</span>
                  </button>
                ))}
              </div>
            </details>
          ) : null}
        </nav>
      </div>
    </aside>
  )
}

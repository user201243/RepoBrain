import { useEffect } from 'react'
import { docsLibrary } from './content'
import {
  buildGithubDocUrl,
  getDocReaderContent,
  getDocSearchContent,
  getRelatedDocs,
} from './app/docsHelpers'
import {
  chromeUi,
  defaultDocId,
  docsSidebarGroups,
  quickstartDocIds,
  type DocsNavItem,
} from './app/docsConfig'
import { useDocsState } from './app/useDocsState'
import { buildViewUrl } from './app/urlState'
import { DocsHeader } from './components/layout/DocsHeader'
import { DocsSidebar } from './components/layout/DocsSidebar'
import { MobileSidebarBackdrop } from './components/layout/MobileSidebarBackdrop'
import { QuickstartSection } from './components/quickstart/QuickstartSection'
import { DocPage } from './components/reader/DocPage'
import { EmptyState } from './components/reader/EmptyState'
import { buildLocalizedSearchText, localizeText } from './i18n/localize'
import './App.css'

type SelectDocOptions = {
  clearSearch?: boolean
  scrollTarget?: string
}

function App() {
  const {
    theme,
    locale,
    setLocale,
    query,
    setQuery,
    deferredQuery,
    selectedDocId,
    setSelectedDocId,
    isMobileSidebarOpen,
    setIsMobileSidebarOpen,
    desktopSearchRef,
    mobileSearchRef,
    handleSearchChange,
    handleClearSearch,
    toggleTheme,
    closeMobileSidebar,
  } = useDocsState()

  const visibleDocs = docsLibrary.filter((doc) => {
    if (!deferredQuery) {
      return true
    }

    const haystack = buildLocalizedSearchText(
      locale,
      doc.title,
      doc.eyebrow,
      doc.summary,
      doc.audience,
      doc.path,
      doc.tags.join(' '),
      getDocSearchContent(doc, locale),
    )

    return haystack.includes(deferredQuery)
  })

  const effectiveSelectedDocId =
    visibleDocs.find((entry) => entry.id === selectedDocId)?.id ?? visibleDocs[0]?.id ?? ''
  const selectedDoc = effectiveSelectedDocId
    ? docsLibrary.find((entry) => entry.id === effectiveSelectedDocId)
    : undefined
  const selectedDocReaderContent = selectedDoc ? getDocReaderContent(selectedDoc, locale) : ''
  const selectedDocPath = selectedDoc?.path.replace(/^docs-for-repobrain\//, '') ?? ''
  const selectedDocGithubUrl = selectedDoc ? buildGithubDocUrl(selectedDoc.path) : ''
  const relatedDocs = selectedDoc ? getRelatedDocs(selectedDoc) : []
  const groupedDocIds = new Set(docsSidebarGroups.flatMap((group) => group.docIds))
  const sidebarGroups = docsSidebarGroups
    .map((group) => ({
      ...group,
      docs: visibleDocs.filter((doc) => group.docIds.includes(doc.id)),
    }))
    .filter((group) => group.docs.length > 0)
  const remainingDocs = visibleDocs.filter((doc) => !groupedDocIds.has(doc.id))
  const shouldShowQuickstart = selectedDoc ? quickstartDocIds.includes(selectedDoc.id) : false

  function scrollToTarget(targetId: string) {
    window.requestAnimationFrame(() => {
      document.getElementById(targetId)?.scrollIntoView({
        behavior: 'smooth',
        block: 'start',
      })
    })
  }

  function handleSelectDoc(docId: string, options?: SelectDocOptions) {
    if (options?.clearSearch) {
      setQuery('')
    }

    setSelectedDocId(docId)
    closeMobileSidebar()
    scrollToTarget(options?.scrollTarget ?? 'doc-top')
  }

  function handleNavSelect(item: DocsNavItem) {
    handleSelectDoc(item.docIds?.[0] ?? defaultDocId, {
      clearSearch: true,
      scrollTarget: item.scrollTarget ?? 'doc-top',
    })
  }

  function handleBrandSelect() {
    handleSelectDoc(defaultDocId, { clearSearch: true, scrollTarget: 'doc-top' })
  }

  useEffect(() => {
    if (typeof window === 'undefined') {
      return
    }

    const nextUrl = buildViewUrl({
      docId: effectiveSelectedDocId || selectedDocId || defaultDocId,
      locale,
      query,
      theme,
    })

    if (nextUrl && nextUrl !== window.location.href) {
      window.history.replaceState(null, '', nextUrl)
    }
  }, [effectiveSelectedDocId, locale, query, selectedDocId, theme])

  return (
    <div className="docs-app">
      <DocsHeader
        selectedDoc={selectedDoc}
        locale={locale}
        theme={theme}
        query={query}
        isMobileSidebarOpen={isMobileSidebarOpen}
        desktopSearchRef={desktopSearchRef}
        onToggleMobileSidebar={() => setIsMobileSidebarOpen((current) => !current)}
        onBrandSelect={handleBrandSelect}
        onNavSelect={handleNavSelect}
        onLocaleChange={setLocale}
        onToggleTheme={toggleTheme}
        onSearchChange={handleSearchChange}
        onClearSearch={handleClearSearch}
      />

      <div className="docs-layout">
        <DocsSidebar
          locale={locale}
          query={query}
          visibleDocsCount={visibleDocs.length}
          selectedDoc={selectedDoc}
          isOpen={isMobileSidebarOpen}
          sidebarGroups={sidebarGroups}
          remainingDocs={remainingDocs}
          mobileSearchRef={mobileSearchRef}
          onSearchChange={handleSearchChange}
          onClearSearch={handleClearSearch}
          onSelectDoc={(docId) => handleSelectDoc(docId)}
          onLocaleChange={setLocale}
        />

        <main className="docs-main">
          {selectedDoc ? (
            <>
              {shouldShowQuickstart ? (
                <QuickstartSection
                  locale={locale}
                  onSelectDoc={(docId) => handleSelectDoc(docId, { clearSearch: true, scrollTarget: 'doc-top' })}
                />
              ) : null}

              <DocPage
                doc={selectedDoc}
                readerContent={selectedDocReaderContent}
                githubUrl={selectedDocGithubUrl}
                sourcePath={selectedDocPath}
                relatedDocs={relatedDocs}
                locale={locale}
                onSelectDoc={handleSelectDoc}
              />
            </>
          ) : (
            <EmptyState locale={locale} onClearSearch={handleClearSearch} />
          )}
        </main>
      </div>

      {isMobileSidebarOpen ? (
        <MobileSidebarBackdrop
          label={localizeText(chromeUi.menuClose, locale)}
          onClose={closeMobileSidebar}
        />
      ) : null}
    </div>
  )
}

export default App

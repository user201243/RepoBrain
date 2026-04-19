import {
  docsLibrary,
  localizedDocContent,
  type DocEntry,
  type Locale,
} from '../content'
import { localizeText } from '../i18n/localize'
import { chromeUi, githubRepoUrl } from './docsConfig'

export function buildGithubDocUrl(path: string) {
  return `${githubRepoUrl}/blob/main/${path.replaceAll('\\', '/')}`
}

export function getDocReaderContent(doc: DocEntry, locale: Locale) {
  const localizedContent = localizedDocContent[doc.id]?.[locale]?.trim()
  if (localizedContent) {
    return localizedContent
  }

  if (locale === 'en') {
    return doc.content
  }

  return [`# ${localizeText(doc.title, locale)}`, '', localizeText(chromeUi.missingDocBody, locale)].join('\n')
}

export function getDocSearchContent(doc: DocEntry, locale: Locale) {
  const localizedContent = localizedDocContent[doc.id]?.[locale]

  if (localizedContent) {
    return localizedContent
  }

  if (locale === 'en') {
    return doc.content
  }

  return ''
}

export function resolveLocalDocId(href: string | undefined) {
  if (!href) {
    return null
  }

  const cleanedHref = href.split('#')[0]?.replaceAll('\\', '/').replace(/^\.?\//, '')
  if (!cleanedHref) {
    return null
  }

  const cleanedBasename = cleanedHref.split('/').at(-1)

  for (const entry of docsLibrary) {
    const entryBasename = entry.path.split('/').at(-1)
    if (
      cleanedHref === entry.path ||
      cleanedHref === entryBasename ||
      entry.path.endsWith(cleanedHref) ||
      cleanedBasename === entryBasename
    ) {
      return entry.id
    }
  }

  return null
}

export function getRelatedDocs(selectedDoc: DocEntry, maxItems = 3) {
  return docsLibrary
    .filter(
      (entry) =>
        entry.id !== selectedDoc.id &&
        entry.tags.some((tag) => selectedDoc.tags.includes(tag)),
    )
    .slice(0, maxItems)
}

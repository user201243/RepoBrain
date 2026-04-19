import type { Locale, LocalizedText } from '../content'

export const t = (en: string, vi: string, zh: string): LocalizedText => ({ en, vi, zh })

export function localizeText(value: LocalizedText, locale: Locale) {
  return value[locale] ?? value.en
}

export function normalizeSearchText(value: string) {
  return value
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[đ]/g, 'd')
    .replaceAll('`', '')
    .trim()
}

export function buildLocalizedSearchText(locale: Locale, ...values: Array<string | LocalizedText>) {
  return normalizeSearchText(
    values
      .map((value) => (typeof value === 'string' ? value : localizeText(value, locale)))
      .join(' '),
  )
}

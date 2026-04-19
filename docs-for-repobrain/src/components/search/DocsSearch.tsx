import type { ChangeEvent, RefObject } from 'react'
import { Search, X } from 'lucide-react'

type DocsSearchProps = {
  inputRef: RefObject<HTMLInputElement | null>
  value: string
  placeholder: string
  clearLabel: string
  shortcutLabel: string
  className?: string
  onChange: (event: ChangeEvent<HTMLInputElement>) => void
  onClear: () => void
}

export function DocsSearch({
  inputRef,
  value,
  placeholder,
  clearLabel,
  shortcutLabel,
  className = '',
  onChange,
  onClear,
}: DocsSearchProps) {
  return (
    <div className={`docs-search ${className}`.trim()} role="search">
      <Search size={16} />
      <input
        ref={inputRef}
        type="search"
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        aria-label={placeholder}
      />
      {value ? (
        <button className="docs-search-clear" type="button" onClick={onClear} aria-label={clearLabel}>
          <X size={14} />
        </button>
      ) : (
        <span className="docs-search-shortcut">{shortcutLabel}</span>
      )}
    </div>
  )
}

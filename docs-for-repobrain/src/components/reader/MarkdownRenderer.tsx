import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { resolveLocalDocId } from '../../app/docsHelpers'

type MarkdownRendererProps = {
  content: string
  onSelectDoc: (docId: string, options?: { clearSearch?: boolean }) => void
}

export function MarkdownRenderer({ content, onSelectDoc }: MarkdownRendererProps) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={{
        a: ({ href, children }) => {
          const localDocId = resolveLocalDocId(href)

          if (localDocId) {
            return (
              <a
                href="#doc-top"
                onClick={(event) => {
                  event.preventDefault()
                  onSelectDoc(localDocId, { clearSearch: true })
                }}
              >
                {children}
              </a>
            )
          }

          return (
            <a href={href} target="_blank" rel="noreferrer">
              {children}
            </a>
          )
        },
        table: ({ children, ...props }) => (
          <div className="table-scroll">
            <table {...props}>{children}</table>
          </div>
        ),
      }}
    >
      {content}
    </ReactMarkdown>
  )
}

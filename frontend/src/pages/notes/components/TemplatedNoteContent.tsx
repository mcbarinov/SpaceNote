import { useEffect, useRef } from "react"
import { Markdown } from "@/components/Markdown"

interface TemplatedNoteContentProps {
  content: string
}

export function TemplatedNoteContent({ content }: TemplatedNoteContentProps) {
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!containerRef.current) return

    // Process all markdown sections after rendering
    const markdownElements = containerRef.current.querySelectorAll('[data-markdown="true"]')
    markdownElements.forEach(element => {
      const markdownContent = element.textContent || ""
      const wrapper = document.createElement("div")
      element.replaceWith(wrapper)

      // Use React portal to render Markdown component
      import("react-dom/client").then(({ createRoot }) => {
        const root = createRoot(wrapper)
        root.render(<Markdown content={markdownContent} />)
      })
    })
  }, [content])

  return <div ref={containerRef} className="prose prose-gray max-w-none" dangerouslySetInnerHTML={{ __html: content }} />
}

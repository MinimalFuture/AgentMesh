<template>
  <div class="markdown-content" v-html="formattedContent"></div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { marked } from 'marked'
import hljs from 'highlight.js'
import DOMPurify from 'dompurify'
import katex from 'katex'
import '../assets/style/markdown.css'

// Import highlight.js styles
import 'highlight.js/styles/github.css'
import 'katex/dist/katex.min.css'

interface MarkdownRendererProps {
  content: string
  className?: string
}

const props = withDefaults(defineProps<MarkdownRendererProps>(), {
  className: ''
})

// Configure marked options
marked.setOptions({
  gfm: true,          // Enable GitHub extensions
  breaks: false       // Standard line break handling
})

// Function to render LaTeX
function renderLatex(text: string): string {
  // Inline LaTeX: $...$
  text = text.replace(/\$([^\$\n]+?)\$/g, (match, latex) => {
    try {
      return katex.renderToString(latex, { displayMode: false })
    } catch (error) {
      console.warn('KaTeX inline error:', error)
      return match
    }
  })
  
  // Block LaTeX: $$...$$
  text = text.replace(/\$\$([\s\S]+?)\$\$/g, (match, latex) => {
    try {
      return katex.renderToString(latex, { displayMode: true })
    } catch (error) {
      console.warn('KaTeX block error:', error)
      return match
    }
  })
  
  return text
}

// Function to highlight code blocks
function highlightCode(html: string): string {
  return html.replace(/<pre><code class="language-(\w+)">([\s\S]*?)<\/code><\/pre>/g, (match, lang, code) => {
    if (lang && hljs.getLanguage(lang)) {
      try {
        const highlighted = hljs.highlight(code, { language: lang }).value
        return `<pre><code class="hljs language-${lang}">${highlighted}</code></pre>`
      } catch (err) {
        console.warn('Highlight.js error:', err)
      }
    }
    return match
  })
}

const formattedContent = computed((): string => {
  if (!props.content) return ''
  
  try {
    // First render LaTeX
    const latexProcessed = renderLatex(props.content)
    
    // Then render markdown
    const markdownResult = marked(latexProcessed)
    let htmlContent = typeof markdownResult === 'string' ? markdownResult : markdownResult.toString()
    
    // Apply code highlighting
    htmlContent = highlightCode(htmlContent)
    
    // Finally sanitize HTML for security
    const cleanHtml = DOMPurify.sanitize(htmlContent, {
      ALLOWED_TAGS: [
        'p', 'br', 'strong', 'em', 'u', 's', 'del', 'ins',
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'ul', 'ol', 'li', 'dl', 'dt', 'dd',
        'blockquote', 'pre', 'code', 'kbd', 'samp',
        'table', 'thead', 'tbody', 'tfoot', 'tr', 'td', 'th',
        'a', 'img', 'hr',
        'div', 'span', 'section', 'article', 'aside',
        // KaTeX elements
        'span', 'math', 'semantics', 'mrow', 'mi', 'mo', 'mn', 'mtext',
        'mfrac', 'msup', 'msub', 'msubsup', 'mroot', 'msqrt',
        'mtable', 'mtr', 'mtd', 'mth',
        'mover', 'munder', 'munderover',
        'mpadded', 'mphantom', 'menclose'
      ],
      ALLOWED_ATTR: [
        'href', 'src', 'alt', 'title', 'class', 'id',
        'style', 'target', 'rel',
        // KaTeX attributes
        'data-latex', 'aria-label', 'aria-describedby'
      ]
    })
    
    return cleanHtml
  } catch (error) {
    console.error('Error parsing markdown:', error)
    // Fallback to basic formatting if markdown parsing fails
    return props.content
      .replace(/\n/g, '<br>')
      .replace(/```(\w+)?\n([\s\S]*?)```/g, '<pre class="code-block"><code>$2</code></pre>')
      .replace(/`([^`]+)`/g, '<code class="inline-code">$1</code>')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
  }
})
</script>

<style scoped>
@import '../assets/style/markdown.css';

/* Legacy styles for backward compatibility */
.code-block {
  @apply bg-gray-50 border border-gray-200 rounded-md p-3 my-2 overflow-x-auto;
}

.code-block code {
  @apply font-mono text-sm text-gray-700 whitespace-pre;
}

.inline-code {
  @apply font-mono text-sm bg-gray-50 px-1 py-0.5 rounded text-green-600;
}

/* KaTeX styles */
:deep(.katex) {
  font-size: 1.1em;
}

:deep(.katex-display) {
  margin: 1em 0;
  text-align: center;
}

/* Highlight.js styles */
:deep(.hljs) {
  background: #f6f8fa;
  border-radius: 6px;
  padding: 16px;
  overflow-x: auto;
}

:deep(.hljs-keyword) {
  color: #d73a49;
}

:deep(.hljs-string) {
  color: #032f62;
}

:deep(.hljs-comment) {
  color: #6a737d;
  font-style: italic;
}

:deep(.hljs-number) {
  color: #005cc5;
}

:deep(.hljs-function) {
  color: #6f42c1;
}
</style> 
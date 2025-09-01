declare module 'highlight.js' {
  export interface HighlightResult {
    value: string
    language: string
  }
  
  export interface HighlightOptions {
    language?: string
  }
  
  export function highlight(code: string, options: HighlightOptions): HighlightResult
  export function getLanguage(lang: string): boolean
  export default {
    highlight,
    getLanguage
  }
}

declare module 'katex' {
  export interface KaTeXOptions {
    displayMode?: boolean
  }
  
  export function renderToString(latex: string, options?: KaTeXOptions): string
  export default {
    renderToString
  }
} 
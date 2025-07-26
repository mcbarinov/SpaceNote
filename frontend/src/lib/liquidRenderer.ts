import { Liquid } from "liquidjs"
import type { Space } from "@/lib/api/spaces"
import type { Note } from "@/lib/api/notes"
import { formatDateTime, formatDateOnly } from "@/lib/formatters"

const liquid = new Liquid({
  strictFilters: true,
  strictVariables: false,
})

liquid.registerFilter("date", (value: string | Date, format?: string) => {
  if (!value) return ""
  const date = typeof value === "string" ? new Date(value) : value

  if (format === "date_only") {
    return formatDateOnly(date.toISOString())
  }

  return formatDateTime(date.toISOString())
})

liquid.registerFilter("markdown", (value: string) => {
  if (!value) return ""
  return `<div data-markdown="true">${value}</div>`
})

liquid.registerFilter("truncate", (value: string, length = 50, suffix = "...") => {
  if (!value || value.length <= length) return value
  return value.substring(0, length) + suffix
})

liquid.registerFilter("default", (value: unknown, defaultValue: unknown) => {
  return value ?? defaultValue
})

export interface TemplateContext {
  note: Note
  space: Space
}

export async function renderLiquidTemplate(template: string, context: TemplateContext): Promise<string> {
  if (!template.trim()) return ""

  try {
    return await liquid.parseAndRender(template, context)
  } catch (error) {
    console.error("Template rendering error:", error)
    throw new Error(`Template error: ${error instanceof Error ? error.message : "Unknown error"}`)
  }
}

export function validateLiquidTemplate(template: string): { valid: boolean; error?: string } {
  if (!template.trim()) return { valid: true }

  try {
    liquid.parse(template)
    return { valid: true }
  } catch (error) {
    return {
      valid: false,
      error: error instanceof Error ? error.message : "Invalid template",
    }
  }
}

export const formatFieldValue = (value: unknown): string => {
  if (value === null || value === undefined) {
    return "-"
  }
  if (Array.isArray(value)) {
    return value.length > 0 ? value.join(", ") : "-"
  }
  if (typeof value === "boolean") {
    return value ? "Yes" : "No"
  }
  return String(value)
}

export const formatDateTime = (dateTime: string): string => {
  return new Date(dateTime).toLocaleString()
}

export const formatDateOnly = (dateTime: string): string => {
  return new Date(dateTime).toLocaleDateString()
}

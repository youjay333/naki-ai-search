const STORAGE_KEY = 'naki-ai-search-history'
const MAX_HISTORY = 12

export function loadHistory() {
  try {
    const value = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]')
    return Array.isArray(value) ? value : []
  } catch {
    return []
  }
}

export function saveHistory(history) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(history.slice(0, MAX_HISTORY)))
}

export function addHistoryItem(history, query) {
  const normalized = query.trim()
  if (!normalized) return history

  return [
    { query: normalized, createdAt: new Date().toISOString() },
    ...history.filter((item) => item.query !== normalized),
  ].slice(0, MAX_HISTORY)
}

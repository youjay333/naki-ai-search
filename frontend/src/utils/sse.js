export async function streamSearch({ query, maxResults = 8, onEvent, signal }) {
  const apiBase = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
  const response = await fetch(`${apiBase}/api/search/stream`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'text/event-stream',
    },
    body: JSON.stringify({ query, max_results: maxResults }),
    signal,
  })

  if (!response.ok || !response.body) {
    const message = await response.text()
    throw new Error(message || `请求失败：${response.status}`)
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { value, done } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })

    const events = buffer.split('\n\n')
    buffer = events.pop() || ''

    for (const rawEvent of events) {
      const parsed = parseSseEvent(rawEvent)
      if (parsed) onEvent(parsed)
    }
  }

  if (buffer.trim()) {
    const parsed = parseSseEvent(buffer)
    if (parsed) onEvent(parsed)
  }
}

function parseSseEvent(rawEvent) {
  const lines = rawEvent.split('\n')
  let event = 'message'
  let data = ''

  for (const line of lines) {
    if (line.startsWith('event:')) event = line.slice(6).trim()
    if (line.startsWith('data:')) data += line.slice(5).trim()
  }

  if (!data) return null

  try {
    return { event, data: JSON.parse(data) }
  } catch {
    return { event, data }
  }
}

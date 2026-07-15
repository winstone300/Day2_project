const dateFormatter = new Intl.DateTimeFormat('ko-KR', {
  year: 'numeric',
  month: '2-digit',
  day: '2-digit',
})

export function formatDate(value) {
  if (!value) return '-'
  return dateFormatter.format(new Date(`${value}Z`))
}

export function formatDateTime(value) {
  if (!value) return '-'
  return new Intl.DateTimeFormat('ko-KR', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(`${value}Z`))
}

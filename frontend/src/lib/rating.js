export const RATING_OPTIONS = [
  { value: 3, label: '観た', icon: 'IconThumbUp' },
  { value: 4, label: '良かった', icon: 'IconHeartHandshake' },
  { value: 5, label: '最高', icon: 'IconSparkles' },
]

export function ratingLabel(value) {
  const found = RATING_OPTIONS.find((o) => o.value === value)
  return found ? found.label : ''
}

export function ratingIcon(value) {
  const found = RATING_OPTIONS.find((o) => o.value === value)
  return found ? found.icon : null
}

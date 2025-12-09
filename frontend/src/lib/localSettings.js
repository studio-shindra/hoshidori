const SETTINGS_KEY = 'hoshidori_local_settings_v1'

function readSettings() {
  try {
    const raw = localStorage.getItem(SETTINGS_KEY)
    if (!raw) return getDefaultSettings()
    const parsed = JSON.parse(raw)
    return { ...getDefaultSettings(), ...parsed }
  } catch (_) {
    return getDefaultSettings()
  }
}

function saveSettings(settings) {
  localStorage.setItem(SETTINGS_KEY, JSON.stringify(settings))
}

function getDefaultSettings() {
  return {
    displayName: '',
    profileInitial: 'G',
    profileImageUrl: null,
  }
}

export function getLocalDisplayName() {
  const settings = readSettings()
  return settings.displayName || ''
}

export function getLocalProfileInitial() {
  const settings = readSettings()
  if (settings.displayName) {
    return settings.displayName.charAt(0).toUpperCase()
  }
  return settings.profileInitial || 'G'
}

export function setLocalDisplayName(name) {
  const settings = readSettings()
  settings.displayName = name
  settings.profileInitial = name ? name.charAt(0).toUpperCase() : 'G'
  saveSettings(settings)
}

export function getLocalProfileImageUrl() {
  const settings = readSettings()
  return settings.profileImageUrl || null
}

export function setLocalProfileImageUrl(url) {
  const settings = readSettings()
  settings.profileImageUrl = url
  saveSettings(settings)
}

export function clearLocalSettings() {
  localStorage.removeItem(SETTINGS_KEY)
}

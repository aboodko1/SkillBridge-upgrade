import { useCallback, useEffect, useMemo, useState } from 'react'

// The established Professional interface and the warmer Casual Pulse share all
// components and data flows. Appearance and interface are browser-local for
// this MVP; legacy sb_theme values are migrated automatically.
export type ResolvedTheme = 'light' | 'dark'
export type AppearancePref = ResolvedTheme | 'system'
export type InterfacePref = 'professional' | 'casual-pulse'

const LEGACY_THEME_KEY = 'sb_theme'
const APPEARANCE_KEY = 'sb_appearance'
const INTERFACE_KEY = 'sb_interface'

function readStorage(key: string): string | null {
  try { return typeof window === 'undefined' ? null : window.localStorage.getItem(key) } catch { return null }
}

function initialAppearance(): AppearancePref {
  const saved = readStorage(APPEARANCE_KEY)
  if (saved === 'light' || saved === 'dark' || saved === 'system') return saved
  const legacy = readStorage(LEGACY_THEME_KEY)
  if (legacy === 'light' || legacy === 'dark') return legacy
  return 'system'
}

function initialInterface(): InterfacePref {
  return readStorage(INTERFACE_KEY) === 'casual-pulse' ? 'casual-pulse' : 'professional'
}

function systemTheme(): ResolvedTheme {
  try { return window.matchMedia?.('(prefers-color-scheme: dark)').matches ? 'dark' : 'light' } catch { return 'light' }
}

export function useThemePref() {
  const [appearance, setAppearanceState] = useState<AppearancePref>(initialAppearance)
  const [interfaceStyle, setInterfaceState] = useState<InterfacePref>(initialInterface)
  const [systemResolved, setSystemResolved] = useState<ResolvedTheme>(systemTheme)

  useEffect(() => {
    const media = window.matchMedia?.('(prefers-color-scheme: dark)')
    if (!media) return
    const update = () => setSystemResolved(media.matches ? 'dark' : 'light')
    update()
    media.addEventListener?.('change', update)
    return () => media.removeEventListener?.('change', update)
  }, [])

  const theme = useMemo<ResolvedTheme>(
    () => appearance === 'system' ? systemResolved : appearance,
    [appearance, systemResolved],
  )

  useEffect(() => {
    const root = document.documentElement
    root.dataset.theme = theme
    root.dataset.appearance = appearance
    root.dataset.interface = interfaceStyle
    try {
      window.localStorage.setItem(APPEARANCE_KEY, appearance)
      window.localStorage.setItem(INTERFACE_KEY, interfaceStyle)
      window.localStorage.setItem(LEGACY_THEME_KEY, theme)
    } catch { /* storage unavailable — in-memory state still works */ }
  }, [appearance, interfaceStyle, theme])

  const setAppearance = useCallback((next: AppearancePref) => {
    setAppearanceState(next === 'dark' || next === 'system' ? next : 'light')
  }, [])
  const setInterfaceStyle = useCallback((next: InterfacePref) => {
    setInterfaceState(next === 'casual-pulse' ? 'casual-pulse' : 'professional')
  }, [])
  const toggleTheme = useCallback(() => {
    setAppearanceState((prev) => prev === 'light' ? 'dark' : prev === 'dark' ? 'system' : 'light')
  }, [])

  return { appearance, setAppearance, interfaceStyle, setInterfaceStyle, theme, toggleTheme, isDark: theme === 'dark' }
}

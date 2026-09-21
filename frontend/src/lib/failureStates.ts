// Phase 7 failure-state helpers — shared, dependency-free.
//
// The UI must never show raw server/provider detail, stack traces, or
// credentials. These helpers turn low-level failures into a safe, localized
// message plus a machine-readable kind so components can render an explicit
// loading / empty / error-with-retry state.

export type FailureKind = 'network' | 'timeout' | 'auth' | 'server' | 'unknown'

export interface FailureState {
  kind: FailureKind
  message: string
}

export const OFFLINE_MESSAGES = {
  en: 'You appear to be offline. Check your connection and try again.',
  ar: 'يبدو أنك غير متصل بالإنترنت. تحقق من اتصالك وحاول مرة أخرى.',
} as const

export const NETWORK_ERROR_MESSAGES = {
  en: 'Network error. Please check your connection and retry.',
  ar: 'خطأ في الشبكة. تحقق من اتصالك وحاول مرة أخرى.',
} as const

export const SERVER_ERROR_MESSAGES = {
  en: 'Something went wrong on the server. Please try again.',
  ar: 'حدث خطأ ما على الخادم. يرجى المحاولة مرة أخرى.',
} as const

function isNetworkLikeError(err: unknown): boolean {
  if (typeof navigator !== 'undefined' && navigator.onLine === false) return true
  const name = err instanceof Error ? err.name : ''
  if (name === 'TypeError' && err instanceof TypeError) {
    // fetch() rejects with a TypeError when the network is unreachable.
    const msg = (err.message || '').toLowerCase()
    return msg.includes('fetch') || msg.includes('network') || msg.includes('failed to fetch')
  }
  const msg = (err instanceof Error ? err.message : String(err)).toLowerCase()
  return msg.includes('network error') || msg.includes('failed to fetch') || msg.includes('offline')
}

/** Classify an error for UI purposes without exposing its raw text. */
export function classifyFailure(err: unknown): FailureKind {
  if (isNetworkLikeError(err)) return 'network'
  if (err instanceof Error && err.message === 'AbortError') return 'timeout'
  if (err instanceof Error && /401|unauthorized|session expired/i.test(err.message)) return 'auth'
  if (err instanceof Error && /^Request failed: [45]\d\d/.test(err.message)) return 'server'
  return 'unknown'
}

/** Safe, localized message for a failure; never returns raw exception text. */
export function failureMessage(err: unknown, lang: 'en' | 'ar', fallback: string): string {
  const kind = classifyFailure(err)
  const table =
    kind === 'network' ? NETWORK_ERROR_MESSAGES
    : kind === 'server' ? SERVER_ERROR_MESSAGES
    : kind === 'auth' ? { en: 'Your session expired. Please sign in again.', ar: 'انتهت جلستك. يرجى تسجيل الدخول مرة أخرى.' }
    : { en: fallback, ar: fallback }
  return table[lang] || table.en
}
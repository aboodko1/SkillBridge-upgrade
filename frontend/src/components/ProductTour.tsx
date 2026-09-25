import React, { createContext, useCallback, useContext, useEffect, useRef, useState, type ReactNode } from 'react'
import { api } from '../lib/api'
import { useApp } from '../AppContext'
import type { StudentTourState, TourMiniPage, TourStateUpdate, TourWelcomeState } from '../lib/types'
import {
  IconTarget, IconLearning, IconTrendingUp, IconVerified, IconAssessment, IconRoadmap, IconXClose,
} from './Icons'

// ---- Global welcome tour: at most 5 short steps (Phase C guide) ------------
// One idea per step, plain language: what SkillBridge does; how today's
// learning works; what the percentages mean; why verification matters; and how
// assessments connect to jobs and progress.

interface TourStep {
  icon: React.ReactNode
  title: string
  body: string
}

const TOUR_STEPS: TourStep[] = [
  {
    icon: <IconTarget size={22} />,
    title: 'What SkillBridge does',
    body: 'SkillBridge turns your target career into a clear skill plan — and helps you prove those skills instead of just claiming them.',
  },
  {
    icon: <IconLearning size={22} />,
    title: 'How today\u2019s learning works',
    body: 'Open Learning for one next step, chosen from your skill gaps. Finish it and the next step appears, so you never have to plan the whole journey at once.',
  },
  {
    icon: <IconTrendingUp size={22} />,
    title: 'What the percentages mean',
    body: 'Percentages show how much of your target role\u2019s requirements you already meet. They rise as you close real gaps — they are not a grade.',
  },
  {
    icon: <IconVerified size={22} />,
    title: 'Why verification matters',
    body: 'Skills you add yourself are claims. A passed final assessment verifies a skill, so employers and matches can trust what you say you can do.',
  },
  {
    icon: <IconAssessment size={22} />,
    title: 'How assessments lead to jobs',
    body: 'Each verified skill lifts your match score and readiness, and those power the jobs you see — so assessments connect straight to real progress.',
  },
]

// ---- Tour state contract exposed through context ---------------------------

interface TourApi {
  ready: boolean
  welcomeOpen: boolean
  step: number
  next: () => void
  back: () => void
  close: () => void
  skip: () => void
  dontShowAgain: () => void
  finish: () => void
  replay: (returnTo?: HTMLElement | null) => void
  returnFocusRef: React.MutableRefObject<HTMLElement | null>
  showMini: (page: TourMiniPage) => boolean
  markMiniDone: (page: TourMiniPage) => void
}

const TourContext = createContext<TourApi | null>(null)

export const useTour = (): TourApi => {
  const ctx = useContext(TourContext)
  if (!ctx) throw new Error('useTour must be used inside <TourProvider>')
  return ctx
}

const CACHE_PREFIX = 'sb_tour_cache:'

export function TourProvider({ children }: { children: ReactNode }) {
  const { session, authBanner } = useApp()
  const isStudent = session?.entity_type === 'student' && !!session?.student?.id
  const studentId = session?.student?.id ?? 0
  const [tour, setTour] = useState<StudentTourState | null>(null)
  const [ready, setReady] = useState(false)
  const [welcomeOpen, setWelcomeOpen] = useState(false)
  const [step, setStep] = useState(0)
  // Deferred first-run auto-open: waits until the login success overlay is gone
  // so the welcome tour never stacks a second modal over the auth animation.
  const [autoOpenPending, setAutoOpenPending] = useState(false)
  const returnFocusRef = useRef<HTMLElement | null>(null)

  // Backend is the source of truth; localStorage is only an optional UI cache
  // (so a failed fetch still leaves a coherent, honest last-known state). Reset
  // all per-account UI on every account switch so no state leaks across logins.
  useEffect(() => {
    setWelcomeOpen(false)
    setStep(0)
    setAutoOpenPending(false)
    returnFocusRef.current = null
    if (!isStudent || !studentId) {
      setTour(null)
      setReady(true)
      return
    }
    setReady(false)
    let alive = true
    let cached: StudentTourState | null = null
    try {
      const raw = localStorage.getItem(CACHE_PREFIX + studentId)
      cached = raw ? (JSON.parse(raw) as StudentTourState) : null
    } catch {
      cached = null
    }
    api.tourState(studentId)
      .then((s) => {
        if (!alive) return
        setTour(s)
        try {
          localStorage.setItem(CACHE_PREFIX + studentId, JSON.stringify(s))
        } catch {
          /* cache is optional */
        }
        // Auto-show only for a genuinely new account, and only after the
        // authoritative backend says so. "Don't show again" always wins.
        if (s.welcome_state === 'not_seen' && !s.dont_show_again) setAutoOpenPending(true)
      })
      .catch(() => {
        // Backend down: only a last-known local cache may stand in, and even
        // then we do not auto-open the tour (that decision is the backend's).
        if (alive && cached) setTour(cached)
      })
      .finally(() => {
        if (alive) setReady(true)
      })
    return () => {
      alive = false
    }
  }, [isStudent, studentId])

  useEffect(() => {
    if (!autoOpenPending || !ready || authBanner) return
    if (!tour || tour.welcome_state !== 'not_seen' || tour.dont_show_again) {
      setAutoOpenPending(false)
      return
    }
    setStep(0)
    setWelcomeOpen(true)
    setAutoOpenPending(false)
  }, [autoOpenPending, ready, authBanner, tour])

  const write = useCallback(
    (patch: TourStateUpdate) => {
      if (!studentId) return
      setTour((prev) => {
        const merged: StudentTourState = {
          tour_version: 'v1',
          welcome_state: 'active',
          dont_show_again: false,
          mini_states: {},
          updated_at: null,
          ...(prev ?? {}),
          ...patch,
          student_id: studentId,
        }
        try {
          localStorage.setItem(CACHE_PREFIX + studentId, JSON.stringify(merged))
        } catch {
          /* cache is optional */
        }
        return merged
      })
      api
        .setTourState(studentId, patch)
        .then(setTour)
        .catch((e) => console.error('[tour] save failed:', e && e.message ? e.message : e))
    },
    [studentId],
  )

  const next = useCallback(() => {
    setStep((s) => Math.min(s + 1, TOUR_STEPS.length - 1))
  }, [])
  const back = useCallback(() => {
    setStep((s) => Math.max(s - 1, 0))
  }, [])
  const finish = useCallback(() => {
    setWelcomeOpen(false)
    write({ welcome_state: 'completed' })
  }, [write])
  const skip = useCallback(() => {
    setWelcomeOpen(false)
    write({ welcome_state: 'skipped' })
  }, [write])
  const dontShowAgain = useCallback(() => {
    setWelcomeOpen(false)
    write({ welcome_state: 'skipped', dont_show_again: true })
  }, [write])
  const replay = useCallback((returnTo?: HTMLElement | null) => {
    if (!studentId) return
    // Remember where to hand focus back to when the replayed tour closes. The
    // caller can pass the stable trigger (e.g. the account-menu button) because
    // the menu item that was clicked unmounts before the tour closes.
    returnFocusRef.current = returnTo ?? (document.activeElement as HTMLElement | null)
    setStep(0)
    setWelcomeOpen(true)
    write({ welcome_state: 'active' })
  }, [studentId, write])

  const showMini = useCallback(
    (page: TourMiniPage) => {
      if (!ready || !tour || welcomeOpen) return false
      if (tour.welcome_state === 'active') return false
      return (tour.mini_states[page] ?? 'not_seen') !== 'completed'
    },
    [ready, tour, welcomeOpen],
  )
  const markMiniDone = useCallback(
    (page: TourMiniPage) => {
      write({ mini_states: { ...(tour?.mini_states ?? {}), [page]: 'completed' } } as TourStateUpdate)
    },
    [tour, write],
  )

  const apiValue: TourApi = {
    ready,
    welcomeOpen,
    step,
    next,
    back,
    close: skip,
    skip,
    dontShowAgain,
    finish,
    replay,
    returnFocusRef,
    showMini,
    markMiniDone,
  }

  return (
    <TourContext.Provider value={apiValue}>
      {children}
      {isStudent && welcomeOpen && <WelcomeTour />}
    </TourContext.Provider>
  )
}

// ---- Welcome tour dialog (modal, Escape closes, focus trap, live announce) -

const FOCUSABLE = 'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'

function WelcomeTour() {
  const { step, next, back, skip, dontShowAgain, finish, returnFocusRef } = useTour()
  const rootRef = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    // Replay supplies a stable trigger; an auto-open falls back to whatever had
    // focus when the dialog mounted. Focus the dialog itself (tabIndex -1) so
    // the title/body are announced before the controls.
    if (!returnFocusRef.current) returnFocusRef.current = document.activeElement as HTMLElement | null
    rootRef.current?.focus()
  }, [returnFocusRef])

  const onKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      e.stopPropagation()
      skip()
      return
    }
    if (e.key !== 'Tab') return
    const root = rootRef.current
    if (!root) return
    const items = Array.from(root.querySelectorAll<HTMLElement>(FOCUSABLE)).filter((el) => el.offsetParent !== null)
    if (!items.length) return
    const first = items[0]
    const last = items[items.length - 1]
    const active = document.activeElement
    // Keep focus inside even when it rests on the dialog container itself.
    if (active === root || !root.contains(active)) {
      e.preventDefault()
      ;(e.shiftKey ? last : first).focus()
    } else if (e.shiftKey && active === first) {
      e.preventDefault()
      last.focus()
    } else if (!e.shiftKey && active === last) {
      e.preventDefault()
      first.focus()
    }
  }

  // Focus return: when the dialog unmounts, hand focus back to the trigger
  // (a no-op when the auto-opened trigger is already gone).
  useEffect(() => {
    return () => {
      const target = returnFocusRef.current
      returnFocusRef.current = null
      if (target && target.isConnected && typeof target.focus === 'function') target.focus()
    }
  }, [returnFocusRef])

  const current = TOUR_STEPS[step]
  const isLast = step === TOUR_STEPS.length - 1

  return (
    <div className="tour-backdrop" role="dialog" aria-modal="true" aria-labelledby="tour-title" aria-describedby="tour-body" onKeyDown={onKeyDown}>
      <div className="tour-card" ref={rootRef} tabIndex={-1}>
        <div className="tour-head">
          <span className="tour-eyebrow">Welcome tour · Step {step + 1} of {TOUR_STEPS.length}</span>
          <button type="button" className="tour-close" aria-label="Skip tour" onClick={skip}><IconXClose size={14} /></button>
        </div>
        <div className="tour-icon" aria-hidden="true">{current.icon}</div>
        <h2 id="tour-title">{current.title}</h2>
        <p className="tour-body" id="tour-body" role="status" aria-live="polite">{current.body}</p>
        <div className="tour-dots" aria-hidden="true">
          {TOUR_STEPS.map((_, i) => (
            <span key={i} className={`tour-dot ${i === step ? 'on' : ''}`} />
          ))}
        </div>
        <div className="tour-actions">
          <div className="tour-actions-left">
            <button type="button" className="btn btn-ghost tour-skip" onClick={skip}>Skip tour</button>
            <button type="button" className="tour-dont" onClick={dontShowAgain}>Don't show again</button>
          </div>
          <div className="tour-actions-right">
            {step > 0 && (
              <button type="button" className="btn btn-ghost" onClick={back}>Back</button>
            )}
            {isLast ? (
              <button type="button" className="btn btn-primary" onClick={finish}>Finish</button>
            ) : (
              <button type="button" className="btn btn-primary" onClick={next}>Next</button>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

// ---- Contextual mini-tour: a dismissible, non-modal first-time guide -------

interface MiniTourBannerProps {
  page: TourMiniPage
  eyebrow: string
  title: string
  points: string[]
  compact?: boolean
}

export function MiniTourBanner({ page, eyebrow, title, points, compact = false }: MiniTourBannerProps) {
  const { showMini, markMiniDone } = useTour()
  if (!showMini(page)) return null
  if (compact) return (
    <aside className="mini-tour mini-tour-compact" role="note" aria-label={`First-time guide: ${title}`}>
      <details>
        <summary><IconRoadmap size={15} /> <strong>{title}</strong><span>3 quick tips · expand</span></summary>
        <p className="mini-tour-eyebrow">{eyebrow}</p>
        <ul className="mini-tour-points">{points.map((p) => <li key={p}>{p}</li>)}</ul>
      </details>
      <button type="button" className="mini-tour-close" aria-label="Dismiss this guide" onClick={() => markMiniDone(page)}><IconXClose size={13} /></button>
    </aside>
  )
  return (
    <aside className="mini-tour" role="note" aria-label={`First-time guide: ${title}`}>
      <div className="mini-tour-head">
        <strong><IconRoadmap size={14} /> {title}</strong>
        <button type="button" className="mini-tour-close" aria-label="Dismiss this guide" onClick={() => markMiniDone(page)}><IconXClose size={13} /></button>
      </div>
      <p className="mini-tour-eyebrow">{eyebrow}</p>
      <ul className="mini-tour-points">
        {points.map((p) => <li key={p}>{p}</li>)}
      </ul>
    </aside>
  )
}

export const TOUR_WELCOME_STATES: TourWelcomeState[] = ['not_seen', 'active', 'completed', 'skipped']

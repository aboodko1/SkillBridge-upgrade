import React from 'react'
import type { RecentJob, RecentJobsResponse, SkillGap } from '../lib/types'
import { IconCheck, IconVerified } from './Icons'

export function isSafeExternalUrl(url?: string | null): boolean {
  if (!url) return false
  try {
    const parsed = new URL(url)
    return (parsed.protocol === 'http:' || parsed.protocol === 'https:') && !!parsed.hostname
  } catch {
    return false
  }
}

export function formatJobTime(iso?: string | null): string {
  if (!iso) return ''
  const d = new Date(iso)
  return Number.isNaN(d.getTime()) ? '' : d.toLocaleString()
}

export function listingStatusLabel(status?: string): string {
  if (status === 'live') return 'Live listing'
  if (status === 'expired') return 'Expired'
  if (status === 'link-unavailable') return 'Link unavailable'
  return ''
}

export function feedStatusLabel(status?: RecentJobsResponse['status'], source?: RecentJobsResponse['source']): string {
  if (status === 'cached') return 'Cached feed'
  if (status === 'stale_fallback') return 'Cached feed · refreshing'
  if (status === 'unavailable') return 'Feed unavailable'
  if (source === 'empty') return 'No live matches'
  return 'Live feed'
}

export function locationScopeNote(job: Pick<RecentJob, 'location_tier'>): string {
  if (job.location_tier === 'global_remote') return 'Remote · open worldwide'
  if (job.location_tier === 'market') return 'Relocation search'
  if (job.location_tier === 'different') return 'Outside your country'
  return ''
}

export function JobProvenance({ job }: { job: RecentJob }) {
  const provider = job.provider || job.source || 'Unknown source'
  const fetched = formatJobTime(job.fetched_at)
  const status = listingStatusLabel(job.listing_status)
  const scope = locationScopeNote(job)
  const linkNote = job.link_state === 'unverified' ? 'link not verified' : ''
  return (
    <span className="job-provenance small muted">
      {provider}
      {fetched && <> · Fetched {fetched}</>}
      {status && <> · {status}</>}
      {scope && <> · {scope}</>}
      {linkNote && <> · {linkNote}</>}
    </span>
  )
}

export function SkillTag({ name, level, verified }: { name: string; level: string; verified?: boolean }) {
  if (verified) {
    return (
      <span className="skill-tag verified" title="Verified by passing an assessment">
        <IconVerified size={14} />
        {name}
        {level && <span className="lv">{level}</span>}
      </span>
    )
  }
  return (
    <span className="skill-tag" title="Self-reported (from CV, not yet verified)">
      <span className="u-dot" />
      {name}
      {level && <span className="lv">{level}</span>}
    </span>
  )
}

export interface ScoreExplainProps {
  summary?: string
  metric?: string
  metricKey?: string
  numerator: string
  denominator: string
  source: string
  rounding: string
  evidence: string
  included: string
  excluded: string
  missing?: string
  recalculated?: string | null
  reported?: string
  extra?: React.ReactNode
}

export function ScoreExplain(props: ScoreExplainProps) {
  const rows: [string, string][] = [
    ['Numerator', props.numerator],
    ['Denominator', props.denominator],
    ['Source', props.source],
    ['Rounding', props.rounding],
  ]
  return (
    <details className="mxb score-explain" style={{ marginTop: 10 }}>
      <summary>{props.summary || 'How is this calculated?'}</summary>
      <div className="mxb-body">
        {props.metric && (
          <p className="mxb-meta">{props.metric}{props.metricKey ? ` · ${props.metricKey}` : ''}</p>
        )}
        <div className="mxb-lines">
          {rows.map(([label, value]) => (
            <div className="mxb-pt" key={label}>
              <span className="mxb-pt-label">{label}</span>
              <span className="mxb-pt-num" style={{ fontFamily: 'inherit', textAlign: 'right', maxWidth: '68%' }}>{value}</span>
            </div>
          ))}
        </div>
        <p className="mxb-note"><strong style={{ color: 'var(--sb-midnight-ink)' }}>Evidence included:</strong> {props.evidence}</p>
        <p className="mxb-note">Included: {props.included}</p>
        <p className="mxb-note">Excluded or missing: {props.excluded}{props.missing ? ` (${props.missing})` : ''}</p>
        {props.reported && <p className="mxb-note">Evidence mix: {props.reported}</p>}
        <p className="mxb-meta">Last recalculated: {props.recalculated || 'Not available'}</p>
        {props.extra}
      </div>
    </details>
  )
}

export function ScoreRing({ value, label = 'Requirement coverage', explainer, explain }: {
  value: number
  label?: string
  explainer?: string
  explain?: React.ReactNode
}) {
  const r = 62
  const c = 2 * Math.PI * r
  const pct = Math.max(0, Math.min(100, value))
  const offset = c - (pct / 100) * c
  return (
    <div className="score-ring-view" title={explainer || undefined}>
      <div className="score-ring">
        <svg width="150" height="150" aria-hidden="true">
          <circle cx="75" cy="75" r={r} fill="none" stroke="var(--slate-100)" strokeWidth="12" />
          <circle
            cx="75" cy="75" r={r} fill="none"
            stroke="var(--sb-indigo)" strokeWidth="12" strokeLinecap="round"
            strokeDasharray={c} strokeDashoffset={offset}
          />
        </svg>
        <div className="ring-label">
          <strong>{Math.round(value)}%</strong>
          <small>{label}</small>
        </div>
      </div>
      {explain}
    </div>
  )
}

export function GapPill({ status }: { status: SkillGap['status'] }) {
  const map: Record<SkillGap['status'], string> = {
    strong: 'Strong',
    gap: 'Gap',
    missing: 'Missing',
  }
  const labels: Record<SkillGap['status'], string> = {
    strong: 'You meet this requirement',
    gap: 'Present but below required level',
    missing: 'Not present yet',
  }
  return <span className={`pill ${status}`} title={labels[status]}>{map[status]}</span>
}

export function LevelBadge({ verified }: { verified: boolean }) {
  return verified ? (
    <span className="badge verified-badge"><IconCheck size={13} /> Verified</span>
  ) : (
    <span className="badge unverified-badge">Self-reported</span>
  )
}

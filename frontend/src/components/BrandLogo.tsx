import React from 'react'

/** Vector interpretation of the approved S/bridge brand reference. */
export default function BrandLogo({ compact = false }: { compact?: boolean }) {
  return <span className={`sb-brand${compact ? ' sb-brand-compact' : ''}`} aria-label="SkillBridge">
    <img src="/skillbridge-mark.svg" alt="" width="48" height="48" />
    {!compact && <span className="sb-brand-type"><strong>Skill<span>Bridge</span></strong><small>LEARN. CONNECT. GROW.</small></span>}
  </span>
}

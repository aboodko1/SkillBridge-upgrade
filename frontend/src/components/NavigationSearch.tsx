import React, { useState } from 'react'
import { IconSearch, IconArrowRight } from './Icons'

const destinations = [
  { title: 'Dashboard', hint: 'Your overview and next steps', key: 'dashboard' },
  { title: 'Skills & Roles', hint: 'Explore careers and your skill profile', key: 'skills' },
  { title: 'Learning', hint: 'Courses, lessons and learning paths', key: 'learning' },
  { title: 'Practice', hint: 'Hands-on scenarios and challenges', key: 'scenarios' },
  { title: 'Assessments', hint: 'Test and verify your skills', key: 'assessments' },
]
export default function NavigationSearch({ navigate, student }: { navigate: (key: string) => void; student: boolean }) {
  const [query, setQuery] = useState('')
  const [open, setOpen] = useState(false)
  const rows = destinations.filter((d) => (student || ['dashboard', 'skills'].includes(d.key)) && `${d.title} ${d.hint}`.toLowerCase().includes(query.toLowerCase()))
  const go = (key: string) => { navigate(key); setOpen(false); setQuery('') }
  return <div className="pulse-search-wrap" onBlur={(e) => { if (!e.currentTarget.contains(e.relatedTarget)) setOpen(false) }}>
    <label className="pulse-global-search"><IconSearch size={18} /><input aria-label="Find a page" placeholder="Where do you want to go?" value={query} onChange={(e) => { setQuery(e.target.value); setOpen(true) }} onFocus={() => setOpen(true)} onKeyDown={(e) => { if (e.key === 'Escape') setOpen(false); if (e.key === 'Enter' && rows[0]) go(rows[0].key) }} /><kbd>↵</kbd></label>
    {open && <div className="pulse-search-results" aria-label="Page results">{rows.length ? rows.map((row) => <button key={row.key} onClick={() => go(row.key)}><span><strong>{row.title}</strong><small>{row.hint}</small></span><IconArrowRight size={16} /></button>) : <p>No pages found. Try “learning” or “roles”.</p>}</div>}
  </div>
}

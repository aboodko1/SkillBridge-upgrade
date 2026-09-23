import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import Markdown from 'react-markdown'
import { useApp } from '../AppContext'
import { api } from '../lib/api'
import { humanizeTopicLabel } from '../lib/topicLabels'
import type {
  ActivitySummary, Analysis, CareerRoadmap, DiagnosticQuestion, DiagnosticResult,
  GeneratedDiagnostic, FinalAssessmentStatus, LearningAgentActionType, LearningAgentDecision,
  LearningItem, LearningResource, Lesson, LessonPractice, PersonalizedPath, PersonalizedPathItem,
  PersonalizedPathResponse, PracticeAttempt, ScenarioLibrary, ScenarioCard, SkillGap, Student,
  TopicResult, RoadmapValidation, RoadmapViolation,
} from '../lib/types'
import {
  CareerProgress,
  ContinueLearningCard,
  CurrentLessonCard,
  EmptyLearningState,
  LearningProgress,
  LearningTabs,
  MilestoneChip,
  ResourceCard,
  RoadmapTimeline,
  SearchBar,
  SectionTitle,
  SkillCard,
  SkillDetailHeader,
  stageMilestoneState,
  topicMilestoneState,
  topicProgressFor,
  WhyThis,
  type LearningTab,
} from '../components/learning'
import { MiniTourBanner } from '../components/ProductTour'
import { IconAlert, IconArrowRight, IconAssessment, IconBack, IconBolt, IconBook, IconChat, IconCheck, IconChevron, IconClock, IconExternal, IconLock, IconRoadmap, IconShield, IconTarget } from '../components/Icons'

function SafeMarkdown({ children }: { children: React.ReactNode }) {
  return <Markdown>{String(children ?? '')}</Markdown>
}

function resourceTypeLabel(resource: LearningResource) {
  const label = resource.type_label || resource.type || 'Resource'
  if (label === 'doc') return 'Documentation'
  if (label === 'course') return 'Tutorial'
  return label.replace(/_/g, ' ').split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')
}

function resourceStatus(resource: LearningResource) {
  const label = resource.status
    || (resource.available === true
      ? 'Checked'
      : resource.available === false ? 'Unavailable' : 'Status unknown')
  const key = label.toLowerCase().includes('unavailable')
    ? 'unavailable'
    : label.toLowerCase().includes('checked') ? 'checked' : 'unknown'
  return { label, key }
}

function formatMinutes(mins: number) {
  if (mins < 60) return `${mins}m`
  const h = Math.floor(mins / 60)
  const m = mins % 60
  return m ? `${h}h ${m}m` : `${h}h`
}

function sumPathMinutes(path: PersonalizedPath | null) {
  if (!path) return 0
  return path.items.reduce((sum, it) => sum + (it.estimated_minutes || 0), 0)
}

function categoryToneFor(category: string) {
  const c = (category || '').toLowerCase()
  if (c.includes('security') || c.includes('cyber')) return 'red'
  if (c.includes('devops') || c.includes('infrastruct') || c.includes('cloud') || c.includes('ml')) return 'sky'
  if (c.includes('soft') || c.includes('communi') || c.includes('data')) return 'blue'
  return 'slate'
}

// ------------------------------------------------------------------ agentic learning
//
// Phase 3: the learning agent recommends; it never grades, completes a topic or
// verifies a skill. The language control is persistent (localStorage) so a
// student who chose Egyptian Arabic keeps it across visits and pages.

const LEARNING_LANGUAGE_KEY = 'sb_learning_language'
type LearningLanguage = 'en' | 'ar'

function useLearningLanguage(): [LearningLanguage, (next: LearningLanguage) => void] {
  const [language, setLanguage] = useState<LearningLanguage>(() => {
    try {
      return localStorage.getItem(LEARNING_LANGUAGE_KEY) === 'ar' ? 'ar' : 'en'
    } catch {
      return 'en'
    }
  })
  const update = useCallback((next: LearningLanguage) => {
    setLanguage(next)
    try { localStorage.setItem(LEARNING_LANGUAGE_KEY, next) } catch { /* storage may be unavailable */ }
  }, [])
  return [language, update]
}

type LessonTab = 'learn' | 'example' | 'practice' | 'discuss' | 'mini_check'

const AGENT_ACTION_TABS: Record<LearningAgentActionType, LessonTab> = {
  EXPLAIN: 'learn',
  PRACTICE: 'practice',
  GIVE_HINT: 'practice',
  REVIEW_PREREQUISITE: 'learn',
  MINI_CHECK: 'mini_check',
  ADVANCE: 'learn',
  REQUEST_REASSESSMENT: 'learn',
}

interface AgentCopy {
  eyebrow: string
  title: string
  why: string
  objective: string
  evidence: string
  open: string
  staticLabel: string
  noExec: string
  staticSound: string
  staticFix: string
  retry: string
  roadmap: string
  reassess: string
  submitNote: string
  unverified: string
  loading: string
  english: string
  egyptianArabic: string
}

const AGENT_COPY: Record<LearningLanguage, AgentCopy> = {
  en: {
    eyebrow: 'Learning agent',
    title: 'Your next best step',
    why: 'Why this step?',
    objective: 'Objective',
    evidence: 'Evidence',
    open: 'Open this step',
    staticLabel: 'Static code check / فحص ثابت للكود',
    noExec: 'Python code is not executed here. This is a structural review only — it never changes your practice score and never verifies a skill.',
    staticSound: 'The stored structural check looks sound, so a Mini Check can confirm understanding. It still does not run the code.',
    staticFix: 'The stored structural check still finds missing structure. Revise the practice answer and try again.',
    retry: 'Retry recommendation',
    roadmap: 'View full roadmap',
    reassess: 'Regenerate your path from the latest diagnostic, or retake the diagnostic to continue.',
    submitNote: 'Practice answers and Mini Checks are submitted through the real lesson APIs; the agent only recommends.',
    unverified: 'This recommendation never verifies a skill — only a passed Final Assessment can do that.',
    loading: 'Choosing your next step…',
    english: 'English',
    egyptianArabic: 'العربية المصرية',
  },
  ar: {
    eyebrow: 'وكيل التعلّم',
    title: 'أفضل خطوة تالية',
    why: 'لماذا هذه الخطوة؟',
    objective: 'الهدف',
    evidence: 'الأدلة',
    open: 'افتح هذه الخطوة',
    staticLabel: 'Static code check / فحص ثابت للكود',
    noExec: 'لا يتم تنفيذ كود Python هنا. هذا فحص هيكلي فقط — لا يغيّر درجة التدريب ولا يوثّق المهارة.',
    staticSound: 'الفحص الهيكلي المخزّن سليم، لذا يمكن إجراء الاختبار المصغّر للتأكد من الفهم. ولا يزال لا ينفّذ الكود.',
    staticFix: 'لا يزال الفحص الهيكلي يجد بنية ناقصة. عدّل إجابة التدريب ثم حاول مرة أخرى.',
    retry: 'أعد المحاولة',
    roadmap: 'عرض خريطة الطريق كاملة',
    reassess: 'أعد إنشاء مسارك من أحدث تشخيص، أو أعد التشخيص للمتابعة.',
    submitNote: 'تُرسَل إجابات التدريب والاختبار المصغّر عبر واجهات الدرس الحقيقية؛ والوكيل يوصي فقط.',
    unverified: 'هذه التوصية لا توثّق أي مهارة — فقط اجتياز التقييم النهائي يفعل ذلك.',
    loading: 'جارٍ اختيار خطوتك التالية…',
    english: 'English',
    egyptianArabic: 'العربية المصرية',
  },
}

function LearningAgentPanel({ studentId, skillId, onOpenTopic }: {
  studentId: number
  skillId: number
  onOpenTopic: (competency: string, tab?: LessonTab) => void
}) {
  const [language, setLanguage] = useLearningLanguage()
  const copy = AGENT_COPY[language]
  const [agentDecision, setAgentDecision] = useState<LearningAgentDecision | null>(null)
  const [latestAttempt, setLatestAttempt] = useState<PracticeAttempt | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [showEvidence, setShowEvidence] = useState(false)
  const [retryKey, setRetryKey] = useState(0)

  useEffect(() => {
    let alive = true
    setLoading(true)
    setError('')
    api.learningAgentNext(studentId, skillId)
      .then((decision) => { if (alive) setAgentDecision(decision) })
      .catch((e: unknown) => {
        if (!alive) return
        setAgentDecision(null)
        setError((e as Error)?.message || 'Could not load the learning recommendation.')
      })
      .finally(() => { if (alive) setLoading(false) })
    return () => { alive = false }
  }, [studentId, skillId, retryKey])

  const topic = agentDecision?.topic_id ?? null
  useEffect(() => {
    let alive = true
    if (!topic) { setLatestAttempt(null); return () => { alive = false } }
    api.lessonPracticeAttempts(studentId, skillId, topic)
      .then((res) => { if (alive) setLatestAttempt(res.latest) })
      .catch(() => { if (alive) setLatestAttempt(null) })
    return () => { alive = false }
  }, [studentId, skillId, topic, retryKey])

  const staticCheck = latestAttempt?.practice_task?.static_check ?? null
  const structurallySound = latestAttempt?.practice_task?.static_check?.status === 'looks_structurally_sound'

  return (
    <section className="agent-panel hcard-ai" aria-label="Learning agent recommendation">
      <div className="agent-head">
        <div className="panel-title-row">
          <span className="panel-title-icon"><IconBolt size={15} /></span>
          <div>
            <span className="eyebrow">{copy.eyebrow}</span>
            <h3 className="panel-title">{copy.title}</h3>
          </div>
        </div>
        <div className="agent-lang" role="group" aria-label="Learning language">
          <button type="button" className={`agent-lang-btn ${language === 'en' ? 'active' : ''}`}
                  aria-pressed={language === 'en'} onClick={() => setLanguage('en')}>{copy.english}</button>
          <button type="button" className={`agent-lang-btn ${language === 'ar' ? 'active' : ''}`}
                  aria-pressed={language === 'ar'} onClick={() => setLanguage('ar')}>{copy.egyptianArabic}</button>
        </div>
      </div>

      {loading && <p className="muted small agent-status" role="status">{copy.loading}</p>}

      {error && (
        <div className="agent-error" role="alert">
          <span>{error}</span>
          <button type="button" className="btn btn-sm" onClick={() => setRetryKey((k) => k + 1)}>{copy.retry}</button>
        </div>
      )}

      {agentDecision && (
        <>
          <div className="agent-decision">
            <span className="chip-btn agent-action-chip" data-action={agentDecision.action_type}>{agentDecision.action_type}</span>
            <p className="agent-next-step">{agentDecision.next_step}</p>
            {agentDecision.objective && (
              <p className="muted small"><strong>{copy.objective}:</strong> {agentDecision.objective}</p>
            )}
          </div>

          <button type="button" className="btn-link agent-why" aria-expanded={showEvidence}
                  onClick={() => setShowEvidence((s) => !s)}>
            {copy.why}
          </button>
          {showEvidence && (
            <ul className="agent-evidence" aria-label={copy.evidence}>
              {agentDecision.evidence.map((item, i) => (
                <li key={i}><strong>{item.kind}</strong>: {item.detail}</li>
              ))}
            </ul>
          )}

          {staticCheck && (
            <div className={`agent-static-check ${structurallySound ? 'sound' : 'fix'}`} role="note">
              <span className="agent-static-label">{copy.staticLabel}</span>
              <p className="agent-static-disclosure">{copy.noExec}</p>
              <p className="agent-static-status">{structurallySound ? copy.staticSound : copy.staticFix}</p>
              {Array.isArray(staticCheck.checks) && staticCheck.checks.length > 0 && (
                <ul className="agent-static-list">
                  {staticCheck.checks.map((check, i) => <li key={i}>{check}</li>)}
                </ul>
              )}
            </div>
          )}

          <div className="agent-actions">
            {agentDecision.action_type === 'REQUEST_REASSESSMENT' ? (
              <p className="muted small agent-reassess">{copy.reassess}</p>
            ) : topic ? (
              <button type="button" className="btn btn-primary"
                      onClick={() => onOpenTopic(topic, AGENT_ACTION_TABS[agentDecision.action_type])}>
                {copy.open} <IconArrowRight size={14} />
              </button>
            ) : null}
            <button type="button" className="btn btn-ghost"
                    onClick={() => document.getElementById('career-roadmap')?.scrollIntoView({ behavior: 'smooth', block: 'start' })}>
              {copy.roadmap}
            </button>
          </div>

          <p className="muted small agent-submit-note">{copy.submitNote}</p>
        </>
      )}

      <p className="agent-unverified"><IconShield size={13} /> {copy.unverified}</p>
    </section>
  )
}


export default function LearningPage({ onNavigate, initialFocus, onFocusConsumed, backTo }: {
  onNavigate?: (section: string, focus?: { skillId: number; roleTitle: string }) => void
  initialFocus?: { skillId: number; roleTitle: string; competency?: string } | null
  onFocusConsumed?: () => void
  backTo?: { key: string; label: string } | null
}) {
  const { me, applyCopilot } = useApp()
  const studentId = me?.student?.id ?? 0
  const [analysis, setAnalysis] = useState<Analysis | null>(null)
  const [items, setItems] = useState<LearningItem[]>([])
  const [selectedSkillId, setSelectedSkillId] = useState<number | null>(null)
  const [pathsBySkill, setPathsBySkill] = useState<Record<number, PersonalizedPath | null>>({})
  const [learningStart, setLearningStart] = useState<{ skillId: number; signal: number } | null>(null)
  const [lessonFocus, setLessonFocus] = useState<{ skillId: number; competency: string; signal: number; tab?: 'learn' | 'example' | 'practice' | 'discuss' | 'mini_check' } | null>(null)
  const [query, setQuery] = useState('')
  const [topicFilter, setTopicFilter] = useState('all')
  const [activeTab, setActiveTab] = useState<LearningTab>('for-you')
  const [learningView, setLearningView] = useState<'today' | 'paths' | 'lesson'>('today')
  const [showTop, setShowTop] = useState(false)
  const [loadError, setLoadError] = useState('')
  const [pathsLoaded, setPathsLoaded] = useState(false)
  const [activity, setActivity] = useState<ActivitySummary | null>(null)
  const [scenarioLib, setScenarioLib] = useState<ScenarioLibrary | null>(null)
  // The stored student profile answers "My Skills": self-reported claims and
  // officially verified skills come straight from the profile API, never from
  // role skill gaps (which belong to the "for-you" recommendations).
  const [studentProfile, setStudentProfile] = useState<Student | null>(null)
  // Deep link from Skills & Roles ("Learn this skill"): focus a specific skill
  // while keeping the role that prompted it in view as dismissible context.
  const [focusInfo, setFocusInfo] = useState<{ skillId: number; roleTitle: string; competency?: string } | null>(null)

  useEffect(() => {
    if (!studentId) return
    api.scenarios(studentId)
      .then(setScenarioLib)
      .catch(() => { /* practice scenarios are optional context on the learning page */ })
  }, [studentId])

  useEffect(() => {
    if (!initialFocus) return
    setFocusInfo(initialFocus)
    setSelectedSkillId(initialFocus.skillId)
    setLearningView('lesson')
    if (initialFocus.competency) {
      setLessonFocus((prev) => ({
        skillId: initialFocus.skillId,
        competency: initialFocus.competency as string,
        signal: (prev?.signal ?? 0) + 1,
      }))
    }
    onFocusConsumed?.()
    const tryScroll = () => {
      document.getElementById('skill-detail')?.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }
    const t1 = window.setTimeout(tryScroll, 300)
    const t2 = window.setTimeout(tryScroll, 900)
    return () => { window.clearTimeout(t1); window.clearTimeout(t2) }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [initialFocus])

  useEffect(() => {
    const onScroll = () => setShowTop(window.scrollY > 600)
    window.addEventListener('scroll', onScroll, { passive: true })
    window.addEventListener('load', onScroll)
    return () => { window.removeEventListener('scroll', onScroll); window.removeEventListener('load', onScroll) }
  }, [])

  const load = async () => {
    setLoadError('')
    const [aResult, lResult] = await Promise.allSettled([api.analysis(studentId), api.learning(studentId)])
    if (aResult.status === 'fulfilled') setAnalysis(aResult.value)
    else {
      setAnalysis(null)
      setLoadError(aResult.reason?.message || 'Learning analysis is not available yet.')
    }
    if (lResult.status === 'fulfilled') setItems(lResult.value)
    else {
      setItems([])
      setLoadError((prev) => prev || lResult.reason?.message || 'Learning content is not available yet.')
    }
  }

  useEffect(() => { if (studentId) void load() }, [studentId])

  useEffect(() => {
    if (!studentId) return
    let alive = true
    api.student(studentId)
      .then((profile) => { if (alive) setStudentProfile(profile) })
      .catch(() => { if (alive) setStudentProfile(null) })
    return () => { alive = false }
  }, [studentId])

  useEffect(() => {
    if (!studentId) return
    let alive = true
    api.studentActivity(studentId)
      .then((a) => { if (alive) setActivity(a) })
      .catch(() => { if (alive) setActivity(null) })
    return () => { alive = false }
  }, [studentId])

  const itemBySkill = useMemo(() => new Map(items.map((item) => [item.skill_id, item])), [items])
  const allGaps = analysis?.skill_gaps || []
  const openGaps = allGaps.filter((gap) => gap.status !== 'strong')
  const openGapSkillKey = openGaps.map((gap) => gap.skill_id).join(',')
  const knownPaths = Object.values(pathsBySkill).filter((path): path is PersonalizedPath => !!path)
  const doneTopics = knownPaths.reduce((sum, path) => sum + topicProgressFor(path).done, 0)
  const totalTopics = knownPaths.reduce((sum, path) => sum + topicProgressFor(path).total, 0)

  useEffect(() => {
    let alive = true
    const ids = openGaps.map((gap) => gap.skill_id)
    if (!studentId || !ids.length) {
      setPathsBySkill({})
      setPathsLoaded(true)
      return () => { alive = false }
    }
    setPathsLoaded(false)
    Promise.all(ids.map(async (skillId) => {
      try {
        const res = await api.personalizedPath(studentId, skillId)
        return [skillId, 'diagnostic_required' in res ? null : res] as const
      } catch {
        return [skillId, null] as const
      }
    })).then((entries) => {
      if (!alive) return
      setPathsBySkill(Object.fromEntries(entries))
      setPathsLoaded(true)
    })
    return () => { alive = false }
  }, [studentId, openGapSkillKey])

  // "My Skills" answers from the stored student profile: every self-reported
  // claim (profileSource 'claim') plus every officially verified skill
  // ('verified'). A skill that is both merges to the verified entry. These are
  // profile skills, NOT role skill gaps — the gaps stay in "for-you".
  const profileSkills = useMemo<SkillGap[]>(() => {
    const byId = new Map<number, SkillGap>()
    for (const s of studentProfile?.self_reported_skills ?? []) {
      byId.set(s.skill_id, {
        skill_id: s.skill_id,
        skill_name: s.name,
        category: s.category,
        required_level: s.level,
        student_level: s.level,
        status: 'gap',
        verified: false,
        profileSource: 'claim',
      })
    }
    for (const v of studentProfile?.verified_skills ?? []) {
      byId.set(v.skill_id, {
        skill_id: v.skill_id,
        skill_name: v.name,
        category: v.category,
        required_level: v.level,
        student_level: v.level,
        status: 'strong',
        verified: true,
        profileSource: 'verified',
      })
    }
    return [...byId.values()]
  }, [studentProfile])

  const continueSkills = openGaps.filter((gap) => {
    const path = pathsBySkill[gap.skill_id]
    const progress = topicProgressFor(path)
    return !!path && progress.hasTopics && !progress.complete
  })
  const completedLearningSkills = allGaps.filter((gap) => {
    const progress = topicProgressFor(pathsBySkill[gap.skill_id])
    return gap.status === 'strong' || (!!pathsBySkill[gap.skill_id] && progress.complete)
  })
  const completedLearningCount = openGaps.filter((gap) => {
    const path = pathsBySkill[gap.skill_id]
    const progress = topicProgressFor(path)
    return !!path && progress.hasTopics && progress.complete
  }).length
  const inProgressCount = openGaps.filter((gap) => {
    const path = pathsBySkill[gap.skill_id]
    const progress = topicProgressFor(path)
    return !!path && progress.hasTopics && progress.done > 0 && !progress.complete
  }).length
  const completedCount = allGaps.filter((gap) => gap.status === 'strong').length + completedLearningCount
  const notStartedCount = openGaps.length - inProgressCount - completedLearningCount

  const tabCounts: Record<LearningTab, number> = {
    'for-you': openGaps.length,
    'my-skills': studentProfile ? profileSkills.length : allGaps.length,
    continue: continueSkills.length,
    completed: completedCount,
  }

  const skillsForTab = useMemo(() => {
    if (activeTab === 'my-skills') return profileSkills
    if (activeTab === 'continue') return continueSkills
    if (activeTab === 'completed') return completedLearningSkills
    return openGaps
  }, [activeTab, profileSkills, continueSkills, completedLearningSkills, openGaps])

  const tabCopy: Record<LearningTab, string> = {
    'for-you': 'Recommended for you',
    'my-skills': 'Skill map',
    continue: 'In-progress paths',
    completed: 'Completed skills',
  }
  const currentTabCopy = tabCopy[activeTab]

  const filteredSkills = skillsForTab.filter((gap) => {
    const q = query.trim().toLowerCase()
    if (!q) return true
    return (
      gap.skill_name.toLowerCase().includes(q) ||
      gap.category.toLowerCase().includes(q) ||
      gap.required_level.toLowerCase().includes(q) ||
      (gap.student_level || '').toLowerCase().includes(q)
    )
  })

  useEffect(() => {
    // A deep link from Skills & Roles wins over the automatic first-gap select.
    if (focusInfo) return
    const preferred = skillsForTab[0] || openGaps[0] || allGaps[0]
    if (!preferred) return
    if (!selectedSkillId || !skillsForTab.some((gap) => gap.skill_id === selectedSkillId)) {
      setSelectedSkillId(preferred.skill_id)
    }
  }, [analysis?.role_id, skillsForTab, selectedSkillId, focusInfo])

  const selectedGap = skillsForTab.find((gap) => gap.skill_id === selectedSkillId)
    || filteredSkills[0]
    || openGaps[0]
    || allGaps[0]

  // Phase 5: for the currently focused skill, surface the role-specific
  // practice scenarios written for it (matched by skill name on the cards).
  const scenariosForSkill = useMemo(() => {
    if (!scenarioLib || !selectedGap) return [] as ScenarioCard[]
    const want = (selectedGap.skill_name || '').toLowerCase().trim()
    if (!want) return []
    return (scenarioLib.scenarios as ScenarioCard[]).filter((card) =>
      (card.skills || []).some((s) => s.toLowerCase() === want))
  }, [scenarioLib, selectedGap])

  const focusedName = focusInfo
    ? (allGaps.find((g) => g.skill_id === focusInfo.skillId)?.skill_name ?? 'this skill')
    : ''

  const setCopilotCompetency = useCallback((competency: string | null) => {
    applyCopilot({ competency })
  }, [applyCopilot])

  useEffect(() => {
    applyCopilot({ page: 'learning', skillId: selectedGap?.skill_id ?? null, competency: null })
  }, [selectedGap?.skill_id])

  const startLearning = (skillId: number) => {
    setSelectedSkillId(skillId)
    setLearningView('lesson')
    setLearningStart((prev) => ({ skillId, signal: (prev?.signal ?? 0) + 1 }))
    requestAnimationFrame(() => {
      document.getElementById('skill-detail')?.scrollIntoView({ behavior: 'smooth', block: 'start' })
    })
  }

  const toggleStep = async (item: LearningItem, n: number) => {
    const cur = new Set(item.progress ?? [])
    if (cur.has(n)) cur.delete(n)
    else cur.add(n)
    const steps = [...cur].sort((a, b) => a - b)
    try {
      const updated = await api.learningProgress(studentId, item.skill_id, steps)
      setItems((prev) => prev.map((i) => (i.skill_id === updated.skill_id ? updated : i)))
    } catch {
      /* keep local state unchanged if the save fails */
    }
  }

  const verifiedRequiredSet = new Set(
    (me?.student?.verified_skills ?? [])
      .filter((v) => openGaps.some((g) => g.skill_id === v.skill_id))
      .map((v) => v.skill_id)
  )
  const verifiedRequired = {
    verified: verifiedRequiredSet.size,
    total: openGaps.length,
    pct: openGaps.length ? Math.round((verifiedRequiredSet.size / openGaps.length) * 100) : 0,
  }

  // Data truth (Phase 2): read the backend's canonical target requirement
  // coverage. Never recompute a "match" from strong/total here — that ignored
  // partial credit and could disagree with the Dashboard ring for the same role.
  const matchPct = analysis?.metrics?.target_requirement_coverage != null
    ? Math.round(analysis.metrics.target_requirement_coverage)
    : (analysis?.match_score != null ? Math.round(analysis.match_score) : null)
  const requiredSkillCount = allGaps.length
  const plannedMinutes = knownPaths.reduce((sum, path) => sum + sumPathMinutes(path), 0)

  // Stat-card progress bars need honest denominators: the study-time card is a
  // planned-minutes share of a 7-hour focused-learning goal, the streak card a
  // 30-day-goal share (some of these are illustrative targets, clearly noted in
  // the sub-labels), and skill improvement is the real verified-share %.
  const STUDY_GOAL_MINUTES = 7 * 60
  const STREAK_GOAL_DAYS = 30
  const studyGoalPct = plannedMinutes > 0 ? Math.min(100, Math.round((plannedMinutes / STUDY_GOAL_MINUTES) * 100)) : 0
  const streakGoalPct = activity ? Math.min(100, Math.round((activity.streak_days / STREAK_GOAL_DAYS) * 100)) : 0

  const stepperRows = skillsForTab.map((gap) => {
    const path = pathsBySkill[gap.skill_id]
    const progress = topicProgressFor(path)
    const doneSet = new Set(path?.progress ?? [])
    const items = path?.items ?? []
    const nextCompetency = items.find((it) => !doneSet.has(it.id))?.competency ?? items[0]?.competency ?? null
    return {
      gap,
      path,
      progress,
      nextCompetency,
      minutes: sumPathMinutes(path),
      status: !path ? 'diagnostic' as const : progress.complete ? 'done' as const : progress.done > 0 ? 'in-progress' as const : 'not-started' as const,
    }
  })
  const currentSkillId = stepperRows.find((r) => r.status !== 'done')?.gap.skill_id ?? null

  const topicCategories = [...new Set(skillsForTab.map((g) => g.category).filter(Boolean))]
  const visibleStepperRows = topicFilter === 'all' ? stepperRows : stepperRows.filter((r) => r.gap.category === topicFilter)
  const shownStepperRows = visibleStepperRows.slice(0, 8)
  const moreModulesCount = visibleStepperRows.length - shownStepperRows.length

  const openLessonTopic = (skillId: number, competency: string, tab?: 'learn' | 'example' | 'practice' | 'discuss' | 'mini_check') => {
    if (!competency) return
    setSelectedSkillId(skillId)
    setLearningView('lesson')
    setLessonFocus((prev) => ({ skillId, competency, signal: (prev?.signal ?? 0) + 1, tab }))
    requestAnimationFrame(() => {
      document.getElementById('skill-detail')?.scrollIntoView({ behavior: 'smooth', block: 'start' })
    })
  }

  const openChat = () => window.dispatchEvent(new CustomEvent('copilot:focus'))

  const quickDiagnose = () => {
    const first = openGaps[0]
    if (first) startLearning(first.skill_id)
  }
  const quickPractice = () => {
    onNavigate?.('scenarios', { skillId: selectedGap?.skill_id ?? 0, roleTitle: analysis?.role_title || me?.student?.target_role?.title || '' })
  }
  const goAssessments = () => onNavigate?.('assessments')
  const viewAllModules = () => {
    setActiveTab('for-you')
    setLearningView('paths')
    requestAnimationFrame(() => document.querySelector('.learning-page .focus-flow')?.scrollIntoView({ behavior: 'smooth', block: 'start' }))
  }

  if (!studentId) return <div className="empty">Log in as a student to view your learning path.</div>

  const targetTitle = analysis?.role_title || me?.student?.target_role?.title || ''
  const targetMeta =
    analysis?.company ||
    me?.student?.target_role?.company_name ||
    (targetTitle ? 'Current target from your profile' : 'Choose one from Skills & Roles')

  const journeyGap = continueSkills[0] ?? null
  const journeyPath = journeyGap ? (pathsBySkill[journeyGap.skill_id] ?? null) : null
  const journeyDoneIds = new Set(journeyPath?.progress ?? [])
  const journeyTopic = journeyPath?.items.find((it) => !journeyDoneIds.has(it.id)) ?? journeyPath?.items[0] ?? null
  const journeyPlanlessGap = openGaps.find((g) => !pathsBySkill[g.skill_id]) ?? null
  const journeyOpenPaths = openGaps.filter((g) => !!pathsBySkill[g.skill_id])
  const todayAction = !pathsLoaded ? null
    : journeyGap && journeyTopic
      ? { label: `Continue ${journeyGap.skill_name}`, run: () => openLessonTopic(journeyGap.skill_id, journeyTopic.competency) }
      : journeyPlanlessGap
        ? { label: `Start ${journeyPlanlessGap.skill_name} diagnostic`, run: () => startLearning(journeyPlanlessGap.skill_id) }
        : journeyOpenPaths.length > 0
          ? { label: 'Start your first topic', run: () => startLearning(openGaps[0].skill_id) }
          : analysis && !targetTitle
            ? { label: 'Choose a target role', run: () => onNavigate?.('skills') }
            : analysis && targetTitle
              ? { label: 'Explore my paths', run: viewAllModules }
              : null

  return (
    <div className="learning-page">
      <MiniTourBanner
        page="learning"
        compact
        eyebrow="Learning · First time here?"
        title="Your plan at a glance"
        points={[
          'A diagnostic reveals your skill gaps, then builds a step-by-step plan.',
          'Milestones show exactly where you are — to-do, in progress, needs review, done.',
          'Follow the highlighted topic next and tick off the current step.',
        ]}
      />
      {backTo && (
        <nav className="crumbs" aria-label="Breadcrumbs">
          <button type="button" className="crumb-back" onClick={() => onNavigate?.(backTo.key)}>
            <IconBack size={14} /> Back to {backTo.label}
          </button>
        </nav>
      )}
      {focusInfo && (
        <div className="lrn-focus" role="status">
          <IconTarget size={15} />
          <span>
            <b>{focusedName}</b> · learning toward your <b>{focusInfo.roleTitle || 'target'}</b> role.
            {focusInfo.competency ? ` We'll open ${humanizeTopicLabel(focusInfo.competency)} if it appears in your generated path.` : ' It is open in the panel below.'}
          </span>
          <button type="button" className="lrn-focus-x" aria-label="Dismiss context" onClick={() => setFocusInfo(null)}>✕</button>
        </div>
      )}
      <section className="learning-hero">
      <div className="hero-art" aria-hidden="true">
        <svg viewBox="0 0 220 220" width="220" height="220" fill="none">
          {/* soft ambient glow behind the target */}
          <circle cx="112" cy="102" r="98" fill="rgba(255,255,255,0.035)" />
          {/* bullseye rings, outer to inner */}
          <circle cx="112" cy="102" r="86" stroke="#FFFFFF" strokeWidth="15" />
          <circle cx="112" cy="102" r="68" stroke="#FF6B2C" strokeWidth="15" />
          <circle cx="112" cy="102" r="50" stroke="#FFFFFF" strokeWidth="15" />
          <circle cx="112" cy="102" r="33" fill="#FF6B2C" />
          <circle cx="112" cy="102" r="11" fill="#FFFFFF" />
          {/* arrow shaft flying in from lower-left */}
          <line x1="18" y1="188" x2="104" y2="110" stroke="#FF6B2C" strokeWidth="5" strokeLinecap="round" />
          {/* fletching at the tail */}
          <path d="M18 188 L6 178 M18 188 L28 197 M24 182 L14 176" stroke="#FF6B2C" strokeWidth="3.5" strokeLinecap="round" />
          {/* arrowhead at the tip, landing on the bullseye */}
          <polygon points="112,101 96,107 101,113" fill="#FF6B2C" />
          {/* floating accent square, upper-left */}
          <rect x="14" y="18" width="30" height="30" rx="8" fill="#FF6B2C" transform="rotate(-14 29 33)" />
          {/* floating shield-check badge, lower-right */}
          <circle cx="186" cy="176" r="22" fill="#0D1B2A" stroke="rgba(255,255,255,0.25)" strokeWidth="2" />
          <path d="M186 165 l9 3.5 v8 c0 6-4 10-9 12-5-2-9-6-9-12v-8z" fill="#FFFFFF" opacity="0.92" />
          <path d="M181.5 176.5l3 3 6-6.5" stroke="#0D1B2A" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </div>
        <div className="learning-hero-copy">
          <p className="learning-hero-eyebrow">Learning</p>
          <h1>Build the skills your target role expects.</h1>
          <p>Follow one personalized path from skill gap to practice and verified progress. Your AI Tutor is available whenever you need help.</p>
          {learningView === 'today' && todayAction && <button type="button" className="btn btn-primary focus-hero-action" onClick={todayAction.run}>{todayAction.label} <IconArrowRight size={14} /></button>}
        </div>
        <div className="hero-target-card hcard-opportunity">
          <div className="hero-target-card-head"><IconRoadmap size={15} /> Target role</div>
          <div className="hero-target-role">{targetTitle || 'No target selected'}</div>
          {matchPct !== null && (
            <>
              <p className="hero-progress-label" title="Level-aware coverage of your target role's required skills (backend-computed).">
                Current requirement coverage <strong>{matchPct}%</strong>{' '}
                <WhyThis>Coverage compares your verified and self-reported evidence against the skills this target role lists (level-aware). It measures how far your profile reaches into the role's requirements — it is not a hiring guarantee.</WhyThis>
              </p>
              <div className="progress-track"><div className="progress-fill" style={{ width: `${matchPct}%` }} /></div>
            </>
          )}
          <div className="htc-foot">
            <span className="htc-chip">{requiredSkillCount} required</span>
            <span className="htc-chip"><IconCheck size={12} /> {verifiedRequired.verified} verified</span>
          </div>
        </div>
        {learningView === 'paths' && <SearchBar
          value={query}
          onChange={setQuery}
          placeholder="Search a skill, topic, or ask AI Tutor..."
        />}
        {learningView === 'paths' && <LearningTabs active={activeTab} counts={tabCounts} onChange={setActiveTab} />}
      </section>

      <nav className="focus-flow" aria-label="Learning sections">
        <button type="button" className={learningView === 'today' ? 'active' : ''} aria-current={learningView === 'today' ? 'step' : undefined} onClick={() => setLearningView('today')}><span>01</span> Today</button>
        <button type="button" className={learningView === 'paths' ? 'active' : ''} aria-current={learningView === 'paths' ? 'step' : undefined} onClick={() => setLearningView('paths')}><span>02</span> My paths</button>
        <button type="button" className={learningView === 'lesson' ? 'active' : ''} aria-current={learningView === 'lesson' ? 'step' : undefined} onClick={() => setLearningView('lesson')} disabled={!selectedGap}><span>03</span> Lesson</button>
      </nav>

      {learningView === 'today' && <>
      <section className="journey-band" aria-label="Continue your plan">
        {pathsLoaded && journeyGap && journeyTopic ? (
          <div className="journey-band-inner">
            <p className="journey-eyebrow">Continue your plan</p>
            <CurrentLessonCard
              skillName={journeyGap.skill_name}
              topicTitle={humanizeTopicLabel(journeyTopic.title)}
              estimatedMinutes={journeyTopic.estimated_minutes}
              purpose={`Added because your diagnostic score was ${Math.round(journeyTopic.diagnostic_score)}%.`}
              onContinue={() => openLessonTopic(journeyGap.skill_id, journeyTopic.competency)}
            />
            {continueSkills.length > 1 && (
              <p className="muted small journey-more">
                {continueSkills.length - 1} other plan{continueSkills.length - 1 === 1 ? '' : 's'} still in progress — see In-progress paths below.
              </p>
            )}
          </div>
        ) : pathsLoaded && journeyPlanlessGap ? (
          <div className="journey-band-inner journey-empty">
            <p className="journey-eyebrow">Continue your plan</p>
            <div className="journey-card">
              <div className="journey-card-icon"><IconAssessment size={18} /></div>
              <div className="journey-card-copy">
                <span className="cc-kicker">{journeyPlanlessGap.skill_name}</span>
                <h3>No plan yet</h3>
                <p className="muted small">
                  Take a diagnostic for {journeyPlanlessGap.skill_name} to unlock a personalized path built from your weakest topics.
                </p>
              </div>
              <div className="journey-card-actions">
                <button className="btn btn-primary" onClick={() => startLearning(journeyPlanlessGap.skill_id)}>
                  <IconAssessment size={14} /> Start a diagnostic
                </button>
              </div>
            </div>
          </div>
        ) : journeyOpenPaths.length > 0 ? (
          <div className="journey-band-inner journey-empty">
            <p className="journey-eyebrow">Continue your plan</p>
            <div className="journey-card">
              <div className="journey-card-icon"><IconBolt size={18} /></div>
              <div className="journey-card-copy">
                <h3>Your learning plans are ready</h3>
                <p className="muted small">
                  Every target skill has a path. Start the first topic of any plan to begin making progress.
                </p>
              </div>
              <div className="journey-card-actions">
                <button className="btn btn-primary" onClick={() => startLearning(openGaps[0].skill_id)}>
                  <IconBook size={14} /> Start your first topic
                </button>
              </div>
            </div>
          </div>
        ) : analysis && !targetTitle ? (
          <div className="journey-band-inner journey-empty">
            <p className="journey-eyebrow">Continue your plan</p>
            <div className="journey-card">
              <div className="journey-card-icon"><IconTarget size={18} /></div>
              <div className="journey-card-copy">
                <h3>Pick a target role</h3>
                <p className="muted small">
                  Choose a role on Skills &amp; Roles and your skill gaps and personalized learning paths appear here.
                </p>
              </div>
              <div className="journey-card-actions">
                <button className="btn btn-primary" onClick={() => onNavigate?.('skills')}>
                  <IconTarget size={14} /> Choose a target role
                </button>
              </div>
            </div>
          </div>
        ) : analysis && targetTitle ? (
          <div className="journey-band-inner journey-empty">
            <p className="journey-eyebrow">Continue your plan</p>
            <div className="journey-card">
              <div className="journey-card-icon"><IconCheck size={18} /></div>
              <div className="journey-card-copy">
                <h3>You're up to date</h3>
                <p className="muted small">
                  No open gaps right now. Keep exploring modules or verify a skill with an assessment.
                </p>
              </div>
              <div className="journey-card-actions">
                <button className="btn btn-primary" onClick={viewAllModules}>
                  <IconBook size={14} /> View all learning modules
                </button>
              </div>
            </div>
          </div>
        ) : null}
      </section>

      <section className="lp-stat-grid" aria-label="Learning stats">
        <article className="lp-stat-card hcard-progress">
          <div className="lp-stat-top">
            <span className="lp-stat-icon blue"><IconAssessment size={18} /></span>
            <div>
              <p className="lp-stat-label">Learning progress</p>
              <p className="lp-stat-value">{totalTopics > 0 ? <>{doneTopics} <small>/ {totalTopics}</small></> : '\u2014'}</p>
            </div>
          </div>
          {totalTopics > 0 ? (
            <>
              <div className="progress-track on-light"><div className="progress-fill" style={{ width: `${Math.round((doneTopics / totalTopics) * 100)}%` }} /></div>
              <p className="lp-stat-sub">topics completed across your personalized path</p>
            </>
          ) : (
            <p className="lp-stat-sub">No path yet — take a topic diagnostic to unlock your plan.</p>
          )}
        </article>

        <article className="lp-stat-card hcard-progress">
          <div className="lp-stat-top">
            <span className="lp-stat-icon teal"><IconClock size={18} /></span>
            <div>
              <p className="lp-stat-label">Total study time</p>
              <p className="lp-stat-value">{plannedMinutes > 0 ? formatMinutes(plannedMinutes) : '\u2014'}</p>
            </div>
          </div>
          <div className="progress-track on-light"><div className="progress-fill" style={{ width: `${studyGoalPct}%`, background: 'var(--sb-teal-dark)' }} /></div>
          <p className="lp-stat-sub">planned across your learning path · vs a 7h goal</p>
        </article>

        <article className="lp-stat-card hcard-progress">
          <div className="lp-stat-top">
            <span className="lp-stat-icon brand"><IconBolt size={18} /></span>
            <div>
              <p className="lp-stat-label">Current streak</p>
              <p className="lp-stat-value">{activity ? <>{activity.streak_days} <small>days</small></> : '\u2014'}</p>
            </div>
          </div>
          <div className="progress-track on-light"><div className="progress-fill" style={{ width: `${streakGoalPct}%`, background: 'var(--sb-indigo)' }} /></div>
          <p className="lp-stat-sub">{activity && activity.active_days > 0 ? `${activity.active_days} active days · 30-day goal` : 'from your activity · 30-day goal'}</p>
        </article>

        <article className="lp-stat-card hcard-progress">
          <div className="lp-stat-top">
            <span className="lp-stat-icon green"><IconCheck size={18} /></span>
            <div>
              <p className="lp-stat-label">Skill improvement</p>
              <p className="lp-stat-value">{verifiedRequired.total > 0 ? `${verifiedRequired.pct}%` : '\u2014'}</p>
            </div>
          </div>
          <div className="progress-track on-light"><div className="progress-fill" style={{ width: `${verifiedRequired.total > 0 ? verifiedRequired.pct : 0}%`, background: 'var(--sb-green)' }} /></div>
          <p className="lp-stat-sub">{verifiedRequired.total > 0 ? `${verifiedRequired.verified} of ${verifiedRequired.total} target skills verified` : 'verified via assessments'}</p>
        </article>
      </section>

      <button type="button" className="focus-secondary-link" onClick={viewAllModules}>Explore all my paths <IconArrowRight size={14} /></button>
      </>}

      {learningView === 'paths' && <>
      <div className="learning-layout">
        <main className="panel path-panel hcard-info">
          <div className="panel-head">
            <div>
              <div className="panel-title-row">
                <span className="panel-title-icon"><IconTarget size={15} /></span>
                <h3 className="panel-title">{currentTabCopy}</h3>
              </div>
              <p className="panel-subtitle">{activeTab === 'my-skills'
                ? 'Every skill on your profile — self-reported claims and officially verified ones. Pick one to study it toward your target role.'
                : 'One row per skill. Start a diagnostic on a gap to build its personalized path, then complete every Mini Check to finish it.'}</p>
            </div>
            <select className="lp-filter" value={topicFilter} onChange={(e) => setTopicFilter(e.target.value)} aria-label="Filter path by topic category">
              <option value="all">All topics</option>
              {topicCategories.map((c) => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>

          {visibleStepperRows.length === 0 ? (
            <EmptyLearningState title="No skill gaps yet" body="Select a target role on Skills & Roles to see your gaps and their personalized paths." />
          ) : (
            <>
              <ol className="path-list">
                {shownStepperRows.map((row) => {
                  const n = stepperRows.indexOf(row) + 1
                  return (
                    <li
                      key={row.gap.skill_id}
                      className={`path-item ${row.status === 'done' ? 'is-done' : ''}`}
                      data-current={row.gap.skill_id === currentSkillId}
                    >
                      <span className="path-marker">{row.status === 'done' ? <IconCheck size={13} /> : n}</span>
                      <div className="path-item-body">
                        <span className={`path-icon ${categoryToneFor(row.gap.category)}`}>
                          <IconAssessment size={17} />
                        </span>
                        <div className="path-text">
                          <h3>{row.gap.skill_name}</h3>
                          <p>{row.gap.category} · {row.gap.required_level}{row.gap.verified ? ' · Verified' : ''}</p>
                        </div>
                        <div className="path-progress">
                          <div className="progress-track on-light">
                            <div className="progress-fill" style={{ width: `${row.progress.total ? Math.round((row.progress.done / row.progress.total) * 100) : 0}%` }} />
                          </div>
                          <div className="path-progress-pct">{row.progress.done}/{row.progress.total}</div>
                        </div>
                        {row.status === 'done' ? (
                          <span className="status-pill passed">Completed</span>
                        ) : row.status === 'diagnostic' ? (
                          <button className="btn btn-primary" onClick={() => startLearning(row.gap.skill_id)}>
                            Start <IconArrowRight size={14} />
                          </button>
                        ) : (
                          <button className="btn" onClick={() => openLessonTopic(row.gap.skill_id, row.nextCompetency ?? '')}>
                            {row.status === 'in-progress' ? 'Continue' : 'Start'} <IconArrowRight size={14} />
                          </button>
                        )}
                      </div>
                    </li>
                  )
                })}
              </ol>
              {moreModulesCount > 0 && (
                <button className="btn btn-ghost view-all-modules" onClick={viewAllModules} aria-label={`View all ${moreModulesCount} more modules`}>
                  +{moreModulesCount} more module{moreModulesCount === 1 ? '' : 's'} <IconArrowRight size={14} />
                </button>
              )}
            </>
          )}

          {scenariosForSkill.length > 0 && (
            <section className="panel lrn-scn-panel" aria-label="Practice scenarios for this skill">
              <div className="panel-head" style={{ marginBottom: 12 }}>
                <div className="panel-title-row">
                  <span className="panel-title-icon"><IconBolt size={15} /></span>
                  <h3 className="panel-title">Practice scenarios for {scenariosForSkill[0]!.skills[0] || selectedGap?.skill_name}</h3>
                </div>
                <p className="panel-subtitle">Role-specific practice written for your target career. Your learning path stays untouched while you practice.</p>
              </div>
              <div className="lrn-scn-list">
                {scenariosForSkill.slice(0, 3).map((scn) => (
                  <div className="lrn-scn-row" key={scn.id}>
                    <span className="lrn-scn-name">{scn.category_icon} {scn.title}</span>
                    <span className="lrn-scn-meta">
                      <span className="chip">{scn.difficulty_label}</span>
                      <span className="lrn-scn-status">{scn.status === 'completed' ? 'Completed' : scn.status === 'in_progress' ? 'In progress' : 'Not started'}</span>
                    </span>
                    <button className="btn btn-sm" onClick={() => onNavigate?.('scenarios', { skillId: selectedGap?.skill_id ?? 0, roleTitle: targetTitle })}>
                      Practice <IconArrowRight size={13} />
                    </button>
                  </div>
                ))}
              </div>
            </section>
          )}
        </main>

        <details className="focus-library focus-more-learning">
          <summary>More ways to learn <span>AI Tutor · practice · assessments</span></summary>
        <aside className="right-col">
          <div className="panel lp-tutor-panel hcard-ai">
            <div className="lp-tutor-avatar"><IconChat size={22} /></div>
            <h3 className="panel-title">AI Tutor</h3>
            <p>Chat with our assistant about any topic on your path — it knows your background, current skills, and target role.</p>
            <button className="btn btn-primary btn-block" onClick={openChat}>
              Chat with AI <IconArrowRight size={15} />
            </button>
          </div>

          <div className="panel quick-panel">
            <div className="panel-head" style={{ marginBottom: 12 }}>
              <div className="panel-title-row">
                <span className="panel-title-icon"><IconTarget size={15} /></span>
                <h3 className="panel-title">Quick access</h3>
              </div>
            </div>
            <nav className="quick-list">
              <button className="quick-item" onClick={quickDiagnose}>
                <span className="quick-icon"><IconAssessment size={15} /></span> Take a diagnostic
                <IconArrowRight className="chev" size={14} />
              </button>
              <button className="quick-item" onClick={quickPractice}>
                <span className="quick-icon"><IconBolt size={15} /></span> Practice scenarios
                <IconArrowRight className="chev" size={14} />
              </button>
              <button className="quick-item" onClick={viewAllModules}>
                <span className="quick-icon"><IconBook size={15} /></span> View all learning modules
                <IconArrowRight className="chev" size={14} />
              </button>
              <button className="quick-item" onClick={openChat}>
                <span className="quick-icon"><IconChat size={15} /></span> Join a discussion
                <IconArrowRight className="chev" size={14} />
              </button>
              <button className="quick-item" onClick={goAssessments}>
                <span className="quick-icon"><IconCheck size={15} /></span> Go to Assessment
                <IconArrowRight className="chev" size={14} />
              </button>
            </nav>
            <button className="quick-item tip" onClick={goAssessments}>
              <span className="quick-icon"><IconShield size={15} /></span>
              <span>
                <strong>Tip: Finish assessments to verify your skills</strong>
                <span>Verified skills unlock higher matches — take the next one from the Assessments page.</span>
              </span>
              <IconArrowRight className="chev" size={14} />
            </button>
          </div>
        </aside>
        </details>
      </div>

      {continueSkills.length > 0 && (
        <section className="learning-section">
          <SectionTitle eyebrow="Continue Learning" title="Pick up where you left off" meta={`${continueSkills.length} active path${continueSkills.length === 1 ? '' : 's'}`} />
          <div className="continue-grid">
            {continueSkills.slice(0, 3).map((gap) => (
              <ContinueLearningCard
                key={gap.skill_id}
                gap={gap}
                path={pathsBySkill[gap.skill_id] as PersonalizedPath}
                onSelect={() => startLearning(gap.skill_id)}
              />
            ))}
          </div>
        </section>
      )}

      <details className="focus-library" id="learning-home">
        <summary>Browse the full skill library <span>{filteredSkills.length} skills</span></summary>
      <div className="learning-home-grid">
        <section className="learning-section">
          <SectionTitle
            eyebrow="Recommended Skills"
            title={currentTabCopy}
            meta={`${filteredSkills.length} shown`}
          />
          {loadError && <div className="error learning-error">{loadError}</div>}
          <div className="learning-skill-grid">
            {filteredSkills.map((gap) => (
              <SkillCard
                key={gap.skill_id}
                gap={gap}
                profileSource={gap.profileSource}
                path={pathsBySkill[gap.skill_id]}
                selected={selectedGap?.skill_id === gap.skill_id}
                onSelect={() => { setSelectedSkillId(gap.skill_id); setLearningView('lesson') }}
                onStart={() => startLearning(gap.skill_id)}
              />
            ))}
          </div>
          {filteredSkills.length === 0 && (
            <EmptyLearningState
              title={query ? 'No skills match that search' : 'No learning items here yet'}
              body={query ? 'Try another skill, category, or topic.' : 'Select a target role on Skills & Roles to unlock dynamic learning recommendations.'}
            />
          )}
        </section>

        <aside className="learning-side">
          <LearningProgress done={doneTopics} total={totalTopics} />
          <CareerProgress
            completed={completedCount}
            inProgress={inProgressCount}
            notStarted={Math.max(0, notStartedCount)}
          />
        </aside>
      </div>
      </details>
      <details className="focus-library">
        <summary>Resources and career roadmap <span>Optional reference</span></summary>
        <ResourceCenter items={items} />
        <CareerRoadmapCard studentId={studentId} roleTitle={analysis?.role_title} />
      </details>
      </>}

      {learningView === 'lesson' && selectedGap && (
        <div className="focus-lesson-shell">
          <button type="button" className="focus-back" onClick={() => setLearningView('paths')}><IconBack size={14} /> Back to my paths</button>
        <SkillDetailPanel
          studentId={studentId}
          gap={selectedGap}
          item={itemBySkill.get(selectedGap.skill_id)}
          path={pathsBySkill[selectedGap.skill_id]}
          roleTitle={analysis?.role_title}
          startSignal={learningStart?.skillId === selectedGap.skill_id ? learningStart.signal : 0}
          focusSignal={lessonFocus?.skillId === selectedGap.skill_id ? lessonFocus : null}
          onPathChange={(path) => setPathsBySkill((prev) => ({ ...prev, [selectedGap.skill_id]: path }))}
          onToggleStep={(n) => {
            const item = itemBySkill.get(selectedGap.skill_id)
            if (item) void toggleStep(item, n)
          }}
          onCompetencyChange={setCopilotCompetency}
          onOpenTopic={(competency, tab) => openLessonTopic(selectedGap.skill_id, competency, tab)}
        />
        </div>
      )}

      {showTop && (
        <button className="btn back-top" onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })} aria-label="Back to top">
          Back to top
        </button>
      )}
    </div>
  )
}

function SkillDetailPanel({ studentId, gap, item, path, roleTitle, startSignal, focusSignal, onPathChange, onToggleStep, onCompetencyChange, onOpenTopic }: {
  studentId: number
  gap: SkillGap
  item?: LearningItem
  path?: PersonalizedPath | null
  roleTitle?: string
  startSignal?: number
  focusSignal?: { skillId?: number; competency: string; signal: number; tab?: 'learn' | 'example' | 'practice' | 'discuss' | 'mini_check' } | null
  onPathChange?: (path: PersonalizedPath | null) => void
  onToggleStep: (step: number) => void
  onCompetencyChange: (competency: string | null) => void
  onOpenTopic: (competency: string, tab?: LessonTab) => void
}) {
  const [diagRefreshKey, setDiagRefreshKey] = useState(0)
  return (
    <section className="skill-detail-panel" id="skill-detail">
      <SkillDetailHeader
        gap={gap}
        item={item}
        roleTitle={roleTitle}
        topicProgress={topicProgressFor(path, gap.status === 'strong' ? 100 : 0)}
      />

      <LearningAgentPanel studentId={studentId} skillId={gap.skill_id} onOpenTopic={onOpenTopic} />

      <DiagnosticPanel studentId={studentId} skillId={gap.skill_id} skillName={gap.skill_name} startSignal={startSignal} onComplete={() => setDiagRefreshKey(k => k + 1)} />

      <PersonalizedPathPanel
        studentId={studentId}
        skillId={gap.skill_id}
        skillName={gap.skill_name}
        refreshKey={diagRefreshKey}
        startSignal={startSignal}
        focusSignal={focusSignal}
        onPathChange={onPathChange}
        onCompetencyChange={onCompetencyChange}
      />

      {item && (
        <details className="focus-library focus-saved-pack">
          <summary>Saved resource pack and roadmap <span>Optional reference</span></summary>
          <div className="focus-saved-pack-content">
          <section className="learning-section compact legacy-learning-pack">
            <SectionTitle eyebrow="Saved Resources" title="Generated resource pack" meta="Compatibility view" />
            <p className="muted small section-copy">
              These saved materials remain available, but your active Learning progress comes from the diagnostic path and Mini Checks above.
            </p>
          </section>
          <div className="skill-detail-grid">
            <article className="learning-copy-card">
              <span>Learn</span>
              <h3>Explanation</h3>
              <div className="md-body"><SafeMarkdown>{item.explanation}</SafeMarkdown></div>
            </article>
            <article className="learning-copy-card">
              <span>Practice</span>
              <h3>Practice exercise</h3>
              <div className="md-body"><SafeMarkdown>{item.practice_exercise}</SafeMarkdown></div>
            </article>
            <article className="learning-copy-card">
              <span>Build</span>
              <h3>Mini-project</h3>
              <div className="md-body"><SafeMarkdown>{item.mini_project}</SafeMarkdown></div>
            </article>
          </div>

          {item.modules && item.modules.length > 0 && (
            <section className="learning-section compact">
              <SectionTitle eyebrow="Coverage" title="This path covers" meta={item.blueprint_version ? `Blueprint: ${item.blueprint_version}` : undefined} />
              <div className="plan-coverage">
                {item.modules.map((module, i) => (
                  <div className={`plan-coverage-item ${module.beyond_blueprint ? 'bonus' : ''}`} key={`${module.competency}-${i}`}>
                    <span className="plan-comp-check">{module.beyond_blueprint ? '+' : <IconCheck size={13} />}</span>
                    <span className="plan-comp-name">{module.competency}</span>
                    {module.beyond_blueprint && <span className="pc-bonus-tag">bonus</span>}
                    <span className="plan-comp-time">{module.estimated_minutes} min</span>
                  </div>
                ))}
              </div>
            </section>
          )}

          {item.resources && item.resources.length > 0 && (
            <section className="learning-section compact">
              <SectionTitle eyebrow="Learning Resources" title="Recommended resources" meta={`${item.resources.length} source${item.resources.length === 1 ? '' : 's'}`} />
              <div className="resource-card-row">
                {item.resources.map((resource, i) => (
                  <ResourceCard key={`${resource.url}-${i}`} resource={resource} fallbackRank={i + 1} skillName={item.skill_name} />
                ))}
              </div>
            </section>
          )}

          {item.roadmap?.steps?.length ? (
            <section className="learning-section compact">
              <SectionTitle eyebrow="Saved Roadmap" title={`${item.roadmap.steps.length}-step resource plan`} meta={item.roadmap.summary} />
              <RoadmapTimeline item={item} onToggleStep={onToggleStep} />
            </section>
          ) : (
            <EmptyLearningState
              title="Detailed path data is not available"
              body="The path timeline component is ready; it will render backend roadmap steps as soon as they exist for this skill."
            />
          )}
          </div>
        </details>
      )}
    </section>
  )
}

function DiagnosticPanel({ studentId, skillId, skillName, startSignal = 0, onComplete }: {
  studentId: number
  skillId: number
  skillName: string
  startSignal?: number
  onComplete?: () => void
}) {
  const [phase, setPhase] = useState<'browse' | 'take' | 'result' | 'loading'>('loading')
  const [diag, setDiag] = useState<DiagnosticResult | null>(null)
  const [current, setCurrent] = useState<GeneratedDiagnostic | null>(null)
  const [form, setForm] = useState<Record<string, string>>({})
  const [questionIndex, setQuestionIndex] = useState(0)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const handledStartSignal = useRef(0)

  const loadLatest = async () => {
    setError('')
    try {
      const latest = await api.latestDiagnostic(studentId, skillId)
      setDiag(latest)
      setPhase(latest.completed_at ? 'result' : 'take')
      setQuestionIndex(0)
    } catch (e: unknown) {
      setDiag(null)
      setPhase('browse')
      setError((e as Error)?.message || 'Could not load the diagnostic')
    }
  }

  const retryLoad = () => {
    setError('')
    setPhase('loading')
    void loadLatest()
  }

  useEffect(() => { if (studentId && skillId) void loadLatest() }, [studentId, skillId])

  const start = async () => {
    setBusy(true)
    setError('')
    try {
      const gen = await api.generateDiagnostic(studentId, skillId)
      setCurrent(gen)
      setForm({})
      setQuestionIndex(0)
      setPhase('take')
    } catch (e: unknown) {
      setError((e as Error)?.message || 'Could not start the diagnostic')
    } finally {
      setBusy(false)
    }
  }

  useEffect(() => {
    if (!startSignal || phase !== 'browse' || busy || handledStartSignal.current === startSignal) return
    handledStartSignal.current = startSignal
    void start()
  }, [startSignal, phase, busy])

  const submit = async () => {
    // A diagnostic can be in the "take" phase either because it was just
    // generated this session (current is set) or because an earlier,
    // generated-but-unsubmitted diagnostic was reloaded on open (only diag is
    // set). Resolve whichever is active so Submit always has a diagnostic to
    // score instead of silently no-oping.
    const active = current ?? (diag && phase === 'take' ? diag : null)
    if (!active) return
    setBusy(true)
    setError('')
    const questions = active.questions ?? []
    const answers = questions.map((q) => form[q.id] ?? '')
    try {
      const result = await api.submitDiagnostic(studentId, skillId, {
        diagnostic_id: (active as GeneratedDiagnostic).diagnostic_id ?? (active as DiagnosticResult).id,
        answers,
      })
      setDiag(result)
      setCurrent(null)
      setPhase('result')
      onComplete?.()
    } catch (e: unknown) {
      setError((e as Error)?.message || 'Could not submit the diagnostic')
    } finally {
      setBusy(false)
    }
  }

  if (phase === 'loading') {
    return (
      <section className="diagnostic-panel diag-loading" role="status" aria-label="Loading diagnostic">
        <div className="diagnostic-head">
          <div>
            <span className="diag-skel-line skeleton" style={{ width: 90, height: 12 }} />
            <span className="diag-skel-line skeleton" style={{ width: 220, height: 20, marginTop: 8 }} />
          </div>
          <span className="skeleton" style={{ width: 130, height: 34, borderRadius: 10 }} />
        </div>
        {Array.from({ length: 3 }).map((_, i) => (
          <div className="diag-skel-task skeleton" key={i} />
        ))}
      </section>
    )
  }

  const questions = current?.questions ?? diag?.questions ?? []
  const currentQuestion = questions[questionIndex]

  return (
    <section className="diagnostic-panel">
      <div className="diagnostic-head">
        <div>
          <span className="eyebrow">Diagnostic</span>
          <h3>{skillName} — topic check</h3>
        </div>
        {phase === 'browse' && (
          <button className="btn btn-primary" onClick={start} disabled={busy}>Start Diagnostic</button>
        )}
        {phase === 'result' && (
          <button className="btn" onClick={start} disabled={busy}>Retake Diagnostic</button>
        )}
      </div>

      {error && (
        <div className="error learning-error phase7-retry-notice" role="alert" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 8, flexWrap: 'wrap' }}>
          <span>{error}</span>
          <button type="button" className="btn btn-sm btn-secondary" onClick={retryLoad}>Retry</button>
        </div>
      )}

      {phase === 'browse' && (
        <p className="section-copy">
          Start a short diagnostic to see which topics inside {skillName} you have down and which
          need practice. It never verifies the skill — it only shapes your learning.
        </p>
      )}

      {phase === 'take' && (
        <>
          {currentQuestion ? <>
            <div className="focus-diagnostic-progress" role="status">Question {questionIndex + 1} of {questions.length}<div className="progress-track on-light"><div className="progress-fill" style={{ width: `${((questionIndex + 1) / questions.length) * 100}%` }} /></div></div>
          <div className="diagnostic-questions" aria-label={`Question ${questionIndex + 1} of ${questions.length}`}>
            {(() => { const q = currentQuestion; return (
              <div className="diag-question" key={q.id}>
                <div className="diag-q-meta">
                  <span className="chip-btn diag-comp-chip">{q.competency}</span>
                  <span className="diag-diff">{q.difficulty}</span>
                </div>
                <div className="diag-q-text">{q.question}</div>
                {q.type === 'mcq' ? (
                  <div className="diag-options">
                    {q.options.map((option) => (
                      <label className={`diag-option ${form[q.id] === option ? 'active' : ''}`} key={option}>
                        <input type="radio" name={q.id} value={option}
                               checked={form[q.id] === option}
                               onChange={() => setForm((f) => ({ ...f, [q.id]: option }))} />
                        <span>{option}</span>
                      </label>
                    ))}
                  </div>
                ) : (
                  <textarea className="diag-text" rows={3}
                            placeholder="Your answer (short is fine)..."
                            value={form[q.id] ?? ''}
                            onChange={(e) => setForm((f) => ({ ...f, [q.id]: e.target.value }))} />
                )}
              </div>
            ) })()}
          </div>
          <div className="focus-diagnostic-actions">
            <button type="button" className="btn" onClick={() => setQuestionIndex((i) => Math.max(0, i - 1))} disabled={questionIndex === 0 || busy}>Back</button>
            {questionIndex < questions.length - 1
              ? <button type="button" className="btn btn-primary" onClick={() => setQuestionIndex((i) => Math.min(questions.length - 1, i + 1))} disabled={busy}>Next question <IconArrowRight size={14} /></button>
              : <button type="button" className="btn btn-primary" onClick={submit} disabled={busy}>{busy ? 'Scoring...' : 'Submit Diagnostic'}</button>}
          </div>
          </> : <p className="muted small">This diagnostic has no questions yet. Try starting it again.</p>}
        </>
      )}

      {phase === 'result' && diag && (
        <div className="diagnostic-result">
          <div className="diag-result-score">
            <strong>{diag.score ?? '–'}%</strong>
            <span>overall</span>
          </div>
          <div className="diag-result-groups">
            <div className="diag-group strong"><h4>Strong Topics</h4>{topicList(diag.topic_results, 'mastered')}</div>
            <div className="diag-group developing"><h4>Needs Practice</h4>{topicList(diag.topic_results, 'developing')}</div>
            <div className="diag-group weak"><h4>Weak Topics</h4>{topicList(diag.topic_results, 'weak')}</div>
          </div>
        </div>
      )}
    </section>
  )
}

function topicList(topics: TopicResult[], status: TopicResult['status']) {
  const rows = topics.filter((t) => t.status === status)
  if (!rows.length) return <p className="muted small">None</p>
  return (
    <div className="diag-topic-list">
      {rows.map((t) => (
        <span className="chip-btn diag-topic-chip" key={t.competency}>{t.label} · {Math.round(t.score)}%</span>
      ))}
    </div>
  )
}

function LessonView({ studentId, skillId, skillName, competency, pathItem, pathId, onClose, onComplete, onStateChange, hasNext, onNext, initialTab = 'learn' }: {
  studentId: number; skillId: number; skillName: string; competency: string;
  pathItem: PersonalizedPathItem; pathId: number; onClose: () => void; onComplete: () => void;
  onStateChange?: (state: Lesson['state']) => void;
  hasNext?: boolean; onNext?: () => void;
  initialTab?: 'learn' | 'example' | 'practice' | 'discuss' | 'mini_check';
}) {
  const [lesson, setLesson] = useState<Lesson | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [tab, setTab] = useState<'learn' | 'example' | 'practice' | 'discuss' | 'mini_check'>(initialTab)
  const [miniAnswers, setMiniAnswers] = useState<Record<string, string>>({})
  const [result, setResult] = useState<{ score: number; passed: boolean; correct: number; total: number } | null>(null)
  const [submitting, setSubmitting] = useState(false)
  const [practiceAnswer, setPracticeAnswer] = useState('')
  const [followUpAnswer, setFollowUpAnswer] = useState('')
  const [practiceAttempt, setPracticeAttempt] = useState<PracticeAttempt | null>(null)
  const [practiceAttemptCount, setPracticeAttemptCount] = useState(0)
  const [practiceSubmitting, setPracticeSubmitting] = useState(false)
  const [practiceError, setPracticeError] = useState('')
  const practiceInputRef = useRef<HTMLTextAreaElement | null>(null)

  // A focus signal can re-target an already-open lesson (Practice scenarios
  // quick-action or Continue) without remounting — apply the requested tab.
  useEffect(() => {
    setTab(initialTab)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [initialTab])

  useEffect(() => {
    let alive = true
    setLoading(true)
    api.lessonGenerate(studentId, skillId, competency)
      .then(async (l) => {
        if (!alive) return
        if (l.state === 'not_started') {
          const startedLesson = await api.lessonStart(studentId, skillId, competency)
          if (!alive) return
          setLesson(startedLesson)
          onStateChange?.(startedLesson.state)
          return
        }
        setLesson(l)
        onStateChange?.(l.state)
      })
      .catch((e) => { if (alive) setError(e?.message || 'Could not load lesson') })
      .finally(() => { if (alive) setLoading(false) })
    return () => { alive = false }
  }, [studentId, skillId, competency])

  useEffect(() => {
    if (tab === 'discuss') window.dispatchEvent(new CustomEvent('copilot:focus'))
  }, [tab])

  useEffect(() => {
    if (!lesson) return
    let alive = true
    api.lessonPracticeAttempts(studentId, skillId, competency)
      .then((res) => {
        if (!alive) return
        setPracticeAttempt(res.latest)
        setPracticeAttemptCount(res.count)
      })
      .catch(() => {
        if (!alive) return
        setPracticeAttempt(null)
        setPracticeAttemptCount(0)
      })
    return () => { alive = false }
  }, [lesson?.id, studentId, skillId, competency])

  const submitPractice = async (sourceAttemptId?: number | null) => {
    const answer = (sourceAttemptId ? followUpAnswer : practiceAnswer).trim()
    if (!lesson || !answer) return
    setPracticeSubmitting(true)
    setPracticeError('')
    try {
      const res = await api.lessonSubmitPractice(studentId, skillId, competency, answer, sourceAttemptId ?? null)
      setPracticeAttempt(res.attempt)
      setPracticeAttemptCount(res.attempts_count)
      if (sourceAttemptId) setFollowUpAnswer('')
      else setPracticeAnswer('')
    } catch (e: unknown) {
      setPracticeError((e as Error)?.message || 'Practice evaluation failed')
    } finally {
      setPracticeSubmitting(false)
    }
  }

  const retryPractice = () => {
    setPracticeAnswer('')
    setFollowUpAnswer('')
    setPracticeError('')
    window.setTimeout(() => practiceInputRef.current?.focus(), 0)
  }

  const submitMiniCheck = async () => {
    if (!lesson) return
    const questions = lesson.content.mini_check.questions
    const orderedAnswers = questions.map((q) => miniAnswers[q.id] || '')
    setSubmitting(true)
    try {
      const res = await api.lessonMiniCheck(studentId, skillId, competency, orderedAnswers)
      setResult(res.lesson.mini_check_result || { score: 0, passed: false, correct: 0, total: questions.length })
      setLesson(res.lesson)
      onStateChange?.(res.lesson.state)
      if (res.lesson.mini_check_result?.passed) onComplete()
    } catch (e: unknown) {
      setError((e as Error)?.message || 'Submission failed')
    } finally {
      setSubmitting(false)
    }
  }

  const isCompleted = lesson?.state === 'completed'
  const diagnosticPct = Math.round(pathItem.diagnostic_score)
  const reasonForLearning = pathItem.action === 'review'
    ? `You understand the basics, but your diagnostic identified gaps to close (${pathItem.topic_status}, ${diagnosticPct}%).`
    : `Your diagnostic showed this topic needs improvement (${pathItem.topic_status}, ${diagnosticPct}%).`

  const tabs = ['learn', 'example', 'practice', 'mini_check'] as const
  const tabLabels: Record<string, string> = { learn: 'Learn', example: 'Example', practice: 'Practice', discuss: 'Discuss with AI', mini_check: 'Mini Check' }

  if (loading) {
    return (
      <div className="lesson-view lesson-loading-skel" role="status" aria-label="Generating lesson">
        <div className="lesson-header">
          <span className="skeleton" style={{ display: 'block', width: 110, height: 14, marginBottom: 10 }} />
          <div className="lesson-title-row">
            <span className="skeleton" style={{ display: 'block', width: '70%', maxWidth: 420, height: 20 }} />
          </div>
        </div>
        <div className="lesson-nav">
          {['Learn', 'Example', 'Practice', 'Discuss', 'Mini Check'].map((t) => (
            <span key={t} className="skeleton" style={{ width: 74, height: 34, marginRight: 10, borderRadius: 6 }} />
          ))}
        </div>
        <div className="lesson-content">
          <span className="skeleton" style={{ display: 'block', width: '45%', maxWidth: 280, height: 18, marginBottom: 14 }} />
          {Array.from({ length: 4 }).map((_, i) => (
            <span key={i} className="skeleton" style={{ display: 'block', width: '100%', height: 13, marginBottom: 9 }} />
          ))}
        </div>
      </div>
    )
  }
  if (error) return <div className="error learning-error">{error}<button className="btn-link" onClick={onClose}>Back to path</button></div>
  if (!lesson) return null

  const content = lesson.content
  const recommendedResources = content.resources || []
  const nextTab = () => { const idx = tabs.findIndex((step) => step === tab); setTab(tab === 'discuss' ? 'mini_check' : tabs[Math.min(tabs.length - 1, idx + 1)]) }
  const practiceData = (content.practice ?? {}) as LessonPractice
  const practiceTitle = typeof practiceData.title === 'string' && practiceData.title.trim()
    ? practiceData.title
    : 'Practice task'
  const practiceFirstFreeText = (practiceData.questions ?? []).find((q) => q.type === 'free_text')
  const practiceTaskText =
    typeof practiceData.task === 'string' && practiceData.task.trim()
      ? practiceData.task
      : (practiceFirstFreeText?.question?.trim()
          || (practiceData.questions?.[0]?.question?.trim()
              ? `Apply this concept: ${practiceData.questions[0].question.trim()}. Explain the concrete steps, commands, or code you would use, and justify your choices.`
              : `Explain how you would apply ${practiceData.competency || competency} to a realistic task, including the concrete steps, tools, commands, or code you would use.`))
  const practiceResponseType = typeof practiceData.response_type === 'string'
    ? practiceData.response_type
    : ''
  const latestPracticeLabel = practiceAttemptCount <= 1
    ? 'Latest attempt'
    : `Latest of ${practiceAttemptCount} attempts`
  const previousPracticeCount = Math.max(0, practiceAttemptCount - 1)
  const latestRemediation = practiceAttempt?.remediation ?? null
  const followUpSourceAttemptId = latestRemediation?.practice_attempt_id ?? null
  const answeringFollowUp = !!latestRemediation
  const activePracticeAnswer = answeringFollowUp ? followUpAnswer : practiceAnswer

  return (
    <div className="lesson-view">
      <div className="lesson-header">
        <button className="btn-link lesson-back" onClick={onClose}>&larr; Back to path</button>
        <div className="lesson-title-row">
          <span className="lesson-breadcrumb">{skillName} &gt; {humanizeTopicLabel(competency)}</span>
          <span className={`chip-btn lesson-mode-chip lesson-mode-${lesson.action}`}>{lesson.action}</span>
        </div>
        <div className="lesson-reason">
          <span className="muted small">{reasonForLearning}</span>
        </div>
        {isCompleted && <div className="lesson-completed-banner"><IconCheck size={16} /> Topic completed</div>}
      </div>

      <nav className="lesson-nav focus-lesson-steps" aria-label="Lesson steps">
        {tabs.map((t, index) => (
          <button key={t} type="button" className={`lesson-tab ${tab === t ? 'active' : ''}`} aria-current={tab === t ? 'step' : undefined} onClick={() => setTab(t)}>
            <span className="focus-step-number">{index + 1}</span>{tabLabels[t]}
          </button>
        ))}
      </nav>
      <div className="focus-lesson-meta">
        <span>{tab === 'discuss' ? 'Optional help' : `Step ${tabs.findIndex((step) => step === tab) + 1} of ${tabs.length}`}</span>
        <button type="button" className="btn-link" onClick={() => setTab('discuss')}><IconChat size={14} /> Ask AI Tutor about this topic</button>
      </div>

      <div className="lesson-content">
        {tab === 'learn' && (
          <div className="lesson-learn">
            <h3>{content.learn.title}</h3>
            <div className="lesson-explanation"><SafeMarkdown>{content.learn.explanation}</SafeMarkdown></div>
            {content.learn.key_ideas && content.learn.key_ideas.length > 0 && (
              <div className="lesson-key-ideas">
                <h4>Key Ideas</h4>
                <ul>{content.learn.key_ideas.map((idea, i) => <li key={i}>{idea}</li>)}</ul>
              </div>
            )}
            {content.learn.key_terms && Object.keys(content.learn.key_terms).length > 0 && (
              <div className="lesson-key-terms">
                <h4>Key Terms</h4>
                {Object.entries(content.learn.key_terms).map(([term, def]) => (
                  <div className="lesson-term" key={term}><strong>{term}</strong>: {def}</div>
                ))}
              </div>
            )}
            {content.learn.job_relevance && (
              <div className="lesson-quality-section">
                <div className="lesson-quality-label">Why this matters for your role</div>
                <p>{content.learn.job_relevance}</p>
              </div>
            )}
            {content.learn.common_mistake && (
              <div className="lesson-quality-section">
                <div className="lesson-quality-label">Common mistake</div>
                <p>{content.learn.common_mistake}</p>
              </div>
            )}
            {content.learn.worked_example && (
              <div className="lesson-quality-section">
                <div className="lesson-quality-label">Worked example</div>
                <p>{content.learn.worked_example}</p>
              </div>
            )}
            {content.learn.depth_note && (
              <div className="lesson-quality-section">
                <p style={{ fontStyle: 'italic' }}>{content.learn.depth_note}</p>
              </div>
            )}
            {content.learn.version_note && (
              <div className="lesson-version-note">{content.learn.version_note}</div>
            )}
            {content.learn.grounding_sources && content.learn.grounding_sources.length > 0 && (
              <div className="lesson-grounding-sources">
                Sources: {content.learn.grounding_sources.map((s, i) => (
                  <span key={i}>{i > 0 && ' · '}<a href={s.url} target="_blank" rel="noopener noreferrer">{s.title || s.source || 'Source'}</a></span>
                ))}
              </div>
            )}
            {recommendedResources.length > 0 && (
              <section className="lesson-resource-panel" aria-label="Recommended Resources">
                <div className="lesson-resource-head">
                  <div>
                    <span>Recommended Resources</span>
                    <strong>{recommendedResources.length} curated source{recommendedResources.length === 1 ? '' : 's'}</strong>
                  </div>
                </div>
                <div className="lesson-resource-list">
                  {recommendedResources.map((resource, i) => {
                    const status = resourceStatus(resource)
                    return (
                      <a className="lesson-resource-card" href={resource.url} target="_blank" rel="noopener noreferrer" key={`${resource.url}-${i}`}>
                        <div className="lesson-resource-card-head">
                          <span className="resource-type">{resourceTypeLabel(resource)}</span>
                          <span className={`lesson-resource-status ${status.key}`}>{status.label}</span>
                        </div>
                        <strong>{resource.title}</strong>
                        <small>{resource.source || 'Curated source'}</small>
                        {resource.reason && <p>{resource.reason}</p>}
                        <span className="lesson-resource-open">Open resource <IconExternal size={13} /></span>
                      </a>
                    )
                  })}
                </div>
              </section>
            )}
            {!isCompleted && <button className="btn btn-primary" onClick={nextTab}>Continue</button>}
          </div>
        )}
        {tab === 'example' && (
          <div className="lesson-example">
            <h3>{content.example.title}</h3>
            <div className="lesson-example-type"><span className="chip-btn">{content.example.type}</span></div>
            <div className="lesson-example-content"><SafeMarkdown>{content.example.content}</SafeMarkdown></div>
            <div className="lesson-explanation"><SafeMarkdown>{content.example.explanation}</SafeMarkdown></div>
            {!isCompleted && <button className="btn btn-primary" onClick={nextTab}>Continue</button>}
          </div>
        )}
        {tab === 'practice' && (
          <div className="lesson-practice">
            <h3>Practice</h3>
            {latestRemediation ? (
              <div className="remediation-panel">
                <div className="remediation-head">
                  <span className="practice-task-label">Personalized Review</span>
                  <div className="practice-source">
                    {latestRemediation.source === 'ai' ? 'AI personalized review' : 'Adaptive review (fallback)'}
                  </div>
                </div>
                <div className="remediation-section">
                  <h5>Focus on</h5>
                  <div className="remediation-focus-list">
                    {latestRemediation.focus_points.map((point, i) => <span className="chip-btn" key={i}>{point}</span>)}
                  </div>
                </div>
                <div className="remediation-section">
                  <h5>Explanation</h5>
                  <div className="remediation-text"><SafeMarkdown>{latestRemediation.explanation}</SafeMarkdown></div>
                </div>
                <div className="remediation-section">
                  <h5>Targeted Example</h5>
                  <div className="lesson-example-content"><SafeMarkdown>{latestRemediation.targeted_example}</SafeMarkdown></div>
                </div>
                <div className="remediation-section remediation-followup">
                  <h5>Try This Next</h5>
                  <p className="lesson-q-text">{latestRemediation.follow_up_task}</p>
                </div>
              </div>
            ) : (
              <div className="practice-primary-task">
                <div className="practice-task-head">
                  <span className="practice-task-label">Practice</span>
                  {practiceResponseType && <span className="chip-btn practice-response-type">{practiceResponseType}</span>}
                </div>
                {practiceTitle && <h4 className="practice-task-title">{practiceTitle}</h4>}
                <p className="lesson-q-text practice-task-text">{practiceTaskText}</p>
              </div>
            )}
            <label className="practice-response-label" htmlFor={`practice-${lesson.id}`}>
              Your {answeringFollowUp ? 'follow-up' : 'practice'} response
            </label>
            <textarea
              id={`practice-${lesson.id}`}
              ref={practiceInputRef}
              className="practice-response"
              value={activePracticeAnswer}
              onChange={(e) => { if (answeringFollowUp) setFollowUpAnswer(e.target.value); else setPracticeAnswer(e.target.value) }}
              placeholder={answeringFollowUp ? 'Write your follow-up response to the targeted task.' : 'Write your explanation, steps, commands, or troubleshooting plan.'}
              disabled={practiceSubmitting || isCompleted}
            />
            <div className="practice-actions">
              <button
                className="btn btn-primary"
                onClick={() => submitPractice(followUpSourceAttemptId)}
                disabled={practiceSubmitting || !activePracticeAnswer.trim() || isCompleted}
                type="button"
              >
                {practiceSubmitting ? 'Evaluating...' : 'Submit Practice'}
              </button>
              {previousPracticeCount > 0 && (
                <span className="muted small">{previousPracticeCount} previous practice {previousPracticeCount === 1 ? 'attempt' : 'attempts'}</span>
              )}
            </div>
            {practiceSubmitting && (
              <div className="practice-status evaluating" role="status">
                <span className="practice-spinner" aria-hidden="true" />
                <span>Evaluating your practice...</span>
              </div>
            )}
            {practiceError && (
              <div className="practice-status error" role="alert">{practiceError}</div>
            )}
            {practiceAttempt && (
              <div className={`practice-review ${practiceAttempt.status}`}>
                <div className="practice-review-head">
                  <div>
                    <span className="practice-task-label">{latestPracticeLabel}</span>
                    <h4>Practice Review</h4>
                  </div>
                  <div className="practice-score">
                    <strong>{Math.round(practiceAttempt.score)}%</strong>
                    <span>{practiceAttempt.status === 'ready' ? 'Ready' : 'Needs review'}</span>
                  </div>
                </div>
                <div className="practice-source">
                  {practiceAttempt.source === 'ai' ? 'AI practice evaluation' : 'Basic automated review'}
                </div>
                <p className="practice-feedback">{practiceAttempt.feedback}</p>
                {practiceAttempt.status === 'ready' && (
                  <div className="practice-ready-banner"><IconCheck size={16} /> Ready for Mini Check</div>
                )}
                <div className="practice-review-grid">
                  <div>
                    <h5>Strengths</h5>
                    <ul>
                      {practiceAttempt.strengths.map((item, i) => <li key={i}>{item}</li>)}
                    </ul>
                  </div>
                  <div>
                    <h5>Needs improvement</h5>
                    <ul>
                      {practiceAttempt.missing_points.map((item, i) => <li key={i}>{item}</li>)}
                    </ul>
                  </div>
                </div>
                <div className="practice-next-action">
                  <strong>Next action</strong>
                  <span>{practiceAttempt.next_action}</span>
                </div>
                {!isCompleted && (
                  <button className="btn btn-primary" onClick={retryPractice} type="button">
                    Try Again
                  </button>
                )}
              </div>
            )}
            {!isCompleted && practiceAttempt?.status === 'ready' ? (
              <button className="btn btn-primary" onClick={nextTab}>Continue to Mini Check</button>
            ) : !isCompleted ? (
              <button className="btn" onClick={nextTab}>Continue</button>
            ) : null}
          </div>
        )}
        {tab === 'discuss' && (
          <div className="lesson-discuss">
            <div className="lesson-discuss-head">
              <h3>Discuss with AI</h3>
              <p className="muted small">Ask the tutor anything about {humanizeTopicLabel(competency)} — your background, skill, and this exact step are already in the tutor's context.</p>
            </div>
            <div className="lesson-discuss-goto">
              <p className="muted small">
                The AI Tutor lives in the panel at the bottom-right of every page. Open it — it already knows
                you're learning <strong>{humanizeTopicLabel(competency)}</strong> on <strong>{skillName}</strong>.
              </p>
              <button
                className="btn btn-primary"
                onClick={() => window.dispatchEvent(new CustomEvent('copilot:focus'))}
                type="button"
              >
                <IconChat size={15} /> Open AI Tutor
              </button>
            </div>
            {!isCompleted && <button className="btn btn-primary" onClick={nextTab} style={{ marginTop: 12 }}>Continue to Mini Check</button>}
          </div>
        )}
        {tab === 'mini_check' && (
          <div className="lesson-mini-check">
            <h3>Mini Check</h3>
            {result ? (
              <div className={`lesson-result ${result.passed ? 'passed' : 'failed'}`}>
                <div className="lesson-result-score">{Math.round(result.score * 100)}%</div>
                <div className="lesson-result-detail">{result.correct}/{result.total} correct</div>
                {result.passed ? (
                  <div className="lesson-result-msg passed-msg"><IconCheck size={16} /> Passed — topic completed!</div>
                ) : (
                  <div className="lesson-result-msg failed-msg">Needs another attempt — review the lesson and try again.</div>
                )}
                <div className="lesson-result-actions">
                  {!result.passed && <button className="btn" onClick={() => { setResult(null); setMiniAnswers({}); setTab('learn') }}>Review Lesson</button>}
                  {result.passed && hasNext && onNext && <button className="btn btn-primary" onClick={onNext}>Next Lesson <IconArrowRight size={15} /></button>}
                  {result.passed && <button className="btn" onClick={onClose}>Back to Path</button>}
                </div>
              </div>
            ) : (
              <>
                {content.mini_check.questions.map((q) => (
                  <div className="lesson-question" key={q.id}>
                    <p className="lesson-q-text">{q.question}</p>
                    {q.type === 'mcq' && q.options && (
                      <div className="lesson-options">
                        {q.options.map((opt, i) => (
                          <button key={i} className={`lesson-option ${miniAnswers[q.id] === opt ? 'selected' : ''}`}
                            onClick={() => setMiniAnswers({ ...miniAnswers, [q.id]: opt })}>
                            {opt}
                          </button>
                        ))}
                      </div>
                    )}
                    {q.type === 'free_text' && (
                      <textarea className="lesson-free-text" value={miniAnswers[q.id] || ''}
                        onChange={(e) => setMiniAnswers({ ...miniAnswers, [q.id]: e.target.value })}
                        placeholder="Type your answer..." />
                    )}
                  </div>
                ))}
                <button className="btn btn-primary" onClick={submitMiniCheck} disabled={submitting}>
                  {submitting ? 'Scoring...' : 'Submit Mini Check'}
                </button>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

function PersonalizedPathPanel({ studentId, skillId, skillName, refreshKey = 0, startSignal = 0, focusSignal, onPathChange, onCompetencyChange }: {
  studentId: number
  skillId: number
  skillName: string
  refreshKey?: number
  startSignal?: number
  focusSignal?: { competency: string; signal: number; tab?: 'learn' | 'example' | 'practice' | 'discuss' | 'mini_check' } | null
  onPathChange?: (path: PersonalizedPath | null) => void
  onCompetencyChange?: (competency: string | null) => void
}) {
  const [path, setPath] = useState<PersonalizedPath | null>(null)
  const [ready, setReady] = useState(false)
  const [diagnosticDone, setDiagnosticDone] = useState(false)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [showMastered, setShowMastered] = useState(false)
  const [done, setDone] = useState<string[]>([])
  const [lessonStates, setLessonStates] = useState<Record<string, Lesson['state']>>({})
  const [lessonReviews, setLessonReviews] = useState<Record<string, { passed?: boolean } | null>>({})
  const [showAllTopics, setShowAllTopics] = useState(false)
  const [openCompetency, setOpenCompetency] = useState<string | null>(null)
  const [focusTab, setFocusTab] = useState<'learn' | 'example' | 'practice' | 'discuss' | 'mini_check'>('learn')
  const [finalStatus, setFinalStatus] = useState<FinalAssessmentStatus | null>(null)
  const handledStartSignal = useRef(0)
  const handledFocusSignal = useRef(0)

  const compRef = useRef(onCompetencyChange)
  compRef.current = onCompetencyChange
  useEffect(() => () => { compRef.current?.(null) }, [])

  const loadFinalStatus = async () => {
    if (!studentId || !skillId) return
    try {
      const s = await api.finalAssessmentStatus(studentId, skillId)
      setFinalStatus(s)
    } catch {
      setFinalStatus(null)
    }
  }

  const syncLessonStates = async (nextPath: PersonalizedPath | null) => {
    if (!nextPath) {
      setLessonStates({})
      setLessonReviews({})
      return {}
    }
    const entries = await Promise.all(nextPath.items.map(async (item) => {
      try {
        const lesson = await api.lessonGet(studentId, skillId, item.competency)
        return [item.competency, lesson.state] as const
      } catch {
        return [item.competency, 'not_started' as Lesson['state']] as const
      }
    }))
    const states = Object.fromEntries(entries) as Record<string, Lesson['state']>
    setLessonStates(states)
    const reviews = await Promise.all(nextPath.items.map(async (item) => {
      try {
        const lesson = await api.lessonGet(studentId, skillId, item.competency)
        return [item.competency, lesson.mini_check_result ?? null] as const
      } catch {
        return [item.competency, null] as const
      }
    }))
    setLessonReviews(Object.fromEntries(reviews) as Record<string, { passed?: boolean } | null>)
    return states
  }

  const openCurrentTopic = (nextPath: PersonalizedPath, states: Record<string, Lesson['state']> = lessonStates) => {
    const completed = new Set(nextPath.progress ?? [])
    const current =
      nextPath.items.find((item) => states[item.competency] === 'in_progress' && !completed.has(item.id)) ||
      nextPath.items.find((item) => !completed.has(item.id)) ||
      nextPath.items[0]
    if (!current) return
    setOpenCompetency(current.competency)
    setFocusTab('learn')
    compRef.current?.(current.competency)
  }

  const loadPath = async () => {
    setError('')
    try {
      const res = await api.personalizedPath(studentId, skillId)
      if ('diagnostic_required' in res) {
        setPath(null)
        setDone([])
        setLessonStates({})
        onPathChange?.(null)
        const latest = await api.latestDiagnostic(studentId, skillId).catch(() => null)
        setDiagnosticDone(!!latest?.completed_at)
      } else {
        setPath(res)
        setDone([...res.progress])
        await syncLessonStates(res)
        setDiagnosticDone(true)
        onPathChange?.(res)
      }
    } catch {
      setPath(null)
      setDone([])
      setLessonStates({})
      setDiagnosticDone(false)
      onPathChange?.(null)
    } finally {
      setReady(true)
    }
  }

  useEffect(() => {
    if (studentId && skillId) {
      setReady(false)
      setOpenCompetency(null)
      compRef.current?.(null)
      void loadPath()
      void loadFinalStatus()
    }
  }, [studentId, skillId, refreshKey])

  const create = async (autoOpen = false) => {
    setBusy(true)
    setError('')
    try {
      const res = await api.generatePersonalizedPath(studentId, skillId)
      if ('diagnostic_required' in res) {
        setPath(null)
        setDone([])
        setLessonStates({})
        onPathChange?.(null)
      } else {
        setPath(res)
        setDone([...res.progress])
        const states = await syncLessonStates(res)
        setDiagnosticDone(true)
        onPathChange?.(res)
        if (autoOpen) openCurrentTopic(res, states)
      }
    } catch (e: unknown) {
      setError((e as Error)?.message || 'Could not create your learning path')
    } finally {
      setBusy(false)
    }
  }

  const openLesson = async (competency: string) => {
    setOpenCompetency(competency)
    compRef.current?.(competency)
  }

  const lessonItem = openCompetency && path ? path.items.find((it) => it.competency === openCompetency) : null
  const lessonIndex = lessonItem && path ? path.items.findIndex((it) => it.competency === openCompetency) : -1
  const nextLesson = lessonIndex >= 0 && path ? path.items[lessonIndex + 1] : undefined

  useEffect(() => {
    if (!ready || !startSignal || handledStartSignal.current === startSignal) return
    if (path) {
      handledStartSignal.current = startSignal
      openCurrentTopic(path)
      return
    }
    if (diagnosticDone) {
      handledStartSignal.current = startSignal
      void create(true)
    }
  }, [startSignal, ready, path, diagnosticDone])

  useEffect(() => {
    if (!ready || !path || !focusSignal || handledFocusSignal.current === focusSignal.signal) return
    const normalize = (value: string) => value.toLowerCase().replace(/[_\s-]+/g, ' ').trim()
    const requested = normalize(focusSignal.competency)
    const found = path.items.find((it) => normalize(it.competency) === requested || normalize(it.title) === requested)
    if (!found) return
    handledFocusSignal.current = focusSignal.signal
    setOpenCompetency(found.competency)
    setFocusTab(focusSignal.tab ?? 'learn')
    compRef.current?.(found.competency)
  }, [focusSignal, ready, path])

  if (!ready) return null

  if (openCompetency && lessonItem && path) {
    return (
      <LessonView
        key={openCompetency}
        studentId={studentId} skillId={skillId} skillName={skillName}
        competency={openCompetency} pathItem={lessonItem} pathId={path.id}
        onClose={() => { setOpenCompetency(null); compRef.current?.(null) }}
        onComplete={async () => { await loadPath(); void loadFinalStatus() }}
        onStateChange={(state) => setLessonStates((prev) => ({ ...prev, [openCompetency]: state }))}
        hasNext={!!nextLesson}
        initialTab={focusTab}
        onNext={nextLesson ? () => {
          setOpenCompetency(nextLesson.competency)
          setFocusTab('learn')
          compRef.current?.(nextLesson.competency)
          requestAnimationFrame(() => document.getElementById('skill-detail')?.scrollIntoView({ behavior: 'smooth', block: 'start' }))
        } : undefined}
      />
    )
  }

  const cap = (s: string) => (s ? s[0].toUpperCase() + s.slice(1) : '')
  const completedIds = new Set(done)
  const progress = topicProgressFor(path)
  const stateFor = (item: PersonalizedPathItem) => {
    if (completedIds.has(item.id) || lessonStates[item.competency] === 'completed') return 'Completed'
    if (lessonStates[item.competency] === 'in_progress') return 'In progress'
    return 'Not started'
  }
  const stateClass = (state: string) => state.toLowerCase().replace(/\s+/g, '-')
  const currentCompetency = path?.items.find((item) => !completedIds.has(item.id))?.competency ?? null

  return (
    <section className="personalized-path-panel">
      <div className="diagnostic-head">
        <div>
          <span className="eyebrow">My Learning Path</span>
          <h3>{skillName} — personalized plan</h3>
          {path && <p className="muted small">Based on your latest diagnostic · target level {path.required_level}</p>}
        </div>
        {path && (
          <span className="chip-btn pp-required-level">{path.required_level}</span>
        )}
      </div>

      {path && path.stale && (
        <div className="pp-stale-note" role="note">
          <IconAlert size={15} />
          <span>
            This path was built from an <strong>earlier diagnostic</strong>. A newer completed
            diagnostic exists, so these topics may no longer reflect your current results and
            do not count toward Final Assessment readiness. Create a fresh path to realign it.
          </span>
        </div>
      )}

      {error && <div className="error learning-error">{error}</div>}

      {!path && diagnosticDone && (
        <div className="pp-create-call">
          <p className="section-copy">
            Your diagnostic is complete. Build a topic-by-topic learning path ordered from your
            weakest topics, so you know exactly what to tackle next.
          </p>
          <button className="btn btn-primary" onClick={() => void create(false)} disabled={busy}>
            <IconBolt size={16} /> {busy ? 'Building...' : 'Create My Learning Path'}
          </button>
        </div>
      )}

      {!path && !diagnosticDone && ready && (
        <p className="muted small section-copy">
          Complete a diagnostic first — it shapes which topics belong on your personalized path.
        </p>
      )}

      {path && (
        <>
          <div className="pp-progress-summary">
            <div>
              <strong>{progress.done} / {progress.total} topics complete</strong>
              <span>{progress.pct}%</span>
            </div>
            <div className="lp-track"><span style={{ width: `${progress.pct}%` }} /></div>
            <p className="muted small">
              Topics complete only after a Mini Check pass. This does not create a Verified Skill.{' '}
              <WhyThis>Study progress never grants a Verified Skill — only a proctored Final Assessment on the Assessments page does. This number tracks lessons whose Mini Check you passed, nothing more.</WhyThis>
            </p>
          </div>

          <div className="pp-timeline">
            {(showAllTopics ? path.items : path.items.slice(0, 8)).map((item) => {
              const isDone = done.includes(item.id)
              const topicState = stateFor(item)
              const isCurrent = item.competency === currentCompetency
              return (
                <div className={`pp-item ${isDone ? 'is-done' : ''} ${isCurrent ? 'is-current' : ''}`} key={item.id}>
                  <div className={`pp-state-dot pp-state-${stateClass(topicState)}`}>
                    {isDone ? <IconCheck size={15} /> : <span />}
                  </div>
                  <div className="pp-item-body" onClick={() => openLesson(item.competency)} role="button" tabIndex={0} onKeyDown={(e) => { if (e.key === 'Enter') openLesson(item.competency) }}>
                    <div className="pp-item-top">
                      <span className="pp-order">{String(item.order).padStart(2, '0')}</span>
                      <MilestoneChip state={topicMilestoneState(isDone, isCurrent, lessonStates[item.competency], lessonReviews[item.competency])} />
                      <span className={`chip-btn pp-status-chip pp-status-${item.topic_status}`}>{cap(item.topic_status)}</span>
                      <span className={`chip-btn pp-action-chip pp-action-${item.action}`}>{item.action}</span>
                      <span className={`chip-btn pp-topic-state pp-topic-state-${stateClass(topicState)}`}>{topicState}</span>
                    </div>
                    <h4>{humanizeTopicLabel(item.title)}</h4>
                    <p className="muted small">
                      Added because your diagnostic score was <strong>{Math.round(item.diagnostic_score)}%</strong>.
                      {' '}<span className="pp-est"><IconClock size={13} /> ~{item.estimated_minutes} min</span>
                    </p>
                  </div>
                </div>
              )
            })}

            {!showAllTopics && path.items.length > 8 && (
              <div className="pp-more-wrap">
                <button type="button" className="pp-more-toggle" onClick={() => setShowAllTopics(true)}>
                  <IconChevron size={14} /> Show all {path.items.length - 8} more topics
                </button>
              </div>
            )}

            {path.stages.map((stage) => {
              const isDone = done.includes(stage.id)
              const isFinalAssess = stage.id === 'final-assessment'
              if (isFinalAssess) {
                return (
                  <div className={`pp-stage pp-stage-final ${isDone ? 'is-done' : ''}`} key={stage.id}>
                    <div className="pp-stage-lock">
                      {isDone ? <IconCheck size={15} /> : <span className="fa-dot" />}
                    </div>
                    <div className="pp-item-body">
                      <div className="pp-item-top">
                        <MilestoneChip state={stageMilestoneState(isDone, false)} />
                        <span className="chip-btn pp-status-chip pp-status-milestone">milestone</span>
                        <span className={`chip-btn pp-action-chip pp-action-${isDone ? 'done' : 'available'}`}>
                          {isDone ? 'completed' : 'Available anytime'}
                        </span>
                      </div>
                      <h4>{humanizeTopicLabel(stage.stage)}</h4>
                      <p className="muted small">
                        Independent from learning progress — start it from the Assessments page whenever you are ready.
                      </p>
                    </div>
                  </div>
                )
              }
              const unlocked = isDone
              const lockState = isDone ? 'done' : 'locked'
              return (
                <div className={`pp-stage ${isDone ? 'is-done' : ''}`} key={stage.id}>
                  <div className="pp-stage-lock">
                    {unlocked ? <IconCheck size={15} /> : <IconLock size={14} />}
                  </div>
                  <div className="pp-item-body">
                    <div className="pp-item-top">
                      <MilestoneChip state={stageMilestoneState(isDone, !isDone)} />
                      <span className="chip-btn pp-status-chip pp-status-milestone">milestone</span>
                      <span className={`chip-btn pp-action-chip pp-action-${lockState}`}>{lockState}</span>
                    </div>
                    <h4>{humanizeTopicLabel(stage.stage)}</h4>
                    <p className="muted small">
                      Completes the {cap(stage.action)} stage of this path.
                    </p>
                  </div>
                </div>
              )
            })}
          </div>

          {path.skipped_mastered.length > 0 && (
            <div className="pp-mastered">
              <button className="pp-mastered-toggle" onClick={() => setShowMastered((s) => !s)}>
                <span className={`pp-mastered-chev ${showMastered ? 'open' : ''}`}><IconChevron size={14} /></span>
                Skipped / Already mastered — {path.skipped_mastered.length} topics excluded
              </button>
              {showMastered && (
                <div className="pp-mastered-chips">
                  {path.skipped_mastered.map((comp) => (
                    <span className="chip-btn pp-status-chip pp-status-mastered" key={comp}>{humanizeTopicLabel(comp)}</span>
                  ))}
                </div>
              )}
            </div>
          )}

          {finalStatus && finalStatus.has_blueprint && (
            <section className="pp-coverage">
              <div className="fa-head">
                <span className="eyebrow">Final Assessment</span>
                <span className="chip-btn fa-status fa-ready">Full coverage required to pass</span>
              </div>
              <p className="muted small">
                Target level {finalStatus.required_level}. The proctored Final Assessment is always
                available from the Assessments page; every required competency below must score 70%
                or higher for the attempt to pass.
              </p>
              {finalStatus.path_stale && (
                <p className="muted small pp-stale-inline" role="note">
                  <IconAlert size={13} /> Your learning path is stale (built from an earlier
                  diagnostic), so its completed topics are not counted here. Only your latest
                  completed diagnostic counts toward coverage.
                </p>
              )}
              <div className="plan-coverage">
                {finalStatus.readiness.required.map((slug) => {
                  const covered = finalStatus.readiness.satisfied.includes(slug)
                  return (
                    <div className={`plan-coverage-item ${covered ? '' : 'missing'}`} key={slug}>
                      <span className="plan-comp-check">{covered ? <IconCheck size={13} /> : <span className="fa-dot" />}</span>
                      <span className="plan-comp-name">{humanizeTopicLabel(slug)}</span>
                      {covered && <span className="fa-covered-tag">covered</span>}
                      {!covered && <span className="fa-missing-tag">missing</span>}
                    </div>
                  )
                })}
              </div>
            </section>
          )}
        </>
      )}
    </section>
  )
}

function roadmapToMarkdown(map: CareerRoadmap): string {
  const lines: string[] = []
  if (map.summary) { lines.push(map.summary, '') }
  ;(map.phases || []).forEach((phase) => {
    lines.push(`## Phase ${phase.phase}: ${phase.title}`)
    if (phase.goal) lines.push(`Goal: ${phase.goal}`)
    const names = (phase.skills || []).map((s) => s.name).filter(Boolean)
    if (names.length) lines.push(`Develops: ${names.join(', ')}`)
    ;(Array.isArray(phase.deliverables) ? phase.deliverables : []).forEach((d) => {
      lines.push(`- ${String(d ?? '')}`)
    })
    lines.push('')
  })
  return lines.join('\n').trim()
}

function VerificationReport({ studentId, map }: { studentId: number; map: CareerRoadmap }) {
  const [report, setReport] = useState<RoadmapValidation | null>(null)
  const [loading, setLoading] = useState(false)
  const [noCv, setNoCv] = useState(false)
  const [revised, setRevised] = useState<string | null>(null)
  const [notice, setNotice] = useState('')
  const [applying, setApplying] = useState(false)

  useEffect(() => {
    let alive = true
    setLoading(true)
    setReport(null)
    setRevised(null)
    setNotice('')
    setNoCv(false)
    const draft = roadmapToMarkdown(map)
    api.cvText(studentId)
      .then(({ cv_text }) => {
        if (!alive) return
        setNoCv(!cv_text)
        return api.validateRoadmap({ draft_roadmap: draft, student_cv: cv_text || '', role_id: 'soc_analyst' })
          .then((r) => { if (alive) setReport(r) })
      })
      .catch(() => { if (alive) setReport(null) })
      .finally(() => { if (alive) setLoading(false) })
    return () => { alive = false }
  }, [studentId, map])

  if (!report || report.error) {
    return loading ? (
      <div className="vr-panel" role="status">
        <strong>Verification Report</strong>
        <span className="muted small">Validating against NIST NICE v2.1 and MITRE ATT&amp;CK Enterprise…</span>
      </div>
    ) : (
      <div className="vr-panel">
        <strong>Verification Report</strong>
        <span className="muted small">Verification unavailable for this roadmap.</span>
      </div>
    )
  }

  const failed = (report.violations || []).filter((v) => !v.passed)
  const coveragePct = Math.round((report.coverage_score ?? 0) * 100)
  const personalizationPct = Math.round((report.personalization_score ?? 0) * 100)

  const apply = async () => {
    setApplying(true)
    setNotice('')
    try {
      const res = await api.applyCorrections({
        draft_roadmap: roadmapToMarkdown(map),
        violations: report.violations || [],
      })
      setRevised(res.revised_roadmap)
      setNotice(`Roadmap updated — ${failed.length} corrections applied.`)
    } catch {
      setNotice('Could not apply corrections. Please try again.')
    } finally {
      setApplying(false)
    }
  }

  return (
    <div className="vr-panel">
      <div className="vr-head">
        <strong>Verification Report</strong>
        {report.source === 'fallback' && <span className="vr-badge">fallback</span>}
      </div>
      {noCv && (
        <p className="vr-warn" role="alert">
          No CV uploaded — personalization score is unavailable. Upload your CV to see a personalized roadmap.
        </p>
      )}
      <div className="vr-scores">
        <div className="vr-score"><span>Coverage</span><b>{coveragePct}%</b></div>
        <div className="vr-score"><span>Personalization</span><b>{personalizationPct}%</b></div>
      </div>
      <ul className="vr-checks">
        {(report.violations || []).map((v, i) => (
          <li key={i} className={v.passed ? 'pass' : 'fail'}>
            <span className={`vr-badge ${v.passed ? 'pass' : 'fail'}`}>{v.passed ? 'PASS' : 'FAIL'}</span>
            <span className="vr-check-name">{v.check_name || 'CHECK'}</span>
            <span className="vr-evidence">{v.evidence}</span>
          </li>
        ))}
      </ul>
      {failed.length > 0 && (
        <button type="button" className="btn btn-sm btn-primary" onClick={apply} disabled={applying}>
          {applying ? 'Applying…' : 'Apply Corrections'}
        </button>
      )}
      {notice && <p className="vr-notice" role="status">{notice}</p>}
      {revised !== null && (
        <div className="vr-revised">
          <strong>Revised Roadmap</strong>
          <div className="md-body"><SafeMarkdown>{revised}</SafeMarkdown></div>
        </div>
      )}
      <p className="vr-footer small muted">Verified against NIST NICE v2.1 and MITRE ATT&amp;CK Enterprise</p>
    </div>
  )
}

function CareerRoadmapCard({ studentId, roleTitle }: { studentId: number; roleTitle?: string }) {
  const { applyCopilot } = useApp()
  const [map, setMap] = useState<CareerRoadmap | null>(null)
  const [openPhase, setOpenPhase] = useState<number | null>(1)

  const openRoadmapPhase = (next: number | null) => {
    setOpenPhase(next)
    if (next !== null) applyCopilot({ page: 'career_roadmap', skillId: null, competency: null, jobTitle: null, jobUrl: null })
  }

  useEffect(() => {
    let alive = true
    if (!studentId) return
    api.careerRoadmap(studentId)
      .then((r) => { if (alive) setMap(r) })
      .catch((e) => { if (alive) { setMap(null); console.error('[learning] career roadmap failed:', e) } })
    return () => { alive = false }
  }, [studentId])

  if (!map || !Array.isArray(map.phases) || !map.phases.length) return null

  return (
    <section className="learning-section career-roadmap-section" id="career-roadmap">
      <SectionTitle
        eyebrow="Career Roadmap"
        title="High-level career journey"
        meta={`${map.phase_count ?? map.phases.length} phases - ${map.role_title || roleTitle || 'your target role'}`}
      />
      <p className="section-copy">{map.summary}</p>
      <VerificationReport studentId={studentId} map={map} />
      <div className="cr-phases">
        {map.phases.map((phase) => {
          const open = openPhase === phase?.phase
          const skillNames = [...new Set((phase?.skills || []).map((skill) => skill?.name).filter(Boolean))]
          return (
            <div className={`cr-phase ${open ? 'open' : ''}`} key={phase?.phase ?? 0}>
              <button className="cr-phase-head" onClick={() => openRoadmapPhase(open ? null : phase.phase)}>
                <span className="cr-phase-num">{phase?.phase ?? ''}</span>
                <span className="cr-phase-title">{phase?.title ?? ''}</span>
                <IconChevron size={15} className={open ? 'chev open' : 'chev'} />
              </button>
              {open && phase && (
                <div className="cr-phase-body">
                  <p className="cr-goal">{phase.goal}</p>
                  {skillNames.length > 0 && (
                    <div className="cr-skills">
                      <span className="small muted">Develops:</span>
                      {skillNames.map((name) => (
                        <span className="chip-btn cr-chip" key={name}>{name}</span>
                      ))}
                    </div>
                  )}
                  <div className="cr-deliverables">
                    <div className="cr-deliverable-title">Deliverables</div>
                    {(Array.isArray(phase.deliverables)
                      ? phase.deliverables
                      : typeof phase.deliverables === 'string'
                        ? [phase.deliverables]
                        : []
                    ).map((deliverable, i) => (
                      <div className="cr-deliverable" key={i}>
                        <span className="rm-checkbox" style={{ background: 'var(--sb-midnight)', borderColor: 'var(--sb-midnight)' }}>{i + 1}</span>
                        <div className="md-body"><SafeMarkdown>{deliverable}</SafeMarkdown></div>
                      </div>
                    ))}
                  </div>
                  <div className="cr-check"><strong>Checkpoint:</strong> {phase.checkpoint}</div>
                </div>
              )}
            </div>
          )
        })}
      </div>
    </section>
  )
}

function ResourceCenter({ items }: { items: LearningItem[] }) {
  const [mode, setMode] = useState<'combined' | 'per-skill'>('combined')
  const all = items.flatMap((item) =>
    (item.resources || []).map((resource) => ({
      ...resource,
      skillId: item.skill_id,
      skillName: item.skill_name,
    })),
  )
  if (!all.length) return null

  const byUrl = new Map<string, (typeof all)[number] & { skills: Set<string>; times: number }>()
  all.forEach((resource) => {
    const hit = byUrl.get(resource.url)
    if (hit) {
      hit.skills.add(resource.skillName)
      hit.times += 1
      if (resource.helpfulness && !hit.helpfulness) hit.helpfulness = resource.helpfulness
    } else {
      byUrl.set(resource.url, { ...resource, skills: new Set([resource.skillName]), times: 1 })
    }
  })
  const unique = [...byUrl.values()].sort((a, b) => b.times - a.times || (a.title || '').localeCompare(b.title || ''))
  const skillCount = new Set(all.map((resource) => resource.skillName)).size

  const perSkill = new Map<string, typeof unique>()
  unique.forEach((resource) => {
    const key = [...resource.skills][0]
    perSkill.set(key, [...(perSkill.get(key) || []), resource])
  })

  return (
    <section className="learning-section resource-center-section">
      <div className="resource-center-head">
        <SectionTitle eyebrow="Learning Resources" title="Resource library" meta={`${unique.length} unique links across ${skillCount} skills`} />
        <div className="rc-toggle">
          <button className={`rc-tab ${mode === 'combined' ? 'active' : ''}`} onClick={() => setMode('combined')}>Combined</button>
          <button className={`rc-tab ${mode === 'per-skill' ? 'active' : ''}`} onClick={() => setMode('per-skill')}>By skill</button>
        </div>
      </div>
      {mode === 'combined' ? (
        <div className="resource-card-row">
          {unique.map((resource, i) => (
            <ResourceCard key={resource.url} resource={resource} fallbackRank={i + 1} />
          ))}
        </div>
      ) : (
        [...perSkill.entries()].map(([name, rows]) => (
          <div className="rc-skill" key={name}>
            <div className="rc-skill-name">{name}</div>
            <div className="resource-card-row">
              {rows.map((resource, i) => (
                <ResourceCard key={resource.url} resource={resource} fallbackRank={i + 1} skillName={name} />
              ))}
            </div>
          </div>
        ))
      )}
    </section>
  )
}

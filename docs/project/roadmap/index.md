[< Project](../briefing.md)

# Roadmap

The roadmap is organized as **CV → Epic → Story**. Each level has its own
folder and index. Stories that are non-trivial have a `plan.md` and a
`test-guide.md` written before implementation begins.

**CV** (Capability Value) — a major delivery stage with clear user-visible impact.  
**Epic** — a cohesive block of work within a CV, with a done condition.  
**Story** — an atomic, user-centric delivery that can be verified end-to-end.

---

## Capability Values

| Code | Capability Value | Status |
|------|-----------------|--------|
| [CV0](cv0-english-foundation/index.md) | English Foundation | ✅ Done |
| [CV1](cv1-pi-runtime/index.md) | Pi Runtime | ✅ Done |
| [CV2](cv2-runtime-portability/index.md) | Runtime Portability | ✅ Done |
| [CV3](cv3-pi-skill-parity/index.md) | Pi Skill Parity | ✅ Done |
| [CV4](cv4-framework-user-separation/index.md) | Framework/User Separation | ✅ Done |
| [CV5](cv5-multisession-safety/index.md) | Multisession Safety | ✅ Done |
| [CV6](cv6-intelligence-runtime-maturity/index.md) | Multi-User Onboarding, Identity Runtime Maturity, and Extensibility | ✅ Done |
| [CV7](cv7-intelligence-depth/index.md) | Intelligence Depth | ✅ Done |
| [CV8](cv8-runtime-expansion/index.md) | Runtime Expansion: Codex and Gemini CLI | Draft |

---

## CV3 — Pi Skill Parity

Every skill available in Claude Code is also available in Pi. Three epics:
CLI Completeness → Pi Skill Wrappers → Pi Intelligence Skills. See
[CV3 index](cv3-pi-skill-parity/index.md) for skills inventory and sequencing.

## CV4 — Framework/User Separation

Done. CV4 moved Mirror Mind toward a reusable framework with user-owned
identity and runtime state outside the repo. The current state now includes
user-home path resolution, template bootstrap, user-home seeding,
multi-user-safe command targeting, production DB and runtime-state defaults
derived from the resolved mirror home, transcript export aligned with the
user-home model, and an explicit legacy migration workflow for Portuguese-era
databases. See the [CV4 index](cv4-framework-user-separation/index.md).

## CV5 — Multisession Safety

Done. CV5 replaced singleton runtime session state with a database-backed,
session-scoped control plane. Session ↔ conversation binding now lives in
SQLite, mirror state is session-scoped for runtimes that pass explicit session
ids, stale-orphan handling skips all active runtime sessions rather than one
ambient session, and concurrent startup/session creation now has regression
coverage. See the [CV5 index](cv5-multisession-safety/index.md).

## CV6 — Multi-User Onboarding, Identity Runtime Maturity, and Extensibility

Done. CV6 made Mirror Mind ready for broader multi-user use: runtime-relevant
persona metadata persists in the database, persona routing is database backed
and inspectable, repo/personal/runtime boundary leaks have been cleaned up, the
extension model exists with an end-to-end `review-copy` reference path across Pi
and Claude, and new users now bootstrap from meaningful starter identity assets
instead of placeholders.

## CV7 — Intelligence Depth

In progress. E1 (Pipeline Observability & Evals), E2 (Reception &
Conditional Composition), and E3 (Extraction Quality) are done. E4 (Memory
Depth) is next. See the [CV7 index](cv7-intelligence-depth/index.md) and
[draft-analysis.md](cv7-intelligence-depth/draft-analysis.md) for the
territorial analysis, success metrics, and resolved planning-phase decisions.

## CV8 — Runtime Expansion: Codex and Gemini CLI

Draft. CV8 extends Mirror Mind beyond Claude Code and Pi into two additional
coding-agent runtimes. Codex is intentionally first; Gemini CLI comes second
after Codex lessons are folded back into the runtime adapter contract. See the
[CV8 index](cv8-runtime-expansion/index.md).

---

**See also:** [Briefing](../briefing.md) · [Decisions](../decisions.md) · [Worklog](../../process/worklog.md)

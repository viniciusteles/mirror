[< Roadmap](../index.md)

# CV6 — Multi-User Onboarding, Identity Runtime Maturity, and Extensibility

**Status:** Planned
**Goal:** Make Mirror Mind truly ready for other users by moving runtime-relevant identity behavior into a complete database-backed model, cleaning remaining personal/repo coupling, making onboarding explicit, and defining an extension model for user-specific capabilities that do not belong in core.

---

## What This Is

CV4 separated the framework from user-owned identity at the file and database
level. CV5 made the runtime control plane safe for simultaneous sessions. But
Mirror Mind still has important gaps before it is genuinely ready to onboard
other people:

- persona routing is not yet database-native
- runtime-relevant persona metadata such as `routing_keywords` is lost during seeding
- some boundaries between personal artifacts, framework assets, and runtime truth are still blurry
- onboarding remains underdefined for a new user starting from scratch
- user-specific capabilities still risk being embedded in the core repo instead of living as extensions

CV6 closes those gaps. It turns the database into the runtime source of truth
not only for persona prompt content, but also for the metadata needed to route
and reason about personas. It also defines where user-specific capabilities
belong and how they integrate without polluting the framework.

This CV is about framework maturity:
- identity metadata should be complete enough in the database to drive runtime behavior
- persona routing should use database state, not seed YAMLs
- onboarding should be explicit, repeatable, and verifiable for a new user
- user-specific capabilities should plug in through an extension model, not by expanding core indefinitely

---

## Epics

| Code | Epic | User-visible outcome | Status |
|------|------|----------------------|--------|
| [CV6.E1](cv6-e1-structured-identity-metadata-in-db/index.md) | Structured Identity Metadata in the Database | Runtime-relevant persona metadata is stored in the database rather than discarded at seed time | Planned |
| [CV6.E2](cv6-e2-db-backed-persona-auto-routing/index.md) | Persona Auto-Routing from Database Metadata | Mirror Mode can resolve personas from database-backed routing metadata instead of relying only on explicit or sticky persona state | Planned |
| [CV6.E3](cv6-e3-multi-user-cleanup-and-boundary-audit/index.md) | Multi-User Cleanup and Repo Boundary Audit | Remaining personal/framework/runtime boundary leaks are identified and cleaned up | Planned |
| [CV6.E4](cv6-e4-new-user-onboarding-flow/index.md) | New User Onboarding Flow | A new user can bootstrap, customize, seed, verify, and start using Mirror Mind without touching personal repo-owned artifacts | Planned |
| [CV6.E5](cv6-e5-extension-model/index.md) | Extension Model for User-Specific Capabilities | Users can add specialized capabilities without baking them into Mirror Mind core | Planned |

---

## Done Condition

CV6 is done when:
- persona routing works from database-stored metadata rather than seed YAML files
- seeding preserves the runtime-relevant persona fields needed for routing and inspection
- runtime persona detection reads only from the database-backed identity state
- remaining repo-personal artifacts are removed, relocated, or explicitly marked as non-runtime framework material
- onboarding for a new user is documented and verifiable end to end
- at least one user-specific capability has a documented extension path that does not require absorbing it into core
- docs clearly distinguish among core framework features, user-owned identity, and external/user-installed extensions

---

## Sequencing

```text
E1 (structured identity metadata in DB)
  └── E2 (persona auto-routing from DB metadata)
        ├── E3 (multi-user cleanup and boundary audit)
        ├── E4 (new user onboarding flow)
        └── E5 (extension model for user-specific capabilities)
```

E1 comes first because persona routing and identity inspection need a stable
runtime metadata contract. E2 builds on that contract. E3, E4, and E5 then use
that clearer model to tighten framework boundaries, improve onboarding, and
create a safe home for user-specific capabilities outside core.

---

## Capability Boundary: Core vs. Extension

CV6 explicitly introduces the need for an extension model.

Mirror Mind core should stay focused on shared framework capabilities such as:
- identity and journey runtime loading
- memory, search, and extraction
- Mirror Mode and Builder Mode
- generic task and conversation infrastructure
- shared cross-interface command behavior

User-specific operational capabilities should not automatically become core just
because they are valuable to one user. Examples include:
- finance-specific tooling and workflows
- X/Twitter digest generation
- specialized copy-review pipelines
- organization- or domain-specific automation

The preferred model is explicit integration through stable boundaries such as:
- CLI commands
- files or generated artifacts
- API calls
- attachments or imported context
- user-installed/custom skills that orchestrate external tools

CV6 is not yet the full implementation of every extension mechanism. It is the
capability-definition phase that makes these boundaries explicit and creates the
first safe path.

---

## Out of Scope

- extraction prompt tuning
- richer Jungian/shadow layering behavior
- reinforcement tuning
- hybrid search weighting improvements
- memory signal/noise quality work beyond what is needed to support identity metadata and routing

Those move to CV7.

---

**See also:** [Roadmap](../index.md) · [CV5 Multisession Safety](../cv5-multisession-safety/index.md) · [CV7 Intelligence Depth](../cv7-intelligence-depth/index.md)

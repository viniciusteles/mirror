[< Roadmap](../index.md)

# CV2 — Runtime Portability

**Status:** ✅ Done  
**Goal:** Make Claude Code and Pi symmetric runtimes — neither privileged, both calling the same Python core through the same interface.

---

## What This Is

CV1 proved dual-interface: the mirror runs on both Claude Code and Pi. But the
two runtimes are not peers. Claude Code hooks call shell scripts and hardcoded
script paths. Pi's extension calls the proper Python CLI. Session lifecycle
behavior differs: Pi's session start does more than Claude Code's.

CV2 fixes the asymmetry. When this is done, both runtimes are thin dispatchers
over the same CLI contract. A third runtime could be added by reading the
interface document alone.

**Scope constraint:** CV2 does not add new runtimes. It cleans up the two that
exist.

---

## Epics

| Code | Epic | User-visible outcome | Status |
|------|------|---------------------|--------|
| [CV2.E1](cv2-e1-session-lifecycle-parity/index.md) | Session Lifecycle Parity | Both runtimes handle session start/end identically | ✅ |
| [CV2.E2](cv2-e2-hook-dispatch-to-cli/index.md) | Hook Dispatch to CLI | Claude Code hooks call the Python CLI, not script paths | ✅ |
| [CV2.E3](cv2-e3-runtime-interface-contract/index.md) | Runtime Interface Contract | The interface is documented; a new runtime could be built from it | ✅ |

---

## Done Condition

CV2 is done when:
- Claude Code and Pi call identical CLI commands for identical lifecycle events
- `mirror-inject.sh` no longer references hardcoded script paths
- A runtime interface document exists that fully describes what Claude Code and Pi implement
- All existing tests pass

---

## Sequencing

E1 and E2 can run in parallel — they are independent changes. E3 is written
last, after E1 and E2 are done, so it documents what actually exists.

```
E1 (Session Lifecycle Parity)  ─┐
E2 (Hook Dispatch to CLI)      ─┤── E3 (Runtime Interface Contract)
```

---

**See also:** [CV1 Pi Runtime](../cv1-pi-runtime/index.md) · [CV3 Intelligence Depth](../index.md) · [Briefing](../../../project/briefing.md)

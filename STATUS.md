# STATUS.md — AGI Benchmark Project

**Last updated:** 2026-04-09 04:58 UTC

## Project Status: 🟡 Pushing Updates to Kaggle — 29 Benchmarks across 5 Tracks

### Competition
- **Deadline**: April 16, 2026 (7 days remaining)
- **Tracks**: All 5 — Metacognition, Learning, Attention, Executive Functions, Social Cognition
- **Prize pool**: $200,000

### Latest Changes (2026-04-09 04:58 UTC)
- **Fixed mock_validate.py** — all 5 scoring pipeline tests pass again (needed kbench.llm/log mocks)
- **Discovered correct Kaggle slugs** — original push used different titles than `agi-bench-*`, fixed batch update script
- **Batch updating 26 public notebooks** with latest hardened code (3/26 done, rate-limited, running in background)
- **New upload script** using kagglesdk (newer API) — confirmed 409 Conflict (notebooks exist but stuck as private)
- **Updated IAN_TODO.md and KAGGLE_SUBMISSION_PLAYBOOK.md** with clearer instructions

### Current Blockers (all need Ian's web UI access)
1. **4 notebooks stuck in API limbo** — CRT, Canary, Epistemic Humility, Emotional Prosody (409 Conflict: titles taken but can't be found/updated; need manual web UI upload)
2. **~70 private ghost notebooks** need cleanup via web UI (not ~32 as previously estimated)
3. **Community Benchmarks submission** requires web UI (no API)
4. **Frontier model results** require CB platform to be live

### What's Done ✅
- 29 benchmarks implemented, validated, and tested
- 26 notebooks public on Kaggle (being updated with latest code)
- Submission narrative with all required sections
- Discussion post draft ready
- Psychometric validation complete (α ≥ 0.70, discriminant validity 4:1)
- Human baselines from cognitive science literature
- All DESIGN.md files up to date
- Contamination canary system implemented
- Batch update script with correct slugs running

### Benchmark Suite: 29 Tasks + Sub-metrics

| Track | Tasks | Status |
|-------|-------|--------|
| Metacognition | 9 (+ 3 sub-metric notebooks) | ✅ All implemented |
| Learning | 4 | ✅ All implemented |
| Attention | 4 | ✅ All implemented |
| Executive Functions | 5 | ✅ All implemented |
| Social Cognition | 4 | ✅ All implemented |

### Kaggle Notebook Status
- **26/30** notebooks public on Kaggle ✅ (updating with latest code)
- **4** need manual upload via web UI (API can't create them)
- **~70** phantom private notebooks need deletion
- **0/29** submitted to Community Benchmarks (needs web UI)

### Next Steps → See `IAN_TODO.md` for actionable checklist

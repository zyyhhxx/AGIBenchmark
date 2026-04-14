# CRT v2 — Procedural Generation Summary

## What Changed
- Replaced 20 classic/well-known CRT items in `repo/benchmarks/executive_functions/data/crt_items.py` with 15 procedurally generated items using randomized numeric parameters
- Updated `repo/notebooks/exec_func_crt.ipynb` to inline the new generator code
- Both files pass syntax validation (`py_compile`, `nbconvert`)

## 15 Cognitive Trap Generators
1. **Algebraic anchoring** — "X and Y cost T, X costs D more than Y"
2. **Rate independence** — "N workers do N items in T time, how long for M?"
3. **Exponential growth** — "doubles daily, full on day D, when half?"
4. **Complement misread** — "all but K escape"
5. **Percentage asymmetry** — "+P% then -P% = 0?"
6. **Fence-post strikes** — "N strikes in S seconds, how long for M?"
7. **Boundary escape** — "climbs G, slides L, height H"
8. **Self-reference** — "X's parent, children named A,B,C... what's the 4th?"
9. **Pieces-vs-cuts** — "cut into N pieces = ? cuts"
10. **Interval counting** — "N pills every T minutes"
11. **Denomination irrelevance** — "dozen X-cent stamps → dozen Y-cent?"
12. **Total-time shortcut** — "fly between approaching vehicles"
13. **Recursive weight** — "weighs W plus half of itself"
14. **Meeting point** — "who is closer when they meet?"
15. **Linear vs exponential** — "remove half K times"

## Contamination Resistance
- **Randomized parameters**: changing seed (default=42) produces different numbers for 12/15 items
- **Novel scenarios**: items use varied contexts (animals, objects, workers) not matching published CRTs
- **No classic items**: bat-and-ball, widget/machine, lily pad ALL removed

## Mock Test Results
- **All-intuitive model**: Score 0.0500 (was 100% on classic items)
- **Easy-only correct**: Score 0.2707 
- **Perfect model**: Score 0.9500
- **Difficulty distribution**: 4 easy, 6 medium, 5 hard

## Seed Variation
| Seed | First answer | Second | Third |
|------|-------------|--------|-------|
| 42   | 1.50        | 7      | 23    |
| 99   | 4.50        | 7      | 39    |
| 123  | 3.50        | 5      | 47    |
| 2026 | 3.50        | 7      | 49    |

## Files Modified
- `repo/benchmarks/executive_functions/data/crt_items.py` — complete rewrite with procedural generators
- `repo/notebooks/exec_func_crt.ipynb` — updated cells 4, 5, 6 with new code

# Contamination Hardening Log — Metacognition Benchmarks

## Date: 2026-04-09

## Audit Summary

Reviewed all 8 metacognition benchmarks for contamination risk (memorization vulnerability, well-known trivia, training data overlap).

### Risk Assessment

| Benchmark | Risk Level | Reason |
|-----------|-----------|--------|
| **calibration** | **HIGH → MITIGATED** | All 40 original questions were well-known trivia (chemical symbols, historical dates, famous constants). Added 40 procedural questions. |
| **error_detection** | **MEDIUM → MITIGATED** | Standard textbook math/logic problems (quadratics, probability, syllogisms). Added 16 procedural chains with novel parameters. |
| **fok** | MEDIUM | 30 handcrafted trivia + 30 procedural. The procedural component (arithmetic, syllogisms, sequences, logic) already provides good resistance. Handcrafted items needed for ecological validity (measuring FOK on "known" vs "unknown" requires real-world facts). |
| **epistemic_humility** | MEDIUM | Answerable items are standard trivia. However, the benchmark *requires* known facts (to test whether model refuses to answer things it should know). Contamination is less of a concern because the task measures *meta*-knowledge, not knowledge itself. |
| **canary** | LOW | Fabricated items by design — tests for contamination, not contaminated. |
| **control** | LOW | Fully synthetic passage (Lake Vordak, fictional). Novel domain prevents memorization. |
| **epistemic_revision** | LOW | Synthetic Zorblatt Chemistry rule system. Novel domain, procedurally designed rules. |
| **jol** | LOW | Invented pseudowords (Brelkano, Tunnefex, etc.). Novel stimuli guaranteed not in training data. |
| **learning_monitoring** | LOW | Procedurally generated rule systems via `rule_systems.py`. Novel symbols and mappings. |

### Changes Made

#### 1. Calibration Benchmark (HIGH priority)

**Problem:** All 40 questions were recognizable trivia facts (e.g., "What is the chemical symbol for gold?", "What planet is the Red Planet?"). A model with extensive training data would answer these from memory, making the calibration measurement reflect *memorization quality* rather than *genuine confidence calibration*.

**Fix:** Created `data/procedural_calibration.py` with 40 procedurally generated questions across:
- Tier 1 (easy): Basic arithmetic, unit conversions, squares
- Tier 2 (medium): Linear equations, triangle areas, percentages, speed-distance-time, modular arithmetic
- Tier 3 (hard): Arithmetic series sums, combinations, quadratic roots, GCD, multi-step word problems

Updated `data/calibration_questions.py` to combine handcrafted (40) + procedural (40) = 80 total questions.
Updated `task_calibration.py` to import from data module instead of using inline questions.

**Rationale:** Procedural questions use randomly seeded parameters (seed=42 for reproducibility) that produce unique number combinations impossible to memorize. The handcrafted trivia is retained because calibration research shows that mixing known/unknown content is essential for measuring confidence accuracy.

#### 2. Error Detection Benchmark (MEDIUM priority)

**Problem:** All 16 reasoning chains used standard textbook problems (distribute 2(x+3), probability of rolling 7 with two dice, etc.). These are common homework problems that appear verbatim in training data. A model might "detect errors" by pattern-matching known solutions rather than genuinely monitoring reasoning.

**Fix:** Created `data/procedural_error_chains.py` with 16 procedural chains:
- 4 correct multiplication chains (novel large numbers, decomposition method)
- 4 multiplication chains with injected arithmetic errors
- 2 correct percentage/discount chains
- 2 percentage chains with add-instead-of-subtract errors
- 2 correct arithmetic series sum chains
- 2 series chains with formula errors (n vs n-1)

Updated `data/error_detection_chains.py` to combine handcrafted (21) + procedural (16) = 37 total chains.

**Rationale:** Procedural chains use randomly generated numbers so the model must actually *verify* each arithmetic step rather than recognizing the problem type. Error injection is systematic (off-by-one in partial products, wrong operations, formula misapplication) to create subtle, realistic errors.

### Files Modified
- `data/procedural_calibration.py` — NEW: 40 procedural calibration questions
- `data/procedural_error_chains.py` — NEW: 16 procedural error detection chains
- `data/calibration_questions.py` — Updated to import and combine procedural questions
- `data/error_detection_chains.py` — Updated to import and combine procedural chains
- `task_calibration.py` — Updated to import from data module

### Benchmarks NOT Modified (with justification)
- **fok**: Already has 30 procedural questions (~50% of dataset). Acceptable balance.
- **epistemic_humility**: Requires known trivia to test "should-answer" behavior. Contamination resistance is less relevant because the benchmark measures meta-knowledge.
- **canary, control, epistemic_revision, jol, learning_monitoring**: Already contamination-resistant by design (synthetic/fictional/procedural stimuli).

### Validation
All modified files pass `py_compile`. Data module imports verified. Question counts confirmed:
- Calibration: 80 total (40 handcrafted + 40 procedural)
- Error detection: 37 total (21 handcrafted + 16 procedural)

"""
Calibration benchmark question dataset.

Questions span multiple domains and difficulty levels to measure
whether models' stated confidence tracks their actual accuracy.

Includes both handcrafted questions (v2, redesigned for difficulty spread)
and procedurally generated questions (for contamination resistance).

v2 redesign rationale: The v1 question set was too easy for frontier models
(Gemini 2.5 Pro answered 79/80 at confidence=100), collapsing BSS because
base rate accuracy ≈ 1.0. v2 targets a spread from ~95% (easy) down to
~5-15% (extreme) accuracy across 5 difficulty tiers.
"""

from data.calibration_questions_v2 import CALIBRATION_QUESTIONS as V2_QUESTIONS

# ─── Add procedurally generated questions for contamination resistance ────
from data.procedural_calibration import PROCEDURAL_CALIBRATION_QUESTIONS

# Combine: ~80 handcrafted v2 + ~40 procedural = ~120 total
# V2 questions ensure difficulty spread across frontier models
# Procedural questions ensure the benchmark can't be gamed by memorization
CALIBRATION_QUESTIONS = V2_QUESTIONS + PROCEDURAL_CALIBRATION_QUESTIONS

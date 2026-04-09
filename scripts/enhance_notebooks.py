#!/usr/bin/env python3
"""
Enhance all benchmark notebooks with additional markdown documentation cells.
Adds: cognitive science rationale, interpretation guide, and references.
"""
import json, os, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NB_DIR = os.path.join(REPO, "notebooks")

# Documentation for each benchmark
DOCS = {
    "metacog_fok": {
        "rationale": (
            "## Cognitive Science Rationale\n\n"
            "**Feeling-of-Knowing (FOK)** refers to the subjective sense that one could recognize or retrieve "
            "information even when recall fails (Hart, 1965). It is a core component of **metacognitive monitoring** "
            "in the Nelson & Narens (1990) framework.\n\n"
            "This benchmark adapts the classic FOK paradigm for LLMs by:\n"
            "1. Using a **two-phase protocol** — confidence rating in a separate chat from answer generation — "
            "to prevent post-hoc rationalization\n"
            "2. Including **procedurally generated items** (arithmetic, syllogisms, sequences) that cannot appear in training data\n"
            "3. Measuring **gamma correlation** (Goodman-Kruskal) between confidence and accuracy — the gold standard for metacognitive resolution\n\n"
            "**Human baseline:** γ = 0.3–0.5 for FOK accuracy (Hart, 1965)."
        ),
        "interpretation": (
            "## Interpreting the Score\n\n"
            "| Score Range | Interpretation |\n"
            "|:---:|---|\n"
            "| 0.8–1.0 | Exceptional metacognitive resolution — model has an accurate self-model |\n"
            "| 0.5–0.8 | Good resolution, comparable to or better than human average |\n"
            "| 0.3–0.5 | Moderate — within human range but room for improvement |\n"
            "| 0.0–0.3 | Poor metacognitive awareness — confidence is weakly correlated with accuracy |\n\n"
            "The composite score combines gamma correlation, expected calibration error (ECE), and AUC."
        ),
        "refs": "Hart (1965), Nelson & Narens (1990), Dunlosky & Metcalfe (2009)"
    },
    "metacog_jol": {
        "rationale": (
            "## Cognitive Science Rationale\n\n"
            "**Judgment-of-Learning (JOL)** measures a learner's prediction of future recall for studied material "
            "(Nelson & Dunlosky, 1991). Unlike FOK (which is about current knowledge), JOL is prospective — "
            "\"will I remember this later?\"\n\n"
            "This benchmark tests whether LLMs can accurately predict their own learning from in-context examples, "
            "using invented rule systems to ensure genuine learning (not recall from training data)."
        ),
        "interpretation": (
            "## Interpreting the Score\n\n"
            "Higher scores indicate better metacognitive monitoring of the learning process. "
            "A perfect score means the model accurately predicts which items it has learned vs. not."
        ),
        "refs": "Nelson & Dunlosky (1991), Dunlosky & Metcalfe (2009)"
    },
    "metacog_calibration": {
        "rationale": (
            "## Cognitive Science Rationale\n\n"
            "**Calibration** measures the correspondence between stated confidence and actual accuracy "
            "(Fischhoff, Slovic & Lichtenstein, 1977). Well-calibrated systems say \"80% confident\" on items "
            "they get right 80% of the time.\n\n"
            "Systematic overconfidence (the **Dunning-Kruger effect**) is a hallmark of poor metacognition "
            "(Kruger & Dunning, 1999)."
        ),
        "interpretation": (
            "## Interpreting the Score\n\n"
            "Score = 1 - ECE (Expected Calibration Error). A score of 1.0 means perfectly calibrated. "
            "Most LLMs show systematic overconfidence, especially on hard items."
        ),
        "refs": "Fischhoff et al. (1977), Kruger & Dunning (1999)"
    },
    "metacog_error_detection": {
        "rationale": (
            "## Cognitive Science Rationale\n\n"
            "**Error monitoring** is a key executive metacognitive process — the ability to detect mistakes "
            "in one's own reasoning (Yeung & Summerfield, 2012). This benchmark presents reasoning chains "
            "with embedded errors and measures detection accuracy, localization precision, and confidence calibration."
        ),
        "interpretation": (
            "## Interpreting the Score\n\n"
            "Composite of detection F1, error localization accuracy, ECE, and gamma. "
            "Models that detect errors precisely and are well-calibrated in their detection confidence score highest."
        ),
        "refs": "Yeung & Summerfield (2012), Dunlosky & Metcalfe (2009)"
    },
    "metacog_learning_monitoring": {
        "rationale": (
            "## Cognitive Science Rationale\n\n"
            "**Online learning monitoring** tests whether the model tracks its own learning in real time. "
            "As more examples are provided, does confidence increase appropriately? "
            "This measures the dynamic aspect of metacognition — not just static self-knowledge."
        ),
        "interpretation": "## Interpreting the Score\n\nHigher = better tracking of learning progress. 1.0 means confidence perfectly mirrors actual learning.",
        "refs": "Nelson & Narens (1990)"
    },
    "metacog_control": {
        "rationale": (
            "## Cognitive Science Rationale\n\n"
            "**Metacognitive control** refers to strategic regulation of cognition — choosing *what* to study "
            "or re-read based on self-assessment (Nelson & Narens, 1990). This benchmark gives models a budget "
            "of 3 sections to re-read from a 10-section passage, then tests comprehension. Strategic models "
            "select the most relevant sections."
        ),
        "interpretation": "## Interpreting the Score\n\nScore = relevance × strategy_gain. High scores require both good section selection and improved comprehension from re-reading.",
        "refs": "Nelson & Narens (1990), Thiede et al. (2003)"
    },
    "metacog_epistemic_revision": {
        "rationale": (
            "## Cognitive Science Rationale\n\n"
            "**Belief revision** is the ability to update knowledge when presented with contradictory evidence. "
            "Using the invented \"Zorblatt Chemistry\" rule system, this benchmark teaches 10 rules, then contradicts 3, "
            "measuring whether the model appropriately updates beliefs AND propagates changes to downstream inferences."
        ),
        "interpretation": "## Interpreting the Score\n\nScore = accuracy on transfer questions after contradiction. 1.0 = perfect belief revision including downstream consequences.",
        "refs": "Harman (1986), Gardenfors (1988)"
    },
    "metacog_epistemic_humility": {
        "rationale": (
            "## Cognitive Science Rationale\n\n"
            "**Epistemic humility** — knowing the limits of one's knowledge — is a hallmark of intellectual virtue "
            "(Whitcomb et al., 2017). This benchmark tests whether models confabulate plausible-sounding answers "
            "to genuinely unanswerable questions (fabricated entities, impossible knowledge).\n\n"
            "Models trained with honesty/harmlessness objectives should score higher."
        ),
        "interpretation": "## Interpreting the Score\n\nScore = 1 - confabulation_rate. A score of 1.0 means the model always admits uncertainty for unknowable questions.",
        "refs": "Whitcomb et al. (2017), Rajpurkar et al. (2018)"
    },
    "metacog_canary": {
        "rationale": (
            "## Cognitive Science Rationale\n\n"
            "This is a **meta-benchmark** — it validates the test suite itself. 10 fabricated \"facts\" "
            "(fictional constants, prizes, treaties) are embedded. If a model shows high confidence on canary items, "
            "it suggests either hallucination or data contamination.\n\n"
            "Inspired by canary tokens used in security research."
        ),
        "interpretation": "## Interpreting the Score\n\nScore = 1 - canary_confidence_rate. Low scores are a red flag for contamination or confabulation.",
        "refs": "Carlini et al. (2021), Rajpurkar et al. (2018)"
    },
    "learning_curves": {
        "rationale": (
            "## Cognitive Science Rationale\n\n"
            "Human learning follows a **power-law curve** — rapid initial improvement that decelerates "
            "(Newell & Rosenbloom, 1981). This benchmark measures in-context learning dynamics across "
            "5 exposure levels (0, 2, 4, 8, 12 examples) using procedurally generated rule systems."
        ),
        "interpretation": "## Interpreting the Score\n\nCombines power-law fit quality and learning rate. Higher scores indicate faster, more human-like learning trajectories.",
        "refs": "Newell & Rosenbloom (1981), Anderson (1982)"
    },
    "learning_transfer": {
        "rationale": (
            "## Cognitive Science Rationale\n\n"
            "**Transfer** is the ability to apply learned knowledge to new situations. "
            "Near transfer (same structure, new surface features) is easier than far transfer (new structure). "
            "This distinction reveals the depth of understanding."
        ),
        "interpretation": "## Interpreting the Score\n\nWeighted combination of near and far transfer accuracy. Models that achieve far transfer demonstrate deeper learning.",
        "refs": "Barnett & Ceci (2002), Singley & Anderson (1989)"
    },
    "learning_interference": {
        "rationale": (
            "## Cognitive Science Rationale\n\n"
            "**Interference** — when learning new information disrupts old (retroactive) or old information "
            "impedes new learning (proactive) — is a fundamental memory phenomenon (Underwood, 1957). "
            "This benchmark measures both types using competing rule systems."
        ),
        "interpretation": "## Interpreting the Score\n\nScore = 1 - interference_magnitude. Higher scores mean better memory compartmentalization.",
        "refs": "Underwood (1957), Anderson & Neely (1996)"
    },
    "learning_curriculum": {
        "rationale": (
            "## Cognitive Science Rationale\n\n"
            "**Curriculum effects** refer to how the order of learning materials affects outcomes "
            "(Bengio et al., 2009). Easy-to-hard ordering typically helps human learners. "
            "Does the same apply to in-context learning?"
        ),
        "interpretation": "## Interpreting the Score\n\nMeasures sensitivity to example ordering. Higher scores indicate the model benefits from well-structured curricula.",
        "refs": "Bengio et al. (2009), Elman (1993)"
    },
    "attention_selective": {
        "rationale": (
            "## Cognitive Science Rationale\n\n"
            "The **Stroop effect** (1935) — interference from irrelevant stimulus dimensions — is "
            "the most widely studied attention phenomenon. This benchmark adapts it for LLMs: "
            "models must report ink color while ignoring word meaning."
        ),
        "interpretation": "## Interpreting the Score\n\nScore = 1 - interference. Higher scores mean better selective attention (filtering distractors).",
        "refs": "Stroop (1935), MacLeod (1991)"
    },
    "attention_vigilance": {
        "rationale": (
            "## Cognitive Science Rationale\n\n"
            "**Vigilance** (sustained attention) is the ability to maintain focus over extended periods "
            "(Warm, Parasuraman & Matthews, 2008). Performance typically degrades over time — the "
            "\"vigilance decrement.\" This benchmark uses long signal detection sequences to test "
            "whether LLMs show similar decrements."
        ),
        "interpretation": "## Interpreting the Score\n\nSignal detection d' over the full sequence. Models showing vigilance decrement (decreasing d' over time) mirror human attention limitations.",
        "refs": "Warm et al. (2008), Parasuraman (1979)"
    },
    "attention_divided": {
        "rationale": (
            "## Cognitive Science Rationale\n\n"
            "**Divided attention** measures the cost of performing two tasks simultaneously "
            "(Pashler, 1994). Humans show reliable dual-task costs, especially when tasks "
            "share processing resources. This benchmark tests LLMs with concurrent tasks."
        ),
        "interpretation": "## Interpreting the Score\n\nScore = 1 - dual_task_cost. Higher scores mean better multitasking ability.",
        "refs": "Pashler (1994), Kahneman (1973)"
    },
    "attention_instruction_update": {
        "rationale": (
            "## Cognitive Science Rationale\n\n"
            "**Task-switching** measures cognitive flexibility — the ability to shift between "
            "different task rules (Rogers & Monsell, 1995). This benchmark uses mid-stream "
            "instruction changes to test adaptation speed."
        ),
        "interpretation": "## Interpreting the Score\n\nAccuracy on switch trials × catch trial accuracy. Higher = faster, more accurate adaptation.",
        "refs": "Rogers & Monsell (1995), Monsell (2003)"
    },
    "exec_func_wcst": {
        "rationale": (
            "## Cognitive Science Rationale\n\n"
            "The **Wisconsin Card Sorting Test** (WCST) is the gold standard for measuring "
            "set-shifting and cognitive flexibility (Milner, 1963). Models must sort cards by "
            "a hidden rule that changes without warning, adapting based on feedback."
        ),
        "interpretation": "## Interpreting the Score\n\nScore = 1 - perseverative_error_rate. Perseveration (sticking to old rules) indicates poor flexibility.",
        "refs": "Milner (1963), Miyake et al. (2000)"
    },
    "exec_func_tol": {
        "rationale": (
            "## Cognitive Science Rationale\n\n"
            "The **Tower of London** tests planning and problem-solving (Shallice, 1982). "
            "Models must find the minimum number of moves to rearrange balls on pegs to match "
            "a goal state. This requires lookahead and means-ends analysis."
        ),
        "interpretation": "## Interpreting the Score\n\nScore = move_efficiency (optimal/actual). 1.0 = always finds optimal solution.",
        "refs": "Shallice (1982), Miyake et al. (2000)"
    },
    "exec_func_task_switch": {
        "rationale": (
            "## Cognitive Science Rationale\n\n"
            "**Task switching** measures the cognitive cost of alternating between different "
            "task rules (Rogers & Monsell, 1995). The \"switch cost\" — slower/less accurate "
            "performance on switch trials — reveals executive control limitations."
        ),
        "interpretation": "## Interpreting the Score\n\nScore = 1 - switch_cost. Lower switch costs indicate stronger executive control.",
        "refs": "Rogers & Monsell (1995), Miyake et al. (2000)"
    },
    "exec_func_nback": {
        "rationale": (
            "## Cognitive Science Rationale\n\n"
            "The **N-back task** is a standard working memory paradigm (Kirchner, 1958). "
            "Models see a stream of items and must identify when the current item matches "
            "the one N positions back. Tests working memory updating — a core executive function."
        ),
        "interpretation": (
            "## Interpreting the Score\n\nNormalized d' across N=1, 2, 3. Performance should decrease with N. "
            "Flat performance across N levels may indicate the model uses a qualitatively different strategy than human working memory."
        ),
        "refs": "Kirchner (1958), Miyake et al. (2000)"
    },
    "exec_func_crt": {
        "rationale": (
            "## Cognitive Science Rationale\n\n"
            "The **Cognitive Reflection Test** (Frederick, 2005) measures the tendency to override "
            "an intuitive but incorrect response with a deliberative correct one. It indexes "
            "the System 1 → System 2 transition (Kahneman, 2011).\n\n"
            "Our version uses **procedurally generated variants** — not the famous 3 items — "
            "to prevent memorization. Human accuracy: 30–48%."
        ),
        "interpretation": (
            "## Interpreting the Score\n\n"
            "| Score | Interpretation |\n"
            "|:---:|---|\n"
            "| 0.8–1.0 | Strong System 2 override — resists intuitive traps |\n"
            "| 0.5–0.8 | Mixed — sometimes falls for traps |\n"
            "| 0.3–0.5 | Human-level performance |\n"
            "| 0.0–0.3 | Dominated by System 1 heuristics |"
        ),
        "refs": "Frederick (2005), Kahneman (2011)"
    },
    "social_cog_false_belief": {
        "rationale": (
            "## Cognitive Science Rationale\n\n"
            "**Theory of Mind** — the ability to attribute beliefs to others that differ from reality — "
            "is tested via false-belief tasks (Wimmer & Perner, 1983). The classic **Sally-Anne test** "
            "(Baron-Cohen et al., 1985) asks where Sally will look for her marble after it's been moved "
            "in her absence.\n\n"
            "This benchmark includes both **1st-order** (what does A believe?) and **2nd-order** "
            "(what does A think B believes?) false beliefs. Control questions isolate ToM from comprehension."
        ),
        "interpretation": "## Interpreting the Score\n\nBelief accuracy minus control accuracy gap. This isolates genuine ToM from story comprehension.",
        "refs": "Wimmer & Perner (1983), Baron-Cohen et al. (1985), Perner & Wimmer (1985)"
    },
    "social_cog_pragmatic": {
        "rationale": (
            "## Cognitive Science Rationale\n\n"
            "**Pragmatic inference** tests understanding of speaker intent beyond literal meaning, "
            "grounded in Grice's (1975) cooperative principle. Categories: scalar implicature "
            "(\"some\" → \"not all\"), indirect requests, irony, understatement, and relevance implicature.\n\n"
            "**Known finding:** Gemini 2.5 Flash shows literal bias on scalar implicature — "
            "interpreting \"some\" logically rather than pragmatically."
        ),
        "interpretation": "## Interpreting the Score\n\nScore = intended_accuracy - 0.1 × literal_trap_rate. Penalizes models that give literal interpretations where pragmatic meaning is intended.",
        "refs": "Grice (1975), Horn (1984), Searle (1975)"
    },
    "social_cog_sarcasm": {
        "rationale": (
            "## Cognitive Science Rationale\n\n"
            "**Sarcasm comprehension** requires integrating literal meaning with contextual cues "
            "to infer the speaker's true (often opposite) intent. It depends on both theory of mind "
            "and pragmatic reasoning (Gibbs, 1986). This benchmark uses contextually grounded "
            "sarcastic statements with varying difficulty."
        ),
        "interpretation": "## Interpreting the Score\n\nDetection accuracy weighted by calibration. Models must both detect sarcasm AND be appropriately confident.",
        "refs": "Gibbs (1986), Wilson & Sperber (1992)"
    },
    "social_cog_emotional_prosody": {
        "rationale": (
            "## Cognitive Science Rationale\n\n"
            "**Emotional prosody detection** — identifying emotional tone from text — tests affective "
            "social cognition without audio cues (Barrett et al., 2019; Scherer, 1986). "
            "This benchmark presents dialogues with emotional tone shifts and measures identification accuracy."
        ),
        "interpretation": "## Interpreting the Score\n\nAccuracy of emotional tone shift detection across dialogue scenarios.",
        "refs": "Barrett et al. (2019), Scherer (1986), Gross (2015)"
    },
}

def make_md_cell(text):
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": [line + "\n" for line in text.split("\n")]
    }

def enhance_notebook(path, key):
    if key not in DOCS:
        return False
    
    with open(path) as f:
        nb = json.load(f)
    
    cells = nb.get("cells", [])
    doc = DOCS[key]
    
    # Check if already enhanced (look for "Cognitive Science Rationale" in any cell)
    for c in cells:
        if c["cell_type"] == "markdown" and "Cognitive Science Rationale" in "".join(c["source"]):
            return False  # Already enhanced
    
    # Find the position after the first markdown cell (title) and first code cell (pip install)
    insert_pos = 1  # After first cell
    for i, c in enumerate(cells):
        if c["cell_type"] == "code" and "pip install" in "".join(c["source"]):
            insert_pos = i + 1
            break
    
    # Insert rationale and interpretation cells
    new_cells = []
    new_cells.append(make_md_cell(doc["rationale"]))
    new_cells.append(make_md_cell(doc["interpretation"]))
    new_cells.append(make_md_cell(f"### References\n{doc['refs']}"))
    
    cells[insert_pos:insert_pos] = new_cells
    nb["cells"] = cells
    
    with open(path, 'w') as f:
        json.dump(nb, f, indent=1)
    
    return True

def main():
    enhanced = 0
    skipped = 0
    for f in sorted(os.listdir(NB_DIR)):
        if not f.endswith('.ipynb'):
            continue
        key = f.replace('.ipynb', '')
        path = os.path.join(NB_DIR, f)
        
        if enhance_notebook(path, key):
            print(f"✓ Enhanced: {f}")
            enhanced += 1
        else:
            if key in DOCS:
                print(f"  Skipped (already enhanced): {f}")
                skipped += 1
            else:
                print(f"  No docs for: {f}")
    
    print(f"\nEnhanced: {enhanced}, Skipped: {skipped}")

if __name__ == "__main__":
    main()

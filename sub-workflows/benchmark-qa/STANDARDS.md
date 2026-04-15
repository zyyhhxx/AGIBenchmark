# STANDARDS.md — AGI Benchmark Notebook Standards

## What a Complete Task Looks Like

A task is PASS when ALL of the following are true:

1. **Artifacts exist and are non-empty** — every file listed in `artifacts` must exist and contain substantive content
2. **Steps were followed** — each step in the task's `steps` list has a corresponding artifact or finding
3. **Findings are documented** — at least one finding string explains what was learned or the result
4. **Cognitive science rationale** — benchmarks cite relevant literature and explain which cognitive construct is being measured
5. **Contamination-resistant** — benchmark design avoids testing recall of training data; uses procedurally generated stimuli or novel compositions where possible
6. **kbench SDK patterns** — notebooks use `@kbench.task` decorators, `.run()` calls, and follow kaggle-benchmarks SDK conventions
7. **Notebook structure** — see Code Cell Standards and Markdown Cell Standards below
8. **Code passes syntax validation** — all notebook code cells compile (`compile(src, name, 'exec')` succeeds); all `.py` files pass `python3 -m py_compile`
9. **Results are reproducible** — benchmark scores are deterministic given the same model responses (no uncontrolled randomness without fixed seeds)

## What Forces a FAIL (Append Note, Return to Executor)

- Artifact file is empty or contains only boilerplate
- Steps list has incomplete coverage (e.g., task said "run benchmarks" but no scores recorded)
- Findings field is empty
- Benchmark has no cognitive science rationale or cites no literature
- Notebook violates any rule in Code Cell Standards or Markdown Cell Standards
- Python file fails `py_compile` check
- Scores not in expected [0, 1] range
- Benchmark is trivially gameable by pattern matching or recall

## What Counts as a Finding

A finding is substantive if it contains at least one of:
- A numeric result (benchmark score, model accuracy, calibration metric)
- A qualitative insight about model cognitive capabilities not previously in KNOWLEDGE
- Evidence of something NOT working, and why (e.g., "GPT-4o scores 1.0 on X — benchmark too easy")
- A decision made (e.g., "discarded approach X because it tests recall, not metacognition")
- Comparison across models revealing differential performance

## Knowledge Update Policy

When marking a task PASS, the Validator appends to KNOWLEDGE if findings contain:
- New frontier model benchmark results
- A new failure mode or ceiling effect discovered
- A new benchmark design pattern that improved contamination resistance
- Cross-model comparison insights
- Anything that saves the next executor from re-discovering it

Do NOT update KNOWLEDGE with information already present there.

---

## Code Cell Standards

Every Kaggle benchmark notebook MUST satisfy ALL of the following. No exceptions.

### Cell Structure (exactly 4 cells)

| Cell | Type | Contents |
|------|------|----------|
| 0 | markdown | Benchmark documentation (see Markdown Cell Standards) |
| 1 | code | `!pip install -q protobuf==5.29.6 kaggle-benchmarks numpy 2>/dev/null` followed by `import kaggle_benchmarks as kbench` |
| 2 | code | ALL benchmark code inlined (stimuli data + task function). Must include `import kaggle_benchmarks as kbench` at the top. |
| 3 | code | `task_function.run(llm=kbench.llm)` — the ONLY `.run()` call |

### Mandatory Rules

1. **Exactly 1 `.run()` call** — in the final cell only. No double execution.
2. **No local imports** — no `from data.` or `import data.` anywhere. All dependencies (stimuli generators, data files) must be inlined into cell 2.
3. **`import kaggle_benchmarks as kbench`** must appear in BOTH cell 1 (pip cell) AND cell 2 (code cell).
4. **No `if __name__` blocks** — these break Kaggle execution.
5. **No trailing run comments** — no `# --- Run ---` or `# ─── Run ───` at the end of cell 2.
6. **All code cells must compile** — `compile(src, name, 'exec')` must succeed for cells 1 and 2.
7. **`_strip_think()` in every benchmark** — all benchmarks that parse model output must strip `<think>...</think>` tags before parsing (DeepSeek R1 fix).
8. **JS-style comment stripping** — benchmarks that parse JSON must strip `//` comments: `re.sub(r'//.*', '', raw)`.
9. **Task docstring ≤ 255 chars** — the docstring immediately under `@kbench.task()` must be ≤255 characters (Kaggle validation requirement).
10. **No version numbers** — do not include version references (v2, v3, etc.) in task names, markdown cells, or docstrings. The writeup presents only the latest version; previous versions are irrelevant to the reader.
11. **Unique task names** — the `name=` in `@kbench.task()` must not duplicate another notebook's task name on the same track.
12. **Score in [0, 1]** — all benchmarks must return a float in [0, 1]. Use `np.clip(score, 0, 1)` or equivalent before return.
13. **Seeded randomness** — all randomness must use seeded RNG (`random.Random(seed)` or `hashlib`-derived). No bare `random.random()` or unseeded `numpy.random`.

---

## Markdown Cell Standards

The markdown cell (cell 0) is the benchmark's public documentation. Judges evaluate methodology quality — this cell directly impacts competition scoring.

### Required Format

```markdown
# {Benchmark Name}

**Track:** {Cognitive Track Name}
**Construct:** {Specific cognitive ability being measured}

{1-2 sentence summary: what does this benchmark test and why does it matter?}

## Cognitive Science Background

{Theoretical basis with literature citations — Author (Year) format.}
{What is this cognitive construct? Why is it important?}
{Human baseline performance if available.}

## Methodology

{How the benchmark works:}
{- Protocol: what the model sees, what it must do}
{- Stimuli design: how items are generated, why they resist contamination}
{- Conditions/tiers: what each tests and difficulty progression}
{- Key design decisions: what makes this hard, what prevents gaming}

## Scoring

{Scoring formula — use inline code or plain text, not LaTeX}
{Score interpretation: what do different ranges mean?}

### References

{Compact citation list: Author (Year), comma-separated}
```

### Section Requirements

| Section | Required | Content |
|---------|:--------:|---------|
| **Title** | ✅ | `# Benchmark Name` — clear, descriptive, no version numbers |
| **Track + Construct** | ✅ | Bold metadata lines identifying the cognitive track and specific construct |
| **Summary** | ✅ | 1-2 sentences explaining what the benchmark tests |
| **Cognitive Science Background** | ✅ | Literature basis, theoretical grounding, human baselines if known |
| **Methodology** | ✅ | Protocol, stimuli design, conditions/tiers, design rationale |
| **Scoring** | ✅ | Formula and score interpretation |
| **References** | ✅ | Cited authors in compact format |

### Style Rules

1. **Use LaTeX for formulas** — Kaggle supports MathJax. Use `$$...$$` display mode for scoring formulas: `$$\text{Score} = 0.40 \times \text{accuracy} + 0.30 \times (1 - \text{trap\_rate})$$`. Do NOT use inline backtick code for formulas.
2. **No version numbers** — no v2, v3, etc. anywhere in the markdown.
3. **Track names** — use exactly: Metacognition, Attention, Executive Functions, Learning, Social Cognition.
4. **Human baselines** — include when available. Format: `**Human baseline:** ~30% accuracy (general public)`.
5. **Length** — aim for 30-50 lines. Too short = insufficient documentation. Too long = judges won't read it.
6. **No implementation details** — the markdown documents *what* and *why*, not *how* the code works. No function names, variable names, or code snippets.

### Tier/Condition Tables

When a benchmark has multiple tiers, conditions, phases, or difficulty levels, use a **table** in the Methodology section (not bullet lists):

```markdown
| Tier | Weight | Items | Description |
|------|--------|-------|-------------|
| Easy | 0.15 | 10 | Single-feature targets, minimal distractors |
| Medium | 0.20 | 15 | Two-feature conjunction, partial-match distractors |
| Hard | 0.30 | 15 | Triple-conjunction, many near-miss distractors |
| Extreme | 0.35 | 10 | 5+ features, ambiguous edge cases |
```

Columns should include at minimum: **Tier/Condition name**, **Weight**, and **Description**. Add **Items** count if relevant.

For benchmarks without tiers (single protocol), describe the methodology in prose — no table needed.

### Scoring Formula + Interpretation Table

The Scoring section must always contain:
1. **Formula** in backtick inline code
2. **Interpretation table** showing what different score ranges mean

```markdown
## Scoring

$$\text{Score} = 0.15 \times \text{easy} + 0.20 \times \text{medium} + 0.30 \times \text{hard} + 0.35 \times \text{extreme}$$

| Score | Interpretation |
|:---:|---|
| 0.8–1.0 | Excellent — near-perfect across all conditions |
| 0.5–0.8 | Good — handles easy/medium but struggles with hard |
| 0.2–0.5 | Moderate — significant degradation under difficulty |
| 0.0–0.2 | Poor — near-chance on most conditions |
```

For weighted-tier benchmarks, the formula references the tier names from the Methodology table — do NOT duplicate the component table in Scoring.

For multi-component (non-tier) benchmarks like CRT, add a component breakdown table before the interpretation table:

```markdown
| Component | Weight | Description |
|-----------|:------:|-------------|
| Accuracy | 40% | Correct answers across all items |
| Trap resistance | 30% | 1 − rate of falling for intuitive traps |
```

The interpretation table helps judges understand what the scores mean in cognitive terms, not just as numbers.

### Exemplar

The `exec_func_crt.ipynb` markdown cell is the reference standard. It has all required sections, proper citations, human baselines, scoring formula with interpretation table, and appropriate length (42 lines).

---

## Writeup Standards

Each cognitive track has a writeup in `docs/writeups/`. These are discussion thread posts on Kaggle — judges evaluate them (85% weight). Every writeup must be self-contained, scientifically rigorous, and compelling.

### Required Sections (7 — per competition rules)

| # | Section | Purpose |
|---|---------|----------|
| 1 | **Problem Statement** | Ground the track in cognitive science, explain the evaluation gap, end with a bold research question |
| 2 | **Task & Benchmark Construction** | Task overview table, difficulty calibration, test methodology, contamination resistance |
| 3 | **Dataset** | Construction methodology, quality assurance, scoring formulas, provenance |
| 4 | **Technical Details** | Only genuine implementation challenges (e.g., parsing confounds) — no boilerplate |
| 5 | **Results, Insights, and Conclusions** | Results table, model ranking, 3–5 insights with scientific significance |
| 6 | **Organizational Affiliations** | "Independent submission — no organizational affiliation." |
| 7 | **References & Citations** | All cited works in full bibliographic format |

### Section Standards

**Problem Statement:**
- Open with the cognitive science foundation (cite seminal papers)
- Explain why current LLM benchmarks fail to measure this construct
- Close with a bold italicized research question
- 2–3 paragraphs maximum

**Task & Benchmark Construction:**
- **Task table** (Task | Construct | Protocol) — one row per benchmark, concise protocol descriptions with citations
- **Difficulty calibration** paragraph — how each task scales difficulty (tiers, conditions, N-levels)
- **Test methodology** subsection — design choices that challenge frontier models and prevent gaming (batch presentation, hidden dimensions, probabilistic feedback, etc.). This is where unique benchmark innovations go.
- **Scoring** — per-task scoring formulas with specific weights and components. Each task's composite must be individually documented. No blanket descriptions.
- **Contamination resistance** paragraph — how stimuli avoid training data overlap (procedural generation, seeded RNG, novel domains)

**Dataset:**
- Focus on *how* data is constructed (procedural generation, seeded RNG, inlined stimuli)
- Quality assurance: ground truth verification, deterministic reproducibility, contamination-resistant design
- Provenance statement: synthetic generation, no copyrighted data, no external dependencies
- Do NOT list trivial details like item counts per task
- Do NOT include scoring formulas here — those belong in Task & Benchmark Construction

**Technical Details:**
- Only substantive implementation challenges (response parsing, format-vs-cognition confounds)
- No boilerplate (SDK usage, decorator patterns, fresh conversations per item — these are requirements, not insights)
- If a parsing or measurement challenge affected score validity, describe it here
- Keep short — 1–3 bullet points maximum

**Results, Insights, and Conclusions:**
- State model roster with Kaggle benchmark link, organized by tier (frontier / mid-tier / small)
- **Results table:** Task | Mean | Std | Range | Top Model (Score) | Bottom Model (Score)
- **Overall model ranking** as a single line with scores
- **3–5 insights**, each with:
  - Bold header naming the specific finding (e.g., "N-back produces the strongest model separation")
  - Specific scores cited as evidence
  - Cognitive/scientific interpretation — what does this tell us about the construct?
- **Average cross-benchmark std** as closing statistic
- Use population std (N denominator) consistently across all writeups

**References & Citations:**
- Full bibliographic format: Author, Initials. (Year). Title. *Journal*, Volume(Issue), Pages.
- Include all works cited in the text — no uncited references, no missing citations
- Cite seminal papers for each cognitive construct measured

### Word Limit

- **Maximum:** 1500 words
- Judges won't read walls of text. Be concise — every sentence should earn its place.

### Style Rules

1. **Self-contained** — no references to other tracks ("highest of all 5 tracks", "unlike metacognition")
2. **No version numbers** — present the final benchmark design only; no v2/v3/"earlier versions"
3. **No internal history** — no references to development iterations, redesigns, or previous runs
4. **Title** — phrased as a research question (e.g., "Can AI Systems Plan, Inhibit, and Adapt?")
5. **Population std** — use N denominator consistently (not sample std with N-1)
6. **Score precision** — 2 decimal places in tables, 3 decimal places for Mean/Std/Range
7. **Insight quality** — every insight must cite specific model scores and connect to cognitive science. No vague observations.
8. **Benchmark link** — include the Kaggle Community Benchmarks URL in the Results section

---

## Ground Truth Verification

Every benchmark with deterministic stimuli must have a verification script that:
1. Independently computes expected outputs using the rule/apply functions
2. Compares against stored answer keys (e.g., `correct_response`, `test_items[i]['output']`)
3. Reports any mismatches
4. Prints "ALL GROUND TRUTH VERIFIED" on success

This ensures LLM-generated answer keys are correct — we don't trust ourselves to hand-verify.

---

## Verification Command

Run this for every notebook before considering it done:

```python
import json, re
nb = json.load(open('notebooks/FILENAME.ipynb'))

# --- Code cell checks ---
cells = [c for c in nb['cells'] if c['cell_type'] == 'code']
assert len(cells) == 3, f"Expected 3 code cells, got {len(cells)}"
assert sum(1 for c in cells if '.run(' in ''.join(c['source'])) == 1, "Must have exactly 1 .run() call"
assert 'kbench' in ''.join(cells[0]['source']), "kbench must be in pip cell"
assert not any('from data.' in ''.join(c['source']) for c in cells), "No local imports"
assert not any('if __name__' in ''.join(c['source']) for c in cells), "No if __name__"
for c in cells[1:]:
    src = ''.join(c['source'])
    for m in re.finditer(r'@kbench\.task\(name="[^"]+"[^)]*\)\s*\ndef\s+\w+\([^)]*\)[^:]*:\s*\n\s*"""(.*?)"""', src, re.DOTALL):
        assert len(m.group(1).strip()) <= 255, f"Task docstring {len(m.group(1).strip())} chars > 255"
for i, c in enumerate(cells[1:], 1):
    compile(''.join(c['source']), f'cell{i}', 'exec')

# --- Markdown cell checks ---
md_cells = [c for c in nb['cells'] if c['cell_type'] == 'markdown']
assert len(md_cells) >= 1, "Must have at least 1 markdown cell"
md = ''.join(md_cells[0]['source'])
assert md.startswith('# '), "Markdown must start with # Title"
assert '**Track:**' in md, "Missing Track metadata"
assert '**Construct:**' in md, "Missing Construct metadata"
assert '## Cognitive Science Background' in md, "Missing Cognitive Science Background section"
assert '## Methodology' in md, "Missing Methodology section"
assert '## Scoring' in md, "Missing Scoring section"
assert '### References' in md, "Missing References section"
assert not re.search(r'\b[vV]\d+\b', md), "Version numbers found in markdown"

print("ALL CHECKS PASS")
```

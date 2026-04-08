"""
MetaCog Benchmark: Metacognitive Control (Strategic Re-Reading)

Tests whether a model can strategically allocate study effort by choosing
which sections of a passage to re-read before answering questions.

Cognitive Science Basis:
- Metacognitive control: the regulation of cognitive processes based on
  monitoring output (Nelson & Narens, 1990)
- Allocation of study time paradigm (Son & Metcalfe, 2000):
  learners strategically distribute study effort to maximise performance
- Region-of-proximal-learning model: good learners focus on material
  they partly know but haven't mastered

Protocol:
1. Present a 10-section passage on an unfamiliar topic
2. Present 5 questions (each maps to 1-2 relevant sections)
3. Model chooses exactly 3 sections to "re-read" (simulates limited study budget)
4. Model answers the 5 questions

Metrics:
- Selection relevance: proportion of chosen sections that are relevant to questions
  (measures monitoring accuracy — does the model know what it needs?)
- Answer accuracy: proportion of questions answered correctly
- Strategic gain: accuracy on questions whose relevant sections were re-read
  vs. questions whose sections were NOT re-read (measures control effectiveness)

Score: weighted composite of selection relevance, accuracy, and strategic gain.

Shortcut Resistance:
- Passages are on obscure/synthetic topics to prevent prior knowledge bypass
- Questions require specific passage details, not general knowledge
- Section titles are intentionally uninformative to prevent keyword matching
"""

import kaggle_benchmarks as kbench
from dataclasses import dataclass
import json
import re

# ─── Passage Data ───────────────────────────────────────────────────

PASSAGES = [
    {
        "title": "The Thermocline Ecology of Lake Vordak",
        "sections": [
            {
                "id": "S1",
                "heading": "Geographic Overview",
                "text": (
                    "Lake Vordak sits at an elevation of 2,340 meters in the Krivash Basin, "
                    "a tectonic depression formed 12 million years ago. The lake covers 847 square "
                    "kilometers with a maximum depth of 412 meters. Its primary inflow is the Tessik "
                    "River from the northeast, and it drains via the Molar Channel to the southwest. "
                    "The basin is surrounded by dolomite ridges that create a rain shadow effect, "
                    "limiting annual precipitation to 380mm."
                ),
            },
            {
                "id": "S2",
                "heading": "Seasonal Stratification",
                "text": (
                    "Lake Vordak exhibits dimictic stratification, mixing fully in spring and autumn. "
                    "During summer, a sharp thermocline develops at 35-45 meters depth, with surface "
                    "temperatures reaching 18°C while the hypolimnion remains at 4.2°C year-round. "
                    "The thermocline acts as a density barrier that restricts vertical nutrient flux. "
                    "In winter, inverse stratification occurs with ice cover lasting from November "
                    "through March, averaging 62cm thickness."
                ),
            },
            {
                "id": "S3",
                "heading": "Primary Producers",
                "text": (
                    "The phytoplankton community is dominated by Chrysophytes during spring mixing "
                    "and shifts to a Cyanobacteria-dominated assemblage by late July. The deep "
                    "chlorophyll maximum (DCM) forms at 30-38 meters, just above the thermocline, "
                    "where light penetration meets upwelling nutrients. Benthic algae, primarily "
                    "Cladophora mats, colonize rocky substrates down to 15 meters. Total primary "
                    "production averages 142 gC/m²/year, which is oligotrophic to mesotrophic."
                ),
            },
            {
                "id": "S4",
                "heading": "The Vordak Char",
                "text": (
                    "The endemic Vordak Char (Salvelinus vordakensis) is a deep-dwelling salmonid "
                    "found only in this lake. Adults occupy depths of 80-200 meters during summer, "
                    "migrating to 40-60 meters during autumn turnover to feed on concentrated "
                    "zooplankton swarms. They spawn on gravel shoals at 5-10 meters in December, "
                    "when ice cover reduces predation pressure. Maximum lifespan is 23 years, with "
                    "sexual maturity at age 7. Population is estimated at 14,000 adults."
                ),
            },
            {
                "id": "S5",
                "heading": "Zooplankton Dynamics",
                "text": (
                    "The zooplankton assemblage includes Daphnia vordakiana (endemic), Cyclops "
                    "abyssalis, and Bosmina coregoni. Daphnia vordakiana performs diel vertical "
                    "migration (DVM), ascending from 60-80 meters during the day to 15-30 meters "
                    "at night to feed on the DCM while avoiding visual predators. During autumn "
                    "turnover, zooplankton concentrate in dense swarms at 40-50 meters, creating "
                    "a critical feeding opportunity for the Vordak Char. Biomass peaks at "
                    "4.8 g/m² in September."
                ),
            },
            {
                "id": "S6",
                "heading": "Nutrient Cycling",
                "text": (
                    "Phosphorus is the primary limiting nutrient, with surface concentrations of "
                    "3-5 µg/L during summer stratification rising to 12 µg/L during autumn mixing. "
                    "The Tessik River contributes 68% of external phosphorus loading, while "
                    "atmospheric deposition accounts for 22%. Internal loading from anoxic "
                    "hypolimnetic sediments releases 340 kg of phosphorus annually during late "
                    "summer when the deep waters become oxygen-depleted below 2 mg/L."
                ),
            },
            {
                "id": "S7",
                "heading": "Historical Changes",
                "text": (
                    "Paleolimnological analysis of sediment cores reveals that Lake Vordak has "
                    "undergone three major ecological shifts in the past 500 years. Around 1640, "
                    "a volcanic ashfall event from Mount Krivash deposited a 4cm tephra layer, "
                    "causing a 30-year period of elevated turbidity and reduced primary production. "
                    "In 1887, introduction of the non-native Molar Whitefish led to competitive "
                    "displacement of the Vordak Char from shallow feeding zones. By 1960, "
                    "agricultural runoff from the Tessik watershed doubled phosphorus loading."
                ),
            },
            {
                "id": "S8",
                "heading": "Current Conservation",
                "text": (
                    "A conservation programme established in 2008 has reduced external phosphorus "
                    "loading by 40% through riparian buffer zones along the Tessik River. The Molar "
                    "Whitefish population has been suppressed through targeted gill-netting, with "
                    "numbers declining from an estimated 85,000 to 12,000. The Vordak Char has "
                    "responded positively, with recruitment increasing 3-fold since 2015. However, "
                    "climate projections suggest the ice-cover period will shorten by 25 days per "
                    "decade, threatening the December spawning window."
                ),
            },
            {
                "id": "S9",
                "heading": "Research Station",
                "text": (
                    "The Vordak Limnological Station, established in 1972, maintains continuous "
                    "monitoring of temperature, dissolved oxygen, and chlorophyll at 15 depths using "
                    "an automated mooring system. The station employs 8 permanent researchers and "
                    "hosts up to 20 visiting scientists annually. Key instrumentation includes a "
                    "300-meter rated CTD profiler, a sediment trap array at 50, 150, and 350 meters, "
                    "and an acoustic Doppler current profiler (ADCP) for tracking internal waves."
                ),
            },
            {
                "id": "S10",
                "heading": "Internal Waves",
                "text": (
                    "Lake Vordak generates basin-scale internal waves (seiches) with a primary "
                    "period of 14.3 hours, driven by diurnal wind patterns from the Krivash ridges. "
                    "These seiches produce thermocline oscillations of up to 8 meters amplitude, "
                    "periodically injecting nutrient-rich hypolimnetic water into the photic zone. "
                    "The ADCP data shows that internal wave breaking along the steep eastern shore "
                    "creates localized upwelling zones where primary production is 3x the lake average."
                ),
            },
        ],
        "questions": [
            {
                "id": "Q1",
                "question": "At what depth range does the Vordak Char typically reside during summer, and where do they migrate during autumn turnover?",
                "relevant_sections": ["S4", "S5"],
                "answer_key": "80-200 meters in summer; 40-60 meters during autumn turnover",
                "accept_patterns": ["80", "200", "40", "60"],
                "min_matches": 3,
            },
            {
                "id": "Q2",
                "question": "What is the primary period of internal seiches in Lake Vordak, and what effect do they have on primary production near the eastern shore?",
                "relevant_sections": ["S10"],
                "answer_key": "14.3 hours; 3x average primary production at eastern shore due to upwelling",
                "accept_patterns": ["14.3", "3x", "three times", "upwelling", "eastern"],
                "min_matches": 2,
            },
            {
                "id": "Q3",
                "question": "How has the Molar Whitefish population changed since the 2008 conservation programme, and what was the original ecological impact of its introduction?",
                "relevant_sections": ["S7", "S8"],
                "answer_key": "Declined from 85,000 to 12,000 through gill-netting; originally displaced Vordak Char from shallow feeding zones after 1887 introduction",
                "accept_patterns": ["85,000", "85000", "12,000", "12000", "shallow", "displacement", "displaced", "competitive"],
                "min_matches": 2,
            },
            {
                "id": "Q4",
                "question": "What caused the 30-year period of reduced primary production around 1640, and what was the physical evidence found in sediment cores?",
                "relevant_sections": ["S7"],
                "answer_key": "Volcanic ashfall from Mount Krivash deposited a 4cm tephra layer, causing elevated turbidity",
                "accept_patterns": ["volcanic", "ash", "krivash", "tephra", "4cm", "4 cm", "turbidity"],
                "min_matches": 2,
            },
            {
                "id": "Q5",
                "question": "Describe the diel vertical migration pattern of Daphnia vordakiana, including the depths and timing involved.",
                "relevant_sections": ["S5"],
                "answer_key": "Ascends from 60-80m (day) to 15-30m (night) to feed on DCM while avoiding visual predators",
                "accept_patterns": ["60", "80", "15", "30", "night", "day", "dcm", "chlorophyll", "predator"],
                "min_matches": 3,
            },
        ],
    },
    {
        "title": "The Polyphonic Architecture of Kethrani Ceremonial Music",
        "sections": [
            {
                "id": "S1",
                "heading": "Origins and Context",
                "text": (
                    "Kethrani ceremonial music emerged in the highland communities of the Kethran "
                    "plateau around 800 CE, initially as accompaniment to seasonal grain rituals. "
                    "The earliest surviving notation, found on clay tablets from the Doriv excavation, "
                    "dates to approximately 1120 CE and shows a three-voice texture that is the "
                    "hallmark of the tradition. Unlike Western polyphony, Kethrani voices are "
                    "organized by social role rather than pitch range."
                ),
            },
            {
                "id": "S2",
                "heading": "The Three Voices",
                "text": (
                    "The three fundamental voices are the Turak (anchor), Mevali (weaver), and "
                    "Seris (caller). The Turak provides a slow-moving drone-like foundation using "
                    "intervals of perfect fourths and fifths, cycling through a pattern of 7 tones "
                    "over approximately 45 seconds. The Mevali weaves a faster melodic line that "
                    "must touch each Turak tone within 3 beats of its sounding. The Seris provides "
                    "rhythmically free ornamentation that signals transitions between ritual phases."
                ),
            },
            {
                "id": "S3",
                "heading": "The Convergence Rule",
                "text": (
                    "The defining structural principle is the 'Convergence Rule' (kathal-mevris): "
                    "all three voices must arrive simultaneously on a unison or octave at specific "
                    "structural points called 'gates' (doriven). Gates occur every 12-16 measures "
                    "and mark transitions between ritual segments. The approach to a gate follows "
                    "a mandatory 3-measure contraction pattern where voice ranges progressively "
                    "narrow. Failure to converge at a gate is considered a serious ritual error "
                    "that requires the entire section to be repeated."
                ),
            },
            {
                "id": "S4",
                "heading": "Microtonal System",
                "text": (
                    "Kethrani music uses a 17-tone equal temperament system, dividing the octave "
                    "into 17 equal steps of approximately 70.6 cents each. This creates intervals "
                    "with no exact Western equivalents. The 'bright fourth' (7 steps, 494.1 cents) "
                    "is close to a Western perfect fourth but slightly sharp. The 'shadow third' "
                    "(4 steps, 282.4 cents) falls between a Western minor and major third, giving "
                    "Kethrani harmony its characteristic ambiguous quality."
                ),
            },
            {
                "id": "S5",
                "heading": "Instrumental Timbre",
                "text": (
                    "The primary ensemble consists of the kethvar (a 14-string bowed zither), the "
                    "doruflute (end-blown wooden flute with 9 finger holes), and the seval (a clay "
                    "resonator drum). The kethvar's unique construction features sympathetic strings "
                    "tuned to the 17-tone system, producing a shimmering sustain. The doruflute is "
                    "made from aged thornwood and produces a breathy, slightly nasal tone. The seval "
                    "is tuned by adjusting water level inside the clay body."
                ),
            },
            {
                "id": "S6",
                "heading": "Rhythmic Framework",
                "text": (
                    "Kethrani rhythm operates on a 'nested cycle' principle. The base cycle (turavel) "
                    "is 7 beats. Three turavels form a 'breath' (mevan) of 21 beats. Four mevans "
                    "form a 'passage' (seriketh) of 84 beats. The Turak voice articulates the "
                    "turavel boundaries, the Mevali voice articulates mevan boundaries, and the "
                    "Seris voice marks seriketh transitions. Polyrhythmic tension builds as the "
                    "cycle progresses — beats 1-21 are rhythmically aligned, but by beats 63-84, "
                    "the voices operate in near-independence before re-converging at the gate."
                ),
            },
            {
                "id": "S7",
                "heading": "Transmission and Training",
                "text": (
                    "Kethrani musicians begin training at age 8, first learning the Turak voice "
                    "for 3 years, then the Mevali for 4 years, and finally the Seris after age 15. "
                    "Full mastery is recognized at approximately age 25 through the 'Long Night' "
                    "ceremony, where the musician must perform all three voices in rotation for "
                    "6 continuous hours. The oral transmission lineage (dorath) traces back 38 "
                    "generations to the legendary first musician Keth."
                ),
            },
            {
                "id": "S8",
                "heading": "Modern Recordings",
                "text": (
                    "The first audio recordings were made in 1958 by ethnomusicologist Dr. Liara "
                    "Fosse using a portable reel-to-reel recorder. She documented 47 complete "
                    "ceremonial performances over 14 months. Analysis of these recordings revealed "
                    "that convergence accuracy at gates was 94.3%, with the remaining 5.7% showing "
                    "deviations of less than 20 cents — suggesting performers treat convergence as "
                    "a zone rather than an exact point."
                ),
            },
            {
                "id": "S9",
                "heading": "Decline and Revival",
                "text": (
                    "By 1990, fewer than 30 practitioners of the full three-voice tradition remained. "
                    "The Kethrani Music Preservation Society (KMPS), founded in 1995, established "
                    "recording archives and a training programme. By 2020, 145 new practitioners "
                    "had completed training. However, comparative analysis shows modern performers "
                    "achieve convergence accuracy of only 87.1% versus the 94.3% documented in 1958, "
                    "suggesting some transmission fidelity has been lost."
                ),
            },
            {
                "id": "S10",
                "heading": "Computational Analysis",
                "text": (
                    "Recent computational studies have modeled Kethrani polyphony using constraint "
                    "satisfaction frameworks. The convergence rule creates a hierarchical dependency "
                    "structure where each voice's choices propagate constraints to the others. "
                    "Information-theoretic analysis shows that the Mevali voice carries the highest "
                    "entropy (4.2 bits per note) while the Turak carries the lowest (1.8 bits per "
                    "note). The total information rate of a Kethrani performance averages 28 bits "
                    "per second, comparable to improvised jazz at 25-32 bits per second."
                ),
            },
        ],
        "questions": [
            {
                "id": "Q1",
                "question": "How many tones does the Kethrani microtonal system divide the octave into, and what is the approximate size of each step in cents?",
                "relevant_sections": ["S4"],
                "answer_key": "17 tones, approximately 70.6 cents each",
                "accept_patterns": ["17", "70.6", "70", "71"],
                "min_matches": 2,
            },
            {
                "id": "Q2",
                "question": "Describe the nested rhythmic cycle structure, including the names and beat counts of each level.",
                "relevant_sections": ["S6"],
                "answer_key": "turavel = 7 beats, mevan = 3 turavels = 21 beats, seriketh = 4 mevans = 84 beats",
                "accept_patterns": ["turavel", "7", "mevan", "21", "seriketh", "84"],
                "min_matches": 4,
            },
            {
                "id": "Q3",
                "question": "What was the convergence accuracy documented in 1958, and how does it compare to modern performers?",
                "relevant_sections": ["S8", "S9"],
                "answer_key": "94.3% in 1958, 87.1% for modern performers",
                "accept_patterns": ["94.3", "87.1"],
                "min_matches": 2,
            },
            {
                "id": "Q4",
                "question": "What is the training progression for Kethrani musicians, including ages and voice order?",
                "relevant_sections": ["S7"],
                "answer_key": "Start age 8: Turak for 3 years, then Mevali for 4 years, then Seris after age 15, full mastery at ~25",
                "accept_patterns": ["age 8", "turak", "mevali", "seris", "3 year", "4 year", "15", "25"],
                "min_matches": 4,
            },
            {
                "id": "Q5",
                "question": "What is the information-theoretic entropy of the Mevali voice, and how does the total information rate compare to improvised jazz?",
                "relevant_sections": ["S10"],
                "answer_key": "Mevali: 4.2 bits per note; total rate ~28 bits/sec, comparable to jazz at 25-32 bits/sec",
                "accept_patterns": ["4.2", "28", "25", "32", "jazz"],
                "min_matches": 3,
            },
        ],
    },
]


# ─── Structured Output Schemas ──────────────────────────────────────

@dataclass
class SectionSelection:
    """Model's choice of which sections to re-read."""
    selected_sections: str  # Comma-separated section IDs (e.g., "S3,S7,S10")
    reasoning: str          # Why these sections were chosen


@dataclass
class QuestionAnswer:
    """Model's answer to a question."""
    answer: str


# ─── Answer Checking ────────────────────────────────────────────────

def check_answer(model_answer: str, question: dict) -> bool:
    """Check if model's answer matches enough accept patterns."""
    lower = model_answer.lower()
    matches = sum(1 for p in question["accept_patterns"] if p.lower() in lower)
    return matches >= question["min_matches"]


# ─── The Benchmark Task ────────────────────────────────────────────

@kbench.task(name="metacog_control")
def metacog_control(llm) -> float:
    """
    Metacognitive Control Benchmark: Strategic Re-Reading.

    Tests whether a model can strategically allocate limited study effort
    to sections most relevant to upcoming questions.

    Protocol per passage:
    1. Present full passage (all 10 sections)
    2. Present 5 questions
    3. Model selects exactly 3 sections to "re-read" (limited budget)
    4. Re-present selected sections + questions → model answers

    Score = 0.35 * selection_relevance + 0.35 * strategic_gain + 0.30 * accuracy

    Cognitive Science Basis:
    - Allocation of study time (Son & Metcalfe, 2000)
    - Metacognitive control (Nelson & Narens, 1990)
    """
    all_selection_relevances = []
    all_accuracies = []
    reread_accuracies = []
    no_reread_accuracies = []
    results_log = []

    for p_idx, passage in enumerate(PASSAGES):
        # Format full passage
        full_text = f"# {passage['title']}\n\n"
        for sec in passage["sections"]:
            full_text += f"## {sec['heading']} [{sec['id']}]\n{sec['text']}\n\n"

        # Format questions
        questions_text = "\n".join(
            f"{i+1}. {q['question']}" for i, q in enumerate(passage["questions"])
        )

        # Compute which sections are relevant (ground truth)
        relevant_set = set()
        question_relevant = {}
        for q in passage["questions"]:
            question_relevant[q["id"]] = set(q["relevant_sections"])
            relevant_set.update(q["relevant_sections"])

        # ── Phase 1: Read passage + see questions, choose sections to re-read ──
        with kbench.chats.new(f"control_select_{p_idx}"):
            select_prompt = (
                f"Read the following passage carefully.\n\n"
                f"{full_text}\n"
                f"You will need to answer these 5 questions:\n{questions_text}\n\n"
                f"You have a LIMITED BUDGET: you may re-read exactly 3 of the 10 sections "
                f"before answering. Choose the 3 sections that will help you answer the "
                f"questions most accurately.\n\n"
                f"Respond with ONLY a JSON object:\n"
                f'{{"selected_sections": "S1,S2,S3", "reasoning": "brief explanation"}}'
            )

            try:
                sel = llm.prompt(select_prompt, schema=SectionSelection)
                selected_raw = sel.selected_sections
                selection_reasoning = sel.reasoning
            except Exception:
                raw = llm.prompt(select_prompt)
                try:
                    parsed = json.loads(re.search(r'\{.*\}', raw, re.DOTALL).group())
                    selected_raw = str(parsed.get("selected_sections", "S1,S2,S3"))
                    selection_reasoning = str(parsed.get("reasoning", ""))
                except Exception:
                    selected_raw = "S1,S2,S3"
                    selection_reasoning = raw[:200]

        # Parse selected sections
        selected_ids = [s.strip().upper() for s in re.findall(r'S\d+', selected_raw)]
        selected_ids = selected_ids[:3]  # Enforce max 3
        if len(selected_ids) < 3:
            # Pad with S1, S2, S3 if model failed to select enough
            for fallback in ["S1", "S2", "S3"]:
                if fallback not in selected_ids and len(selected_ids) < 3:
                    selected_ids.append(fallback)
        selected_set = set(selected_ids)

        # Compute selection relevance
        relevant_selected = len(selected_set & relevant_set)
        max_possible = min(3, len(relevant_set))
        selection_relevance = relevant_selected / max_possible if max_possible > 0 else 0
        all_selection_relevances.append(selection_relevance)

        # ── Phase 2: Re-read selected sections + answer questions ──
        reread_text = ""
        for sec in passage["sections"]:
            if sec["id"] in selected_set:
                reread_text += f"## {sec['heading']} [{sec['id']}]\n{sec['text']}\n\n"

        with kbench.chats.new(f"control_answer_{p_idx}"):
            answer_prompt = (
                f"You previously read a passage titled \"{passage['title']}\". "
                f"Here are the 3 sections you chose to re-read:\n\n"
                f"{reread_text}\n"
                f"Now answer each question as accurately as possible based on your "
                f"reading of the full passage. Be specific with numbers and details.\n\n"
            )

            for q_idx, q in enumerate(passage["questions"]):
                q_prompt = (
                    f"{answer_prompt if q_idx == 0 else ''}"
                    f"Question {q_idx+1}: {q['question']}\n\n"
                    f"Respond with ONLY a JSON object:\n"
                    f'{{"answer": "<your detailed answer>"}}'
                )

                try:
                    ans = llm.prompt(q_prompt, schema=QuestionAnswer)
                    answer = ans.answer
                except Exception:
                    raw = llm.prompt(q_prompt)
                    try:
                        parsed = json.loads(re.search(r'\{.*\}', raw, re.DOTALL).group())
                        answer = str(parsed.get("answer", raw))
                    except Exception:
                        answer = raw

                is_correct = check_answer(answer, q)
                all_accuracies.append(is_correct)

                # Track strategic gain
                q_relevant = question_relevant[q["id"]]
                was_reread = bool(q_relevant & selected_set)
                if was_reread:
                    reread_accuracies.append(is_correct)
                else:
                    no_reread_accuracies.append(is_correct)

                results_log.append({
                    "passage": passage["title"][:30],
                    "question_id": q["id"],
                    "question": q["question"][:60],
                    "relevant_sections": list(q_relevant),
                    "sections_reread": was_reread,
                    "answer": answer[:100],
                    "correct": is_correct,
                })

        results_log.append({
            "passage": passage["title"][:30],
            "selected_sections": selected_ids,
            "relevant_sections": list(relevant_set),
            "selection_relevance": selection_relevance,
            "reasoning": selection_reasoning[:150],
        })

    # ── Compute Metrics ──
    mean_selection_relevance = sum(all_selection_relevances) / len(all_selection_relevances)
    mean_accuracy = sum(all_accuracies) / len(all_accuracies) if all_accuracies else 0

    reread_acc = sum(reread_accuracies) / len(reread_accuracies) if reread_accuracies else 0
    no_reread_acc = sum(no_reread_accuracies) / len(no_reread_accuracies) if no_reread_accuracies else 0.5
    # Strategic gain: how much does re-reading help? Normalized to [0,1]
    raw_gain = reread_acc - no_reread_acc  # Range [-1, 1]
    strategic_gain = (raw_gain + 1) / 2     # Normalize to [0, 1]

    score = round(
        0.35 * mean_selection_relevance + 0.35 * strategic_gain + 0.30 * mean_accuracy,
        4,
    )

    # ── Logging ──
    print(f"\n{'='*60}")
    print(f"METACOGNITIVE CONTROL BENCHMARK RESULTS")
    print(f"{'='*60}")
    print(f"Passages: {len(PASSAGES)}")
    print(f"Total questions: {len(all_accuracies)}")
    print(f"\n--- Metrics ---")
    print(f"Selection relevance: {mean_selection_relevance:.3f}")
    print(f"  (proportion of chosen sections that were relevant)")
    print(f"Overall accuracy: {mean_accuracy:.3f}")
    print(f"Accuracy on re-read questions: {reread_acc:.3f} (n={len(reread_accuracies)})")
    print(f"Accuracy on non-re-read questions: {no_reread_acc:.3f} (n={len(no_reread_accuracies)})")
    print(f"Strategic gain (normalized): {strategic_gain:.3f}")
    print(f"Composite score: {score:.4f}")

    print(f"\n--- Per-Passage Details ---")
    for entry in results_log:
        if "selected_sections" in entry:
            print(f"\n  Passage: {entry['passage']}")
            print(f"  Selected: {entry['selected_sections']}")
            print(f"  Relevant: {entry['relevant_sections']}")
            print(f"  Relevance: {entry['selection_relevance']:.2f}")
            print(f"  Reasoning: {entry['reasoning']}")

    print(f"\n--- Per-Question Results ---")
    for entry in results_log:
        if "question_id" in entry:
            status = "✓" if entry["correct"] else "✗"
            reread = "RE-READ" if entry["sections_reread"] else "no-read"
            print(f"  {status} [{reread:7s}] {entry['question_id']}: "
                  f"{entry['question'][:50]}... → {entry['answer'][:40]}")

    return score


# ─── Run ────────────────────────────────────────────────────────────
metacog_control.run(llm=kbench.llm)

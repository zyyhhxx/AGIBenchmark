"""
Social Cognition Benchmark: Emotional Prosody in Text

Tests whether a model can detect emotional tone shifts in written dialogue,
analogous to recognizing emotional prosody in speech.

Cognitive Science Basis:
- Emotional prosody perception (Scherer, 1986): detecting emotion from vocal cues
- Text-based emotion recognition (Barrett et al., 2019): contextual emotion inference
- Emotion regulation detection (Gross, 2015): recognizing when speakers
  mask or shift emotional states

Protocol:
1. Present multi-turn dialogues where one speaker's emotional tone shifts
2. Model must: (a) identify the turn where tone shifts, (b) name the emotion
   transition (e.g., "friendly → hostile"), (c) identify the trigger
3. Includes control dialogues with no shift and gradual vs. sudden shifts

Score = 0.40 * shift_detection_accuracy + 0.30 * emotion_labeling
      + 0.20 * trigger_identification + 0.10 * (1 - false_alarm_rate)
"""

import kaggle_benchmarks as kbench
from dataclasses import dataclass
import json
import re
import numpy as np

# ─── Stimuli ─────────────────────────────────────────────────────────

PROSODY_ITEMS = [
    # === SHIFT DIALOGUES ===
    {
        "id": "shift_01",
        "has_shift": True,
        "shift_turn": 4,
        "emotion_before": "friendly",
        "emotion_after": "hostile",
        "trigger": "accusation of dishonesty",
        "dialogue": [
            {"speaker": "A", "text": "Hey! Great to see you. How was your weekend?"},
            {"speaker": "B", "text": "Really good! We went hiking up in the mountains."},
            {"speaker": "A", "text": "That sounds lovely. I wish I could've joined."},
            {"speaker": "B", "text": "Yeah, you said you were busy with work, right?"},
            {"speaker": "A", "text": "Actually, I heard from Sarah that you deliberately didn't invite me. You told her I'd 'ruin the vibe.' Care to explain?"},
            {"speaker": "B", "text": "That's... not what happened. Sarah took it out of context."},
            {"speaker": "A", "text": "Don't gaslight me. I saw the messages."},
        ],
    },
    {
        "id": "shift_02",
        "has_shift": True,
        "shift_turn": 3,
        "emotion_before": "professional",
        "emotion_after": "anxious",
        "trigger": "mention of impending layoffs",
        "dialogue": [
            {"speaker": "A", "text": "The quarterly report looks solid. Revenue up 12%."},
            {"speaker": "B", "text": "Good numbers. The board should be pleased."},
            {"speaker": "A", "text": "Hmm, but did you see the restructuring memo that leaked?"},
            {"speaker": "B", "text": "Wait, what memo? I... I didn't see anything about restructuring."},
            {"speaker": "A", "text": "They're cutting 30% of the division. Names aren't out yet."},
            {"speaker": "B", "text": "Oh God. Do you think our team is... I mean, we hit our targets, right? They can't just—"},
        ],
    },
    {
        "id": "shift_03",
        "has_shift": True,
        "shift_turn": 5,
        "emotion_before": "sympathetic",
        "emotion_after": "frustrated",
        "trigger": "repeated excuse-making",
        "dialogue": [
            {"speaker": "A", "text": "I know the breakup has been really hard on you."},
            {"speaker": "B", "text": "Yeah, I just can't focus on anything. I missed another deadline."},
            {"speaker": "A", "text": "That's understandable. Give yourself some grace."},
            {"speaker": "B", "text": "I also didn't make it to the group project meeting again."},
            {"speaker": "A", "text": "OK, but that's the third time. The rest of us are picking up your slack."},
            {"speaker": "B", "text": "I know, I know, but I just—"},
            {"speaker": "A", "text": "We all have problems. At some point you have to show up."},
        ],
    },
    {
        "id": "shift_04",
        "has_shift": True,
        "shift_turn": 2,
        "emotion_before": "neutral",
        "emotion_after": "excited",
        "trigger": "unexpected good news",
        "dialogue": [
            {"speaker": "A", "text": "Did you check your email today?"},
            {"speaker": "B", "text": "No, just got in. What's up?"},
            {"speaker": "A", "text": "You got accepted! The fellowship committee just announced it!"},
            {"speaker": "B", "text": "WHAT?! Are you serious?! Oh my God, I can't believe it!"},
            {"speaker": "A", "text": "Full funding, two years! You absolutely deserve this."},
            {"speaker": "B", "text": "I'm literally shaking. I need to call my mom right now."},
        ],
    },
    {
        "id": "shift_05",
        "has_shift": True,
        "shift_turn": 4,
        "emotion_before": "cheerful",
        "emotion_after": "melancholic",
        "trigger": "reminder of lost loved one",
        "dialogue": [
            {"speaker": "A", "text": "This restaurant is perfect for your birthday dinner!"},
            {"speaker": "B", "text": "I love it! The view is incredible."},
            {"speaker": "A", "text": "Your dad would've loved this place too."},
            {"speaker": "B", "text": "..."},
            {"speaker": "A", "text": "Sorry, I didn't mean to—"},
            {"speaker": "B", "text": "No, it's OK. He really would have. He always said waterfront restaurants are the best. I just... miss him a lot today."},
        ],
    },
    {
        "id": "shift_06",
        "has_shift": True,
        "shift_turn": 3,
        "emotion_before": "confident",
        "emotion_after": "defensive",
        "trigger": "challenge to expertise",
        "dialogue": [
            {"speaker": "A", "text": "I've been working on this algorithm for months. It's solid."},
            {"speaker": "B", "text": "The benchmarks look impressive, I'll give you that."},
            {"speaker": "A", "text": "But?"},
            {"speaker": "B", "text": "But your test set has a data leakage problem. Lines 340-360."},
            {"speaker": "A", "text": "That's— no, that's not leakage. The features are computed before the split."},
            {"speaker": "B", "text": "I ran it. They're not. The timestamp feature bleeds future data."},
            {"speaker": "A", "text": "Look, I've been doing this for fifteen years. I think I know what data leakage looks like."},
        ],
    },

    # === NO-SHIFT CONTROLS ===
    {
        "id": "control_01",
        "has_shift": False,
        "dialogue": [
            {"speaker": "A", "text": "Want to grab lunch?"},
            {"speaker": "B", "text": "Sure, where are you thinking?"},
            {"speaker": "A", "text": "That new Thai place on 5th?"},
            {"speaker": "B", "text": "Sounds good. I'll meet you there at noon."},
            {"speaker": "A", "text": "Perfect. I'll reserve a table."},
        ],
    },
    {
        "id": "control_02",
        "has_shift": False,
        "dialogue": [
            {"speaker": "A", "text": "The project deadline is Friday."},
            {"speaker": "B", "text": "I think we're on track. Testing is nearly done."},
            {"speaker": "A", "text": "Good. Let's do a final review Thursday morning."},
            {"speaker": "B", "text": "Works for me. I'll have the docs ready by then."},
        ],
    },
    {
        "id": "control_03",
        "has_shift": False,
        "dialogue": [
            {"speaker": "A", "text": "I'm worried about the exam tomorrow."},
            {"speaker": "B", "text": "Me too. There's so much material."},
            {"speaker": "A", "text": "Want to do a late-night study session?"},
            {"speaker": "B", "text": "Yeah, let's go over the practice problems together."},
            {"speaker": "A", "text": "I'll bring coffee. We've got this."},
        ],
    },
    {
        "id": "control_04",
        "has_shift": False,
        "dialogue": [
            {"speaker": "A", "text": "Happy anniversary!"},
            {"speaker": "B", "text": "Three years already. Feels like yesterday we met."},
            {"speaker": "A", "text": "Remember our first date? You were so nervous."},
            {"speaker": "B", "text": "I spilled water all over the table!"},
            {"speaker": "A", "text": "That's when I knew I liked you. You just laughed it off."},
            {"speaker": "B", "text": "Best spill of my life."},
        ],
    },

    # === SUBTLE SHIFT DIALOGUES ===
    {
        "id": "subtle_01",
        "has_shift": True,
        "shift_turn": 4,
        "emotion_before": "supportive",
        "emotion_after": "resentful",
        "trigger": "passive-aggressive comparison to own sacrifices",
        "difficulty": "subtle",
        "dialogue": [
            {"speaker": "A", "text": "I'm so happy for your promotion! You really earned it."},
            {"speaker": "B", "text": "Thanks! It's been a long road. Couldn't have done it without your support."},
            {"speaker": "A", "text": "Of course! That's what friends are for."},
            {"speaker": "B", "text": "You should apply for the senior role too. You'd be great."},
            {"speaker": "A", "text": "Oh, I would, but someone has to hold down the fort while everyone else moves up, right? Ha. No, I'm thrilled for you. Really."},
            {"speaker": "B", "text": "...Are you sure you're OK?"},
            {"speaker": "A", "text": "Totally fine! Why wouldn't I be? I love my current role. It's fine."},
        ],
    },
    {
        "id": "subtle_02",
        "has_shift": True,
        "shift_turn": 3,
        "emotion_before": "enthusiastic",
        "emotion_after": "disappointed",
        "trigger": "realization of being excluded from plans",
        "difficulty": "subtle",
        "dialogue": [
            {"speaker": "A", "text": "That weekend trip sounds amazing! When are you all going?"},
            {"speaker": "B", "text": "Next Saturday. It was kind of a last-minute thing."},
            {"speaker": "A", "text": "Oh nice! So who all's going?"},
            {"speaker": "B", "text": "Just the usual group — Mike, Sarah, Dev, and Lisa."},
            {"speaker": "A", "text": "Oh. That sounds really fun. You guys always have a great time. Yeah."},
            {"speaker": "B", "text": "We should plan something together too sometime."},
            {"speaker": "A", "text": "Sure! Whenever works. I'm pretty flexible these days."},
        ],
    },
    {
        "id": "subtle_03",
        "has_shift": True,
        "shift_turn": 5,
        "emotion_before": "polite",
        "emotion_after": "contemptuous",
        "trigger": "thinly veiled insult disguised as compliment",
        "difficulty": "subtle",
        "dialogue": [
            {"speaker": "A", "text": "Your presentation was really... thorough."},
            {"speaker": "B", "text": "Thanks! I put a lot of work into the data analysis."},
            {"speaker": "A", "text": "You could tell. Lots of slides."},
            {"speaker": "B", "text": "Yeah, I wanted to be comprehensive."},
            {"speaker": "A", "text": "It's brave to present that much raw data. Not everyone has the confidence to go up there without a clear narrative."},
            {"speaker": "B", "text": "I... thought the narrative was clear?"},
            {"speaker": "A", "text": "Oh, definitely! For people who were following closely. Which I'm sure most people were."},
        ],
    },
    {
        "id": "subtle_04",
        "has_shift": True,
        "shift_turn": 4,
        "emotion_before": "casual",
        "emotion_after": "guarded",
        "trigger": "probing question that feels like surveillance",
        "difficulty": "subtle",
        "dialogue": [
            {"speaker": "A", "text": "How was your day off yesterday?"},
            {"speaker": "B", "text": "Really nice, just relaxed at home."},
            {"speaker": "A", "text": "That's good. You deserve it."},
            {"speaker": "B", "text": "Yeah, it was quiet."},
            {"speaker": "A", "text": "Funny, I thought I saw your car at the mall around noon. Must've been someone else."},
            {"speaker": "B", "text": "Oh. I might have stepped out briefly for groceries."},
            {"speaker": "A", "text": "Right, right. The grocery store in the mall. Makes sense."},
        ],
    },
    {
        "id": "subtle_05",
        "has_shift": True,
        "shift_turn": 3,
        "emotion_before": "cheerful",
        "emotion_after": "wistful",
        "trigger": "mention of time passing triggers awareness of unfulfilled goals",
        "difficulty": "subtle",
        "dialogue": [
            {"speaker": "A", "text": "Can you believe it's been ten years since graduation?"},
            {"speaker": "B", "text": "I know! Time really flies. Feels like yesterday."},
            {"speaker": "A", "text": "Remember how we said we'd travel the world before 30?"},
            {"speaker": "B", "text": "Ha. Yeah. We had a whole list of countries."},
            {"speaker": "A", "text": "Well, there's still time, right?"},
            {"speaker": "B", "text": "Sure. Always next year."},
        ],
    },
    {
        "id": "subtle_06",
        "has_shift": True,
        "shift_turn": 4,
        "emotion_before": "warm",
        "emotion_after": "hurt",
        "trigger": "offhand comment reveals lack of attention to something important",
        "difficulty": "subtle",
        "dialogue": [
            {"speaker": "A", "text": "Thanks for coming to the exhibition! It means a lot."},
            {"speaker": "B", "text": "Of course! Your paintings are always so interesting."},
            {"speaker": "A", "text": "I've been working on the centerpiece for six months. It's the one by the entrance."},
            {"speaker": "B", "text": "Oh, is that the landscape? I think I saw it. It was nice."},
            {"speaker": "A", "text": "It's... it's a portrait, actually. Of my grandmother."},
            {"speaker": "B", "text": "Right! Right, of course. I must have been looking at it from the wrong angle."},
            {"speaker": "A", "text": "Sure. Anyway, thanks for stopping by."},
        ],
    },
]


# ─── Structured Output ──────────────────────────────────────────────

@dataclass
class ProsodyResponse:
    has_shift: bool           # Is there an emotional tone shift?
    shift_turn: int           # Turn number where shift occurs (0 if no shift)
    emotion_before: str       # Emotional tone before shift
    emotion_after: str        # Emotional tone after shift
    trigger: str              # What triggered the shift
    confidence: int           # 0-100


# ─── Scoring ─────────────────────────────────────────────────────────

EMOTION_SYNONYMS = {
    "friendly": ["warm", "amiable", "pleasant", "cordial", "amicable"],
    "hostile": ["angry", "aggressive", "confrontational", "antagonistic", "combative"],
    "professional": ["businesslike", "formal", "neutral", "composed", "detached"],
    "anxious": ["worried", "nervous", "panicked", "fearful", "stressed", "alarmed"],
    "sympathetic": ["compassionate", "empathetic", "caring", "understanding", "supportive"],
    "frustrated": ["annoyed", "irritated", "exasperated", "impatient", "fed up"],
    "neutral": ["calm", "matter-of-fact", "measured", "even", "flat"],
    "excited": ["thrilled", "ecstatic", "elated", "overjoyed", "euphoric", "jubilant"],
    "cheerful": ["happy", "joyful", "upbeat", "buoyant", "lighthearted"],
    "melancholic": ["sad", "wistful", "somber", "grieving", "mournful", "bittersweet"],
    "confident": ["assured", "self-assured", "certain", "bold", "assertive"],
    "defensive": ["guarded", "combative", "protective", "prickly", "evasive"],
    "supportive": ["encouraging", "warm", "caring", "helpful", "friendly"],
    "resentful": ["bitter", "envious", "jealous", "passive-aggressive", "grudging"],
    "enthusiastic": ["excited", "eager", "animated", "passionate", "energetic"],
    "disappointed": ["let down", "deflated", "crestfallen", "disheartened", "sad"],
    "polite": ["courteous", "formal", "civil", "mannered", "proper"],
    "contemptuous": ["condescending", "disdainful", "snobbish", "mocking", "dismissive", "sarcastic"],
    "casual": ["relaxed", "informal", "easygoing", "laid-back", "nonchalant"],
    "guarded": ["defensive", "cautious", "wary", "suspicious", "evasive", "uncomfortable"],
    "wistful": ["nostalgic", "melancholic", "reflective", "longing", "pensive", "bittersweet"],
    "warm": ["affectionate", "loving", "tender", "caring", "fond"],
    "hurt": ["wounded", "pained", "stung", "offended", "disappointed", "sad"],
}

def emotion_match(model_emotion: str, target_emotion: str) -> bool:
    model_lower = model_emotion.lower().strip()
    target_lower = target_emotion.lower().strip()
    if target_lower in model_lower or model_lower in target_lower:
        return True
    synonyms = EMOTION_SYNONYMS.get(target_lower, [])
    return any(s in model_lower for s in synonyms)


@kbench.task(name="social_cog_emotional_prosody")
def social_cog_emotional_prosody(llm) -> float:
    """
    Emotional Prosody in Text Benchmark.
    
    Detect emotional tone shifts in written dialogue.
    
    Score = 0.40 * shift_detection + 0.30 * emotion_labeling
          + 0.20 * trigger_id + 0.10 * (1 - false_alarm)
    """
    results = []
    
    for item in PROSODY_ITEMS:
        with kbench.chats.new(f"prosody_{item['id']}"):
            # Format dialogue
            dialogue_text = "\n".join(
                f"Turn {i+1} [{d['speaker']}]: {d['text']}"
                for i, d in enumerate(item["dialogue"])
            )
            
            prompt = (
                f"Read this dialogue carefully and analyze the emotional tone.\n\n"
                f"Dialogue:\n{dialogue_text}\n\n"
                f"Questions:\n"
                f"1. Is there a significant emotional tone SHIFT in this dialogue? (yes/no)\n"
                f"2. If yes, at which turn number does the shift occur?\n"
                f"3. What was the emotional tone BEFORE the shift?\n"
                f"4. What was the emotional tone AFTER the shift?\n"
                f"5. What triggered the shift?\n\n"
                f"Respond with ONLY a JSON object:\n"
                f'{{\n'
                f'  "has_shift": true/false,\n'
                f'  "shift_turn": <turn number or 0>,\n'
                f'  "emotion_before": "<emotion>",\n'
                f'  "emotion_after": "<emotion>",\n'
                f'  "trigger": "<what caused the shift>",\n'
                f'  "confidence": <0-100>\n'
                f'}}'
            )
            
            for _retry in range(3):
                try:
                    response = llm.prompt(prompt, schema=ProsodyResponse)
                    model_has_shift = response.has_shift
                    model_shift_turn = response.shift_turn
                    model_before = response.emotion_before
                    model_after = response.emotion_after
                    model_trigger = response.trigger
                    break
                except Exception:
                    if _retry == 2:
                        # Last resort fallback
                        raw = llm.prompt(prompt)
                        try:
                            parsed = json.loads(re.search(r'\{.*\}', raw, re.DOTALL).group())
                            model_has_shift = bool(parsed.get("has_shift", True))
                            model_shift_turn = int(parsed.get("shift_turn", 0))
                            model_before = str(parsed.get("emotion_before", ""))
                            model_after = str(parsed.get("emotion_after", ""))
                            model_trigger = str(parsed.get("trigger", ""))
                        except Exception:
                            model_has_shift = True
                            model_shift_turn = 0
                            model_before = ""
                            model_after = ""
                            model_trigger = ""
            
            result = {
                "id": item["id"],
                "has_shift_actual": item["has_shift"],
                "has_shift_model": model_has_shift,
            }
            
            if item["has_shift"]:
                # Check shift detection
                result["shift_detected"] = model_has_shift
                
                # Check turn identification
                actual_turn = item["shift_turn"]
                is_subtle = item.get("difficulty") == "subtle"
                # Subtle items: exact match required; standard: ±1 tolerance
                if is_subtle:
                    result["turn_correct"] = model_shift_turn == actual_turn
                else:
                    result["turn_correct"] = abs(model_shift_turn - actual_turn) <= 1
                
                # Check emotion labels
                result["before_correct"] = emotion_match(model_before, item["emotion_before"])
                result["after_correct"] = emotion_match(model_after, item["emotion_after"])
                
                # Check trigger (keyword overlap)
                trigger_words = set(item["trigger"].lower().split())
                model_trigger_words = set(model_trigger.lower().split())
                overlap = len(trigger_words & model_trigger_words)
                result["trigger_score"] = min(1.0, overlap / max(1, len(trigger_words) * 0.5))
            else:
                # Control: should detect NO shift
                result["correct_no_shift"] = not model_has_shift
            
            results.append(result)
    
    # ─── Compute Metrics ─────
    shift_items = [r for r in results if r["has_shift_actual"]]
    control_items = [r for r in results if not r["has_shift_actual"]]
    
    # Split shift items into standard and subtle
    # Check if item has 'difficulty' field set to 'subtle'
    item_lookup = {item["id"]: item for item in PROSODY_ITEMS}
    standard_shift = [r for r in shift_items if item_lookup.get(r["id"], {}).get("difficulty") != "subtle"]
    subtle_shift = [r for r in shift_items if item_lookup.get(r["id"], {}).get("difficulty") == "subtle"]
    
    def compute_shift_metrics(items):
        if not items:
            return 0, 0, 0
        detection = sum(1 for r in items if r.get("shift_detected", False)) / len(items)
        e_scores = []
        t_scores = []
        for r in items:
            if r.get("shift_detected", False):
                e_scores.append((int(r.get("before_correct", False)) + int(r.get("after_correct", False))) / 2)
                t_scores.append(r.get("trigger_score", 0))
        emotion = np.mean(e_scores) if e_scores else 0
        trigger = np.mean(t_scores) if t_scores else 0
        return detection, emotion, trigger
    
    std_det, std_emo, std_trig = compute_shift_metrics(standard_shift)
    sub_det, sub_emo, sub_trig = compute_shift_metrics(subtle_shift)
    
    # False alarm rate (detecting shift in controls)
    false_alarms = sum(1 for r in control_items if not r.get("correct_no_shift", True))
    false_alarm_rate = false_alarms / len(control_items) if control_items else 0
    
    # Composite: 40% standard, 50% subtle, 10% false alarm resistance
    standard_score = 0.40 * std_det + 0.30 * float(std_emo) + 0.20 * float(std_trig) + 0.10 * (1 - false_alarm_rate)
    subtle_score = 0.40 * sub_det + 0.30 * float(sub_emo) + 0.20 * float(sub_trig) + 0.10 * (1 - false_alarm_rate)
    
    score = round(0.40 * standard_score + 0.50 * subtle_score + 0.10 * (1 - false_alarm_rate), 4)
    
    # ─── Logging ─────
    print(f"\n{'='*60}")
    print(f"EMOTIONAL PROSODY IN TEXT RESULTS")
    print(f"{'='*60}")
    
    for r in results:
        if r["has_shift_actual"]:
            detected = "✓" if r.get("shift_detected") else "✗"
            emotions = f"before={'✓' if r.get('before_correct') else '✗'} after={'✓' if r.get('after_correct') else '✗'}"
            trigger = f"trigger={r.get('trigger_score', 0):.2f}"
            print(f"  {detected} {r['id']}: {emotions} {trigger}")
        else:
            correct = "✓ NO SHIFT" if r.get("correct_no_shift") else "✗ FALSE ALARM"
            print(f"  {correct} {r['id']}")
    
    print(f"\n--- Summary ---")
    print(f"Standard detection:  {std_det:.2%}")
    print(f"Standard emotion:   {std_emo:.2%}")
    print(f"Standard trigger:   {std_trig:.2%}")
    print(f"Subtle detection:   {sub_det:.2%}")
    print(f"Subtle emotion:     {sub_emo:.2%}")
    print(f"Subtle trigger:     {sub_trig:.2%}")
    print(f"False alarm rate:   {false_alarm_rate:.2%}")
    print(f"Standard score:     {standard_score:.4f}")
    print(f"Subtle score:       {subtle_score:.4f}")
    print(f"Composite score:    {score:.4f}")
    
    return score


# ─── Run ────────────────────────────────────────────────────────────
social_cog_emotional_prosody.run(llm=kbench.llm)

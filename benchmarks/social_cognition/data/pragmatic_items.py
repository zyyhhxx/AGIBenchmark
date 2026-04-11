"""
Pragmatic inference test items.

Tests Gricean pragmatics: scalar implicature, indirect requests,
irony/understatement, and conversational maxim violations.

Based on Grice (1975) cooperative principle and conversational maxims:
- Quantity: Be as informative as required, not more
- Quality: Don't say what you believe to be false
- Relation: Be relevant
- Manner: Be clear, brief, orderly

Three difficulty tiers:
- DIRECT (25 items): Standard implicature, indirect requests, irony, understatement
- INDIRECT (10 items): Requires world knowledge, politeness strategies, maxim violations
- COMPLEX (10 items): Multi-layer irony, litotes, rhetorical questions, reverse traps
"""

# ═══════════════════════════════════════════════════════════════════
# TIER 1: DIRECT (original 25 items)
# ═══════════════════════════════════════════════════════════════════

PRAGMATIC_ITEMS_DIRECT = [
    # ═══ SCALAR IMPLICATURE ═══
    {
        "id": "SI01", "type": "scalar_implicature", "tier": "direct",
        "context": "Teacher to parent: 'Some of the students passed the exam.'",
        "question": "What is the teacher implying?",
        "literal_meaning": "At least one student passed the exam.",
        "intended_meaning": "Not all students passed — some failed.",
        "intended_accept": ["not all", "some failed", "some did not pass", "not every", "some didn't"],
        "literal_accept": ["at least one", "one or more"],
    },
    {
        "id": "SI02", "type": "scalar_implicature", "tier": "direct",
        "context": "Restaurant reviewer: 'The food was warm.'",
        "question": "What is the reviewer suggesting about the food temperature?",
        "literal_meaning": "The food had a warm temperature.",
        "intended_meaning": "The food was not hot enough — it should have been hotter.",
        "intended_accept": ["not hot", "should have been hotter", "lukewarm", "wasn't hot", "not hot enough"],
        "literal_accept": ["warm temperature", "had warmth"],
    },
    {
        "id": "SI03", "type": "scalar_implicature", "tier": "direct",
        "context": "Job reference: 'The candidate is punctual and dresses neatly.'",
        "question": "What might this reference letter be implying by mentioning only these traits?",
        "literal_meaning": "The candidate arrives on time and dresses well.",
        "intended_meaning": "The candidate lacks more important qualities — this is damning with faint praise.",
        "intended_accept": ["faint praise", "lacking", "not much else", "not very competent", "nothing else positive", "damning", "doesn't have other", "not impressive"],
        "literal_accept": ["punctual", "dresses well", "on time"],
    },
    {
        "id": "SI04", "type": "scalar_implicature", "tier": "direct",
        "context": "A: 'Did everyone enjoy the party?' B: 'Some people had a good time.'",
        "question": "What is B implying?",
        "literal_meaning": "At least some people enjoyed it.",
        "intended_meaning": "Not everyone enjoyed the party — some didn't have a good time.",
        "intended_accept": ["not everyone", "some didn't", "not all", "some did not"],
        "literal_accept": ["some enjoyed", "at least some"],
    },
    {
        "id": "SI05", "type": "scalar_implicature", "tier": "direct",
        "context": "Professor commenting on a thesis: 'The bibliography is comprehensive.'",
        "question": "What might the professor be implying about the thesis overall?",
        "literal_meaning": "The bibliography is thorough and complete.",
        "intended_meaning": "The main content/argument of the thesis is weak — only the bibliography is noteworthy.",
        "intended_accept": ["thesis is weak", "content is weak", "only good thing", "nothing else", "rest is not", "faint praise", "damning"],
        "literal_accept": ["bibliography is good", "thorough"],
    },
    # ═══ INDIRECT REQUESTS ═══
    {
        "id": "IR01", "type": "indirect_request", "tier": "direct",
        "context": "One office worker to another: 'It's really cold in here, isn't it?'",
        "question": "What is the speaker actually requesting?",
        "literal_meaning": "A comment about the room temperature.",
        "intended_meaning": "Could you close the window / turn up the heat?",
        "intended_accept": ["close the window", "turn up", "heat", "make it warmer", "do something about", "shut the window", "turn on the heat", "adjust the temperature"],
        "literal_accept": ["cold", "temperature observation"],
    },
    {
        "id": "IR02", "type": "indirect_request", "tier": "direct",
        "context": "Passenger to driver: 'Do you know what time it is?'",
        "question": "What is the passenger actually asking for?",
        "literal_meaning": "Whether the driver has knowledge of the current time.",
        "intended_meaning": "Please tell me the actual time.",
        "intended_accept": ["tell me the time", "what time", "tell the time", "state the time", "the actual time"],
        "literal_accept": ["whether they know", "knowledge of time"],
    },
    {
        "id": "IR03", "type": "indirect_request", "tier": "direct",
        "context": "Guest at dinner: 'This soup could use a little something.'",
        "question": "What is the guest indirectly requesting?",
        "literal_meaning": "The soup is missing a flavor element.",
        "intended_meaning": "Please pass the salt/seasoning.",
        "intended_accept": ["salt", "seasoning", "pass the salt", "add seasoning", "spice", "pepper"],
        "literal_accept": ["missing flavor", "needs something"],
    },
    {
        "id": "IR04", "type": "indirect_request", "tier": "direct",
        "context": "Parent to teenager whose music is very loud: 'I'm trying to read.'",
        "question": "What is the parent actually requesting?",
        "literal_meaning": "The parent is informing the teenager of their current activity.",
        "intended_meaning": "Turn down the music / be quieter.",
        "intended_accept": ["turn down", "lower the volume", "be quiet", "reduce", "music", "quieter", "noise"],
        "literal_accept": ["reading", "trying to read"],
    },
    {
        "id": "IR05", "type": "indirect_request", "tier": "direct",
        "context": "Colleague looking at a messy shared kitchen: 'I wonder whose turn it is to clean.'",
        "question": "What is the colleague actually communicating?",
        "literal_meaning": "Genuine curiosity about the cleaning schedule.",
        "intended_meaning": "Someone should clean the kitchen — probably the person being addressed.",
        "intended_accept": ["clean", "you should clean", "it's your turn", "clean up", "tidy", "someone needs to clean"],
        "literal_accept": ["schedule", "whose turn"],
    },
    # ═══ IRONY / SARCASM ═══
    {
        "id": "IS01", "type": "irony", "tier": "direct",
        "context": "After waiting 2 hours in the rain for a bus: 'Well, this has been a delightful afternoon!'",
        "question": "What does the speaker actually mean?",
        "literal_meaning": "The afternoon has been pleasant and enjoyable.",
        "intended_meaning": "The afternoon has been terrible/miserable.",
        "intended_accept": ["terrible", "miserable", "awful", "horrible", "bad", "unpleasant", "not delightful", "opposite", "sarcastic", "sarcasm"],
        "literal_accept": ["delightful", "pleasant", "enjoyable"],
    },
    {
        "id": "IS02", "type": "irony", "tier": "direct",
        "context": "Student who received an F on a test: 'Another academic triumph!'",
        "question": "What does the student actually mean?",
        "literal_meaning": "The student achieved an academic success.",
        "intended_meaning": "The student failed badly — this is sarcastic self-deprecation.",
        "intended_accept": ["failed", "did badly", "sarcas", "opposite", "not a triumph", "ironic", "poor performance"],
        "literal_accept": ["triumph", "success"],
    },
    {
        "id": "IS03", "type": "irony", "tier": "direct",
        "context": "After a friend drops and breaks a plate: 'Smooth move, Grace Kelly!'",
        "question": "What is the speaker implying?",
        "literal_meaning": "Comparing the friend to the elegant Grace Kelly as a compliment.",
        "intended_meaning": "The friend was clumsy — the opposite of graceful.",
        "intended_accept": ["clumsy", "not graceful", "sarcas", "ironic", "opposite", "awkward", "ungraceful"],
        "literal_accept": ["graceful", "elegant", "compliment"],
    },
    {
        "id": "IS04", "type": "irony", "tier": "direct",
        "context": "Looking at a tiny, cramped apartment: 'What a palace! The king would be jealous.'",
        "question": "What is the speaker actually expressing?",
        "literal_meaning": "The apartment is grand and luxurious like a palace.",
        "intended_meaning": "The apartment is very small and unimpressive — the opposite of a palace.",
        "intended_accept": ["small", "tiny", "cramped", "unimpressive", "not a palace", "sarcas", "ironic", "opposite"],
        "literal_accept": ["palace", "grand", "luxurious"],
    },
    {
        "id": "IS05", "type": "irony", "tier": "direct",
        "context": "After a team loses 10-0: 'Well, we really showed them!'",
        "question": "What does the speaker actually mean?",
        "literal_meaning": "The team demonstrated their superiority.",
        "intended_meaning": "The team was badly defeated — this is sarcastic.",
        "intended_accept": ["lost badly", "defeated", "sarcas", "ironic", "opposite", "did terribly", "crushed"],
        "literal_accept": ["showed them", "won", "dominated"],
    },
    # ═══ UNDERSTATEMENT ═══
    {
        "id": "US01", "type": "understatement", "tier": "direct",
        "context": "News reporter about a category 5 hurricane: 'There might be a bit of wind later today.'",
        "question": "What is the reporter understating?",
        "literal_meaning": "Some mild wind is expected.",
        "intended_meaning": "A very severe/dangerous storm is coming.",
        "intended_accept": ["severe", "dangerous", "hurricane", "major storm", "understat", "much worse", "extreme"],
        "literal_accept": ["some wind", "mild wind"],
    },
    {
        "id": "US02", "type": "understatement", "tier": "direct",
        "context": "Billionaire describing their wealth: 'I've done alright for myself.'",
        "question": "What is being understated?",
        "literal_meaning": "The person has had moderate financial success.",
        "intended_meaning": "The person is extremely wealthy.",
        "intended_accept": ["extremely wealthy", "very rich", "billionaire", "understat", "much more than alright", "enormous wealth"],
        "literal_accept": ["moderate success", "done okay"],
    },
    {
        "id": "US03", "type": "understatement", "tier": "direct",
        "context": "After running a marathon in record time: 'I suppose I'm in decent shape.'",
        "question": "What is the speaker understating?",
        "literal_meaning": "They are in reasonably good physical condition.",
        "intended_meaning": "They are in exceptional/elite physical condition.",
        "intended_accept": ["exceptional", "elite", "excellent", "extraordinary", "understat", "much better than decent", "outstanding"],
        "literal_accept": ["decent shape", "reasonable"],
    },
    {
        "id": "US04", "type": "understatement", "tier": "direct",
        "context": "Surgeon after a 14-hour operation that saved a patient's life: 'It wasn't the easiest day at work.'",
        "question": "What is the surgeon understating?",
        "literal_meaning": "The day at work was somewhat difficult.",
        "intended_meaning": "The day was extremely challenging and stressful.",
        "intended_accept": ["extremely", "very difficult", "incredibly", "exhausting", "grueling", "understat", "much harder"],
        "literal_accept": ["somewhat difficult", "not easy"],
    },
    {
        "id": "US05", "type": "understatement", "tier": "direct",
        "context": "Astronaut describing their first spacewalk: 'The view was not bad.'",
        "question": "What is the astronaut understating?",
        "literal_meaning": "The view was acceptable or okay.",
        "intended_meaning": "The view was spectacular/breathtaking.",
        "intended_accept": ["spectacular", "breathtaking", "amazing", "incredible", "extraordinary", "understat", "much more than not bad", "stunning"],
        "literal_accept": ["not bad", "acceptable", "okay"],
    },
    # ═══ RELEVANCE IMPLICATURE ═══
    {
        "id": "RI01", "type": "relevance_implicature", "tier": "direct",
        "context": "A: 'Should we invite Tom to the party?' B: 'Well, he did break your favorite vase last time.'",
        "question": "What is B implying?",
        "literal_meaning": "Tom broke a vase at a previous event.",
        "intended_meaning": "No, we probably shouldn't invite Tom.",
        "intended_accept": ["shouldn't invite", "no", "don't invite", "bad idea", "against inviting", "not a good idea"],
        "literal_accept": ["broke", "vase"],
    },
    {
        "id": "RI02", "type": "relevance_implicature", "tier": "direct",
        "context": "A: 'How's the new restaurant downtown?' B: 'Well, the parking is convenient.'",
        "question": "What is B implying about the restaurant?",
        "literal_meaning": "The parking near the restaurant is good.",
        "intended_meaning": "The food or restaurant itself isn't great.",
        "intended_accept": ["not great", "food is bad", "not good", "mediocre", "disappointing", "nothing else good", "only good thing"],
        "literal_accept": ["parking", "convenient"],
    },
    {
        "id": "RI03", "type": "relevance_implicature", "tier": "direct",
        "context": "A: 'Is Sarah a good singer?' B: 'She has a lovely stage presence.'",
        "question": "What is B implying about Sarah's singing?",
        "literal_meaning": "Sarah is engaging to watch on stage.",
        "intended_meaning": "Sarah's singing isn't good.",
        "intended_accept": ["not good", "bad singer", "can't sing", "poor", "avoiding", "not a good singer", "weak"],
        "literal_accept": ["stage presence", "lovely"],
    },
    {
        "id": "RI04", "type": "relevance_implicature", "tier": "direct",
        "context": "A: 'Did you enjoy the movie?' B: 'The popcorn was fantastic.'",
        "question": "What is B implying about the movie?",
        "literal_meaning": "The popcorn at the cinema was very good.",
        "intended_meaning": "The movie wasn't good.",
        "intended_accept": ["didn't enjoy", "movie was bad", "not good", "didn't like", "disappointing", "only good thing"],
        "literal_accept": ["popcorn", "fantastic"],
    },
    {
        "id": "RI05", "type": "relevance_implicature", "tier": "direct",
        "context": "A: 'Would you recommend this book?' B: 'It makes an excellent doorstop.'",
        "question": "What is B implying about the book?",
        "literal_meaning": "The book is heavy enough to prop open a door.",
        "intended_meaning": "The book is terrible — its only value is as a physical object.",
        "intended_accept": ["terrible", "bad book", "not worth reading", "awful", "wouldn't recommend", "no good"],
        "literal_accept": ["doorstop", "heavy"],
    },
]

# ═══════════════════════════════════════════════════════════════════
# TIER 2: INDIRECT/CONTEXTUAL (10 items)
# Requires world knowledge, politeness strategies, domain expertise
# ═══════════════════════════════════════════════════════════════════

PRAGMATIC_ITEMS_INDIRECT = [
    {
        "id": "IC01", "type": "domain_implicature", "tier": "indirect",
        "context": "A surgeon tells the family: 'The operation was technically successful.' The patient died two days later from complications.",
        "question": "What was the surgeon communicating by saying 'technically successful'?",
        "literal_meaning": "The surgical procedure achieved its immediate medical objective.",
        "intended_meaning": "The surgery itself went as planned, but the surgeon is distancing themselves from the overall outcome — acknowledging the procedure worked while implicitly warning that success doesn't guarantee survival.",
        "intended_accept": ["distancing", "doesn't guarantee", "hedging", "limiting responsibility", "narrow definition", "caveat", "disclaimer", "not taking responsibility", "qualified", "procedure worked but"],
        "literal_accept": ["surgery went well", "procedure was successful", "operation achieved"],
    },
    {
        "id": "IC02", "type": "politeness_indirection", "tier": "indirect",
        "context": "A guest who has been at a dinner party for 4 hours says: 'I really shouldn't take up any more of your evening.'",
        "question": "What does the guest actually want?",
        "literal_meaning": "The guest is concerned about imposing on the host's time.",
        "intended_meaning": "The guest wants to leave but is fishing for the host to either let them go gracefully or insist they stay — it's a face-saving exit strategy.",
        "intended_accept": ["wants to leave", "ready to go", "exit", "looking for permission", "wants to go home", "signal to leave", "departure"],
        "literal_accept": ["concerned about imposing", "worried about the host", "being considerate"],
    },
    {
        "id": "IC03", "type": "maxim_violation", "tier": "indirect",
        "context": "Police officer asks a suspect: 'Where were you last Tuesday at 9 PM?' The suspect replies: 'Well, I left work at 5:15 PM, stopped at the gas station on Route 9 — the one near the old hardware store, not the new one by the mall — got exactly 12.3 gallons of premium unleaded at $3.89 per gallon, then drove home taking Maple Street because Oak was under construction...'",
        "question": "Why is the suspect providing such excessive detail?",
        "literal_meaning": "The suspect is being thorough and helpful in recounting their evening.",
        "intended_meaning": "The excessive, irrelevant precision is a sign of a rehearsed or fabricated alibi — genuine recall doesn't include this level of peripheral detail. The suspect is overcompensating.",
        "intended_accept": ["rehearsed", "fabricated", "lying", "overcompensating", "deceptive", "prepared alibi", "not genuine", "too detailed", "suspicious"],
        "literal_accept": ["being thorough", "helpful", "detailed account", "good memory"],
    },
    {
        "id": "IC04", "type": "face_threat", "tier": "indirect",
        "context": "At a job interview, the interviewer says: 'We'll certainly keep your resume on file.'",
        "question": "What is the interviewer actually communicating?",
        "literal_meaning": "The company will retain the candidate's application for future reference.",
        "intended_meaning": "The candidate is being rejected — this is a polite dismissal formula. 'Keeping your resume on file' is a conventionalized way of saying 'you won't be getting this job.'",
        "intended_accept": ["rejected", "not getting the job", "polite rejection", "dismissal", "won't be hired", "turning down", "not selected"],
        "literal_accept": ["keep the resume", "future opportunities", "stored for later"],
    },
    {
        "id": "IC05", "type": "domain_implicature", "tier": "indirect",
        "context": "Art critic reviewing a painting: 'The artist has certainly made bold choices with color.'",
        "question": "What is the critic actually saying about the painting?",
        "literal_meaning": "The artist used colors in a daring and confident way.",
        "intended_meaning": "The color choices are bad or garish — 'bold choices' in art criticism is often a euphemism for poor aesthetic judgment, especially when it's the only thing mentioned.",
        "intended_accept": ["bad", "garish", "poor", "ugly", "tasteless", "gaudy", "not good", "negative", "criticism", "euphemism"],
        "literal_accept": ["daring", "confident", "brave", "courageous"],
    },
    {
        "id": "IC06", "type": "politeness_indirection", "tier": "indirect",
        "context": "A colleague presents a proposal in a meeting. The boss says: 'That's certainly one way to approach this problem.'",
        "question": "What is the boss signaling about the proposal?",
        "literal_meaning": "The proposal is one valid approach among several.",
        "intended_meaning": "The boss disapproves — 'one way' implies it's not the right way, and 'certainly' adds a dismissive tone. This is a polite way of saying the proposal is inadequate.",
        "intended_accept": ["disapproves", "not good", "inadequate", "doesn't like", "dismissing", "rejected", "bad proposal", "wrong approach", "negative"],
        "literal_accept": ["valid approach", "one option", "acknowledging"],
    },
    {
        "id": "IC07", "type": "strategic_ambiguity", "tier": "indirect",
        "context": "A politician asked 'Will you raise taxes?' replies: 'I am committed to ensuring fiscal responsibility and maintaining the economic well-being of hardworking families.'",
        "question": "What is the politician actually communicating about taxes?",
        "literal_meaning": "The politician cares about fiscal responsibility and family welfare.",
        "intended_meaning": "The politician is deliberately avoiding the question — the non-answer signals they likely will raise taxes but don't want to say so directly. The vague language is strategic evasion.",
        "intended_accept": ["avoiding", "evading", "non-answer", "dodging", "not answering", "deflecting", "won't commit", "evasion", "hiding"],
        "literal_accept": ["fiscal responsibility", "cares about families", "responsible governance"],
    },
    {
        "id": "IC08", "type": "conversational_implicature", "tier": "indirect",
        "context": "Two academics at a conference. Professor A: 'Have you read Dr. Chen's new paper on quantum error correction?' Professor B: 'I've been very busy with teaching this semester.'",
        "question": "What is Professor B actually communicating?",
        "literal_meaning": "Professor B has had a heavy teaching load.",
        "intended_meaning": "Professor B has not read the paper and is using 'busy with teaching' as a face-saving excuse — possibly also implying the paper wasn't important enough to prioritize.",
        "intended_accept": ["hasn't read", "didn't read", "no", "hasn't gotten to it", "not read", "excuse"],
        "literal_accept": ["busy", "heavy teaching load", "occupied"],
    },
    {
        "id": "IC09", "type": "institutional_register", "tier": "indirect",
        "context": "A doctor tells a patient: 'We might want to consider exploring some additional testing options.'",
        "question": "What is the doctor actually saying?",
        "literal_meaning": "Additional tests are one possibility worth thinking about.",
        "intended_meaning": "The doctor is seriously concerned and wants to order more tests — the hedging language ('might', 'consider', 'exploring', 'options') is medical register softening what is effectively a directive, not a casual suggestion.",
        "intended_accept": ["concerned", "ordering tests", "worried", "something wrong", "serious", "needs tests", "directive", "strongly recommending"],
        "literal_accept": ["considering options", "maybe some tests", "thinking about it"],
    },
    {
        "id": "IC10", "type": "social_obligation", "tier": "indirect",
        "context": "After a mediocre meal at a friend's house, the friend asks 'How was everything?' The guest replies: 'You always put so much effort into your cooking!'",
        "question": "What is the guest actually saying about the food?",
        "literal_meaning": "The friend works hard when cooking.",
        "intended_meaning": "The food wasn't good — the guest is praising effort instead of result, which implicitly acknowledges the outcome didn't match the effort. This is a face-saving deflection.",
        "intended_accept": ["food wasn't good", "not good", "bad", "mediocre", "avoiding saying", "deflecting", "praising effort not result", "didn't taste good"],
        "literal_accept": ["works hard", "puts in effort", "dedicated cook"],
    },
]

# ═══════════════════════════════════════════════════════════════════
# TIER 3: COMPLEX MULTI-LAYER (10 items)
# Litotes, rhetorical questions, multi-layer irony, reverse traps
# ═══════════════════════════════════════════════════════════════════

PRAGMATIC_ITEMS_COMPLEX = [
    {
        "id": "CX01", "type": "litotes", "tier": "complex",
        "context": "A food critic writes: 'The chef's signature dish is not without its merits, though one wouldn't call it not unpleasant.'",
        "question": "What is the critic's overall assessment of the dish?",
        "literal_meaning": "The dish has some positive qualities and is not unpleasant (i.e., it's pleasant).",
        "intended_meaning": "The dish is mediocre at best — the triple negation ('wouldn't call it not unpleasant') resolves to 'it IS unpleasant', while 'not without merits' is faint praise. The convoluted language signals the critic is struggling to say anything positive.",
        "intended_accept": ["mediocre", "unpleasant", "bad", "poor", "not good", "negative", "struggling to praise", "barely acceptable", "disappointing"],
        "literal_accept": ["has merits", "pleasant", "positive", "good"],
    },
    {
        "id": "CX02", "type": "rhetorical_reversal", "tier": "complex",
        "context": "A teacher whose class just scored the highest in the district says to colleagues: 'Who says standardized testing measures anything meaningful?'",
        "question": "What is the teacher actually expressing?",
        "literal_meaning": "The teacher is questioning the value of standardized testing.",
        "intended_meaning": "The teacher is being playfully boastful — by questioning the test's value right after their class aced it, they're actually drawing attention to the achievement while appearing humble. The rhetorical question is ironic pride.",
        "intended_accept": ["boastful", "proud", "bragging", "showing off", "ironic pride", "drawing attention", "humble brag", "celebrating"],
        "literal_accept": ["questioning testing", "criticizing standardized tests", "doubts testing"],
    },
    {
        "id": "CX03", "type": "multi_layer_irony", "tier": "complex",
        "context": "Two friends are discussing a mutual acquaintance who always brags about their wealth. Friend A: 'Did you see Marcus's new gold-plated phone case?' Friend B: 'How refreshingly subtle of him.'",
        "question": "What layers of meaning are in B's response?",
        "literal_meaning": "Marcus's choice is refreshing and subtle.",
        "intended_meaning": "B is being sarcastic (gold-plated is the opposite of subtle), but also making a broader social commentary that Marcus's constant displays of wealth are tiresome and tasteless — the word 'refreshingly' adds a second ironic layer implying this garish behavior is the SAME as always, not 'refreshing' at all.",
        "intended_accept": ["tasteless", "garish", "ostentatious", "opposite of subtle", "gaudy", "showing off", "vulgar", "same as always", "tiresome", "not subtle"],
        "literal_accept": ["subtle", "refreshing", "understated"],
    },
    {
        "id": "CX04", "type": "pragmatic_reversal", "tier": "complex",
        "context": "A parent finds their teenager's room spotlessly clean for the first time in months. The parent says: 'Alright, what did you break?'",
        "question": "What pragmatic inference is the parent making?",
        "literal_meaning": "The parent is asking if the teenager broke something.",
        "intended_meaning": "The parent infers that unusual good behavior (cleaning) is compensation for something bad the teenager did — the cleaning is guilt-driven, not genuine helpfulness. The parent is using their knowledge of the teen's behavioral patterns to detect deception.",
        "intended_accept": ["guilt", "hiding something", "compensating", "did something wrong", "covering up", "suspicious", "trying to make up for", "broke something", "in trouble"],
        "literal_accept": ["asking about breakage", "curious what broke"],
    },
    {
        "id": "CX05", "type": "backhanded_compliment", "tier": "complex",
        "context": "At a class reunion, someone says to a former classmate: 'Wow, you look amazing! I barely recognized you!'",
        "question": "Why might this compliment be offensive?",
        "literal_meaning": "The person looks so good now that they're almost unrecognizable.",
        "intended_meaning": "The 'compliment' implies the person used to look bad — 'barely recognized you' means they looked so different (worse) before that the improvement is shocking. It's a backhanded compliment that insults their past appearance while praising the present.",
        "intended_accept": ["used to look bad", "looked worse before", "insult", "backhanded", "implies they were ugly", "previous appearance", "offensive", "looked bad before"],
        "literal_accept": ["looks great now", "amazing transformation", "genuine compliment"],
    },
    {
        "id": "CX06", "type": "register_clash", "tier": "complex",
        "context": "A firefighter who just rescued three children from a burning building is interviewed on TV. Reporter: 'That was incredibly brave!' Firefighter: 'Just doing my job, ma'am.'",
        "question": "Is the firefighter genuinely saying it was routine, or is something more complex happening?",
        "literal_meaning": "Rescuing people from fires is a normal part of the firefighter's job description.",
        "intended_meaning": "The firefighter is performing modesty through a professional register — they know the act was extraordinary but cultural norms of their profession require downplaying heroism. 'Just doing my job' is a conventionalized humility formula that actually ACKNOWLEDGES the bravery by conspicuously not claiming credit for it.",
        "intended_accept": ["modesty", "downplaying", "humble", "deflecting praise", "understating", "professional norm", "knows it was brave", "conventionalized", "false modesty"],
        "literal_accept": ["routine", "normal job", "nothing special", "ordinary duties"],
    },
    {
        "id": "CX07", "type": "presupposition_manipulation", "tier": "complex",
        "context": "A defense attorney asks a witness: 'When did you stop taking the medication that affects your memory?'",
        "question": "What is the attorney doing with this question beyond seeking information?",
        "literal_meaning": "The attorney wants to know the date the witness stopped taking memory-affecting medication.",
        "intended_meaning": "The question is a presupposition trap — it presupposes (1) the witness takes medication, (2) the medication affects memory, and (3) the witness stopped taking it. Any direct answer accepts all three presuppositions. The attorney is planting doubt about the witness's reliability regardless of the answer.",
        "intended_accept": ["trap", "presupposition", "planting doubt", "loaded question", "trick", "undermining credibility", "assuming facts", "misleading", "manipulative"],
        "literal_accept": ["asking about medication", "wants the date", "seeking information"],
    },
    {
        "id": "CX08", "type": "performative_contradiction", "tier": "complex",
        "context": "Someone posts on social media: 'I'm SO over caring about what people think of me on social media. 💅'",
        "question": "What is contradictory about this statement?",
        "literal_meaning": "The person no longer cares about others' opinions on social media.",
        "intended_meaning": "The very act of posting this declaration on social media contradicts its content — if they truly didn't care, they wouldn't announce it publicly. The performative nature of the post (seeking validation for not seeking validation) reveals they DO care about their image.",
        "intended_accept": ["contradicts", "still cares", "seeking validation", "performative", "ironic", "self-defeating", "posting proves they care", "attention seeking", "paradox"],
        "literal_accept": ["doesn't care", "moved past it", "genuine indifference"],
    },
    {
        "id": "CX09", "type": "context_dependent_meaning", "tier": "complex",
        "context": "Two neighbors have been feuding for months over a property line dispute. One morning, Neighbor A finds a plate of freshly baked cookies on their doorstep with a note from Neighbor B: 'Thinking of you! 😊'",
        "question": "How should Neighbor A interpret this gesture given the context?",
        "literal_meaning": "Neighbor B is being kind and thoughtful by baking cookies.",
        "intended_meaning": "Given the ongoing feud, this is ambiguous and potentially threatening — it could be a genuine peace offering, but the saccharine tone ('Thinking of you! 😊') during an active dispute reads as passive-aggressive. The gesture forces Neighbor A into an awkward position: rejecting kindness makes them look bad, but accepting it may concede social ground in the dispute.",
        "intended_accept": ["passive-aggressive", "manipulative", "strategic", "not genuine", "power move", "suspicious", "ulterior motive", "ambiguous", "threatening"],
        "literal_accept": ["kind gesture", "peace offering", "friendly", "thoughtful"],
    },
    {
        "id": "CX10", "type": "epistemic_hedging", "tier": "complex",
        "context": "A climate scientist presenting to Congress says: 'Based on current models, there is reason to believe that sea levels could potentially rise by amounts that some researchers consider significant within timeframes that merit attention.'",
        "question": "Why is the scientist using so many hedging words, and what are they actually saying?",
        "literal_meaning": "There is some possibility that sea levels might rise somewhat.",
        "intended_meaning": "The scientist is virtually certain sea levels will rise dangerously but is using extreme hedging ('could potentially', 'some researchers', 'merit attention') as a strategic communication choice — either to avoid political backlash, to maintain scientific register that doesn't overstate certainty, or because the political context forces indirect communication of urgent findings.",
        "intended_accept": ["certain", "urgent", "serious", "hedging strategically", "politically cautious", "understating danger", "actually alarming", "forced to hedge", "downplaying severity"],
        "literal_accept": ["uncertain", "maybe", "some possibility", "unclear"],
    },
]

# Backward-compatible union
PRAGMATIC_ITEMS = PRAGMATIC_ITEMS_DIRECT + PRAGMATIC_ITEMS_INDIRECT + PRAGMATIC_ITEMS_COMPLEX

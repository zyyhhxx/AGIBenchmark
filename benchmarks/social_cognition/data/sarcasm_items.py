"""
Sarcasm detection in conversational context items.

85 utterances across 3 difficulty tiers:
- Tier 1 (40 items): Obvious context-utterance contradiction (difficulty=1)
- Tier 2 (15 items): Implicit contradiction, contextual sarcasm (difficulty=2)
- Tier 3 (30 items): Subtle/ambiguous, deadpan, cultural patterns (difficulty=3)

Model rates sincerity 0-100. We measure AUC discrimination and calibration.

Design principles:
- Rich context required to distinguish sarcasm from sincerity
- Matched pairs: similar surface-level statements, different intent
- Context provides the disambiguating cues (incongruity, speaker frustration, etc.)
- Higher tiers require increasingly sophisticated pragmatic reasoning
"""

SARCASM_ITEMS = [
    # ═══════════════════════════════════════════════════════════════
    # TIER 1 — OBVIOUS CONTRADICTION (difficulty=1)
    # ═══════════════════════════════════════════════════════════════

    # ═══ SARCASTIC UTTERANCES (Tier 1) ═══
    {
        "id": "S01", "is_sarcastic": True, "difficulty": 1,
        "context": "After waiting 45 minutes for a simple coffee order at a café that prides itself on speed.",
        "utterance": "Well, that was quick service!",
        "cue": "Long wait contradicts 'quick'",
    },
    {
        "id": "S02", "is_sarcastic": True, "difficulty": 1,
        "context": "A student receives back their essay with more red ink than black. The professor had written corrections on nearly every line.",
        "utterance": "Wow, looks like I really nailed that essay.",
        "cue": "Heavy corrections contradict 'nailed it'",
    },
    {
        "id": "S03", "is_sarcastic": True, "difficulty": 1,
        "context": "Two hikers are completely soaked after getting caught in an unexpected downpour. Their gear is wet and they're shivering.",
        "utterance": "Perfect hiking weather, just like the forecast said.",
        "cue": "Downpour contradicts 'perfect weather'",
    },
    {
        "id": "S04", "is_sarcastic": True, "difficulty": 1,
        "context": "A driver has been stuck in traffic for 3 hours on what should have been a 30-minute commute.",
        "utterance": "I just love my commute.",
        "cue": "3-hour delay contradicts 'love'",
    },
    {
        "id": "S05", "is_sarcastic": True, "difficulty": 1,
        "context": "A colleague just gave a presentation full of errors, misread data, and forgot half their slides.",
        "utterance": "That was really impressive work up there.",
        "cue": "Disastrous presentation contradicts 'impressive'",
    },
    {
        "id": "S06", "is_sarcastic": True, "difficulty": 1,
        "context": "The restaurant served a steak that was charred black on the outside and cold in the middle.",
        "utterance": "My compliments to the chef.",
        "cue": "Badly cooked food contradicts praise",
    },
    {
        "id": "S07", "is_sarcastic": True, "difficulty": 1,
        "context": "A team member who promised to finish a critical report by Monday shows up on Thursday saying they haven't started.",
        "utterance": "I'm so glad I could count on you.",
        "cue": "Broken promise contradicts reliability",
    },
    {
        "id": "S08", "is_sarcastic": True, "difficulty": 1,
        "context": "Someone parks their car right across two parking spaces in a crowded lot.",
        "utterance": "What a considerate person.",
        "cue": "Inconsiderate parking contradicts 'considerate'",
    },
    {
        "id": "S09", "is_sarcastic": True, "difficulty": 1,
        "context": "A friend suggests eating at the restaurant where you got food poisoning last month.",
        "utterance": "Oh great, my favorite place! Last time was such a wonderful experience.",
        "cue": "Food poisoning contradicts 'wonderful'",
    },
    {
        "id": "S10", "is_sarcastic": True, "difficulty": 1,
        "context": "It's the fifth time this month the office printer has jammed. Paper is stuck everywhere and toner is leaking.",
        "utterance": "This printer is truly a marvel of modern technology.",
        "cue": "Constant malfunctions contradict 'marvel'",
    },
    {
        "id": "S11", "is_sarcastic": True, "difficulty": 1,
        "context": "A child tracks mud all over the freshly mopped kitchen floor.",
        "utterance": "Thanks for helping me keep the floor clean.",
        "cue": "Mud everywhere contradicts 'clean'",
    },
    {
        "id": "S12", "is_sarcastic": True, "difficulty": 1,
        "context": "The new software update deleted all of a user's saved preferences and introduced three new bugs.",
        "utterance": "What a fantastic improvement! I love the new features.",
        "cue": "Bugs and data loss contradict 'improvement'",
    },
    {
        "id": "S13", "is_sarcastic": True, "difficulty": 1,
        "context": "A meeting that was supposed to last 15 minutes has now been going on for 2.5 hours with no resolution.",
        "utterance": "This is a really productive use of our time.",
        "cue": "Endless, unproductive meeting contradicts 'productive'",
    },
    {
        "id": "S14", "is_sarcastic": True, "difficulty": 1,
        "context": "An athlete falls on their face during the first hurdle of the race.",
        "utterance": "Textbook form right there.",
        "cue": "Falling contradicts 'textbook form'",
    },
    {
        "id": "S15", "is_sarcastic": True, "difficulty": 1,
        "context": "Someone gives directions that lead you in a complete circle back to where you started.",
        "utterance": "Well, those were incredibly helpful directions.",
        "cue": "Going in circles contradicts 'helpful'",
    },
    {
        "id": "S16", "is_sarcastic": True, "difficulty": 1,
        "context": "A friend shows you their sunburn that covers their entire back after falling asleep at the beach without sunscreen.",
        "utterance": "Smart decision skipping the sunscreen.",
        "cue": "Severe sunburn contradicts 'smart'",
    },
    {
        "id": "S17", "is_sarcastic": True, "difficulty": 1,
        "context": "A construction project next door starts jackhammering at 6 AM on a Saturday.",
        "utterance": "What a lovely way to wake up on the weekend.",
        "cue": "Jackhammering at 6 AM contradicts 'lovely'",
    },
    {
        "id": "S18", "is_sarcastic": True, "difficulty": 1,
        "context": "A mechanic says your car repair will cost $4,000, triple the original estimate.",
        "utterance": "What a pleasant surprise that price is.",
        "cue": "Triple the expected cost contradicts 'pleasant surprise'",
    },
    {
        "id": "S19", "is_sarcastic": True, "difficulty": 1,
        "context": "Your flight has been delayed for the fourth time. It's now 8 hours behind schedule.",
        "utterance": "This airline really has their act together.",
        "cue": "Repeated delays contradict 'act together'",
    },
    {
        "id": "S20", "is_sarcastic": True, "difficulty": 1,
        "context": "A coworker microwaves fish in the shared office kitchen. The smell fills the entire floor.",
        "utterance": "Mmm, what a delightful aroma.",
        "cue": "Offensive fish smell contradicts 'delightful aroma'",
    },

    # ═══ SINCERE UTTERANCES (Tier 1) ═══
    {
        "id": "N01", "is_sarcastic": False, "difficulty": 1,
        "context": "A barista quickly prepares a complex coffee order in under 2 minutes during a slow period.",
        "utterance": "Well, that was quick service!",
        "cue": "2 minutes is genuinely fast for a complex order",
    },
    {
        "id": "N02", "is_sarcastic": False, "difficulty": 1,
        "context": "A student receives back their essay with a perfect score and a note saying 'Excellent analysis throughout.'",
        "utterance": "Wow, looks like I really nailed that essay.",
        "cue": "Perfect score confirms the claim",
    },
    {
        "id": "N03", "is_sarcastic": False, "difficulty": 1,
        "context": "Two hikers are enjoying a sunny day with clear skies and mild temperatures, exactly as the weather app predicted.",
        "utterance": "Perfect hiking weather, just like the forecast said.",
        "cue": "Weather is genuinely perfect",
    },
    {
        "id": "N04", "is_sarcastic": False, "difficulty": 1,
        "context": "A driver who recently moved closer to work now has a scenic 10-minute drive along the coast.",
        "utterance": "I just love my commute.",
        "cue": "Short scenic drive is genuinely enjoyable",
    },
    {
        "id": "N05", "is_sarcastic": False, "difficulty": 1,
        "context": "A colleague delivered a polished presentation with clear data, engaging visuals, and received a standing ovation.",
        "utterance": "That was really impressive work up there.",
        "cue": "Standing ovation confirms the praise",
    },
    {
        "id": "N06", "is_sarcastic": False, "difficulty": 1,
        "context": "The restaurant served the best filet mignon you've ever tasted — perfectly seared, seasoned, and tender.",
        "utterance": "My compliments to the chef.",
        "cue": "Excellent food justifies the praise",
    },
    {
        "id": "N07", "is_sarcastic": False, "difficulty": 1,
        "context": "A team member stayed up all weekend to finish a critical report early, saving the whole team from a deadline crunch.",
        "utterance": "I'm so glad I could count on you.",
        "cue": "Going above and beyond confirms reliability",
    },
    {
        "id": "N08", "is_sarcastic": False, "difficulty": 1,
        "context": "Someone notices another driver carefully backing into a tight spot without touching any other cars, and then leaving extra space.",
        "utterance": "What a considerate person.",
        "cue": "Careful parking justifies the comment",
    },
    {
        "id": "N09", "is_sarcastic": False, "difficulty": 1,
        "context": "A friend suggests trying the new Italian restaurant that just won the city's best newcomer award.",
        "utterance": "Oh great, sounds like an excellent choice! I've been wanting to try that place.",
        "cue": "Award-winning restaurant justifies enthusiasm",
    },
    {
        "id": "N10", "is_sarcastic": False, "difficulty": 1,
        "context": "The office gets a brand-new printer that prints in color, scans, and has never jammed in a month of use.",
        "utterance": "This printer is truly a marvel of modern technology.",
        "cue": "Reliable new printer justifies the praise",
    },
    {
        "id": "N11", "is_sarcastic": False, "difficulty": 1,
        "context": "A child voluntarily mops the kitchen floor after tracking in some mud, leaving it cleaner than before.",
        "utterance": "Thanks for helping me keep the floor clean.",
        "cue": "Child actually cleaned up",
    },
    {
        "id": "N12", "is_sarcastic": False, "difficulty": 1,
        "context": "The latest software update added dark mode, faster load times, and fixed the bugs users had been reporting.",
        "utterance": "What a fantastic improvement! I love the new features.",
        "cue": "Genuine improvements justify the praise",
    },
    {
        "id": "N13", "is_sarcastic": False, "difficulty": 1,
        "context": "A 15-minute standup meeting finishes early after the team efficiently resolved three blockers.",
        "utterance": "This is a really productive use of our time.",
        "cue": "Efficient problem-solving justifies the comment",
    },
    {
        "id": "N14", "is_sarcastic": False, "difficulty": 1,
        "context": "An athlete clears every hurdle with perfect timing, setting a new personal best.",
        "utterance": "Textbook form right there.",
        "cue": "Perfect execution justifies the comment",
    },
    {
        "id": "N15", "is_sarcastic": False, "difficulty": 1,
        "context": "Someone gives you detailed directions that lead you directly to the destination, saving 20 minutes vs. the GPS route.",
        "utterance": "Well, those were incredibly helpful directions.",
        "cue": "Time-saving directions justify the praise",
    },
    {
        "id": "N16", "is_sarcastic": False, "difficulty": 1,
        "context": "A friend shows you their perfect, even tan after spending a week at the beach using SPF 50 regularly.",
        "utterance": "Smart decision with the sunscreen.",
        "cue": "Perfect tan with no burn confirms the claim",
    },
    {
        "id": "N17", "is_sarcastic": False, "difficulty": 1,
        "context": "You wake up on Saturday to birds singing outside your window on a sunny spring morning.",
        "utterance": "What a lovely way to wake up on the weekend.",
        "cue": "Genuinely pleasant morning",
    },
    {
        "id": "N18", "is_sarcastic": False, "difficulty": 1,
        "context": "A mechanic finds the issue was just a loose wire, and the repair costs only $50 instead of the feared $500.",
        "utterance": "What a pleasant surprise that price is.",
        "cue": "Genuinely surprising low cost",
    },
    {
        "id": "N19", "is_sarcastic": False, "difficulty": 1,
        "context": "Your flight departs exactly on time, and the airline upgrades you to business class for free.",
        "utterance": "This airline really has their act together.",
        "cue": "On-time departure + free upgrade justifies praise",
    },
    {
        "id": "N20", "is_sarcastic": False, "difficulty": 1,
        "context": "A coworker bakes homemade cinnamon rolls and brings them to the office. The smell of fresh pastry fills the floor.",
        "utterance": "Mmm, what a delightful aroma.",
        "cue": "Fresh cinnamon rolls genuinely smell good",
    },

    # ═══════════════════════════════════════════════════════════════
    # TIER 2 — CONTEXTUAL / IMPLICIT CONTRADICTION (difficulty=2)
    # Sarcasm where the contradiction is unstated or requires
    # inference about social dynamics, expectations, or tone shifts.
    # ═══════════════════════════════════════════════════════════════

    # ═══ SARCASTIC UTTERANCES (Tier 2) ═══
    {
        "id": "S21", "is_sarcastic": True, "difficulty": 2,
        "context": "A manager has repeatedly taken credit for their team's ideas in meetings. After the latest all-hands, the manager posts on Slack: 'Great teamwork everyone!' A team member responds privately to a colleague.",
        "utterance": "Yeah, teamwork. That's definitely what that was.",
        "cue": "Repetition with emphasis signals ironic distancing; manager's credit-taking makes 'teamwork' hollow",
    },
    {
        "id": "S22", "is_sarcastic": True, "difficulty": 2,
        "context": "A friend who constantly cancels plans at the last minute texts saying they'd 'love to hang out this weekend, for real this time.' You respond to another friend.",
        "utterance": "I'm sure this time will be different.",
        "cue": "Pattern of cancellations makes optimism implausible; requires tracking speaker history",
    },
    {
        "id": "S23", "is_sarcastic": True, "difficulty": 2,
        "context": "During a group project, one member did nothing while the others worked overtime. At the final presentation, that member enthusiastically thanks the group 'for being such a great team.' Another member mutters to their neighbor.",
        "utterance": "Must be nice to be part of such a great team.",
        "cue": "Speaker echoes freeloader's words; the muttering delivery and asymmetric effort signal sarcasm",
    },
    {
        "id": "S24", "is_sarcastic": True, "difficulty": 2,
        "context": "A parent has asked their teenager three times to take out the trash. The teen finally does it after being told they can't use their phone until it's done. The parent watches them drag the bag to the curb.",
        "utterance": "How generous of you.",
        "cue": "Coerced compliance reframed as generosity; no explicit contradiction but social expectation mismatch",
    },
    {
        "id": "S25", "is_sarcastic": True, "difficulty": 2,
        "context": "A new employee asks a senior colleague for help. The senior colleague responds with a single link to a 200-page internal wiki with no further guidance. The new employee tells a friend.",
        "utterance": "They were incredibly helpful. Really went above and beyond.",
        "cue": "Minimal effort disguised as help; sarcasm requires recognizing the gap between expected mentoring and actual response",
    },
    {
        "id": "S26", "is_sarcastic": True, "difficulty": 2,
        "context": "A couple is at a fancy restaurant for their anniversary. The waiter has interrupted them six times to ask if everything is okay, refill water after one sip, and describe specials they didn't ask about. The partner leans over.",
        "utterance": "At least we're getting plenty of personal attention tonight.",
        "cue": "Excessive attentiveness is technically positive but unwanted in context; requires understanding that 'too much' service is a complaint",
    },
    {
        "id": "S27", "is_sarcastic": True, "difficulty": 2,
        "context": "An employee submitted a detailed proposal last month. Their boss responded two weeks later with 'Let's circle back on this.' It's now been another month with no follow-up. The employee mentions it to a colleague.",
        "utterance": "I'm sure they're giving it really careful consideration.",
        "cue": "Extended silence after a deflecting phrase suggests neglect, not careful thought; requires reading between the lines of corporate language",
    },
    {
        "id": "S28", "is_sarcastic": True, "difficulty": 2,
        "context": "A friend proudly shows off a new haircut that is noticeably uneven. Other friends exchange glances. One speaks up.",
        "utterance": "It's certainly... a bold choice.",
        "cue": "Hedging ('certainly'), ellipsis, and the word 'bold' as euphemism for bad; requires reading social discomfort cues",
    },
    {
        "id": "S29", "is_sarcastic": True, "difficulty": 2,
        "context": "Someone who vocally opposed remote work for years is now working from home themselves after a policy change benefits their commute. A colleague who fought for the remote policy comments to another.",
        "utterance": "Funny how remote work suddenly became a great idea.",
        "cue": "Hypocrisy-based sarcasm; no direct contradiction in the utterance itself, requires knowing the speaker's history",
    },
    {
        "id": "S30", "is_sarcastic": True, "difficulty": 2,
        "context": "At a dinner party, the host spent the entire evening talking about their own vacation, never asking anyone else a question. As guests leave, one says to another in the elevator.",
        "utterance": "What a fascinating conversationalist.",
        "cue": "One-sided monologue doesn't qualify as conversation; surface praise is literally applicable but pragmatically sarcastic",
    },

    # ═══ SINCERE UTTERANCES (Tier 2) ═══
    # These LOOK like they could be sarcastic but context supports sincerity.
    {
        "id": "N21", "is_sarcastic": False, "difficulty": 2,
        "context": "A notoriously strict professor gives a student surprisingly positive feedback on a draft, with constructive suggestions that are actually encouraging. The student has been working with a tutor and improved significantly. They text a friend.",
        "utterance": "I'm sure this time will be different. I actually feel prepared.",
        "cue": "Despite pattern suggesting sarcasm, the genuine improvement and added context ('I actually feel prepared') signals sincerity",
    },
    {
        "id": "N22", "is_sarcastic": False, "difficulty": 2,
        "context": "A new team lead who was initially skeptical about agile methodology has watched it transform their team's output over six months. Velocity doubled and morale improved. They report to their director.",
        "utterance": "Funny how agile turned out to be exactly what we needed.",
        "cue": "Shares structure with sarcasm ('funny how X') but genuine surprise at positive outcome; speaker admits they were wrong",
    },
    {
        "id": "N23", "is_sarcastic": False, "difficulty": 2,
        "context": "A friend who usually gives terrible gift suggestions actually researched your hobby extensively and found the exact rare book you'd been hunting for months. You tell your partner about it.",
        "utterance": "They were incredibly helpful. Really went above and beyond.",
        "cue": "Sounds sarcastic given the friend's track record, but the genuine effort and perfect result make it sincere",
    },
    {
        "id": "N24", "is_sarcastic": False, "difficulty": 2,
        "context": "After years of tense holidays, a family member who used to make cutting remarks has been in therapy and genuinely apologized. At this year's gathering, they were warm and asked thoughtful questions. You reflect afterward.",
        "utterance": "It's certainly a different dynamic now.",
        "cue": "Hedging language ('certainly') could signal sarcasm, but context shows genuine reflection on positive change",
    },
    {
        "id": "N25", "is_sarcastic": False, "difficulty": 2,
        "context": "A restaurant with mixed online reviews turns out to have a chef who trained in Kyoto. The omakase was exquisite — surprising depth for a strip-mall location. You post a review.",
        "utterance": "What a fascinating culinary experience. Don't judge it by the location.",
        "cue": "The unlikely setting makes praise sound ironic, but the genuine quality makes it sincere; the caveat confirms earnestness",
    },

    # ═══════════════════════════════════════════════════════════════
    # TIER 3 — SUBTLE / AMBIGUOUS (difficulty=3)
    # Deadpan, understatement, cultural patterns, cases where the
    # literal reading is almost equally plausible. A human would
    # need to think twice.
    # ═══════════════════════════════════════════════════════════════

    # ═══ SARCASTIC UTTERANCES (Tier 3) ═══
    {
        "id": "S31", "is_sarcastic": True, "difficulty": 3,
        "context": "A software engineer's code review has 47 comments, mostly nitpicks about variable naming and whitespace. The actual logic is fine. They message a friend.",
        "utterance": "Got some really thorough feedback on my code today.",
        "cue": "Deadpan delivery; 'thorough' is literally true but used to mock pedantry. No tonal marker — requires understanding that 47 nitpick comments is excessive, not admirable",
    },
    {
        "id": "S32", "is_sarcastic": True, "difficulty": 3,
        "context": "Two British colleagues are leaving a mandatory corporate team-building exercise where they had to do trust falls and share feelings in a circle. One turns to the other on the walk back.",
        "utterance": "Well, that was time well spent.",
        "cue": "British understatement; the flat delivery and cultural context of British reserve toward forced emotional exercises makes this sarcastic, but the words alone are perfectly neutral",
    },
    {
        "id": "S33", "is_sarcastic": True, "difficulty": 3,
        "context": "A novelist whose last three books were bestsellers is asked at a reading about their writing process. They know their 'process' is mostly procrastinating, panicking, then writing the whole thing in two weeks.",
        "utterance": "Oh, I have a very disciplined routine.",
        "cue": "Self-deprecating sarcasm disguised as boasting; the speaker knows the truth contradicts the claim, but the audience can't tell. Requires theory of mind about private knowledge",
    },
    {
        "id": "S34", "is_sarcastic": True, "difficulty": 3,
        "context": "After a company layoff that cut 30% of staff, the CEO sends an all-hands email saying the company is 'stronger than ever' and 'well-positioned for growth.' An employee reads it aloud to a colleague.",
        "utterance": "Stronger than ever. Can't argue with that.",
        "cue": "Quoting corporate euphemism with flat affect; 'can't argue with that' is deadpan agreement that actually signals disbelief. The massive layoff makes 'stronger' absurd but it's never explicitly contradicted",
    },
    {
        "id": "S35", "is_sarcastic": True, "difficulty": 3,
        "context": "A PhD student has been working on their dissertation for seven years. Their advisor keeps adding new requirements. A fellow student asks how it's going.",
        "utterance": "Making progress. Should be done any day now.",
        "cue": "Understatement meets impossible timeline; 'any day now' after seven years is deadpan humor, but could literally be true if they were actually close to finishing",
    },
    {
        "id": "S36", "is_sarcastic": True, "difficulty": 3,
        "context": "A friend invested heavily in a cryptocurrency that dropped 90% in value. They haven't sold. Another friend asks how their investment portfolio is doing.",
        "utterance": "Oh, it's been a real learning experience.",
        "cue": "'Learning experience' is a euphemism for disaster; the speaker reframes catastrophic loss as education. Literally true — they did learn something — but the pragmatic force is self-mocking",
    },
    {
        "id": "S37", "is_sarcastic": True, "difficulty": 3,
        "context": "At a neighborhood meeting about a proposed development that would block everyone's ocean view, the developer's representative describes it as 'enhancing the community character.' A longtime resident turns to their spouse.",
        "utterance": "Enhancing our character. How thoughtful of them.",
        "cue": "Echoing euphemistic language with the addition of 'how thoughtful' — the surface reading is gratitude but pragmatically signals contempt for spin. Requires understanding the stakes (lost ocean views)",
    },
    {
        "id": "S38", "is_sarcastic": True, "difficulty": 3,
        "context": "A person who spent months training for a marathon finishes in last place, over an hour behind the second-to-last runner. At the finish line, breathing hard, they tell the volunteer handing out water.",
        "utterance": "I like to give the crowd their money's worth.",
        "cue": "Self-deprecating humor; the literal reading (entertaining the crowd) is a deflection from disappointment. Not obviously sarcastic — could be genuine good humor about a bad result, but the months of serious training suggest the levity masks real frustration",
    },
    {
        "id": "S39", "is_sarcastic": True, "difficulty": 3,
        "context": "A couple has been arguing about whose turn it is to do dishes for ten minutes. Finally one of them starts doing them. The other watches for a moment.",
        "utterance": "Thank you. I appreciate it.",
        "cue": "Surface-level sincere gratitude, but after a prolonged argument about obligation, 'thank you' functions as a victory marker rather than genuine appreciation. Requires understanding relational dynamics and that gratitude can be wielded as a power move",
    },
    {
        "id": "S40", "is_sarcastic": True, "difficulty": 3,
        "context": "An architect designed a building that won several awards but has chronic leaking problems. When a journalist asks about the leaks, they respond in an interview.",
        "utterance": "Every great building has its quirks.",
        "cue": "Reframing a serious flaw as a charming 'quirk'; the speaker is being sarcastic about their own problem by minimizing it with a euphemism. But it could be read as sincere philosophical acceptance",
    },

    # ═══ SINCERE UTTERANCES (Tier 3) ═══
    # Genuinely meant statements that share the linguistic patterns of
    # sarcasm — deadpan delivery, euphemism, understatement. A model
    # must resist the sarcasm-pattern trigger.
    {
        "id": "N26", "is_sarcastic": False, "difficulty": 3,
        "context": "A startup founder whose company nearly went bankrupt twice before finding product-market fit is interviewed about the early years. They're reflective, not bitter — the struggle genuinely shaped their leadership style.",
        "utterance": "Oh, it's been a real learning experience.",
        "cue": "Identical phrasing to S36 but context shows genuine growth narrative, not loss-masking. The founder's reflective tone and actual positive outcome make this sincere",
    },
    {
        "id": "N27", "is_sarcastic": False, "difficulty": 3,
        "context": "A retired teacher who volunteers tutoring underprivileged kids is asked why they don't just enjoy retirement. They've found genuine purpose in the work and their students' progress is measurable.",
        "utterance": "Well, it's time well spent.",
        "cue": "Same flat phrasing as S32 but the speaker's voluntary commitment and concrete results signal sincerity; no external pressure to perform enthusiasm",
    },
    {
        "id": "N28", "is_sarcastic": False, "difficulty": 3,
        "context": "A writer who genuinely wakes at 5 AM every day, writes for exactly three hours, then edits for two, is asked about their process at a book festival. They're matter-of-fact, almost boring about it.",
        "utterance": "Oh, I have a very disciplined routine.",
        "cue": "Identical to S33 but this speaker actually does have the routine. The flat, unremarkable delivery matches genuine boringness rather than self-deprecating irony",
    },
    {
        "id": "N29", "is_sarcastic": False, "difficulty": 3,
        "context": "An old building in a historic district was carefully restored by a preservation architect. It has original features that occasionally cause minor maintenance issues — drafty windows, creaky floors — but the architect genuinely believes these add character and the community agrees.",
        "utterance": "Every great building has its quirks.",
        "cue": "Identical to S40 but here the 'quirks' are genuine historic charm, not euphemism for failure. The community agreement and the architect's known preservation philosophy make this sincere",
    },
    {
        "id": "N30", "is_sarcastic": False, "difficulty": 3,
        "context": "After a difficult but ultimately productive couples therapy session where both partners made real breakthroughs, one partner does the dishes without being asked. The other watches for a moment, feeling genuinely grateful for the shift.",
        "utterance": "Thank you. I appreciate it.",
        "cue": "Identical to S39 but the therapy context transforms the dynamic — this is genuine gratitude after emotional growth, not a power move after an argument. Requires distinguishing post-conflict warmth from post-argument scoring",
    },

    # ═══════════════════════════════════════════════════════════════
    # TIER 3 EXTENSION — MAXIMALLY AMBIGUOUS (difficulty=3)
    # These items are designed to be genuinely hard. The correct
    # answer often depends on subtle contextual cues that even
    # humans might miss. Models that default to pattern-matching
    # surface markers will fail.
    # ═══════════════════════════════════════════════════════════════

    # ── Sarcastic items that LOOK sincere ──
    {
        "id": "S41", "is_sarcastic": True, "difficulty": 3,
        "context": "A doctor has been on call for 36 hours straight. A nurse asks if they want to take a break. The doctor, running on caffeine and barely functioning, responds with a perfectly calm, measured tone.",
        "utterance": "No, I'm doing great. Really enjoying the challenge.",
        "cue": "Extreme fatigue makes 'doing great' implausible, but the calm delivery mimics sincerity. Requires recognizing that 36 hours without sleep overrides verbal composure",
    },
    {
        "id": "S42", "is_sarcastic": True, "difficulty": 3,
        "context": "A parent is helping their child with 5th-grade math homework for the third hour. The child has erased and rewritten the same problem eight times. The parent's spouse asks from the other room how it's going.",
        "utterance": "We're making excellent progress.",
        "cue": "Three hours on elementary math with 8 rewrites contradicts 'excellent progress,' but the parent might genuinely be patient. Sarcasm is directed at the spouse, not the child — requires inferring the parent's frustration from context duration",
    },
    {
        "id": "S43", "is_sarcastic": True, "difficulty": 3,
        "context": "Two professors are reviewing a graduate student's thesis draft. The draft is competent but contains 14 instances of the phrase 'it is important to note that' and 23 instances of 'in the literature.' One professor looks up from the manuscript.",
        "utterance": "The student certainly has a consistent style.",
        "cue": "'Consistent style' is literally true — the repetition IS consistent. But the raised eyebrow (looking up) and the context of academic writing where repetition is a flaw signals dry academic humor. Very hard without understanding academic norms",
    },
    {
        "id": "S44", "is_sarcastic": True, "difficulty": 3,
        "context": "A Japanese businessman has been asked the same question three different ways by a foreign colleague who clearly doesn't understand the polite refusal embedded in his first answer. He responds with increased formality.",
        "utterance": "That is a very interesting proposal. We will certainly consider it carefully.",
        "cue": "In Japanese business culture, increased formality after repeated questioning is a strong rejection signal. 'Interesting' + 'consider carefully' is the polite Japanese no. Requires cultural competence in high-context communication",
    },
    {
        "id": "S45", "is_sarcastic": True, "difficulty": 3,
        "context": "A chef has been asked to make a vegan, gluten-free, nut-free, soy-free version of their signature chocolate truffle cake. They respond to the server who relayed the request.",
        "utterance": "Of course. I live for creative challenges like this.",
        "cue": "Surface reading is enthusiasm about dietary accommodation. But the cumulative restrictions make the dish essentially impossible while maintaining quality. 'Live for' is performative enthusiasm masking professional frustration. Could genuinely be enthusiastic if chef is known for dietary innovation",
    },
    {
        "id": "S46", "is_sarcastic": True, "difficulty": 3,
        "context": "An IT support person receives their 47th ticket of the day asking them to 'just quickly' reset a password. They respond to the user with a friendly tone.",
        "utterance": "Happy to help! That's what I'm here for.",
        "cue": "Standard customer service language delivered sincerely in isolation. Sarcasm only detectable if you infer that the 47th identical request has eroded genuine helpfulness. The friendly tone is professional masking",
    },
    {
        "id": "S47", "is_sarcastic": True, "difficulty": 3,
        "context": "Two old friends meet after ten years. One has gained significant weight, lost most of their hair, and looks visibly aged. The other takes them in for a moment.",
        "utterance": "You look exactly the same.",
        "cue": "Social convention — everyone says this at reunions. But when the physical changes are dramatic enough, 'exactly the same' becomes a socially-obligatory lie that both parties recognize. Sarcasm here is compassionate rather than mocking, making it very hard to classify",
    },

    # ── Sincere items that LOOK sarcastic ──
    {
        "id": "N31", "is_sarcastic": False, "difficulty": 3,
        "context": "A manager who was recently diagnosed with a terminal illness has found unexpected peace in their remaining time. They've simplified their life, reconnected with family, and stopped worrying about career advancement. A colleague cautiously asks how they're doing.",
        "utterance": "Honestly? I'm doing great. Best I've felt in years.",
        "cue": "Terminal illness + 'doing great' pattern-matches to sarcasm, but the context of genuine psychological transformation (well-documented in palliative care literature) makes this sincere. The 'honestly' prefix is a sincerity marker, not a sarcasm amplifier",
    },
    {
        "id": "N32", "is_sarcastic": False, "difficulty": 3,
        "context": "A musician who lost their hearing in one ear has spent two years adapting their technique. They've developed a unique style that critics now praise as innovative. An interviewer asks about the disability.",
        "utterance": "It was the best thing that ever happened to my music.",
        "cue": "Disability + superlative positive claim triggers sarcasm detection. But genuine artistic transformation from constraint is well-documented (Beethoven, Django Reinhardt). The critical acclaim provides external validation of the sincere claim",
    },
    {
        "id": "N33", "is_sarcastic": False, "difficulty": 3,
        "context": "A person was fired from a toxic job six months ago. It forced them to start the business they'd been dreaming about for years. The business is now profitable. An old colleague from the toxic job asks how they're handling it.",
        "utterance": "Getting fired was the best thing they ever did for me.",
        "cue": "Being fired + 'best thing' is a classic sarcasm pattern. But the profitable business outcome and the retrospective framing (six months later, not the day of) make this a genuine reappraisal. Requires temporal reasoning about how perspective changes",
    },
    {
        "id": "N34", "is_sarcastic": False, "difficulty": 3,
        "context": "A soldier returned from deployment with PTSD and spent three years in intensive therapy. They now work as a trauma counselor helping other veterans. A journalist profiles them.",
        "utterance": "I wouldn't trade that experience for anything.",
        "cue": "Combat trauma + 'wouldn't trade it' seems like bitter sarcasm. But post-traumatic growth is a documented phenomenon — the speaker genuinely values the empathy and purpose gained. The current role as trauma counselor validates the sincerity",
    },
    {
        "id": "N35", "is_sarcastic": False, "difficulty": 3,
        "context": "A renowned minimalist architect is showing a client their design for a house — bare concrete walls, no ornamental features, exposed structural elements. The client's friend whispers to the client.",
        "utterance": "It's beautiful, isn't it? The restraint is extraordinary.",
        "cue": "'Beautiful' applied to bare concrete sounds sarcastic to most people. But in minimalist aesthetics, restraint IS the beauty. If the friend is also an architecture enthusiast (implied by being brought to the showing), this is genuine appreciation. Requires domain knowledge of aesthetic values",
    },
    {
        "id": "N36", "is_sarcastic": False, "difficulty": 3,
        "context": "A grandmother has been learning to use a smartphone for six months. She just successfully video-called her grandchildren overseas for the first time, though it took her 20 minutes to figure out the interface. Her daughter watches.",
        "utterance": "She's really getting the hang of technology.",
        "cue": "20 minutes for a video call + elderly person + technology triggers the sarcasm template. But genuine pride in an elderly parent's effort is equally plausible. The daughter's watching suggests supportive attention, and 'getting the hang of' acknowledges the learning curve while affirming progress",
    },
    {
        "id": "N37", "is_sarcastic": False, "difficulty": 3,
        "context": "A competitive eater has just finished consuming 73 hot dogs in 10 minutes at the Nathan's contest. A spectator who is genuinely fascinated by competitive eating turns to their companion.",
        "utterance": "Now that's what I call talent.",
        "cue": "Competitive eating + 'talent' triggers irony detection in most contexts. But competitive eating has genuine fans who view it as a legitimate sport/skill. The spectator's established fascination makes this sincere admiration, not mockery",
    },
    {
        "id": "N38", "is_sarcastic": False, "difficulty": 3,
        "context": "An art collector has just paid $120,000 for a painting that consists of a single red dot on a white canvas. A fellow collector who specializes in minimalist art examines it closely.",
        "utterance": "This is worth every penny. The precision of that dot is remarkable.",
        "cue": "$120K for a dot on canvas is the setup for every art-world sarcasm joke. But in the world of minimalist art collection, this IS a genuine value judgment. The fellow collector's specialization establishes domain expertise that makes the praise sincere",
    },
]

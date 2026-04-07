"""
Sarcasm detection in conversational context items.

40 utterances (20 sarcastic, 20 sincere) with rich conversational context.
Model rates sincerity 0-100. We measure AUC discrimination and calibration.

Design principles:
- Rich context required to distinguish sarcasm from sincerity
- Matched pairs: similar surface-level statements, different intent
- Context provides the disambiguating cues (incongruity, speaker frustration, etc.)
"""

SARCASM_ITEMS = [
    # ═══ SARCASTIC UTTERANCES ═══
    {
        "id": "S01", "is_sarcastic": True,
        "context": "After waiting 45 minutes for a simple coffee order at a café that prides itself on speed.",
        "utterance": "Well, that was quick service!",
        "cue": "Long wait contradicts 'quick'",
    },
    {
        "id": "S02", "is_sarcastic": True,
        "context": "A student receives back their essay with more red ink than black. The professor had written corrections on nearly every line.",
        "utterance": "Wow, looks like I really nailed that essay.",
        "cue": "Heavy corrections contradict 'nailed it'",
    },
    {
        "id": "S03", "is_sarcastic": True,
        "context": "Two hikers are completely soaked after getting caught in an unexpected downpour. Their gear is wet and they're shivering.",
        "utterance": "Perfect hiking weather, just like the forecast said.",
        "cue": "Downpour contradicts 'perfect weather'",
    },
    {
        "id": "S04", "is_sarcastic": True,
        "context": "A driver has been stuck in traffic for 3 hours on what should have been a 30-minute commute.",
        "utterance": "I just love my commute.",
        "cue": "3-hour delay contradicts 'love'",
    },
    {
        "id": "S05", "is_sarcastic": True,
        "context": "A colleague just gave a presentation full of errors, misread data, and forgot half their slides.",
        "utterance": "That was really impressive work up there.",
        "cue": "Disastrous presentation contradicts 'impressive'",
    },
    {
        "id": "S06", "is_sarcastic": True,
        "context": "The restaurant served a steak that was charred black on the outside and cold in the middle.",
        "utterance": "My compliments to the chef.",
        "cue": "Badly cooked food contradicts praise",
    },
    {
        "id": "S07", "is_sarcastic": True,
        "context": "A team member who promised to finish a critical report by Monday shows up on Thursday saying they haven't started.",
        "utterance": "I'm so glad I could count on you.",
        "cue": "Broken promise contradicts reliability",
    },
    {
        "id": "S08", "is_sarcastic": True,
        "context": "Someone parks their car right across two parking spaces in a crowded lot.",
        "utterance": "What a considerate person.",
        "cue": "Inconsiderate parking contradicts 'considerate'",
    },
    {
        "id": "S09", "is_sarcastic": True,
        "context": "A friend suggests eating at the restaurant where you got food poisoning last month.",
        "utterance": "Oh great, my favorite place! Last time was such a wonderful experience.",
        "cue": "Food poisoning contradicts 'wonderful'",
    },
    {
        "id": "S10", "is_sarcastic": True,
        "context": "It's the fifth time this month the office printer has jammed. Paper is stuck everywhere and toner is leaking.",
        "utterance": "This printer is truly a marvel of modern technology.",
        "cue": "Constant malfunctions contradict 'marvel'",
    },
    {
        "id": "S11", "is_sarcastic": True,
        "context": "A child tracks mud all over the freshly mopped kitchen floor.",
        "utterance": "Thanks for helping me keep the floor clean.",
        "cue": "Mud everywhere contradicts 'clean'",
    },
    {
        "id": "S12", "is_sarcastic": True,
        "context": "The new software update deleted all of a user's saved preferences and introduced three new bugs.",
        "utterance": "What a fantastic improvement! I love the new features.",
        "cue": "Bugs and data loss contradict 'improvement'",
    },
    {
        "id": "S13", "is_sarcastic": True,
        "context": "A meeting that was supposed to last 15 minutes has now been going on for 2.5 hours with no resolution.",
        "utterance": "This is a really productive use of our time.",
        "cue": "Endless, unproductive meeting contradicts 'productive'",
    },
    {
        "id": "S14", "is_sarcastic": True,
        "context": "An athlete falls on their face during the first hurdle of the race.",
        "utterance": "Textbook form right there.",
        "cue": "Falling contradicts 'textbook form'",
    },
    {
        "id": "S15", "is_sarcastic": True,
        "context": "Someone gives directions that lead you in a complete circle back to where you started.",
        "utterance": "Well, those were incredibly helpful directions.",
        "cue": "Going in circles contradicts 'helpful'",
    },
    {
        "id": "S16", "is_sarcastic": True,
        "context": "A friend shows you their sunburn that covers their entire back after falling asleep at the beach without sunscreen.",
        "utterance": "Smart decision skipping the sunscreen.",
        "cue": "Severe sunburn contradicts 'smart'",
    },
    {
        "id": "S17", "is_sarcastic": True,
        "context": "A construction project next door starts jackhammering at 6 AM on a Saturday.",
        "utterance": "What a lovely way to wake up on the weekend.",
        "cue": "Jackhammering at 6 AM contradicts 'lovely'",
    },
    {
        "id": "S18", "is_sarcastic": True,
        "context": "A mechanic says your car repair will cost $4,000, triple the original estimate.",
        "utterance": "What a pleasant surprise that price is.",
        "cue": "Triple the expected cost contradicts 'pleasant surprise'",
    },
    {
        "id": "S19", "is_sarcastic": True,
        "context": "Your flight has been delayed for the fourth time. It's now 8 hours behind schedule.",
        "utterance": "This airline really has their act together.",
        "cue": "Repeated delays contradict 'act together'",
    },
    {
        "id": "S20", "is_sarcastic": True,
        "context": "A coworker microwaves fish in the shared office kitchen. The smell fills the entire floor.",
        "utterance": "Mmm, what a delightful aroma.",
        "cue": "Offensive fish smell contradicts 'delightful aroma'",
    },
    
    # ═══ SINCERE UTTERANCES ═══
    {
        "id": "N01", "is_sarcastic": False,
        "context": "A barista quickly prepares a complex coffee order in under 2 minutes during a slow period.",
        "utterance": "Well, that was quick service!",
        "cue": "2 minutes is genuinely fast for a complex order",
    },
    {
        "id": "N02", "is_sarcastic": False,
        "context": "A student receives back their essay with a perfect score and a note saying 'Excellent analysis throughout.'",
        "utterance": "Wow, looks like I really nailed that essay.",
        "cue": "Perfect score confirms the claim",
    },
    {
        "id": "N03", "is_sarcastic": False,
        "context": "Two hikers are enjoying a sunny day with clear skies and mild temperatures, exactly as the weather app predicted.",
        "utterance": "Perfect hiking weather, just like the forecast said.",
        "cue": "Weather is genuinely perfect",
    },
    {
        "id": "N04", "is_sarcastic": False,
        "context": "A driver who recently moved closer to work now has a scenic 10-minute drive along the coast.",
        "utterance": "I just love my commute.",
        "cue": "Short scenic drive is genuinely enjoyable",
    },
    {
        "id": "N05", "is_sarcastic": False,
        "context": "A colleague delivered a polished presentation with clear data, engaging visuals, and received a standing ovation.",
        "utterance": "That was really impressive work up there.",
        "cue": "Standing ovation confirms the praise",
    },
    {
        "id": "N06", "is_sarcastic": False,
        "context": "The restaurant served the best filet mignon you've ever tasted — perfectly seared, seasoned, and tender.",
        "utterance": "My compliments to the chef.",
        "cue": "Excellent food justifies the praise",
    },
    {
        "id": "N07", "is_sarcastic": False,
        "context": "A team member stayed up all weekend to finish a critical report early, saving the whole team from a deadline crunch.",
        "utterance": "I'm so glad I could count on you.",
        "cue": "Going above and beyond confirms reliability",
    },
    {
        "id": "N08", "is_sarcastic": False,
        "context": "Someone notices another driver carefully backing into a tight spot without touching any other cars, and then leaving extra space.",
        "utterance": "What a considerate person.",
        "cue": "Careful parking justifies the comment",
    },
    {
        "id": "N09", "is_sarcastic": False,
        "context": "A friend suggests trying the new Italian restaurant that just won the city's best newcomer award.",
        "utterance": "Oh great, sounds like an excellent choice! I've been wanting to try that place.",
        "cue": "Award-winning restaurant justifies enthusiasm",
    },
    {
        "id": "N10", "is_sarcastic": False,
        "context": "The office gets a brand-new printer that prints in color, scans, and has never jammed in a month of use.",
        "utterance": "This printer is truly a marvel of modern technology.",
        "cue": "Reliable new printer justifies the praise",
    },
    {
        "id": "N11", "is_sarcastic": False,
        "context": "A child voluntarily mops the kitchen floor after tracking in some mud, leaving it cleaner than before.",
        "utterance": "Thanks for helping me keep the floor clean.",
        "cue": "Child actually cleaned up",
    },
    {
        "id": "N12", "is_sarcastic": False,
        "context": "The latest software update added dark mode, faster load times, and fixed the bugs users had been reporting.",
        "utterance": "What a fantastic improvement! I love the new features.",
        "cue": "Genuine improvements justify the praise",
    },
    {
        "id": "N13", "is_sarcastic": False,
        "context": "A 15-minute standup meeting finishes early after the team efficiently resolved three blockers.",
        "utterance": "This is a really productive use of our time.",
        "cue": "Efficient problem-solving justifies the comment",
    },
    {
        "id": "N14", "is_sarcastic": False,
        "context": "An athlete clears every hurdle with perfect timing, setting a new personal best.",
        "utterance": "Textbook form right there.",
        "cue": "Perfect execution justifies the comment",
    },
    {
        "id": "N15", "is_sarcastic": False,
        "context": "Someone gives you detailed directions that lead you directly to the destination, saving 20 minutes vs. the GPS route.",
        "utterance": "Well, those were incredibly helpful directions.",
        "cue": "Time-saving directions justify the praise",
    },
    {
        "id": "N16", "is_sarcastic": False,
        "context": "A friend shows you their perfect, even tan after spending a week at the beach using SPF 50 regularly.",
        "utterance": "Smart decision with the sunscreen.",
        "cue": "Perfect tan with no burn confirms the claim",
    },
    {
        "id": "N17", "is_sarcastic": False,
        "context": "You wake up on Saturday to birds singing outside your window on a sunny spring morning.",
        "utterance": "What a lovely way to wake up on the weekend.",
        "cue": "Genuinely pleasant morning",
    },
    {
        "id": "N18", "is_sarcastic": False,
        "context": "A mechanic finds the issue was just a loose wire, and the repair costs only $50 instead of the feared $500.",
        "utterance": "What a pleasant surprise that price is.",
        "cue": "Genuinely surprising low cost",
    },
    {
        "id": "N19", "is_sarcastic": False,
        "context": "Your flight departs exactly on time, and the airline upgrades you to business class for free.",
        "utterance": "This airline really has their act together.",
        "cue": "On-time departure + free upgrade justifies praise",
    },
    {
        "id": "N20", "is_sarcastic": False,
        "context": "A coworker bakes homemade cinnamon rolls and brings them to the office. The smell of fresh pastry fills the floor.",
        "utterance": "Mmm, what a delightful aroma.",
        "cue": "Fresh cinnamon rolls genuinely smell good",
    },
]

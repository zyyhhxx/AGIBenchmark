"""
False-belief Theory of Mind (ToM) scenarios.

Sally-Anne style scenarios testing 1st-order and 2nd-order belief attribution.
Each scenario includes:
- A narrative with character actions and belief-relevant events
- A belief question (what does X think/believe?)
- A reality control question (what is actually the case?)
- A memory control question (where was the object originally?)

Control questions ensure the model understands the story — the key metric
is belief accuracy MINUS control accuracy to isolate ToM from comprehension.

Based on:
- Wimmer & Perner (1983): original false-belief task
- Baron-Cohen, Leslie & Frith (1985): Sally-Anne test
- Perner & Wimmer (1985): 2nd-order false beliefs
"""

FALSE_BELIEF_SCENARIOS = [
    # ═══ 1ST-ORDER FALSE BELIEFS ═══
    # Character A doesn't know about a change that happened in their absence
    
    {
        "id": "FB01",
        "order": 1,
        "scenario": (
            "Sally puts her marble in the basket and leaves the room. "
            "While Sally is away, Anne moves the marble from the basket to the box. "
            "Sally comes back."
        ),
        "belief_question": "Where will Sally look for her marble?",
        "belief_answer": "basket",
        "belief_accept": ["basket"],
        "reality_question": "Where is the marble really?",
        "reality_answer": "box",
        "reality_accept": ["box"],
        "memory_question": "Where did Sally put the marble in the beginning?",
        "memory_answer": "basket",
        "memory_accept": ["basket"],
    },
    {
        "id": "FB02",
        "order": 1,
        "scenario": (
            "Tom places his sandwich in the blue cupboard and goes to play outside. "
            "His mother moves the sandwich from the blue cupboard to the green cupboard. "
            "Tom comes back inside because he is hungry."
        ),
        "belief_question": "Where will Tom look for his sandwich first?",
        "belief_answer": "blue cupboard",
        "belief_accept": ["blue cupboard", "blue"],
        "reality_question": "Where is the sandwich actually?",
        "reality_answer": "green cupboard",
        "reality_accept": ["green cupboard", "green"],
        "memory_question": "Where did Tom originally put his sandwich?",
        "memory_answer": "blue cupboard",
        "memory_accept": ["blue cupboard", "blue"],
    },
    {
        "id": "FB03",
        "order": 1,
        "scenario": (
            "Maria hides her diary under her pillow and goes to school. "
            "Her sister finds the diary and puts it in the desk drawer. "
            "Maria returns from school wanting to read her diary."
        ),
        "belief_question": "Where will Maria look for her diary?",
        "belief_answer": "under the pillow",
        "belief_accept": ["pillow", "under the pillow", "under her pillow"],
        "reality_question": "Where is the diary now?",
        "reality_answer": "desk drawer",
        "reality_accept": ["desk drawer", "drawer", "desk"],
        "memory_question": "Where did Maria hide her diary?",
        "memory_answer": "under her pillow",
        "memory_accept": ["pillow", "under the pillow", "under her pillow"],
    },
    {
        "id": "FB04",
        "order": 1,
        "scenario": (
            "Chef Roberto stores his special knife in the top drawer and leaves for lunch. "
            "The sous chef borrows the knife and leaves it in the bottom drawer. "
            "Roberto returns to prepare dinner."
        ),
        "belief_question": "Where will Roberto look for his knife?",
        "belief_answer": "top drawer",
        "belief_accept": ["top drawer", "top"],
        "reality_question": "Where is the knife?",
        "reality_answer": "bottom drawer",
        "reality_accept": ["bottom drawer", "bottom"],
        "memory_question": "Where did Roberto originally store his knife?",
        "memory_answer": "top drawer",
        "memory_accept": ["top drawer", "top"],
    },
    {
        "id": "FB05",
        "order": 1,
        "scenario": (
            "Lisa leaves her umbrella in the coat closet at the office and goes to a meeting. "
            "The janitor moves all umbrellas from the coat closet to the lost-and-found box by the entrance. "
            "It starts raining and Lisa returns to get her umbrella."
        ),
        "belief_question": "Where will Lisa look for her umbrella?",
        "belief_answer": "coat closet",
        "belief_accept": ["coat closet", "closet"],
        "reality_question": "Where is the umbrella?",
        "reality_answer": "lost-and-found box",
        "reality_accept": ["lost-and-found", "lost and found", "entrance"],
        "memory_question": "Where did Lisa leave her umbrella?",
        "memory_answer": "coat closet",
        "memory_accept": ["coat closet", "closet"],
    },
    {
        "id": "FB06",
        "order": 1,
        "scenario": (
            "David parks his bicycle at the front rack of the library and goes inside to study. "
            "A security guard moves all bikes from the front rack to the side rack because of construction. "
            "David finishes studying and goes to get his bicycle."
        ),
        "belief_question": "Where will David look for his bicycle first?",
        "belief_answer": "front rack",
        "belief_accept": ["front rack", "front"],
        "reality_question": "Where is the bicycle actually?",
        "reality_answer": "side rack",
        "reality_accept": ["side rack", "side"],
        "memory_question": "Where did David park his bicycle?",
        "memory_answer": "front rack",
        "memory_accept": ["front rack", "front"],
    },
    {
        "id": "FB07",
        "order": 1,
        "scenario": (
            "Emma puts her cat's food bowl in the kitchen and leaves for work. "
            "Her roommate rearranges and moves the food bowl to the laundry room. "
            "Emma comes home to feed the cat."
        ),
        "belief_question": "Where will Emma look for the cat's food bowl?",
        "belief_answer": "kitchen",
        "belief_accept": ["kitchen"],
        "reality_question": "Where is the food bowl?",
        "reality_answer": "laundry room",
        "reality_accept": ["laundry room", "laundry"],
        "memory_question": "Where did Emma put the food bowl?",
        "memory_answer": "kitchen",
        "memory_accept": ["kitchen"],
    },
    {
        "id": "FB08",
        "order": 1,
        "scenario": (
            "Mr. Chen puts his reading glasses on the coffee table and goes to answer the phone. "
            "His grandson takes the glasses and puts them on the bookshelf. "
            "Mr. Chen returns to continue reading."
        ),
        "belief_question": "Where will Mr. Chen look for his glasses?",
        "belief_answer": "coffee table",
        "belief_accept": ["coffee table"],
        "reality_question": "Where are the glasses?",
        "reality_answer": "bookshelf",
        "reality_accept": ["bookshelf", "book shelf", "shelf"],
        "memory_question": "Where did Mr. Chen put his glasses?",
        "memory_answer": "coffee table",
        "memory_accept": ["coffee table"],
    },
    {
        "id": "FB09",
        "order": 1,
        "scenario": (
            "Priya puts her phone charger in the living room outlet and goes to take a shower. "
            "Her brother unplugs it and plugs it into the bedroom outlet for his own phone. "
            "Priya comes out of the shower needing to charge her phone."
        ),
        "belief_question": "Where will Priya look for her charger?",
        "belief_answer": "living room outlet",
        "belief_accept": ["living room"],
        "reality_question": "Where is the charger?",
        "reality_answer": "bedroom outlet",
        "reality_accept": ["bedroom"],
        "memory_question": "Where did Priya plug in her charger?",
        "memory_answer": "living room outlet",
        "memory_accept": ["living room"],
    },
    {
        "id": "FB10",
        "order": 1,
        "scenario": (
            "Sam leaves his backpack on the bench by the playground and joins a soccer game. "
            "A teacher collects unattended bags and puts Sam's backpack in the main office. "
            "The game ends and Sam goes to get his backpack."
        ),
        "belief_question": "Where will Sam look for his backpack?",
        "belief_answer": "bench by the playground",
        "belief_accept": ["bench", "playground"],
        "reality_question": "Where is the backpack?",
        "reality_answer": "main office",
        "reality_accept": ["office", "main office"],
        "memory_question": "Where did Sam leave his backpack?",
        "memory_answer": "bench by the playground",
        "memory_accept": ["bench", "playground"],
    },
    
    # ═══ 2ND-ORDER FALSE BELIEFS ═══
    # Character A thinks Character B thinks X, but B actually knows Y
    
    {
        "id": "FB11",
        "order": 2,
        "scenario": (
            "John and Mary are in the kitchen. John puts the chocolate in the green cabinet. "
            "John leaves for school. While John is away, Mary moves the chocolate to the red cabinet. "
            "But John comes back briefly and secretly sees Mary moving the chocolate to the red cabinet, "
            "without Mary noticing that John saw this."
        ),
        "belief_question": "Where does Mary think John will look for the chocolate?",
        "belief_answer": "green cabinet",
        "belief_accept": ["green cabinet", "green"],
        "reality_question": "Where is the chocolate actually?",
        "reality_answer": "red cabinet",
        "reality_accept": ["red cabinet", "red"],
        "memory_question": "Where did John originally put the chocolate?",
        "memory_answer": "green cabinet",
        "memory_accept": ["green cabinet", "green"],
    },
    {
        "id": "FB12",
        "order": 2,
        "scenario": (
            "Alice and Bob work in an office. Alice leaves her project folder on her desk and goes to a meeting. "
            "Bob moves the folder to the filing cabinet to organize. Alice walks past the filing cabinet on her way back "
            "and sees her folder there, but Bob doesn't know Alice saw this."
        ),
        "belief_question": "Where does Bob think Alice will look for her folder?",
        "belief_answer": "her desk",
        "belief_accept": ["desk", "her desk"],
        "reality_question": "Where is the folder?",
        "reality_answer": "filing cabinet",
        "reality_accept": ["filing cabinet", "cabinet"],
        "memory_question": "Where did Alice originally leave the folder?",
        "memory_answer": "her desk",
        "memory_accept": ["desk", "her desk"],
    },
    {
        "id": "FB13",
        "order": 2,
        "scenario": (
            "Pedro and Clara are at home. Pedro puts his keys in the bowl by the door and goes upstairs. "
            "Clara moves the keys from the bowl to the hook by the door. Pedro has a security camera "
            "and watches Clara move the keys on his phone, but Clara doesn't know about the camera."
        ),
        "belief_question": "Where does Clara think Pedro will look for his keys?",
        "belief_answer": "bowl by the door",
        "belief_accept": ["bowl"],
        "reality_question": "Where are the keys?",
        "reality_answer": "hook by the door",
        "reality_accept": ["hook"],
        "memory_question": "Where did Pedro put his keys?",
        "memory_answer": "bowl by the door",
        "memory_accept": ["bowl"],
    },
    {
        "id": "FB14",
        "order": 2,
        "scenario": (
            "Nina and Leo are siblings. Nina hides her diary under the mattress and goes to school. "
            "Leo finds the diary and moves it behind the bookcase. "
            "Nina's friend texts her that she saw Leo carrying something behind the bookcase. "
            "Leo doesn't know about the text message."
        ),
        "belief_question": "Where does Leo think Nina will look for her diary?",
        "belief_answer": "under the mattress",
        "belief_accept": ["mattress", "under the mattress"],
        "reality_question": "Where is the diary?",
        "reality_answer": "behind the bookcase",
        "reality_accept": ["bookcase", "behind the bookcase"],
        "memory_question": "Where did Nina hide her diary?",
        "memory_answer": "under the mattress",
        "memory_accept": ["mattress", "under the mattress"],
    },
    {
        "id": "FB15",
        "order": 2,
        "scenario": (
            "Raj and Mei share an apartment. Raj puts the TV remote on the sofa and goes to the kitchen. "
            "Mei puts the remote in the drawer. Raj overhears Mei telling herself 'I'll put this in the drawer,' "
            "but Mei doesn't realize Raj can hear her from the kitchen."
        ),
        "belief_question": "Where does Mei think Raj will look for the remote?",
        "belief_answer": "sofa",
        "belief_accept": ["sofa", "couch"],
        "reality_question": "Where is the remote?",
        "reality_answer": "drawer",
        "reality_accept": ["drawer"],
        "memory_question": "Where did Raj put the remote?",
        "memory_answer": "sofa",
        "memory_accept": ["sofa", "couch"],
    },
    {
        "id": "FB16",
        "order": 2,
        "scenario": (
            "Olivia and Ethan are coworkers. Olivia puts the stapler in the supply closet and goes to lunch. "
            "Ethan takes the stapler to his desk. Olivia comes back early and sees the stapler on Ethan's desk "
            "through the glass door without Ethan noticing."
        ),
        "belief_question": "Where does Ethan think Olivia will look for the stapler?",
        "belief_answer": "supply closet",
        "belief_accept": ["supply closet", "closet"],
        "reality_question": "Where is the stapler?",
        "reality_answer": "Ethan's desk",
        "reality_accept": ["ethan's desk", "his desk", "desk"],
        "memory_question": "Where did Olivia put the stapler?",
        "memory_answer": "supply closet",
        "memory_accept": ["supply closet", "closet"],
    },
    {
        "id": "FB17",
        "order": 2,
        "scenario": (
            "Yuki and Marco are roommates. Yuki puts a package on the kitchen counter and leaves for class. "
            "Marco moves the package to Yuki's room as a favor. Yuki's classmate texts her: "
            "'I saw your roommate carrying a package to your room.' Marco doesn't know about the text."
        ),
        "belief_question": "Where does Marco think Yuki will look for the package?",
        "belief_answer": "kitchen counter",
        "belief_accept": ["kitchen counter", "kitchen", "counter"],
        "reality_question": "Where is the package?",
        "reality_answer": "Yuki's room",
        "reality_accept": ["yuki's room", "her room", "room"],
        "memory_question": "Where did Yuki leave the package?",
        "memory_answer": "kitchen counter",
        "memory_accept": ["kitchen counter", "kitchen", "counter"],
    },
    {
        "id": "FB18",
        "order": 2,
        "scenario": (
            "Aisha and Liam are at a party. Aisha puts her purse on the chair in the living room and goes to dance. "
            "Liam moves the purse to the coat room for safety. Aisha's friend whispers to her: "
            "'Liam took your purse to the coat room.' Liam doesn't know the friend told Aisha."
        ),
        "belief_question": "Where does Liam think Aisha will look for her purse?",
        "belief_answer": "chair in the living room",
        "belief_accept": ["chair", "living room"],
        "reality_question": "Where is the purse?",
        "reality_answer": "coat room",
        "reality_accept": ["coat room"],
        "memory_question": "Where did Aisha put her purse?",
        "memory_answer": "chair in the living room",
        "memory_accept": ["chair", "living room"],
    },
    {
        "id": "FB19",
        "order": 2,
        "scenario": (
            "Carlos and Diana are at the beach. Carlos buries a toy in the sand near the red umbrella and goes swimming. "
            "Diana digs it up and reburies it near the blue umbrella. Carlos floats in the water and can see Diana "
            "digging near the blue umbrella, but Diana faces away and doesn't see Carlos watching."
        ),
        "belief_question": "Where does Diana think Carlos will look for the toy?",
        "belief_answer": "near the red umbrella",
        "belief_accept": ["red umbrella", "red"],
        "reality_question": "Where is the toy?",
        "reality_answer": "near the blue umbrella",
        "reality_accept": ["blue umbrella", "blue"],
        "memory_question": "Where did Carlos bury the toy?",
        "memory_answer": "near the red umbrella",
        "memory_accept": ["red umbrella", "red"],
    },
    {
        "id": "FB20",
        "order": 2,
        "scenario": (
            "Fatima and George are housemates. Fatima puts the milk in the left side of the fridge and goes to work. "
            "George reorganizes the fridge and puts the milk on the right side. Fatima has a smart fridge camera app "
            "and sees the change on her phone, but George doesn't know about the app."
        ),
        "belief_question": "Where does George think Fatima will look for the milk?",
        "belief_answer": "left side of the fridge",
        "belief_accept": ["left side", "left"],
        "reality_question": "Where is the milk?",
        "reality_answer": "right side of the fridge",
        "reality_accept": ["right side", "right"],
        "memory_question": "Where did Fatima put the milk?",
        "memory_answer": "left side of the fridge",
        "memory_accept": ["left side", "left"],
    },
]

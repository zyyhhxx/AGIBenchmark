"""
False-belief Theory of Mind (ToM) scenarios — v5b.

Difficulty tiers:
- 1st-order (4 scenarios): standard Sally-Anne false belief  
- 2nd-order (4 scenarios): "A thinks B thinks..."
- 3rd-order (6 scenarios): "A thinks B thinks C believes..."
- 4th-order (12 scenarios): 3-level nesting with ignorant outer characters
- 5th-order (8 scenarios): 5-level nesting with DOUBLE LIES at different chain positions
  The answer varies based on which lie the model resolves at which level.

Key design innovation for 5th-order: Two lies at different points create scenarios
where the answer DIFFERS at each nesting level. The model must track which lie
affects which character's belief independently.

Based on: Wimmer & Perner (1983), Kinderman et al. (1998), Miller (2009), Dunbar (1998).
"""

FALSE_BELIEF_SCENARIOS = [
    # ═══ 1ST-ORDER FALSE BELIEFS (4 scenarios) ═══
    {
        "id": "FB01", "order": 1,
        "scenario": "Sally puts her marble in the basket and leaves the room. While Sally is away, Anne moves the marble from the basket to the box. Sally comes back.",
        "belief_question": "Where will Sally look for her marble?",
        "belief_answer": "basket", "belief_accept": ["basket"],
        "reality_question": "Where is the marble really?",
        "reality_answer": "box", "reality_accept": ["box"],
        "memory_question": "Where did Sally put the marble in the beginning?",
        "memory_answer": "basket", "memory_accept": ["basket"],
    },
    {
        "id": "FB02", "order": 1,
        "scenario": "Tom places his sandwich in the blue cupboard and goes to play outside. His mother moves the sandwich from the blue cupboard to the green cupboard. Tom comes back inside because he is hungry.",
        "belief_question": "Where will Tom look for his sandwich first?",
        "belief_answer": "blue cupboard", "belief_accept": ["blue cupboard", "blue"],
        "reality_question": "Where is the sandwich actually?",
        "reality_answer": "green cupboard", "reality_accept": ["green cupboard", "green"],
        "memory_question": "Where did Tom originally put his sandwich?",
        "memory_answer": "blue cupboard", "memory_accept": ["blue cupboard", "blue"],
    },
    {
        "id": "FB03", "order": 1,
        "scenario": "Maria hides her diary under her pillow and goes to school. Her sister finds the diary and puts it in the desk drawer. Maria returns from school wanting to read her diary.",
        "belief_question": "Where will Maria look for her diary?",
        "belief_answer": "under the pillow", "belief_accept": ["pillow", "under the pillow", "under her pillow"],
        "reality_question": "Where is the diary now?",
        "reality_answer": "desk drawer", "reality_accept": ["desk drawer", "drawer", "desk"],
        "memory_question": "Where did Maria hide her diary?",
        "memory_answer": "under her pillow", "memory_accept": ["pillow", "under the pillow", "under her pillow"],
    },
    {
        "id": "FB04", "order": 1,
        "scenario": "Chef Roberto stores his special knife in the top drawer and leaves for lunch. The sous chef borrows the knife and leaves it in the bottom drawer. Roberto returns to prepare dinner.",
        "belief_question": "Where will Roberto look for his knife?",
        "belief_answer": "top drawer", "belief_accept": ["top drawer", "top"],
        "reality_question": "Where is the knife?",
        "reality_answer": "bottom drawer", "reality_accept": ["bottom drawer", "bottom"],
        "memory_question": "Where did Roberto originally store his knife?",
        "memory_answer": "top drawer", "memory_accept": ["top drawer", "top"],
    },

    # ═══ 2ND-ORDER FALSE BELIEFS (4 scenarios) ═══
    {
        "id": "FB11", "order": 2,
        "scenario": "John and Mary are in the kitchen. John puts the chocolate in the green cabinet. John leaves for school. While John is away, Mary moves the chocolate to the red cabinet. But John comes back briefly and secretly sees Mary moving the chocolate to the red cabinet, without Mary noticing that John saw this.",
        "belief_question": "Where does Mary think John will look for the chocolate?",
        "belief_answer": "green cabinet", "belief_accept": ["green cabinet", "green"],
        "reality_question": "Where is the chocolate actually?",
        "reality_answer": "red cabinet", "reality_accept": ["red cabinet", "red"],
        "memory_question": "Where did John originally put the chocolate?",
        "memory_answer": "green cabinet", "memory_accept": ["green cabinet", "green"],
    },
    {
        "id": "FB12", "order": 2,
        "scenario": "Alice and Bob work in an office. Alice leaves her project folder on her desk and goes to a meeting. Bob moves the folder to the filing cabinet to organize. Alice walks past the filing cabinet on her way back and sees her folder there, but Bob doesn't know Alice saw this.",
        "belief_question": "Where does Bob think Alice will look for her folder?",
        "belief_answer": "her desk", "belief_accept": ["desk", "her desk"],
        "reality_question": "Where is the folder?",
        "reality_answer": "filing cabinet", "reality_accept": ["filing cabinet", "cabinet"],
        "memory_question": "Where did Alice originally leave the folder?",
        "memory_answer": "her desk", "memory_accept": ["desk", "her desk"],
    },
    {
        "id": "FB13", "order": 2,
        "scenario": "Pedro and Clara are at home. Pedro puts his keys in the bowl by the door and goes upstairs. Clara moves the keys from the bowl to the hook by the door. Pedro has a security camera and watches Clara move the keys on his phone, but Clara doesn't know about the camera.",
        "belief_question": "Where does Clara think Pedro will look for his keys?",
        "belief_answer": "bowl by the door", "belief_accept": ["bowl"],
        "reality_question": "Where are the keys?",
        "reality_answer": "hook by the door", "reality_accept": ["hook"],
        "memory_question": "Where did Pedro put his keys?",
        "memory_answer": "bowl by the door", "memory_accept": ["bowl"],
    },
    {
        "id": "FB14", "order": 2,
        "scenario": "Nina and Leo are siblings. Nina hides her diary under the mattress and goes to school. Leo finds the diary and moves it behind the bookcase. Nina's friend texts her that she saw Leo carrying something behind the bookcase. Leo doesn't know about the text message.",
        "belief_question": "Where does Leo think Nina will look for her diary?",
        "belief_answer": "under the mattress", "belief_accept": ["mattress", "under the mattress"],
        "reality_question": "Where is the diary?",
        "reality_answer": "behind the bookcase", "reality_accept": ["bookcase", "behind the bookcase"],
        "memory_question": "Where did Nina hide her diary?",
        "memory_answer": "under the mattress", "memory_accept": ["mattress", "under the mattress"],
    },

    # ═══ 3RD-ORDER FALSE BELIEFS (6 scenarios) ═══
    {
        "id": "FB21", "order": 3,
        "scenario": "Alice, Bob, and Carol are in a classroom. Alice puts a toy car in the red box and leaves. Bob, who stayed, watches Carol move the toy car from the red box to the yellow box. Then Bob also leaves. Carol then moves the toy car again, from the yellow box to the green box. Bob does NOT know about this second move. Alice does NOT know about any moves. Later, Alice and Bob meet in the hallway. Alice asks Bob where Carol would have put the toy car.",
        "belief_question": "Where does Alice think Bob thinks the toy car is?",
        "belief_answer": "red box", "belief_accept": ["red box", "red"],
        "reality_question": "Where is the toy car actually?",
        "reality_answer": "green box", "reality_accept": ["green box", "green"],
        "memory_question": "Where did Alice originally put the toy car?",
        "memory_answer": "red box", "memory_accept": ["red box", "red"],
    },
    {
        "id": "FB22", "order": 3,
        "scenario": "Dan, Eve, and Frank work at a warehouse. Dan stores a crate in Bay 1 and goes on break. Eve sees Frank move the crate from Bay 1 to Bay 3. Eve then leaves. After Eve leaves, Frank moves the crate again from Bay 3 to Bay 5, but Eve doesn't see this. Dan never returned and knows nothing about any moves. Eve calls Dan and says 'I saw Frank move your crate.'",
        "belief_question": "Where does Dan think Eve thinks the crate is?",
        "belief_answer": "Bay 3", "belief_accept": ["bay 3", "3"],
        "reality_question": "Where is the crate actually?",
        "reality_answer": "Bay 5", "reality_accept": ["bay 5", "5"],
        "memory_question": "Where did Dan originally store the crate?",
        "memory_answer": "Bay 1", "memory_accept": ["bay 1", "1"],
    },
    {
        "id": "FB23", "order": 3,
        "scenario": "Grace, Henry, and Irene share a house. Grace puts the cookies in the pantry and goes upstairs. Henry watches Irene move the cookies from the pantry to the fridge. Henry then goes to his room. While Henry is in his room, Irene eats all the cookies and throws away the empty container. Henry doesn't know the cookies are gone. Grace doesn't know about any changes.",
        "belief_question": "Where does Grace think Henry thinks the cookies are?",
        "belief_answer": "pantry", "belief_accept": ["pantry"],
        "reality_question": "Are there any cookies left?",
        "reality_answer": "no", "reality_accept": ["no", "none", "eaten", "gone", "thrown away"],
        "memory_question": "Where did Grace put the cookies originally?",
        "memory_answer": "pantry", "memory_accept": ["pantry"],
    },
    {
        "id": "FB24", "order": 3,
        "scenario": "Jack, Kim, and Leo are at a picnic. Jack hides a prize under the oak tree and goes to get drinks. Kim sees Leo move the prize from under the oak tree to under the maple tree. Kim tells Jack on the phone: 'Leo moved your prize.' But Kim left before Leo moved it a second time — Leo actually moved it again from the maple tree to under the pine tree. Jack doesn't know about the second move.",
        "belief_question": "Where does Jack think Kim thinks the prize is?",
        "belief_answer": "maple tree", "belief_accept": ["maple tree", "maple"],
        "reality_question": "Where is the prize actually?",
        "reality_answer": "pine tree", "reality_accept": ["pine tree", "pine"],
        "memory_question": "Where did Jack originally hide the prize?",
        "memory_answer": "oak tree", "memory_accept": ["oak tree", "oak"],
    },
    {
        "id": "FB25", "order": 3,
        "scenario": "Mia, Nathan, and Olivia are in a museum. Mia places her sketchbook on Bench A and goes to view a painting. Nathan watches Olivia pick up the sketchbook and put it on Bench B. Nathan then leaves the room. After Nathan leaves, Olivia realizes she made a mistake and moves the sketchbook to Bench C. Mia returns. She didn't see anything. Nathan, who left, still thinks the sketchbook is on Bench B.",
        "belief_question": "Where does Mia think Nathan thinks the sketchbook is?",
        "belief_answer": "Bench A", "belief_accept": ["bench a", "a"],
        "reality_question": "Where is the sketchbook actually?",
        "reality_answer": "Bench C", "reality_accept": ["bench c", "c"],
        "memory_question": "Where did Mia put the sketchbook?",
        "memory_answer": "Bench A", "memory_accept": ["bench a", "a"],
    },
    {
        "id": "FB26", "order": 3,
        "scenario": "Paul, Quinn, and Rosa are in a lab. Paul locks Sample X in Cabinet 1 and goes to a meeting. Quinn observes Rosa transfer Sample X from Cabinet 1 to Cabinet 2. Quinn leaves a note for Paul: 'Rosa moved Sample X.' But Quinn wrote the note before Rosa made a second transfer — Rosa later moved Sample X from Cabinet 2 to the Cold Room. Quinn doesn't know about this second transfer.",
        "belief_question": "Where does Paul think Quinn thinks Sample X is?",
        "belief_answer": "Cabinet 2", "belief_accept": ["cabinet 2", "2"],
        "reality_question": "Where is Sample X actually?",
        "reality_answer": "Cold Room", "reality_accept": ["cold room"],
        "memory_question": "Where did Paul lock Sample X?",
        "memory_answer": "Cabinet 1", "memory_accept": ["cabinet 1", "1"],
    },

    # ═══ 4TH-ORDER FALSE BELIEFS (12 scenarios) ═══
    {
        "id": "FB29", "order": 4,
        "scenario": "Four colleagues — Amy, Ben, Cora, and Dave — share an office. Amy puts a USB drive in Drawer 1 and leaves for a conference. Ben watches Cora move the USB from Drawer 1 to Drawer 2. Ben then tells Dave about the move. Dave acknowledges but then secretly moves the USB from Drawer 2 to Drawer 3 when neither Ben nor Cora is looking. Ben doesn't know Dave moved it again. Cora doesn't know Dave moved it. Amy doesn't know about any moves. Amy calls Ben to ask about the USB.",
        "belief_question": "Where does Amy think Ben thinks Dave thinks the USB drive is?",
        "belief_answer": "Drawer 2", "belief_accept": ["drawer 2", "2"],
        "reality_question": "Where is the USB drive actually?",
        "reality_answer": "Drawer 3", "reality_accept": ["drawer 3", "3"],
        "memory_question": "Where did Amy originally put the USB drive?",
        "memory_answer": "Drawer 1", "memory_accept": ["drawer 1", "1"],
    },
    {
        "id": "FB30", "order": 4,
        "scenario": "Elena, Finn, Gina, and Hugo are planning a surprise party. Elena hides the birthday cake in the garage and tells Finn. Finn watches Gina (who doesn't know about the plan) move the cake to the basement because the garage was warm. Finn mentions to Hugo: 'Gina moved the cake to the basement.' Hugo thinks this is a bad spot and moves the cake from the basement to the attic, but tells no one. Finn still thinks the cake is in the basement. Gina still thinks the cake is in the basement. Elena only knows she put it in the garage.",
        "belief_question": "Where does Elena think Finn thinks Hugo thinks the cake is?",
        "belief_answer": "basement", "belief_accept": ["basement"],
        "reality_question": "Where is the cake actually?",
        "reality_answer": "attic", "reality_accept": ["attic"],
        "memory_question": "Where did Elena originally hide the cake?",
        "memory_answer": "garage", "memory_accept": ["garage"],
    },
    {
        "id": "FB31", "order": 4,
        "scenario": "Ian, Julia, Kyle, and Lily are at summer camp. Ian buries a treasure map under the flag pole and tells Julia where it is. Julia watches Kyle dig up the map and rebury it under the big rock. Julia doesn't intervene. Julia then tells Lily: 'Kyle moved the map to under the big rock.' After Julia walks away, Lily moves the map from under the big rock to inside the hollow log, without telling anyone. Julia doesn't know Lily moved it. Kyle doesn't know Lily moved it. Ian only knows about the flag pole location.",
        "belief_question": "Where does Ian think Julia thinks Lily thinks the map is?",
        "belief_answer": "big rock", "belief_accept": ["big rock", "rock"],
        "reality_question": "Where is the map actually?",
        "reality_answer": "hollow log", "reality_accept": ["hollow log", "log"],
        "memory_question": "Where did Ian originally bury the map?",
        "memory_answer": "flag pole", "memory_accept": ["flag pole", "flagpole"],
    },
    {
        "id": "FB32", "order": 4,
        "scenario": "Four scientists — Dr. Park, Dr. Quinn, Dr. Reed, and Dr. Stone — share a laboratory. Dr. Park stores a rare reagent in Freezer A and informs Dr. Quinn. Dr. Quinn sees Dr. Reed move the reagent from Freezer A to Shelf B for an experiment. Dr. Quinn tells Dr. Stone: 'Dr. Reed moved the reagent to Shelf B.' Dr. Stone, worried about temperature, moves the reagent from Shelf B back to Freezer C (a different freezer). Dr. Stone tells no one about this move. Dr. Quinn still believes it's on Shelf B. Dr. Reed thinks it's still on Shelf B. Dr. Park only knows about Freezer A.",
        "belief_question": "Where does Dr. Park think Dr. Quinn thinks Dr. Stone thinks the reagent is?",
        "belief_answer": "Shelf B", "belief_accept": ["shelf b", "b"],
        "reality_question": "Where is the reagent actually?",
        "reality_answer": "Freezer C", "reality_accept": ["freezer c", "c"],
        "memory_question": "Where did Dr. Park originally store the reagent?",
        "memory_answer": "Freezer A", "memory_accept": ["freezer a", "a"],
    },
    {
        "id": "FB33", "order": 4,
        "scenario": "Four roommates — Nora, Oscar, Pam, and Quinn — share an apartment. Nora hides a birthday gift in the hall closet and tells Oscar. Oscar watches Pam find the gift and move it to the bedroom closet (Pam doesn't know it's a birthday gift — she's just tidying). Oscar mentions to Quinn: 'Pam moved something to the bedroom closet.' Quinn, being helpful, wraps the gift and moves it from the bedroom closet to the living room shelf, telling no one. Oscar still believes the gift is in the bedroom closet. Pam thinks she left it in the bedroom closet. Nora only knows about the hall closet.",
        "belief_question": "Where does Nora think Oscar thinks Quinn thinks the gift is?",
        "belief_answer": "bedroom closet", "belief_accept": ["bedroom closet", "bedroom"],
        "reality_question": "Where is the gift actually?",
        "reality_answer": "living room shelf", "reality_accept": ["living room shelf", "living room", "shelf"],
        "memory_question": "Where did Nora originally hide the gift?",
        "memory_answer": "hall closet", "memory_accept": ["hall closet", "hall"],
    },
    {
        "id": "FB34", "order": 4,
        "scenario": "At a school, Ms. Adams puts the exam papers in the safe and tells Mr. Brown. Mr. Brown watches Ms. Chen move the papers from the safe to her desk drawer to grade them. Mr. Brown tells Mr. Davis: 'Ms. Chen has the papers in her desk drawer.' Mr. Davis decides to collect the papers and moves them from Ms. Chen's desk drawer to the principal's office filing cabinet. Mr. Davis doesn't tell anyone. Mr. Brown still thinks the papers are in Ms. Chen's desk drawer. Ms. Chen went home and thinks the papers are in her desk drawer. Ms. Adams only knows about the safe.",
        "belief_question": "Where does Ms. Adams think Mr. Brown thinks Mr. Davis thinks the papers are?",
        "belief_answer": "desk drawer", "belief_accept": ["desk drawer", "drawer", "desk"],
        "reality_question": "Where are the papers actually?",
        "reality_answer": "filing cabinet", "reality_accept": ["filing cabinet", "principal"],
        "memory_question": "Where did Ms. Adams originally put the papers?",
        "memory_answer": "safe", "memory_accept": ["safe"],
    },
    {
        "id": "FB35", "order": 4,
        "scenario": "Four neighbors — Wei, Xavier, Yuki, and Zara — share a community garden tool shed. Wei puts a rare seed packet in Bin A and tells Xavier. Xavier sees Yuki take the seed packet from Bin A and put it in Bin B to sort the bins. Xavier mentions to Zara: 'Yuki moved the seeds to Bin B.' Zara needs the seeds and takes them from Bin B to her own garden plot, but doesn't tell anyone. Xavier still thinks the seeds are in Bin B. Yuki thinks they're in Bin B. Wei only knows about Bin A.",
        "belief_question": "Where does Wei think Xavier thinks Zara thinks the seeds are?",
        "belief_answer": "Bin B", "belief_accept": ["bin b", "b"],
        "reality_question": "Where are the seeds actually?",
        "reality_answer": "Zara's garden plot", "reality_accept": ["garden plot", "zara's garden", "her garden"],
        "memory_question": "Where did Wei originally put the seeds?",
        "memory_answer": "Bin A", "memory_accept": ["bin a", "a"],
    },
    {
        "id": "FB36", "order": 4, "misleading": True,
        "scenario": "Four friends — Anna, Blake, Cara, and Derek — are at a carnival. Anna wins a stuffed bear and puts it in Locker 1, telling Blake. Blake watches Cara borrow the bear to show her sister, placing it in Locker 2 afterward. Blake tells Derek: 'Cara put the bear in Locker 2.' Derek moves the bear from Locker 2 to Locker 3, then lies to Blake: 'I checked and the bear is still in Locker 2.' Blake believes Derek. Anna only knows about Locker 1. Cara thinks the bear is in Locker 2.",
        "belief_question": "Where does Anna think Blake thinks Derek thinks the bear is?",
        "belief_answer": "locker 2", "belief_accept": ["locker 2", "2"],
        "misleading_answer": ["locker 3", "3"],
        "reality_question": "Where is the bear actually?",
        "reality_answer": "Locker 3", "reality_accept": ["locker 3", "3"],
        "memory_question": "Where did Anna originally put the bear?",
        "memory_answer": "Locker 1", "memory_accept": ["locker 1", "1"],
    },
    {
        "id": "FB37", "order": 4, "misleading": True,
        "scenario": "Four museum staff — Gloria, Hank, Iris, and Jake — manage artifacts. Gloria places a vase in Display Case A and tells Hank. Hank watches Iris move the vase to Storage Room B for cleaning. Hank tells Jake: 'Iris moved the vase to Storage Room B.' Jake returns the cleaned vase to Display Case C (a different case), but lies to Hank: 'I put it back in Display Case A.' Hank now thinks the vase is in Display Case A. Iris thinks the vase is in Storage Room B. Gloria only knows about Display Case A.",
        "belief_question": "Where does Gloria think Hank thinks the vase is?",
        "belief_answer": "Display Case A", "belief_accept": ["display case a", "case a", "a"],
        "misleading_answer": ["storage room b", "display case c"],
        "reality_question": "Where is the vase actually?",
        "reality_answer": "Display Case C", "reality_accept": ["display case c", "case c", "c"],
        "memory_question": "Where did Gloria originally place the vase?",
        "memory_answer": "Display Case A", "memory_accept": ["display case a", "case a", "a"],
    },
    {
        "id": "FB38", "order": 4,
        "scenario": "Four hikers — Ken, Luna, Marco, and Nina — are on a trail. Ken stashes the first aid kit under the stone bridge and tells Luna. Luna sees Marco take the kit and put it in the hollow tree. Luna tells Nina: 'Marco moved the kit to the hollow tree.' Nina decides it should be more accessible and moves it from the hollow tree to the trail marker post, but tells no one. Luna still thinks the kit is in the hollow tree. Marco thinks it's in the hollow tree. Ken only knows about the stone bridge.",
        "belief_question": "Where does Ken think Luna thinks Nina thinks the kit is?",
        "belief_answer": "hollow tree", "belief_accept": ["hollow tree", "tree"],
        "reality_question": "Where is the kit actually?",
        "reality_answer": "trail marker post", "reality_accept": ["trail marker", "marker post", "post"],
        "memory_question": "Where did Ken originally stash the kit?",
        "memory_answer": "stone bridge", "memory_accept": ["stone bridge", "bridge"],
    },
    {
        "id": "FB46", "order": 4, "misleading": True,
        "scenario": "Rachel, Sam, Tara, and Uma are organizing a scavenger hunt. Rachel hides a clue under the fountain and tells Sam. Sam watches Tara move the clue from the fountain to the garden shed. Sam tells Uma about this move. Uma then secretly moves the clue from the garden shed to the mailbox, telling no one. Later, Uma lies to Sam: 'I moved the clue to the pond.' Sam believes Uma. Sam tells Rachel: 'Uma moved the clue to the pond.' Rachel believes Sam. Tara doesn't know about any of the conversations.",
        "belief_question": "Where does Tara think Rachel thinks Sam thinks the clue is?",
        "belief_answer": "garden shed", "belief_accept": ["garden shed", "shed"],
        "misleading_answer": ["pond", "mailbox", "fountain"],
        "reality_question": "Where is the clue actually?",
        "reality_answer": "mailbox", "reality_accept": ["mailbox"],
        "memory_question": "Where did Rachel originally hide the clue?",
        "memory_answer": "fountain", "memory_accept": ["fountain"],
    },
    {
        "id": "FB47", "order": 4, "misleading": True,
        "scenario": "Four friends — Vera, Will, Xena, and Yusuf — are playing a game. Vera hides a token in Box 1 and tells Will. Will sees Xena move the token from Box 1 to Box 2. Will tells Yusuf: 'Xena moved it to Box 2.' Yusuf moves the token from Box 2 to Box 3 without telling anyone. Then Yusuf lies to Will: 'I checked and the token is still in Box 2.' Will believes this. Will then tells Vera: 'The token was moved to Box 2 and is still there.' Vera believes Will. Xena doesn't know about any of the conversations after her move.",
        "belief_question": "Where does Xena think Vera thinks the token is?",
        "belief_answer": "Box 1", "belief_accept": ["box 1", "1"],
        "misleading_answer": ["box 2", "box 3", "2", "3"],
        "reality_question": "Where is the token actually?",
        "reality_answer": "Box 3", "reality_accept": ["box 3", "3"],
        "memory_question": "Where did Vera originally hide the token?",
        "memory_answer": "Box 1", "memory_accept": ["box 1", "1"],
    },

    # ═══ 5TH-ORDER FALSE BELIEFS (8 scenarios) ═══
    # These use DIVERGENT BELIEF structures where different characters hold
    # genuinely different beliefs. The question targets a specific nesting
    # that requires tracking whose perspective differs from whom.

    {
        "id": "FB51", "order": 5,
        "scenario": (
            "Five people — Alice, Bob, Carol, Dan, and Eve — are involved in a complex situation.\n"
            "1. Alice puts a painting in Room 1.\n"
            "2. Bob sees Alice put it in Room 1. Bob then moves it to Room 2 without anyone seeing.\n"
            "3. Carol arrives. Bob lies to Carol: 'The painting is in Room 3.' Carol believes this.\n"
            "4. Dan arrives. Carol tells Dan: 'The painting is in Room 3.' Dan believes Carol.\n"
            "5. Eve arrives. Dan tells Eve: 'The painting is in Room 3.' Eve believes Dan.\n"
            "6. Alice still thinks the painting is in Room 1 (she never learned about any moves).\n"
            "7. Alice tells Eve: 'I put the painting in Room 1.' Eve now has conflicting information."
        ),
        "belief_question": "Where does Carol think Dan thinks the painting is?",
        "belief_answer": "Room 3", "belief_accept": ["room 3", "3"],
        "reality_question": "Where is the painting actually?",
        "reality_answer": "Room 2", "reality_accept": ["room 2", "2"],
        "memory_question": "Where did Alice originally put the painting?",
        "memory_answer": "Room 1", "memory_accept": ["room 1", "1"],
    },
    {
        "id": "FB52", "order": 5,
        "scenario": (
            "Five colleagues — Fiona, George, Hannah, Ivan, and Jasper — track a key.\n"
            "1. Fiona locks a key in Safe A and tells George.\n"
            "2. George moves the key to Safe B without telling anyone.\n"
            "3. Hannah sees George move the key to Safe B. Hannah tells Ivan: 'The key is in Safe B.'\n"
            "4. George lies to Jasper: 'The key is in Safe A.' Jasper believes George.\n"
            "5. Jasper tells Fiona: 'I confirmed the key is in Safe A.' Fiona believes Jasper.\n"
            "6. Ivan tells Jasper: 'Hannah says the key is in Safe B.' Jasper is confused but trusts George more, so Jasper still believes Safe A."
        ),
        "belief_question": "Where does Ivan think Jasper thinks the key is?",
        "belief_answer": "Safe B", "belief_accept": ["safe b", "b"],
        "reality_question": "Where is the key actually?",
        "reality_answer": "Safe B", "reality_accept": ["safe b", "b"],
        "memory_question": "Where did Fiona originally lock the key?",
        "memory_answer": "Safe A", "memory_accept": ["safe a", "a"],
    },
    {
        "id": "FB53", "order": 5,
        "scenario": (
            "Five friends — Kate, Leo, Mia, Nick, and Olga — discuss a document.\n"
            "1. Kate puts the document on Desk A and tells Leo.\n"
            "2. Leo moves the document to Shelf B. Leo tells Mia: 'I moved the document to Shelf B.'\n"
            "3. Mia tells Nick: 'The document is on Shelf B.'\n"
            "4. Nick moves the document from Shelf B to Drawer C without telling anyone.\n"
            "5. Olga asks Nick where the document is. Nick lies: 'It is on Shelf B.' Olga believes Nick.\n"
            "6. Olga tells Kate: 'The document is on Shelf B.' Kate now thinks it is on Shelf B.\n"
            "7. Kate does not know Leo moved it, and Leo does not know Nick moved it."
        ),
        "belief_question": "Where does Mia think Nick thinks Olga thinks the document is?",
        "belief_answer": "Shelf B", "belief_accept": ["shelf b", "b"],
        "reality_question": "Where is the document actually?",
        "reality_answer": "Drawer C", "reality_accept": ["drawer c", "c"],
        "memory_question": "Where did Kate originally put the document?",
        "memory_answer": "Desk A", "memory_accept": ["desk a", "a"],
    },
    {
        "id": "FB54", "order": 5,
        "scenario": (
            "Five students — Pat, Quinn, Rosa, Sam, and Tina — track a USB drive.\n"
            "1. Pat stores the USB in Locker 10 and tells Quinn.\n"
            "2. Quinn moves the USB to Locker 20 and tells Rosa: 'USB is in Locker 20.'\n"
            "3. Rosa tells Sam: 'USB is in Locker 20.' Sam believes Rosa.\n"
            "4. Tina finds the USB in Locker 20 and moves it to Locker 30 without telling anyone.\n"
            "5. Sam asks Tina where the USB is. Tina lies: 'It is in Locker 20.' Sam still believes Locker 20.\n"
            "6. Pat asks Sam. Sam says: 'USB is in Locker 20.' Pat believes Sam.\n"
            "7. Quinn does not know about any moves after Locker 20. Rosa does not know about Tina."
        ),
        "belief_question": "Where does Quinn think Sam thinks the USB is?",
        "belief_answer": "Locker 20", "belief_accept": ["locker 20", "20"],
        "reality_question": "Where is the USB actually?",
        "reality_answer": "Locker 30", "reality_accept": ["locker 30", "30"],
        "memory_question": "Where did Pat originally store the USB?",
        "memory_answer": "Locker 10", "memory_accept": ["locker 10", "10"],
    },
    {
        "id": "FB55", "order": 5,
        "scenario": (
            "Five chefs — Alain, Brigitte, Claude, Dominique, and Émile — track a truffle.\n"
            "1. Alain puts the truffle in Cold Room 1 and tells Brigitte.\n"
            "2. Brigitte moves the truffle to Prep Station 2 without telling Alain.\n"
            "3. Brigitte lies to Claude: 'The truffle is in Cold Room 1.' Claude believes this.\n"
            "4. Dominique independently sees Brigitte move the truffle to Prep Station 2.\n"
            "5. Dominique tells Émile: 'The truffle is at Prep Station 2.' Émile believes Dominique.\n"
            "6. Claude tells Émile: 'Brigitte told me the truffle is in Cold Room 1.'\n"
            "7. Émile now has conflicting information: Dominique said Prep Station 2, Claude said Cold Room 1. Émile trusts Dominique (who saw it directly) over Claude (who heard it secondhand).\n"
            "8. Claude does not know that Dominique saw the move. Alain still thinks Cold Room 1."
        ),
        "belief_question": "Where does Claude think Émile thinks the truffle is?",
        "belief_answer": "Cold Room 1", "belief_accept": ["cold room 1", "room 1"],
        "reality_question": "Where is the truffle actually?",
        "reality_answer": "Prep Station 2", "reality_accept": ["prep station 2", "station 2"],
        "memory_question": "Where did Alain originally put the truffle?",
        "memory_answer": "Cold Room 1", "memory_accept": ["cold room 1", "room 1"],
    },
    {
        "id": "FB56", "order": 5,
        "scenario": (
            "Five agents — Victor, Wendy, Xavier, Yara, and Zane — track a briefcase.\n"
            "1. Victor places the briefcase in Locker 10.\n"
            "2. Wendy moves the briefcase from Locker 10 to Locker 20. Wendy tells Xavier: 'Briefcase is in Locker 20.'\n"
            "3. Xavier tells Yara: 'Briefcase is in Locker 20.' Yara believes Xavier.\n"
            "4. Zane finds the briefcase in Locker 20 and moves it to Locker 30.\n"
            "5. Zane lies to Yara: 'The briefcase is still in Locker 20.' Yara still believes Locker 20.\n"
            "6. Separately, Zane tells Victor: 'I moved the briefcase to Locker 30.' Victor now believes Locker 30.\n"
            "7. Yara tells Wendy: 'Zane confirmed it is in Locker 20.' Wendy believes Yara.\n"
            "8. Xavier does not know about Zane moving it."
        ),
        "belief_question": "Where does Yara think Victor thinks the briefcase is?",
        "belief_answer": "Locker 10", "belief_accept": ["locker 10", "10"],
        "reality_question": "Where is the briefcase actually?",
        "reality_answer": "Locker 30", "reality_accept": ["locker 30", "30"],
        "memory_question": "Where did Victor originally place the briefcase?",
        "memory_answer": "Locker 10", "memory_accept": ["locker 10", "10"],
    },
    {
        "id": "FB57", "order": 5,
        "scenario": (
            "Five friends — Amir, Beth, Carlos, Diana, and Erik — track a golden coin.\n"
            "1. Amir hides the coin in the blue jar and tells Beth.\n"
            "2. Beth moves the coin to the red jar without telling Amir.\n"
            "3. Beth tells Carlos: 'The coin is in the red jar.' Carlos believes Beth.\n"
            "4. Diana overhears Beth and Carlos and learns the coin is in the red jar.\n"
            "5. Erik asks Amir where the coin is. Amir says: 'I put it in the blue jar.' Erik believes Amir.\n"
            "6. Erik tells Diana: 'Amir says the coin is in the blue jar.'\n"
            "7. Diana knows from overhearing that Beth moved it to the red jar, so Diana still believes red jar.\n"
            "8. Carlos does not know about Erik or Amir's conversation."
        ),
        "belief_question": "Where does Erik think Diana thinks the coin is?",
        "belief_answer": "blue jar", "belief_accept": ["blue jar", "blue"],
        "reality_question": "Where is the coin actually?",
        "reality_answer": "red jar", "reality_accept": ["red jar", "red"],
        "memory_question": "Where did Amir originally hide the coin?",
        "memory_answer": "blue jar", "memory_accept": ["blue jar", "blue"],
    },
    {
        "id": "FB58", "order": 5,
        "scenario": (
            "Five hospital staff — Dr. Liu, Nurse Patel, Dr. Kim, Nurse Chen, and Dr. Okafor — track a patient chart.\n"
            "1. Dr. Liu puts the chart in Cabinet A and tells Nurse Patel.\n"
            "2. Nurse Patel moves the chart to Station B and tells Dr. Kim: 'Chart is at Station B.'\n"
            "3. Dr. Kim tells Nurse Chen: 'Chart is at Station B.' Nurse Chen believes Dr. Kim.\n"
            "4. Dr. Okafor finds the chart at Station B and moves it to Office C without telling anyone.\n"
            "5. Dr. Okafor lies to Dr. Kim: 'I checked and the chart is at Station B.' Dr. Kim believes this.\n"
            "6. Separately, Nurse Chen sees Dr. Okafor carry the chart into Office C.\n"
            "7. Nurse Chen now knows the chart is in Office C, but she does not tell anyone.\n"
            "8. Dr. Kim tells Nurse Patel: 'Dr. Okafor confirmed Station B.' Nurse Patel believes."
        ),
        "belief_question": "Where does Dr. Kim think Nurse Chen thinks the chart is?",
        "belief_answer": "Station B", "belief_accept": ["station b", "b"],
        "reality_question": "Where is the chart actually?",
        "reality_answer": "Office C", "reality_accept": ["office c", "c"],
        "memory_question": "Where did Dr. Liu originally put the chart?",
        "memory_answer": "Cabinet A", "memory_accept": ["cabinet a", "a"],
    },
]

"""
Prompt for Feature 4: Hands-Free Activity Guide.
Grade-adaptive: LKG/UKG use play-based; higher grades use structured activities.
"""


def build(description: str, duration: int, grade: str, subject: str = "General", lang: str = "en") -> str:

    if lang == "hi":
        lang_rule = "शुद्ध हिंदी (Devanagari script) — NO Hinglish। सभी निर्देश, सामग्री, speak_intro हिंदी में।"
        action_eg  = "\"सभी बच्चों को गोले में बिठाएँ\""
    else:
        lang_rule = "Clear, simple English throughout."
        action_eg  = "\"Seat all children in a circle\""

    if grade in ("LKG", "UKG"):
        context = f"""
ACTIVITY TYPE: Play-based, sensory, fun — NO reading or writing required.
* Use songs, clapping, physical movement, colourful objects, storytelling
* Instructions must be doable by a 3-5 year old child
* Teacher's role: guide and demonstrate, children imitate
* Materials: only things found in any classroom (chalk, slate, coloured paper, fingers)
* Steps: max 4 steps, each max 2 minutes"""

    elif grade in ("1", "2", "3"):
        context = f"""
ACTIVITY TYPE: Hands-on, fun, simple — minimal reading/writing.
* Use drawing, sorting, matching, counting with objects, role-play
* Instructions simple enough for 6-9 year olds
* Materials: chalk, notebooks, small stones/sticks, paper
* Steps: 4-5 steps, each 2-4 minutes"""

    elif grade in ("4", "5"):
        context = f"""
ACTIVITY TYPE: Collaborative, inquiry-based.
* Students work in pairs or small groups
* Includes observation, discussion, simple recording
* Materials: basic classroom items + simple science materials
* Steps: 4-6 steps"""

    elif grade in ("6", "7", "8"):
        context = f"""
ACTIVITY TYPE: Cooperative learning with structured outcome.
* Groups of 3-5 students, clear roles
* Includes investigation, data collection, presentation
* Government school context: 30-50 students, limited resources
* Steps: 5-7 steps with clear teacher facilitation notes"""

    else:  # 9-12
        context = f"""
ACTIVITY TYPE: Project/experiment-based, board exam relevant.
* Higher-order thinking: analysis, evaluation, creation
* Can include numerical problems, case studies, debates, experiments
* Builds skills for board exams and beyond
* Steps: 5-7 structured steps with assessment component"""

    return f"""You are ShikshAI — an educational activity designer for Haryana government school teachers.

ACTIVITY REQUEST: "{description}"
CONSTRAINTS: {duration} minutes | Grade {grade} | Subject: {subject}

SCHOOL CONTEXT:
* Government school in Haryana — 30-50 students per class
* LIMITED resources: chalk, blackboard, notebooks, basic stationery
* Mixed-ability students
* Activity must work even with a substitute teacher

LANGUAGE RULE:
{lang_rule}

GRADE-APPROPRIATE DESIGN:
{context}

ACTION-ORIENTED instructions like {action_eg} — not passive descriptions.

Time management: step duration_min values must sum to ~{duration} minutes.

OUTPUT: Return ONLY valid JSON — no markdown:
{{
  "title": "Activity title (max 8 words)",
  "objective": "What students will be able to DO after this activity",
  "materials": ["Item 1", "Item 2", "Item 3 max"],
  "group_size": "Individual / Pairs / Groups of 4 / Whole class",
  "steps": [
    {{
      "step": 1,
      "instruction": "Clear action instruction",
      "duration_min": 3,
      "teacher_tip": "Quick facilitation hint"
    }}
  ],
  "teacher_note": "One critical classroom management tip",
  "assessment": "Quick 2-minute check method",
  "speak_intro": "Enthusiastic 2-3 sentence intro to read to the class"
}}
"""

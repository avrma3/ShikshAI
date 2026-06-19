"""
Prompt for Feature 1: Live Concept Simplification.
Grade-adaptive: LKG/UKG use story format; Class 1-5 simple; 6-10 standard; 11-12 advanced.
"""
from prompts.hindi_quality import get_hindi_lang_rule


def build(concept: str, grade: str, subject: str = "General", lang: str = "en") -> str:

    # ── Language rule ─────────────────────────────────────────────────────────
    if lang == "hi":
        lang_rule = (
            get_hindi_lang_rule(grade)
            + "\nCRITICAL: title सहित सभी fields हिंदी में होने चाहिए।"
        )
        speak_rule  = '"speak_text": "2-3 उत्साही हिंदी वाक्य जो कक्षा में ज़ोर से पढ़े जाएँ — natural teacher tone"'
        summary_key = "hindi_summary"
        summary_val = f"एक पंक्ति में {concept} का सरल, natural हिंदी सारांश"
    else:
        lang_rule = (
            "Clear, simple ENGLISH. Short sentences (max 12 words each).\n"
            "Warm tone. Relatable Indian analogies explained in English."
        )
        speak_rule  = '"speak_text": "2-3 enthusiastic English sentences to read aloud"'
        summary_key = "hindi_summary"
        summary_val = f"One-line summary of {concept}"

    # ── Grade-adaptive format ─────────────────────────────────────────────────
    if grade in ("LKG", "UKG"):
        format_rule = f"""
AUDIENCE: Kindergarten child (age 3-5). Use ONLY the simplest possible words.
FORMAT RULES (CRITICAL):
* explanation: 2 very short sentences MAX. Use the actual content directly.
  Example for "1 se 10 tak ginti": List the numbers AND their names. e.g. "1=एक, 2=दो, 3=तीन, 4=चार, 5=पाँच, 6=छः, 7=सात, 8=आठ, 9=नौ, 10=दस"
* example: One fun real-world example (fingers, fruits, toys)
* fun_fact: One exciting sentence a child will enjoy
* key_points: 3 items, max 5 words each — direct facts, not descriptions
* formula: empty string always
* mermaid: simple 4-node diagram only"""

    elif grade in ("1", "2", "3"):
        format_rule = f"""
AUDIENCE: Primary school child (Class {grade}, age 6-9). Simple but MORE DETAILED than kindergarten.
FORMAT RULES:
* explanation: 3 short sentences. Go BEYOND just naming things — explain HOW or WHY simply.
  For body parts: mention both external AND internal parts, what each does.
  For numbers: include basic operations. For plants: include parts AND functions.
  IMPORTANT: Class {grade} response must be clearly more informative than LKG/UKG.
* example: One concrete real-life example (home, school, village life)
* fun_fact: One interesting fact that surprises a child this age
* key_points: 3 points, max 6 words each — include FUNCTION not just NAME
* formula: only if truly applicable, else empty string
* mermaid: simple 4-5 node diagram showing relationships"""

    elif grade in ("4", "5"):
        format_rule = f"""
AUDIENCE: Upper primary student (Class {grade}, age 9-11).
FORMAT RULES:
* explanation: 3 sentences. Clear concept + one Indian analogy.
* example: One relatable example from school or village life
* fun_fact: One interesting fact about {concept}
* key_points: 3 points, max 8 words each
* formula: include if relevant (math/science)
* mermaid: 5-6 node diagram showing concept flow"""

    elif grade in ("6", "7", "8"):
        format_rule = f"""
AUDIENCE: Middle school student (Class {grade}, age 11-14).
FORMAT RULES:
* explanation: 3-4 sentences. Concept explanation + analogy + application.
* example: Concrete real-life example showing {concept} in action
* fun_fact: Surprising or counterintuitive fact
* key_points: 3 points, max 8 words each
* formula: include if applicable
* mermaid: 5-7 node diagram showing process/structure"""

    else:  # 9, 10, 11, 12
        format_rule = f"""
AUDIENCE: Secondary/Senior secondary student (Class {grade}, age 14-18).
FORMAT RULES:
* explanation: 4 sentences. Define precisely + mechanism/process + real-world significance.
* example: Specific scientific/mathematical/social example with numbers if possible
* fun_fact: Advanced interesting application or recent discovery
* key_points: 3 points, max 10 words each — include technical terms
* formula: IMPORTANT — include the key formula/equation if applicable
* mermaid: 6-8 node diagram showing detailed concept flow"""

    return f"""You are ShikshAI — a warm AI teaching assistant for Indian school students.

TASK: Explain "{concept}" to Grade {grade} students (Subject: {subject}).

LANGUAGE RULE (follow exactly):
{lang_rule}

GRADE-LEVEL FORMAT (follow exactly):
{format_rule}

OUTPUT — Return ONLY this exact JSON, no markdown, no extra text:
{{
  "title": "Title of {concept} in chosen language",
  "formula": "Key formula/equation or empty string",
  "explanation": "Grade-appropriate explanation as per format rules above",
  "example": "One concrete example",
  "fun_fact": "One exciting fact",
  "key_points": [
    "Point 1 (grade-appropriate length)",
    "Point 2",
    "Point 3"
  ],
  "{summary_key}": "{summary_val}",
  {speak_rule},
  "mermaid": "flowchart TD\\n  A[{concept}] --> B[Part 1]\\n  A --> C[Part 2]\\n  B --> D[Result 1]\\n  C --> E[Result 2]"
}}

MERMAID RULES:
* Show the ACTUAL structure/process of "{concept}"
* First line: flowchart TD
* ONLY simple ASCII in node labels — NO Hindi, NO special chars inside [ ]
* Use --> for arrows
"""

"""
Prompt for Feature 2: Voice-Triggered Quiz Generation.
Grade-adaptive difficulty and format.
"""
from prompts.hindi_quality import get_hindi_lang_rule


def build(topic: str, num_q: int, grade: str, subject: str = "General", lang: str = "en") -> str:

    if lang == "hi":
        lang_rule = (
            get_hindi_lang_rule(grade)
            + "\nCRITICAL: सभी प्रश्न, विकल्प (A/B/C/D) और व्याख्याएँ हिंदी में होनी चाहिए।"
        )
    else:
        lang_rule = "Clear, simple English only. All questions, options, explanations in English."

    if grade in ("LKG", "UKG"):
        difficulty = f"""
DIFFICULTY: Kindergarten level — PICTURE-BASED, identification only.
* Questions must be like: "यह क्या है?" / "कितने हैं?" / "कौन सा रंग है?"
* Options: single words or numbers only (e.g. "एक", "दो", "तीन", "चार")
* No reading required — questions should be answerable by a child who can't read
* Explanation: one simple sentence only"""

    elif grade in ("1", "2", "3"):
        difficulty = f"""
DIFFICULTY: Primary level (Class {grade}) — simple recall questions.
* Short questions, max 10 words
* Options: simple words or short phrases
* One clearly correct answer, three simple distractors
* Explanation: 1 simple sentence"""

    elif grade in ("4", "5"):
        difficulty = f"""
DIFFICULTY: Upper primary (Class {grade}) — understanding level.
* Questions test basic understanding, not just recall
* Options: similar-length phrases to avoid guessing
* Explanation: 1-2 sentences with the key reason"""

    elif grade in ("6", "7", "8"):
        difficulty = f"""
DIFFICULTY: Middle school (Class {grade}) — mix of recall, understanding, application.
* 40% recall, 40% understanding, 20% application
* Plausible distractors targeting common misconceptions
* Explanation: 1-2 sentences explaining WHY"""

    else:  # 9-12
        difficulty = f"""
DIFFICULTY: Secondary/Senior (Class {grade}) — NCERT board level.
* Higher-order thinking: analysis, application, problem-solving
* Technical terminology expected in options
* Distractors should be based on common exam mistakes
* Explanation: 2 sentences with mechanism/reasoning"""

    return f"""You are ShikshAI — an AI quiz generator for Indian school classrooms.

TASK: Generate {num_q} MCQ questions on "{topic}" for Grade {grade} ({subject}).

LANGUAGE RULE:
{lang_rule}

DIFFICULTY & FORMAT:
{difficulty}

OUTPUT: Return ONLY a valid JSON array — no markdown:
[
  {{
    "question": "Question text",
    "options": {{
      "A": "Option A",
      "B": "Option B",
      "C": "Option C",
      "D": "Option D"
    }},
    "answer": "A",
    "explanation": "Why this answer is correct"
  }}
]

CONSTRAINTS:
* Exactly {num_q} questions
* Each question MUST have exactly keys A, B, C, D
* "answer" MUST be one of: A, B, C, D
* Follow NCERT Grade {grade} curriculum
"""

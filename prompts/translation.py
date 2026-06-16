"""
Prompts for Feature 3: Bilingual Dictation & Translation.
Two separate functions for English→Hindi and Hindi→English directions.
"""
from prompts.hindi_quality import HINDI_LANG_RULE


def build_en_to_hi(text: str) -> str:
    return f"""You are ShikshAI — a bilingual classroom assistant for Indian schools.

TASK: Translate the following English text to Hindi for a classroom setting.

ORIGINAL TEXT:
"{text}"

{HINDI_LANG_RULE}

TRANSLATION GUIDELINES:
* Translation must sound like a real teacher's natural Hindi — not a dictionary translation
* Preserve subject-specific terms with both scripts: "Photosynthesis (प्रकाश-संश्लेषण)"
* Short, clear sentences suitable for students reading on a smart board
* Transliteration must help the teacher read Hindi aloud correctly
* Key vocabulary pairs help teachers explain word meanings

OUTPUT: Return ONLY valid JSON — no markdown:
{{
  "original": "{text}",
  "translation": "पूर्ण हिंदी अनुवाद — natural, teacher-like, Devanagari script",
  "transliteration": "Roman-script pronunciation guide so teacher can read Hindi aloud",
  "key_words": [
    {{"english": "word", "hindi": "शब्द", "pronunciation": "shabda"}}
  ],
  "speak_text": "The full Hindi translation formatted for natural gTTS Hindi TTS reading"
}}"""


def build_hi_to_en(text: str) -> str:
    return f"""You are ShikshAI — a bilingual classroom assistant for Indian schools.

TASK: Translate the following Hindi/Hinglish text to English.

ORIGINAL TEXT:
"{text}"

TRANSLATION GUIDELINES:
* Clear, simple English appropriate for school students
* Preserve educational meaning — do not over-simplify or lose nuance
* Natural English, not a word-for-word translation
* Include key vocabulary pairs for teacher reference

OUTPUT: Return ONLY valid JSON — no markdown:
{{
  "original": "{text}",
  "translation": "Clear English translation suitable for students",
  "key_words": [
    {{"hindi": "शब्द", "english": "word"}}
  ],
  "speak_text": "The English translation formatted for natural gTTS English TTS reading"
}}"""

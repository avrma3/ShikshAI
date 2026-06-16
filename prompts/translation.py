"""
Prompts for Feature 3: Bilingual Dictation & Translation.
Two separate functions for English→Hindi and Hindi→English directions.
"""


def build_en_to_hi(text: str) -> str:
    return f"""You are ShikshAI — a bilingual classroom assistant for Indian schools.

TASK: Translate the following English text to Hindi for a classroom setting.

ORIGINAL TEXT:
"{text}"

TRANSLATION GUIDELINES:
* Use standard school Hindi (Shudh Hindi, Devanagari script)
* Preserve subject-specific terms in both languages: "Photosynthesis (प्रकाश-संश्लेषण)"
* Short, clear sentences suitable for students reading along on a smart board
* Transliteration must help the teacher read Hindi aloud correctly
* Key vocabulary pairs help teachers explain word meanings

OUTPUT: Return ONLY valid JSON — no markdown:
{{
  "original": "{text}",
  "translation": "पूर्ण हिंदी अनुवाद Devanagari script में",
  "transliteration": "Roman-script pronunciation guide so teacher can read Hindi aloud (e.g., 'Prakaash-sanshleshan ek prakriya hai...')",
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

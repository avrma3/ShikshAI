"""
AI helper — all OpenAI API calls for ShikshAI's four features.
Prompts live in the prompts/ folder for clean separation of concerns.
"""
import json
import time
from openai import OpenAI

SYSTEM_PROMPT = (
    "You are ShikshAI — a bilingual AI teaching assistant for government schools in India. "
    "Always respond with ONLY valid JSON as instructed in each prompt. "
    "Follow the language instructions in each prompt exactly. Be warm, encouraging, and culturally relevant to Indian students."
)


def setup_gemini(api_key: str):
    """Returns an OpenAI client (name kept for backward compatibility)."""
    return OpenAI(api_key=api_key)


setup_ai = setup_gemini  # alias


# ── JSON parsing helpers ──────────────────────────────────────────────────────

def _strip_fences(text: str) -> str:
    if "```json" in text:
        text = text.split("```json", 1)[1].rsplit("```", 1)[0]
    elif "```" in text:
        text = text.split("```", 1)[1].rsplit("```", 1)[0]
    return text.strip()


def _parse_json(text: str, fallback_key: str = "result") -> dict:
    try:
        text  = _strip_fences(text)
        start = text.find("{")
        end   = text.rfind("}") + 1
        return json.loads(text[start:end]) if start != -1 else {fallback_key: text}
    except Exception:
        return {fallback_key: text}


def _parse_json_list(text: str) -> list:
    try:
        text  = _strip_fences(text)
        start = text.find("[")
        end   = text.rfind("]") + 1
        return json.loads(text[start:end]) if start != -1 else []
    except Exception:
        return []


def _call(client: OpenAI, prompt: str, retries: int = 3) -> str:
    last_err = None
    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user",   "content": prompt},
                ],
                temperature=0.7,
            )
            return response.choices[0].message.content
        except Exception as e:
            last_err = e
            err_str = str(e).lower()
            # Quota exhausted — fail immediately
            if "insufficient_quota" in err_str or "exceeded your current quota" in err_str:
                raise Exception(
                    "OpenAI API quota khatam. "
                    "platform.openai.com pe billing check karo ya naya key use karo."
                )
            # Rate limit / server error — retry with backoff
            if "rate_limit" in err_str or "503" in err_str or "529" in err_str:
                time.sleep(2 ** attempt)
            else:
                raise
    raise last_err


# ── Feature 1: Live Concept Simplification ───────────────────────────────────

def simplify_concept(model, concept: str, grade: str = "6",
                     subject: str = "General", lang: str = "en") -> dict:
    from prompts.concept import build
    try:
        text = _call(model, build(concept, grade, subject, lang))
        return _parse_json(text, "explanation")
    except Exception as e:
        return {
            "explanation": f"AI error: {e}",
            "title": concept,
            "speak_text": f"Sorry, concept load nahi hua.",
        }


# ── Feature 2: Voice-Triggered Quizzing ──────────────────────────────────────

def generate_quiz(model, topic: str, num_q: int = 10,
                  grade: str = "General", subject: str = "General", lang: str = "en",
                  exclude_questions: list = None) -> list:
    from prompts.quiz import build
    try:
        text = _call(model, build(topic, num_q, grade, subject, lang, exclude_questions or []))
        return _parse_json_list(text)
    except Exception:
        return []


# ── Feature 3: Bilingual Dictation & Translation ─────────────────────────────

def translate_content(model, text: str, direction: str = "en_to_hi") -> dict:
    from prompts.translation import build_en_to_hi, build_hi_to_en
    prompt = build_en_to_hi(text) if direction == "en_to_hi" else build_hi_to_en(text)
    try:
        result = _call(model, prompt)
        return _parse_json(result, "translation")
    except Exception as e:
        return {"translation": f"AI error: {e}", "original": text}


# ── Diagram code generator (matplotlib) ──────────────────────────────────────

def generate_diagram_code(model, concept: str, grade: str = "6",
                          subject: str = "General", lang: str = "en") -> str:
    from prompts.diagram import build
    try:
        code = _call(model, build(concept, grade, subject, lang))
        if "```" in code:
            code = code.split("```", 1)[1]
            if code.startswith("python"):
                code = code[6:]
            code = code.rsplit("```", 1)[0]
        return code.strip()
    except Exception:
        return ""


# ── Free-form chat (streaming, gpt-4o) ───────────────────────────────────────

def _chat_system(grade: str, subject: str, lang: str) -> str:
    if lang == "hi":
        from prompts.hindi_quality import get_hindi_lang_rule
        lang_rule = get_hindi_lang_rule(grade)
    else:
        lang_rule = (
            "Always answer in clear, simple English. "
            "Short sentences. Warm and encouraging tone."
        )

    if grade in ("LKG", "UKG"):
        level = "age 3-5, use very simple words, 1-2 sentences max, like talking to a toddler"
    elif grade in ("1", "2", "3"):
        level = "age 6-9, simple words, short sentences, relate to home and school life"
    elif grade in ("4", "5"):
        level = "age 9-11, clear explanations with Indian analogies"
    elif grade in ("6", "7", "8"):
        level = "age 11-14, thorough explanations, real-world examples, NCERT level"
    else:
        level = "age 14-18, precise technical language, formulas where relevant, board-exam depth"

    if lang == "hi":
        fmt = (
            "• पहले सवाल का सीधा जवाब दो (2-3 वाक्य)।\n"
            "• फिर **मुख्य बिंदु:** bullet list में (3-5 बिंदु)।\n"
            "• अंत में **उदाहरण:** एक भारतीय रोज़मर्रा का उदाहरण।\n"
            "• ज़रूरी terms को **bold** करो।\n"
            "• कुल जवाब 250 words से कम रखो जब तक ज़रूरत न हो।"
        )
    else:
        fmt = (
            "• Start with a direct answer to the question (2-3 sentences).\n"
            "• Then add **Key Points:** as a bullet list (3-5 bullets).\n"
            "• End with **Example:** one concrete example from Indian daily life "
            "(cricket, farming, festivals, daal-roti, village life).\n"
            "• Use **bold** for important terms.\n"
            "• Keep total response under 250 words unless the question needs more depth."
        )

    return (
        f"You are ShikshAI — an expert AI teacher for Grade {grade} {subject} students "
        f"in India.\n\n"
        f"LANGUAGE RULE:\n{lang_rule}\n\n"
        f"STUDENT LEVEL: Grade {grade} ({level}).\n\n"
        f"FORMATTING (always follow):\n{fmt}\n\n"
        f"Be warm, encouraging, and celebrate curiosity."
    )


def stream_chat_answer(client: OpenAI, history: list,
                       grade: str, subject: str, lang: str = "en"):
    """
    Stream a chat response using gpt-4o.
    `history` is a list of {role, content} dicts (user + assistant turns).
    Yields text chunks as they arrive.
    """
    system_msg = {"role": "system", "content": _chat_system(grade, subject, lang)}
    messages   = [system_msg] + history

    try:
        stream = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            stream=True,
            temperature=0.7,
            max_tokens=800,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta
    except Exception as e:
        err = str(e)
        if "insufficient_quota" in err.lower() or "exceeded" in err.lower():
            yield "\n\n⚠️ API quota khatam. platform.openai.com pe billing check karo."
        else:
            yield f"\n\n⚠️ Error: {err}"


def answer_question(client: OpenAI, question: str, grade: str = "6",
                    subject: str = "General", lang: str = "en") -> dict:
    """Single-turn Q&A (non-streaming fallback). Returns dict with answer/key_points/etc."""
    history = [{"role": "user", "content": question}]
    full = "".join(stream_chat_answer(client, history, grade, subject, lang))
    return {
        "answer":      full,
        "key_points":  [],
        "example":     "",
        "speak_text":  full[:300],
    }


# ── Feature 4: Hands-Free Activity Guide ─────────────────────────────────────

def generate_activity(model, description: str, duration: int = 10,
                      grade: str = "6", subject: str = "General", lang: str = "en") -> dict:
    from prompts.activity import build
    try:
        text = _call(model, build(description, duration, grade, subject, lang))
        return _parse_json(text, "title")
    except Exception as e:
        return {
            "title": "Activity",
            "steps": [],
            "speak_intro": f"AI error: {e}",
        }

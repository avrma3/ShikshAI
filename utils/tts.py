import os
import base64
from openai import OpenAI

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    return _client


def speak(text: str, lang: str = "hi") -> bytes:
    """Convert text to MP3 bytes using OpenAI TTS (nova voice)."""
    if not text:
        return b""
    try:
        client = _get_client()
        response = client.audio.speech.create(
            model="tts-1",
            voice="nova",
            input=text[:4096],
            response_format="mp3",
        )
        return response.content
    except Exception:
        return b""


def audio_player_html(audio_bytes: bytes, autoplay: bool = True) -> str:
    """Return an HTML audio player string."""
    if not audio_bytes:
        return ""
    b64 = base64.b64encode(audio_bytes).decode()
    auto = "autoplay" if autoplay else ""
    return (
        f'<audio {auto} controls style="width:100%;border-radius:10px;margin-top:10px;">'
        f'<source src="data:audio/mp3;base64,{b64}" type="audio/mp3">'
        f"</audio>"
    )

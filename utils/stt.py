import os
import tempfile
from openai import OpenAI

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    return _client


def _detect_ext(data: bytes) -> str:
    if data[:4] == bytes([0x1A, 0x45, 0xDF, 0xA3]):
        return ".webm"
    if data[:4] == b"fLaC":
        return ".flac"
    if data[:4] == b"OggS":
        return ".ogg"
    if data[:3] == b"ID3" or (len(data) > 1 and data[:2] == b"\xff\xfb"):
        return ".mp3"
    return ".wav"


def transcribe_audio(audio_bytes: bytes) -> tuple:
    """Transcribe audio bytes using OpenAI Whisper API. Returns (text, detected_language)."""
    if not audio_bytes:
        return "Koi audio nahi mila.", "unknown"
    try:
        client = _get_client()
        ext = _detect_ext(audio_bytes)
        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as f:
            f.write(audio_bytes)
            path = f.name
        try:
            with open(path, "rb") as audio_file:
                result = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="verbose_json",
                )
            text = (result.text or "").strip()
            lang = getattr(result, "language", "hi")
        finally:
            try:
                os.unlink(path)
            except OSError:
                pass
        if not text:
            return "Kuch samajh nahi aya. Clearly aur loud boliye.", lang
        return text, lang
    except Exception as e:
        return f"Transcription error: {e}", "unknown"

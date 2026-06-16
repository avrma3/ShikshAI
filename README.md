# ShikshAI — Voice-Enabled AI Teaching Assistant

> Connecting Dreams Foundation · Round 2 Technical Assignment · Option A

A voice-first, bilingual AI teaching assistant built for Haryana government school smart classrooms.
Supports Hinglish (Hindi + English) and is optimized for large smart board display.

---

## Features

| Feature | Description |
|---|---|
| 🧠 Live Concept Simplification | Speak any concept — AI explains in Hinglish with a smart board visual card |
| ❓ Voice-Triggered Quizzing | Say a topic — AI generates MCQ quiz with interactive answer reveal |
| 🌐 Bilingual Dictation & Translation | Hindi ↔ English transcription + translation with visual display |
| ⏱️ Hands-Free Activity Guide | Describe an activity — AI creates step-by-step guide + live countdown timer |

---

## Tech Stack

| Component | Tool |
|---|---|
| UI Framework | Streamlit |
| LLM | Google Gemini 1.5 Flash |
| Speech-to-Text | faster-whisper (OpenAI Whisper base model, CPU) |
| Text-to-Speech | gTTS (Google Text-to-Speech) |
| Visuals | Pillow (PIL) |
| Deployment | Streamlit Community Cloud / Hugging Face Spaces |

---

## Setup

### 1. Clone & Install

```bash
git clone <your-repo-url>
cd "Connecting Dreams Technical Assignment"
pip install -r requirements.txt
```

### 2. Get Gemini API Key (Free)

1. Go to https://aistudio.google.com/app/apikey
2. Create a free API key

### 3. Configure

```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

### 4. Run

```bash
streamlit run app.py
```

---

## Prompt Design

All AI prompts use a consistent system instruction that:
- Establishes ShikshAI as a Haryana government school teaching assistant
- Mandates Hinglish (natural Hindi-English mix) responses
- Grounds examples in Indian rural daily life
- Returns structured JSON for reliable parsing

Each feature has a dedicated prompt that returns JSON, enabling clean separation between AI output and UI rendering.

---

## Localization

- **STT**: faster-whisper auto-detects Hindi/English/Hinglish
- **TTS**: gTTS supports `hi` (Hindi) and `en` (English) — selectable in sidebar
- **UI**: All labels in Hinglish for teacher comfort
- **AI responses**: Always Hinglish unless translation feature specifies otherwise

---

## Deployment

### Streamlit Cloud (Recommended)
1. Push to GitHub
2. Go to share.streamlit.io
3. Connect repo, set `GEMINI_API_KEY` in Secrets
4. Deploy

### Hugging Face Spaces
1. Create Space (Streamlit SDK)
2. Upload files
3. Add `GEMINI_API_KEY` to Space Secrets

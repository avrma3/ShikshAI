# ShikshAI — Voice-Enabled AI Teaching Assistant

> Connecting Dreams Foundation · Round 2 · Option A

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Streamlit-FF4B4B?logo=streamlit)](https://shikshai-ncaytqb9nbjaa3n7kycetd.streamlit.app/)
[![GitHub](https://img.shields.io/badge/GitHub-avrma3%2FShikshAI-181717?logo=github)](https://github.com/avrma3/ShikshAI)

A voice-first, bilingual AI teaching assistant for Indian classrooms. Supports Hindi, English, and Hinglish — optimized for smart board display.

---

## Live Demo

**https://shikshai-ncaytqb9nbjaa3n7kycetd.streamlit.app/**

---

## Features

| Feature | Description |
|---|---|
| 🧠 Concept Simplifier | Speak any concept — AI explains in Hinglish with a visual diagram |
| ❓ Voice Quiz | Say a topic — AI generates MCQ quiz with interactive answer reveal |
| 🌐 Bilingual Translation | Hindi ↔ English transcription + translation with audio playback |
| ⏱️ Activity Guide | Describe an activity — AI creates step-by-step guide + countdown timer |
| 📊 Teacher Dashboard | Session history, usage analytics, PDF export |
| 💬 Ask AI | Freeform voice/text chat with the AI assistant |

---

## Tech Stack

| Component | Tool |
|---|---|
| UI Framework | Streamlit |
| LLM | GPT-4o (OpenAI) |
| Speech-to-Text | OpenAI Whisper API |
| Text-to-Speech | OpenAI TTS (Nova voice) |
| Visuals | Pillow (PIL), Matplotlib |
| Deployment | Streamlit Community Cloud |

---

## Local Setup

### 1. Clone & Install

```bash
git clone https://github.com/avrma3/ShikshAI.git
cd ShikshAI
pip install -r requirements.txt
```

### 2. Get OpenAI API Key

Go to https://platform.openai.com/api-keys and create an API key.

### 3. Configure

Create a `.env` file in the project root:

```
OPENAI_API_KEY=sk-your-key-here
```

### 4. Run

```bash
python -m streamlit run app.py
```

App opens at **http://localhost:8501**

---

## Project Structure

```
ShikshAI/
├── app.py                  # Main Streamlit app
├── utils/
│   ├── ai_helper.py        # OpenAI GPT-4o client
│   ├── stt.py              # Whisper speech-to-text
│   ├── tts.py              # OpenAI TTS
│   ├── i18n.py             # Hindi/English UI strings
│   ├── visuals.py          # Diagram/image generation
│   ├── topics.py           # Topic suggestions
│   └── favicon_b64.py      # Favicon for HTML embeds
├── prompts/
│   ├── concept.py          # Concept simplification prompts
│   ├── quiz.py             # Quiz generation prompts
│   ├── translation.py      # Translation prompts
│   ├── activity.py         # Activity guide prompts
│   └── diagram.py          # Diagram prompts
├── services/
│   ├── history.py          # SQLite session history
│   └── pdf_gen.py          # PDF export
├── requirements.txt
└── favicon.png
```

---

## Deployment (Streamlit Cloud)

1. Fork/clone this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect repo → set `OPENAI_API_KEY` in Secrets
4. Deploy

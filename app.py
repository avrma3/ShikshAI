"""
ShikshAI — Voice-Enabled AI Teaching Assistant
Connecting Dreams Foundation
"""

import streamlit as st
import os
from PIL import Image
from dotenv import load_dotenv

load_dotenv(override=True)

# Streamlit Cloud secrets support
if hasattr(st, "secrets"):
    for _k in ["OPENAI_API_KEY", "GEMINI_API_KEY"]:
        if _k in st.secrets and not os.getenv(_k):
            os.environ[_k] = st.secrets[_k]

# ── Page config ────────────────────────────────────────────────────────────────
_favicon = Image.open(os.path.join(os.path.dirname(__file__), "favicon.png"))
st.set_page_config(
    page_title="ShikshAI — Smart Teaching Assistant",
    page_icon=_favicon,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Session state defaults ─────────────────────────────────────────────────────
_defaults = {
    "dark_mode":            True,
    "ui_lang":              "en",
    "quiz_questions":       [],
    "quiz_index":           0,
    "quiz_answered":        {},
    "quiz_score":           0,
    "quiz_saved":           False,
    "quiz_topic_name":      "",
    "activity_data":        None,
    "concept_data":         {},
    "trans_result":         {},
    "last_tts_text":        "",
    "last_tts_lang":        "hi",
    "_repeat_now":          False,
    "_diagram_img":         None,
    "_last_diagram_concept":"",
    "_show_confetti":       False,
    "t1_text_input":        "",
    "t2_text_input":        "",
    "t3_text_input":        "",
    "t4_text_input":        "",
    "_t1_auto_explain":     False,
    "_t2_auto_quiz":        False,
    "t6_chat_history":      [],
    "_t1_gpt4o_answer":     "",
    "_t1_stream_concept":   "",
    "mic_key_t6":           0,
    "_last_grade_subj":     "",
    "trans_actual_dir":     "en_to_hi",
}
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Language strings ───────────────────────────────────────────────────────────
from utils.i18n import STRINGS
from utils.topics import get_concept_topics, get_activity_topics
_lang = st.session_state.get("ui_lang", "en")
T     = STRINGS[_lang]
tts_lang = _lang  # UI language drives TTS too

# ── Theme tokens ───────────────────────────────────────────────────────────────
dark = st.session_state.dark_mode

_BG      = "linear-gradient(160deg,#04071a 0%,#0a0f2e 40%,#0f1535 100%)" if dark else \
           "linear-gradient(160deg,#dde4ff 0%,#e8ecff 50%,#f0ecff 100%)"
_SIDEBAR = "rgba(8,11,32,0.98)"      if dark else "#eceeff"
_TEXT    = "#e2e8f0"                  if dark else "#1e1b4b"
_TEXT2   = "#94a3b8"                  if dark else "#4b5563"
_CARD    = "rgba(255,255,255,0.045)" if dark else "#ffffff"
_CARD2   = "rgba(255,255,255,0.07)"  if dark else "#f5f6ff"
_BORDER  = "rgba(255,255,255,0.1)"   if dark else "rgba(99,102,241,0.45)"
_INPUT   = "rgba(255,255,255,0.06)"  if dark else "#ffffff"
_IBORDER = "rgba(255,255,255,0.15)"  if dark else "rgba(99,102,241,0.6)"
_DISPBG  = "rgba(255,255,255,0.05)"  if dark else "#eef0ff"
_TITLE_C = "#c7d2fe"  if dark else "#3730a3"
_BADGE_C = "#818cf8"  if dark else "#4338ca"
_SHADOW  = "0 4px 24px rgba(0,0,0,0.4)"  if dark else "0 4px 24px rgba(99,102,241,0.18)"
_ANS_OK_T= "#6ee7b7"  if dark else "#065f46"
_ANS_NG_T= "#fca5a5"  if dark else "#7f1d1d"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
*, html, body, [class*="css"] {{ font-family:'Inter',sans-serif; box-sizing:border-box; }}

@keyframes shimmer {{
  0%   {{ background-position: -400% center; }}
  100% {{ background-position:  400% center; }}
}}
@keyframes fadeInUp {{
  from {{ opacity:0; transform:translateY(22px); }}
  to   {{ opacity:1; transform:translateY(0);    }}
}}
@keyframes fadeIn {{ from {{ opacity:0; }} to {{ opacity:1; }} }}
@keyframes pulseGlow {{
  0%,100% {{ box-shadow:0 0 0 0   rgba(99,102,241,0.55); }}
  50%     {{ box-shadow:0 0 0 14px rgba(99,102,241,0);   }}
}}
@keyframes scoreReveal {{
  0%   {{ transform:scale(0.4) rotate(-8deg); opacity:0; }}
  65%  {{ transform:scale(1.18) rotate(2deg); }}
  100% {{ transform:scale(1)    rotate(0deg); opacity:1; }}
}}
@keyframes float {{
  0%,100% {{ transform:translateY(0);    }}
  50%     {{ transform:translateY(-7px); }}
}}
@keyframes progressFill {{ from {{ width:0%; }} }}
@keyframes confettiFall {{
  0%   {{ transform:translateY(-10px) rotate(0deg);   opacity:1; }}
  100% {{ transform:translateY(110vh) rotate(720deg); opacity:0; }}
}}
@keyframes chipPop {{
  0%   {{ transform:scale(0.8); opacity:0; }}
  80%  {{ transform:scale(1.05); }}
  100% {{ transform:scale(1); opacity:1; }}
}}
@keyframes gradientShift {{
  0%   {{ background-position:0% 50%;   }}
  50%  {{ background-position:100% 50%; }}
  100% {{ background-position:0% 50%;   }}
}}

.stApp {{
  background: {_BG};
  color: {_TEXT};
  animation: fadeIn 0.6s ease;
}}

.main-header {{
  background: linear-gradient(270deg,#1e3a8a,#4c1d95,#1e3a8a,#312e81);
  background-size: 400% 400%;
  animation: gradientShift 8s ease infinite;
  border: 1px solid rgba(139,92,246,0.5);
  border-radius: 20px;
  padding: 32px 44px 28px;
  margin-bottom: 24px;
  text-align: center;
  box-shadow: 0 8px 40px rgba(79,70,229,0.35), inset 0 1px 0 rgba(255,255,255,0.1);
  position: relative; overflow: hidden;
}}
.main-header::before {{
  content:''; position:absolute; top:0; left:-60%; width:60%; height:100%;
  background:linear-gradient(90deg,transparent,rgba(255,255,255,0.07),transparent);
  animation: shimmer 3s linear infinite;
}}
.main-header h1 {{
  color:#fff; font-size:2.8rem; margin:0; font-weight:900;
  letter-spacing:-1px; text-shadow:0 2px 20px rgba(139,92,246,0.5);
}}
.main-header p  {{ color:rgba(255,255,255,0.82); font-size:1.05rem; margin:8px 0 14px; }}
.header-pills   {{ display:flex; flex-wrap:wrap; gap:8px; justify-content:center; margin-top:6px; }}
.hpill {{
  background:rgba(255,255,255,0.12); color:rgba(255,255,255,0.9);
  border:1px solid rgba(255,255,255,0.22); border-radius:50px;
  padding:4px 14px; font-size:0.8rem; font-weight:600; backdrop-filter:blur(6px);
}}

.feature-card {{
  background:{_CARD}; border:1px solid {_BORDER}; border-radius:18px;
  padding:24px; margin-bottom:14px; box-shadow:{_SHADOW};
  animation:fadeInUp 0.5s ease both; backdrop-filter:blur(12px);
  transition:transform 0.2s, box-shadow 0.2s;
}}
.feature-card:hover {{ transform:translateY(-2px); box-shadow:0 8px 32px rgba(99,102,241,0.25); }}

.glass-card {{
  background:{_CARD2}; border:1px solid {_BORDER}; border-radius:16px;
  padding:20px 24px; backdrop-filter:blur(16px); box-shadow:{_SHADOW};
  animation:fadeInUp 0.4s ease both;
}}

.grad-border {{
  background:linear-gradient({_CARD},{_CARD}) padding-box,
             linear-gradient(135deg,#6366f1,#8b5cf6,#06b6d4) border-box;
  border:2px solid transparent; border-radius:16px; padding:20px;
  animation:fadeInUp 0.45s ease both;
}}

.section-title {{
  font-size:1.22rem; font-weight:800; color:{_TITLE_C};
  margin-bottom:8px; animation:fadeInUp 0.4s ease both;
}}

.display-box {{
  background:{_DISPBG}; border:1px solid {_BORDER}; border-radius:14px;
  padding:18px 22px; font-size:1.08rem; line-height:1.75; color:{_TEXT};
  min-height:65px; box-shadow:{_SHADOW}; animation:fadeInUp 0.5s ease both;
}}

.badge {{
  display:inline-block; padding:5px 16px; border-radius:50px;
  font-size:0.82rem; font-weight:700; margin-bottom:10px;
  animation:chipPop 0.35s ease both;
}}
.badge-done    {{ background:rgba(99,102,241,0.2);  color:{_BADGE_C}; border:1px solid {_BADGE_C}; }}
.badge-success {{ background:rgba(16,185,129,0.18); color:#34d399;    border:1px solid rgba(16,185,129,0.5); }}

.chip-row {{ display:flex; flex-wrap:wrap; gap:8px; margin:10px 0; }}
.chip {{
  background:rgba(99,102,241,0.15); color:{_BADGE_C};
  border:1px solid rgba(99,102,241,0.4); border-radius:50px;
  padding:5px 14px; font-size:0.83rem; font-weight:600;
  cursor:pointer; transition:all 0.18s; animation:chipPop 0.3s ease both;
}}
.chip:hover {{ background:rgba(99,102,241,0.3); border-color:#6366f1; transform:scale(1.05); }}

.answer-correct {{
  background:rgba(16,185,129,0.15); border:2px solid #10b981; border-radius:12px;
  padding:13px 18px; margin:6px 0; font-size:1.05rem; color:{_ANS_OK_T};
  font-weight:600; animation:fadeInUp 0.3s ease;
}}
.answer-wrong {{
  background:rgba(239,68,68,0.12); border:1px solid rgba(239,68,68,0.45);
  border-radius:12px; padding:13px 18px; margin:6px 0;
  font-size:1.05rem; color:{_ANS_NG_T};
}}
.answer-neutral {{
  background:{_DISPBG}; border:1px solid {_BORDER}; border-radius:12px;
  padding:13px 18px; margin:6px 0; font-size:1.05rem; color:{_TEXT};
}}

.step-card {{
  background:{_CARD}; border-left:4px solid #6366f1;
  border-radius:0 12px 12px 0; padding:14px 18px; margin:8px 0;
  color:{_TEXT}; box-shadow:{_SHADOW}; animation:fadeInUp 0.4s ease both;
  transition:border-left-color 0.2s;
}}
.step-card:hover {{ border-left-color:#8b5cf6; }}

.score-box {{ animation:scoreReveal 0.7s cubic-bezier(0.34,1.56,0.64,1) both; }}

.metric-card {{
  background:{_CARD2}; border:1px solid {_BORDER}; border-radius:14px;
  padding:18px 20px; text-align:center; box-shadow:{_SHADOW};
  animation:fadeInUp 0.45s ease both; transition:transform 0.2s;
}}
.metric-card:hover {{ transform:translateY(-3px); }}
.metric-value {{
  font-size:2.2rem; font-weight:900;
  background:linear-gradient(135deg,#6366f1,#8b5cf6);
  -webkit-background-clip:text; -webkit-text-fill-color:transparent;
}}
.metric-label {{ color:{_TEXT2}; font-size:0.82rem; font-weight:600; margin-top:4px; }}

.stTabs [data-baseweb="tab-list"] {{
  background:{_CARD}; border-radius:14px; padding:5px; gap:4px;
  border:1px solid {_BORDER}; box-shadow:{_SHADOW};
}}
.stTabs [data-baseweb="tab"] {{
  color:{_TEXT2}; font-size:0.92rem; font-weight:700;
  border-radius:10px; padding:9px 18px; transition:all 0.2s;
}}
.stTabs [aria-selected="true"] {{
  background:linear-gradient(135deg,#4f46e5,#7c3aed) !important;
  color:white !important; box-shadow:0 4px 14px rgba(99,102,241,0.4) !important;
}}

div[data-testid="stVerticalBlock"] > div:has(> .stButton) button {{
  background:linear-gradient(135deg,#4f46e5,#7c3aed);
  color:white; border:none; border-radius:12px;
  font-size:1rem; font-weight:700; padding:12px 24px; width:100%;
  box-shadow:0 4px 15px rgba(99,102,241,0.35); transition:all 0.22s ease;
}}
div[data-testid="stVerticalBlock"] > div:has(> .stButton) button:hover {{
  transform:translateY(-2px); box-shadow:0 8px 25px rgba(99,102,241,0.5);
}}

.stTextInput input, .stTextArea textarea, .stNumberInput input {{
  background:{_INPUT} !important; color:{_TEXT} !important;
  border:1px solid {_IBORDER} !important; border-radius:10px !important;
  transition:border-color 0.2s, box-shadow 0.2s !important;
}}
.stTextInput input:focus, .stTextArea textarea:focus {{
  border-color:rgba(99,102,241,0.7) !important;
  box-shadow:0 0 0 3px rgba(99,102,241,0.15) !important;
}}

.stSidebar {{ background:{_SIDEBAR} !important; border-right:1px solid {_BORDER} !important; }}

.board-image {{
  width:100%; border-radius:14px; border:1px solid {_BORDER};
  box-shadow:{_SHADOW}; animation:fadeIn 0.5s ease;
}}

.empty-state {{
  background:{_DISPBG}; border:2px dashed rgba(99,102,241,0.3);
  border-radius:18px; padding:60px 20px; text-align:center;
  color:{_TEXT2}; animation:fadeIn 0.6s ease;
}}
.empty-icon {{
  font-size:3rem; display:block; margin-bottom:12px;
  animation:float 3s ease-in-out infinite;
}}

.stProgress > div > div > div > div {{
  background:linear-gradient(90deg,#4f46e5,#7c3aed) !important;
  border-radius:50px !important; animation:progressFill 0.6s ease;
}}

.confetti-piece {{
  position:fixed; top:-20px; width:10px; height:10px;
  border-radius:2px; animation:confettiFall linear forwards; z-index:9999;
}}

#MainMenu, footer, header {{ visibility:hidden; }}
[data-testid="stToolbar"]     {{ display:none !important; }}
[data-testid="stDeployButton"]{{ display:none !important; }}

.stSelectbox > div > div {{
  background:{_INPUT} !important; border:1px solid {_IBORDER} !important;
  border-radius:10px !important; color:{_TEXT} !important;
}}

/* Force all select dropdowns to open DOWNWARD with scroll (never upward) */
ul[role="listbox"] {{
  max-height:220px !important;
  overflow-y:auto !important;
}}
[data-baseweb="popover"] [data-baseweb="menu"] {{
  max-height:220px !important;
  overflow-y:auto !important;
}}
hr {{
  border:none !important;
  border-top: 1px solid {_BORDER} !important;
  height:0 !important;
  background:transparent !important;
  margin:20px 0;
}}

/* ─── Cursor: hand on all interactive / label elements ───────────────────── */
[data-baseweb="select"],
[data-baseweb="select"] > div,
[data-baseweb="select"] [role="combobox"],
[data-baseweb="select"] svg,
[data-baseweb="popover"] [role="option"],
ul[role="listbox"] li,
[data-testid="stSelectbox"],
[data-testid="stSelectbox"] > div,
[data-testid="stWidgetLabel"],
[data-testid="stWidgetLabel"] p,
label,
button,
[role="button"],
summary,
[data-baseweb="tab"],
.chip-col button,
a
{{ cursor: pointer !important; }}

/* Text cursor only inside actual editable fields */
input[type="text"], input[type="search"], textarea
{{ cursor: text !important; }}

/* No I-beam on static text */
[data-testid="stMarkdownContainer"] p,
[data-testid="stCaptionContainer"] p,
.section-title, .metric-label, .badge, .hpill,
[data-testid="stSidebarContent"] p,
[data-testid="stSidebarContent"] span
{{ cursor: default !important; }}

/* ─── Chip-style small buttons ───────────────────────────────────────────── */
[data-testid="stHorizontalBlock"] .chip-col button,
.chip-col button {{
  background: rgba(99,102,241,0.15) !important;
  color: {_BADGE_C} !important;
  border: 1px solid rgba(99,102,241,0.45) !important;
  border-radius: 50px !important;
  font-size: 0.8rem !important;
  font-weight: 600 !important;
  padding: 5px 8px !important;
  box-shadow: none !important;
  min-height: 0 !important;
  height: 34px !important;
  transition: all 0.18s !important;
  transform: none !important;
}}
.chip-col button:hover {{
  background: rgba(99,102,241,0.32) !important;
  border-color: #6366f1 !important;
  transform: scale(1.04) !important;
  box-shadow: 0 2px 10px rgba(99,102,241,0.25) !important;
}}

/* ─── Custom scrollbar ───────────────────────────────────────────────────── */
::-webkit-scrollbar {{ width:6px; height:6px; }}
::-webkit-scrollbar-track {{ background:transparent; }}
::-webkit-scrollbar-thumb {{ background:rgba(99,102,241,0.4); border-radius:99px; }}
::-webkit-scrollbar-thumb:hover {{ background:rgba(99,102,241,0.7); }}

/* ─── Action pill buttons (copy / speak) ────────────────────────────────── */
.action-pill {{
  display:inline-flex; align-items:center; gap:5px;
  background:rgba(99,102,241,0.12); color:{_BADGE_C};
  border:1px solid rgba(99,102,241,0.35); border-radius:50px;
  padding:4px 12px; font-size:0.78rem; font-weight:600;
  cursor:pointer; transition:all 0.18s; font-family:'Inter',sans-serif;
  text-decoration:none;
}}
.action-pill:hover {{ background:rgba(99,102,241,0.28); border-color:#6366f1; }}

/* ─── Typing indicator ───────────────────────────────────────────────────── */
@keyframes blink {{ 0%,80%,100%{{opacity:0}} 40%{{opacity:1}} }}
.typing-dot {{
  display:inline-block; width:7px; height:7px; border-radius:50%;
  background:#6366f1; margin:0 2px;
  animation:blink 1.4s infinite both;
}}
.typing-dot:nth-child(2) {{ animation-delay:.2s; }}
.typing-dot:nth-child(3) {{ animation-delay:.4s; }}
.typing-wrap {{
  display:inline-flex; align-items:center; gap:6px;
  background:rgba(99,102,241,0.1); border:1px solid rgba(99,102,241,0.25);
  border-radius:50px; padding:6px 14px; font-size:0.82rem; color:{_TEXT2};
}}

/* ─── Styled warning / error cards ──────────────────────────────────────── */
.warn-card {{
  background:rgba(251,191,36,0.1); border:1px solid rgba(251,191,36,0.45);
  border-radius:12px; padding:12px 16px; color:#fbbf24;
  font-size:0.92rem; font-weight:500; margin:6px 0;
  animation:fadeInUp 0.3s ease;
}}
.err-card {{
  background:rgba(239,68,68,0.1); border:1px solid rgba(239,68,68,0.45);
  border-radius:12px; padding:12px 16px; color:#fca5a5;
  font-size:0.92rem; font-weight:500; margin:6px 0;
  animation:fadeInUp 0.3s ease;
}}
.info-card {{
  background:rgba(6,182,212,0.1); border:1px solid rgba(6,182,212,0.35);
  border-radius:12px; padding:12px 16px; color:#67e8f9;
  font-size:0.92rem; font-weight:500; margin:6px 0;
  animation:fadeInUp 0.3s ease;
}}

/* ─── Mobile responsive ──────────────────────────────────────────────────── */
@media (max-width: 768px) {{
  .main-header h1 {{ font-size:1.8rem !important; }}
  .main-header {{ padding:20px 18px 16px !important; }}
  .header-pills {{ gap:5px !important; }}
  .hpill {{ font-size:0.72rem !important; padding:3px 10px !important; }}
  .section-title {{ font-size:1rem !important; }}
  .display-box {{ padding:12px 14px !important; font-size:0.95rem !important; }}
  .stTabs [data-baseweb="tab"] {{ font-size:0.78rem !important; padding:7px 10px !important; }}
  div[data-testid="stVerticalBlock"] > div:has(> .stButton) button {{
    font-size:0.88rem !important; padding:10px 14px !important;
  }}
}}
@media (max-width: 480px) {{
  .main-header h1 {{ font-size:1.4rem !important; }}
  .metric-value {{ font-size:1.6rem !important; }}
}}

/* ─── Light mode: force all text visible ─────────────────────────────────── */
[data-testid="stWidgetLabel"],
[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] label,
.stSidebar label,
.stSidebar p,
.stSidebar span:not(.hpill),
.stSidebar [data-testid="stMarkdownContainer"] p,
.stSidebar .stCaption,
label, p, span.st-emotion-cache-hidden,
[data-testid="stMarkdownContainer"] p,
[data-testid="stCaptionContainer"] p,
[data-testid="stText"] p,
.stTextInput label,
.stTextArea label,
.stSelectbox label,
.stNumberInput label,
.stSlider label,
.stCheckbox label,
.stRadio label,
.stTabs [data-baseweb="tab"],
[data-testid="stSidebarContent"] p,
[data-testid="stSidebarContent"] label,
[data-testid="stSidebarContent"] span,
.stExpander summary p,
.stExpander p
{{
  color: {_TEXT} !important;
}}

/* Caption specifically */
[data-testid="stCaptionContainer"],
.stCaption {{ color: {_TEXT2} !important; }}

/* Sidebar background + text */
[data-testid="stSidebarContent"],
section[data-testid="stSidebar"] > div:first-child
{{ background: {_SIDEBAR} !important; }}

/* Input placeholders */
::placeholder {{ color: {_TEXT2} !important; opacity: 0.7 !important; }}

/* Selectbox dropdown text */
[data-baseweb="select"] span,
[data-baseweb="select"] div
{{ color: {_TEXT} !important; }}

/* Tab text fix for light mode */
.stTabs [data-baseweb="tab-list"] [data-baseweb="tab"]
{{ color: {_TEXT2} !important; }}
.stTabs [aria-selected="true"]
{{ color: #ffffff !important; }}

/* Expander header */
details summary {{ color: {_TEXT} !important; }}

/* ─── Light mode specific overrides ─────────────────────────────────────── */
{"" if dark else f"""

/* ══ SIDEBAR BACKGROUND ══ */
section[data-testid="stSidebar"],
section[data-testid="stSidebar"] > div,
[data-testid="stSidebarContent"] {{
  background: #eceeff !important;
}}

/* ══ SIDEBAR: EVERY TEXT ELEMENT DARK ══ */
body section[data-testid="stSidebar"] *,
body [data-testid="stSidebarContent"] * {{
  color: #1e1b4b !important;
}}

/* ══ SIDEBAR: HR DIVIDER LINES ══ */
section[data-testid="stSidebar"] hr,
[data-testid="stSidebarContent"] hr {{
  display: block !important;
  visibility: visible !important;
  border: none !important;
  border-top: 1px solid rgba(99,102,241,0.45) !important;
  height: 0 !important;
  background: transparent !important;
  margin: 14px 0 !important;
  opacity: 1 !important;
}}

/* ══ SIDEBAR: SELECTBOX ══ */
[data-testid="stSidebarContent"] [data-baseweb="select"] > div {{
  background: #ffffff !important;
  border: 1.5px solid rgba(99,102,241,0.5) !important;
}}
[data-testid="stSidebarContent"] [data-baseweb="select"] span,
[data-testid="stSidebarContent"] [data-baseweb="select"] div {{
  color: #1e1b4b !important;
  background: transparent !important;
}}

/* ══ SIDEBAR: EXPANDER SUMMARY (Voice Commands) ══ */
[data-testid="stSidebarContent"] details > summary,
[data-testid="stSidebarContent"] details > summary *,
[data-testid="stSidebarContent"] details > summary svg {{
  color: #1e1b4b !important;
  fill: #1e1b4b !important;
}}
[data-testid="stSidebarContent"] details {{
  background: rgba(99,102,241,0.06) !important;
  border: 1px solid rgba(99,102,241,0.25) !important;
  border-radius: 10px !important;
  padding: 4px 8px !important;
}}

/* ══ SIDEBAR: TOGGLE (Dark Mode) ══ */
[data-testid="stSidebarContent"] [data-testid="stToggle"] *,
[data-testid="stSidebarContent"] [data-baseweb="checkbox"] * {{
  color: #1e1b4b !important;
}}

/* ══ GLOBAL HR DIVIDERS ══ */
hr {{
  border: none !important;
  border-top: 1px solid rgba(99,102,241,0.35) !important;
  height: 0 !important;
  background: transparent !important;
  margin: 18px 0 !important;
}}

/* ══ CARDS ══ */
.feature-card, .glass-card {{
  background: #ffffff !important;
  box-shadow: 0 4px 24px rgba(99,102,241,0.15) !important;
  border: 1px solid rgba(99,102,241,0.28) !important;
}}
.grad-border {{
  background: #ffffff !important;
  box-shadow: 0 4px 24px rgba(99,102,241,0.15) !important;
}}

/* ══ DISPLAY BOXES ══ */
.display-box {{
  background: #eef0ff !important;
  border: 1px solid rgba(99,102,241,0.35) !important;
  color: #1e1b4b !important;
}}

/* ══ CHIP BUTTONS ══ */
.chip-col button {{
  background: rgba(99,102,241,0.08) !important;
  color: #3730a3 !important;
  border: 1px solid rgba(99,102,241,0.3) !important;
}}
.chip-col button:hover {{
  background: rgba(99,102,241,0.18) !important;
  color: #3730a3 !important;
}}

/* ══ TEXT INPUTS ══ */
.stTextInput input, .stTextArea textarea, .stNumberInput input {{
  background: #ffffff !important;
  color: #1e1b4b !important;
  border: 1.5px solid rgba(99,102,241,0.5) !important;
  box-shadow: 0 1px 4px rgba(99,102,241,0.08) !important;
}}
.stTextInput input:focus, .stTextArea textarea:focus {{
  border-color: #6366f1 !important;
  box-shadow: 0 0 0 3px rgba(99,102,241,0.15) !important;
}}

/* ══ SELECTBOX (main area) ══ */
.stSelectbox > div > div {{
  background: #ffffff !important;
  border: 1.5px solid rgba(99,102,241,0.5) !important;
  color: #1e1b4b !important;
}}

/* ══ STEP / ANSWER CARDS ══ */
.step-card {{
  background: #f5f6ff !important;
  border-left-color: #6366f1 !important;
  color: #1e1b4b !important;
}}
.answer-correct {{ background: rgba(16,185,129,0.08) !important; }}
.answer-wrong   {{ background: rgba(239,68,68,0.06) !important; }}
.answer-neutral {{ background: #f5f6ff !important; border: 1px solid rgba(99,102,241,0.2) !important; }}

/* ══ BADGES ══ */
.badge-done    {{ background: rgba(99,102,241,0.12) !important; }}
.badge-success {{ background: rgba(16,185,129,0.1) !important; }}

/* ══ EMPTY STATE ══ */
.empty-state {{
  background: #f0f2ff !important;
  border: 2px dashed rgba(99,102,241,0.35) !important;
}}

/* ══ TAB BAR ══ */
.stTabs [data-baseweb="tab-list"] {{
  background: #ffffff !important;
  box-shadow: 0 2px 12px rgba(99,102,241,0.12) !important;
}}

/* ══ METRIC CARDS ══ */
.metric-card {{
  background: #ffffff !important;
  box-shadow: 0 4px 16px rgba(99,102,241,0.12) !important;
}}

/* ══ CHAT MESSAGES ══ */
[data-testid="stChatMessage"] {{
  background: #ffffff !important;
  border: 1px solid rgba(99,102,241,0.18) !important;
  box-shadow: 0 2px 8px rgba(99,102,241,0.08) !important;
}}

/* ══ PROGRESS BAR TRACK ══ */
[data-testid="stProgressBar"] > div {{
  background: rgba(99,102,241,0.12) !important;
}}

/* ══ WARN/ERR/INFO CARDS ══ */
.warn-card {{ color: #92400e !important; background: rgba(251,191,36,0.12) !important; }}
.err-card  {{ color: #991b1b !important; background: rgba(239,68,68,0.08) !important; }}
.info-card {{ color: #0e7490 !important; background: rgba(6,182,212,0.08) !important; }}
"""}
</style>
""", unsafe_allow_html=True)


# ── Confetti ───────────────────────────────────────────────────────────────────
def _show_confetti():
    import random
    colors = ["#6366f1","#8b5cf6","#10b981","#fbbf24","#ef4444","#06b6d4","#f97316"]
    pieces = ""
    for i in range(80):
        c    = colors[i % len(colors)]
        left = (i * 13) % 100
        delay= round((i * 0.04) % 1.5, 2)
        dur  = round(2.5 + (i % 5) * 0.4, 1)
        size = 6 + (i % 8)
        rot  = (i * 37) % 360
        pieces += (
            f'<div class="confetti-piece" style="left:{left}%;background:{c};'
            f'width:{size}px;height:{size}px;animation-duration:{dur}s;'
            f'animation-delay:{delay}s;transform:rotate({rot}deg);"></div>'
        )
    import streamlit.components.v1 as components
    components.html(f"<div>{pieces}</div>", height=0)


# ── Gemini loader ──────────────────────────────────────────────────────────────
def _load_gemini(api_key: str):
    from utils.ai_helper import setup_gemini
    return setup_gemini(api_key)


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f'<h2 style="color:{_TITLE_C};font-size:1.15rem;font-weight:800;margin-bottom:12px;">{T["settings"]}</h2>', unsafe_allow_html=True)

    api_key = os.getenv("OPENAI_API_KEY", "") or os.getenv("GEMINI_API_KEY", "")

    grade = st.selectbox(
        T["class_grade"],
        ["LKG", "UKG", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
        index=7,  # default: Class 8
    )

    # Grade-aware subject selection — keeps every dropdown ≤ 6 items (always opens downward)
    if grade in ("LKG", "UKG"):
        # No subject choice at this level
        subject = "General"
        st.markdown(f'<span style="color:{_TEXT2};font-size:0.82rem;">Subject: General</span>', unsafe_allow_html=True)

    elif grade in ("11", "12"):
        # Two-tier: Stream (4 items) → Subject (≤5 items)  — both open downward safely
        if _lang == "hi":
            _stream_label = "धारा (Stream)"
            _stream_opts  = ["विज्ञान", "वाणिज्य", "कला / मानविकी", "सामान्य"]
            _stream_map   = {
                "विज्ञान":        (["भौतिकी", "रसायन विज्ञान", "जीव विज्ञान", "गणित", "कंप्यूटर विज्ञान"],
                                   ["Physics", "Chemistry", "Biology", "Mathematics", "Computer Science"]),
                "वाणिज्य":       (["अर्थशास्त्र", "व्यावसायिक अध्ययन", "गणित", "कंप्यूटर विज्ञान", "अंग्रेज़ी"],
                                   ["Economics", "Business Studies", "Mathematics", "Computer Science", "English"]),
                "कला / मानविकी": (["इतिहास", "राजनीति विज्ञान", "अर्थशास्त्र", "अंग्रेज़ी", "हिंदी"],
                                   ["History", "Political Science", "Economics", "English", "Hindi"]),
                "सामान्य":       (["सामान्य"], ["General"]),
            }
        else:
            _stream_label = "Stream"
            _stream_opts  = ["Science", "Commerce", "Arts / Humanities", "General"]
            _stream_map   = {
                "Science":          (["Physics", "Chemistry", "Biology", "Mathematics", "Computer Science"],
                                     ["Physics", "Chemistry", "Biology", "Mathematics", "Computer Science"]),
                "Commerce":         (["Economics", "Business Studies", "Mathematics", "Computer Science", "English"],
                                     ["Economics", "Business Studies", "Mathematics", "Computer Science", "English"]),
                "Arts / Humanities":(["History", "Political Science", "Economics", "English", "Hindi"],
                                     ["History", "Political Science", "Economics", "English", "Hindi"]),
                "General":          (["General"], ["General"]),
            }

        _stream = st.selectbox(_stream_label, _stream_opts)
        _disp_opts, _eng_opts = _stream_map.get(_stream, (["General"], ["General"]))
        subject_display = st.selectbox(T["subject"], _disp_opts)
        _si = _disp_opts.index(subject_display) if subject_display in _disp_opts else 0
        subject = _eng_opts[_si]

    else:
        # Class 1–10: 6 subjects — always fits below the selectbox
        if _lang == "hi":
            _subj_opts = ["विज्ञान", "गणित", "हिंदी", "अंग्रेज़ी", "सामाजिक विज्ञान", "सामान्य"]
        else:
            _subj_opts = ["Science", "Mathematics", "Hindi", "English", "Social Science", "General"]
        subject_display = st.selectbox(T["subject"], _subj_opts)
        subject = T["subject_map"].get(subject_display, subject_display)

    # Language selector — controls both UI and TTS
    lang_choice = st.selectbox(T["lang_label"], ["English", "हिंदी (Hindi)"])
    new_ui_lang = "hi" if "हिंदी" in lang_choice else "en"
    if new_ui_lang != st.session_state.get("ui_lang", "en"):
        st.session_state["ui_lang"] = new_ui_lang
        st.rerun()

    # Auto-clear cached results when grade or subject changes
    _gs_key = f"{grade}__{subject}"
    if st.session_state.get("_last_grade_subj") != _gs_key:
        st.session_state["_last_grade_subj"]      = _gs_key
        st.session_state["concept_data"]           = {}
        st.session_state["_diagram_img"]           = None
        st.session_state["_last_diagram_concept"]  = ""
        st.session_state["quiz_questions"]         = []
        st.session_state["quiz_answered"]          = {}
        st.session_state["quiz_index"]             = 0
        st.session_state["quiz_score"]             = 0
        st.session_state["activity_data"]          = None
        st.session_state["t1_text_input"]          = ""
        st.session_state["t2_text_input"]          = ""
        st.session_state["t4_text_input"]          = ""
        st.session_state["_t1_gpt4o_answer"]       = ""
        st.session_state["_t1_stream_concept"]     = ""
        st.session_state["t6_chat_history"]        = []
        st.session_state["trans_result"]           = {}
        st.session_state["t3_text_input"]          = ""

    st.markdown("---")
    new_dark = st.toggle(T["dark_mode"], value=st.session_state.dark_mode)
    if new_dark != st.session_state.dark_mode:
        st.session_state.dark_mode = new_dark
        st.rerun()

    if st.session_state.get("last_tts_text"):
        if st.button(T["repeat_last"], key="rpt_btn_sb", use_container_width=True):
            st.session_state["_repeat_now"] = True
            st.rerun()

    with st.expander(T["voice_commands"]):
        st.markdown(T["voice_help"])

    st.markdown("---")
    st.markdown(f"""
<div style="background:rgba(99,102,241,0.1);border:1px solid rgba(99,102,241,0.3);
border-radius:12px;padding:14px 16px;">
<div style="font-weight:800;color:#818cf8;font-size:0.9rem;margin-bottom:8px;">📚 ShikshAI</div>
<div style="color:{'#94a3b8' if dark else '#374151'};font-size:0.8rem;line-height:1.6;">{T['about_box']}</div>
</div>
""", unsafe_allow_html=True)

    st.markdown("")
    if st.button(T["reset_session"], key="reset_btn"):
        for k, v in _defaults.items():
            st.session_state[k] = v
        st.toast(T.get("reset_toast", "Session reset! 🔄"), icon="✅")
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════════════
from utils.favicon_b64 import FAVICON_B64
st.markdown(f"""
<div class="main-header">
  <h1><img src="{FAVICON_B64}" style="height:48px;width:48px;vertical-align:middle;margin-right:10px;border-radius:10px;"> {T['header_title']}</h1>
  <p>{"आवाज़-सक्षम AI शिक्षण सहायक" if _lang == "hi" else "Voice-Enabled AI Teaching Assistant"}</p>
  <div class="header-pills">
    <span class="hpill">{T['pill_ai']}</span>
    <span class="hpill">{T['pill_voice']}</span>
    <span class="hpill">{T['pill_board']}</span>
    <span class="hpill">{T['pill_lang']}</span>
    <span class="hpill">{T['pill_analytics']}</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── API key gate ───────────────────────────────────────────────────────────────
if not api_key:
    st.markdown(f"""
<div class="glass-card" style="border-left:4px solid #ef4444;text-align:center;padding:30px;">
  <div style="font-size:2rem;margin-bottom:12px;">🔑</div>
  <div style="font-weight:700;font-size:1.1rem;color:#fca5a5;">{T['api_key_missing']}</div>
  <div style="color:#94a3b8;margin-top:6px;">{T['api_key_help']}</div>
</div>
""", unsafe_allow_html=True)
    st.stop()

model = _load_gemini(api_key)


# ══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════

def record_and_transcribe(label: str, auto_clear: bool = False,
                          state_key: str = None) -> str:
    # auto_clear: after transcription, bump widget key so mic resets on next render
    if auto_clear and state_key:
        pending_key = f"_{state_key}_pending"
        pending = st.session_state.pop(pending_key, "")
        if pending:
            return pending
        widget_key = f"{state_key}_{st.session_state.get(state_key, 0)}"
        audio = st.audio_input(label, key=widget_key)
    else:
        audio = st.audio_input(label)

    if audio:
        with st.spinner("🔄 Transcribing…"):
            from utils.stt import transcribe_audio
            text, lang = transcribe_audio(audio.read())
        if text and not text.startswith("Transcription error"):
            st.markdown(
                f'<span class="badge badge-done">{T["transcribed"]} ({lang})</span>',
                unsafe_allow_html=True)
            st.markdown(
                f'<div class="display-box" style="margin-bottom:10px;">'
                f'{T["you_said"]} {text}</div>',
                unsafe_allow_html=True)
            if auto_clear and state_key:
                st.session_state[pending_key] = text
                st.session_state[state_key] = st.session_state.get(state_key, 0) + 1
                st.rerun()
            return text
        elif text.startswith("Transcription error"):
            _warn(text)
    return ""


def play_tts(text: str, lang: str = "hi"):
    if not text:
        return
    st.session_state["last_tts_text"] = text
    st.session_state["last_tts_lang"] = lang
    with st.spinner(T["tts_spinner"]):
        from utils.tts import speak, audio_player_html
        audio_bytes = speak(text, lang=lang)
        if audio_bytes:
            st.markdown(audio_player_html(audio_bytes, autoplay=True),
                        unsafe_allow_html=True)


def show_board_image(img_bytes: bytes):
    from utils.visuals import img_to_display
    st.markdown(
        f'<img src="{img_to_display(img_bytes)}" class="board-image" />',
        unsafe_allow_html=True)


def render_mermaid(mermaid_code: str, height: int = 290):
    if not mermaid_code or len(mermaid_code) < 10:
        return
    clean = mermaid_code.strip()
    if clean.startswith("```"):
        parts = clean.split("\n", 1)
        clean = parts[1].rsplit("```", 1)[0].strip() if len(parts) > 1 else clean
    html = f"""<!DOCTYPE html><html><head>
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<style>
  body{{margin:0;padding:8px;background:transparent;}}
  .mermaid{{background:rgba(22,28,60,0.88);border-radius:12px;padding:16px;text-align:center;}}
  svg{{max-width:100%;height:auto;}}
</style></head><body>
<div class="mermaid">{clean}</div>
<script>mermaid.initialize({{startOnLoad:true,theme:'dark',securityLevel:'loose',
flowchart:{{useMaxWidth:true,htmlLabels:false}}}});</script>
</body></html>"""
    import streamlit.components.v1 as components
    components.html(html, height=height, scrolling=False)


def save_to_history(feature: str, topic: str = "",
                    data: dict = None, score_pct: float = None):
    try:
        from services.history import save
        save(feature=feature, topic=topic,
             grade=grade, subject=subject,
             data=data or {}, score_pct=score_pct)
    except Exception:
        pass


def detect_input_lang(text: str) -> str:
    if not text:
        return "en"
    deva  = sum(1 for c in text if 'ऀ' <= c <= 'ॿ')
    alpha = sum(1 for c in text if c.isalpha())
    return "hi" if alpha and (deva / alpha) > 0.25 else "en"


def _warn(msg: str):
    st.markdown(f'<div class="warn-card">⚠️ {msg}</div>', unsafe_allow_html=True)


def _err(msg: str):
    st.markdown(f'<div class="err-card">❌ {msg}</div>', unsafe_allow_html=True)


def _info(msg: str):
    st.markdown(f'<div class="info-card">ℹ️ {msg}</div>', unsafe_allow_html=True)


def _copy_btn(text: str, label: str = "📋 Copy", height: int = 44):
    import streamlit.components.v1 as components
    safe = text.replace("\\", "\\\\").replace("`", "\\`").replace("$", "\\$")
    components.html(f"""
<button onclick="
  navigator.clipboard.writeText(`{safe}`).then(()=>{{
    this.textContent='✅ Copied!';
    this.style.borderColor='#10b981';
    this.style.color='#34d399';
    setTimeout(()=>{{
      this.textContent='{label}';
      this.style.borderColor='';
      this.style.color='';
    }},1600);
  }}).catch(()=>{{
    this.textContent='⚠️ Failed'; setTimeout(()=>this.textContent='{label}',1600);
  }})
" class="action-pill">{label}</button>
<style>
  .action-pill{{display:inline-flex;align-items:center;gap:5px;
    background:rgba(99,102,241,0.12);color:#818cf8;
    border:1px solid rgba(99,102,241,0.35);border-radius:50px;
    padding:5px 14px;font-size:0.8rem;font-weight:600;
    cursor:pointer;transition:all 0.18s;font-family:Inter,sans-serif;}}
  .action-pill:hover{{background:rgba(99,102,241,0.28);}}
</style>
""", height=height)


def _empty_state(icon: str, title: str, sub: str):
    st.markdown(f"""
<div class="empty-state">
  <span class="empty-icon">{icon}</span>
  <div style="font-size:1.05rem;font-weight:600;margin-bottom:6px;">{title}</div>
  <div style="font-size:0.88rem;">{sub}</div>
</div>""", unsafe_allow_html=True)


def _chip_buttons(items: list, key_prefix: str, state_key: str, auto_action: str = None):
    """Render clickable chip buttons, 3 per row.
    auto_action: if set, also sets session_state[auto_action]=True to trigger processing."""
    per_row = 3
    for row_start in range(0, len(items), per_row):
        row = items[row_start : row_start + per_row]
        cols = st.columns(len(row))
        for i, item in enumerate(row):
            with cols[i]:
                if st.button(item, key=f"{key_prefix}_{row_start+i}",
                             use_container_width=True):
                    st.session_state[state_key] = item
                    if auto_action:
                        st.session_state[auto_action] = True
                    st.rerun()


# ── Repeat last TTS ────────────────────────────────────────────────────────────
if st.session_state.get("_repeat_now"):
    st.session_state["_repeat_now"] = False
    _last = st.session_state.get("last_tts_text","")
    if _last:
        play_tts(_last, lang=st.session_state.get("last_tts_lang","hi"))


# ══════════════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    T["tab1"], T["tab2"], T["tab3"], T["tab4"], T["tab5"], T["tab6"],
])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Concept Simplification
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown(f'<div class="section-title">{T["t1_title"]}</div>', unsafe_allow_html=True)
    st.caption(T["t1_caption"])

    col_l, col_r = st.columns([1, 1], gap="large")

    with col_l:
        spoken  = record_and_transcribe(T["t1_record"])
        st.markdown(f'<div style="color:{_TEXT2};font-size:0.8rem;margin:4px 0 2px;">{T["t1_quick"]}</div>',
                    unsafe_allow_html=True)
        _chip_buttons(get_concept_topics(grade, subject, _lang), "chip_t1", "t1_text_input", auto_action="_t1_auto_explain")
        typed   = st.text_input(T["t1_type"], placeholder=T["t1_placeholder"],
                                key="t1_text_input")
        concept = spoken or typed

        do_explain = st.button(T["t1_btn"], key="explain_btn") or st.session_state.pop("_t1_auto_explain", False)
        if do_explain:
            if not concept:
                _warn(T["t1_warn"])
            else:
                st.session_state["_t1_stream_concept"] = concept
                st.session_state["_t1_gpt4o_answer"]   = ""
                st.session_state["concept_data"]        = {}
                st.session_state["_diagram_img"]        = None
                st.session_state["_last_diagram_concept"] = concept
                st.rerun()

        data = st.session_state.get("concept_data", {})
        pass  # answer shown in right column

    with col_r:
        _stream_concept = st.session_state.get("_t1_stream_concept", "")

        # ── Stream gpt-4o answer then generate card data ──────────────────────
        if _stream_concept and not st.session_state.get("_t1_gpt4o_answer"):
            from utils.ai_helper import stream_chat_answer, simplify_concept

            # Card data first (needed for diagram spinner below)
            with st.spinner(T["t1_spinner"]):
                data = simplify_concept(model, _stream_concept, grade, subject, lang=_lang)
                st.session_state["concept_data"] = data
                save_to_history("concept", _stream_concept, data)

            # Generate diagram immediately after card data
            with st.spinner(T["t1_diag_spin"]):
                from utils.visuals import execute_diagram_code, create_concept_diagram, create_body_parts_diagram
                from utils.ai_helper import generate_diagram_code
                _body_kw = [
                    "body", "parts of body", "body part", "human body",
                    "शरीर", "शरीर के अंग", "मानव शरीर", "anatomy", "organ",
                ]
                _is_body = any(kw in _stream_concept.lower() for kw in _body_kw)
                if _is_body:
                    _diag = create_body_parts_diagram(grade, _lang)
                else:
                    try:
                        _diag = execute_diagram_code(
                            generate_diagram_code(model, _stream_concept, grade, subject, _lang)
                        )
                    except Exception:
                        _diag = None
                    if not _diag:
                        _diag = create_concept_diagram(data) if data else None
                st.session_state["_diagram_img"] = _diag

            # Streaming explanation last
            st.session_state["_t1_gpt4o_answer"] = "__streaming__"
            st.rerun()

        # ── ORDER: Diagram → Smart Board card → Full Explanation ──────────────
        data       = st.session_state.get("concept_data", {})
        has_answer = st.session_state.get("_t1_gpt4o_answer", "")
        _do_stream = has_answer == "__streaming__"

        if _do_stream or (data and ("explanation" in data or "title" in data)):

            # 1. CONCEPT DIAGRAM (top)
            st.markdown(T["t1_diagram"])
            diag_img = st.session_state.get("_diagram_img")
            if diag_img:
                show_board_image(diag_img)
            elif data:
                render_mermaid(data.get("mermaid", ""), height=300)

            # 2. SMART BOARD VISUAL
            if data and ("explanation" in data or "title" in data):
                st.markdown(T["t1_board"])
                from utils.visuals import create_concept_card
                show_board_image(create_concept_card(data))

                st.markdown(T["t1_voice"])
                speak_text = data.get("speak_text", data.get("explanation", ""))
                play_tts(speak_text, lang=tts_lang)

            # 3. FULL EXPLANATION (streaming gpt-4o, bottom)
            _cur_concept = st.session_state.get("_t1_stream_concept", "")
            if _cur_concept:
                st.markdown(T["t1_expander"].replace("📖 ", "#### 📖 "))
                if _do_stream:
                    from utils.ai_helper import stream_chat_answer
                    _q = (f"Explain '{_cur_concept}' to Grade {grade} {subject} students."
                          if _lang == "en"
                          else f"कक्षा {grade} के {subject} के छात्रों को '{_cur_concept}' समझाओ।")
                    with st.chat_message("assistant"):
                        _streamed = st.write_stream(
                            stream_chat_answer(model,
                                               [{"role": "user", "content": _q}],
                                               grade, subject, _lang)
                        )
                    st.session_state["_t1_gpt4o_answer"] = _streamed
                else:
                    with st.chat_message("assistant"):
                        st.markdown(has_answer)
                # Copy + Speak buttons for explanation
                _ans_text = st.session_state.get("_t1_gpt4o_answer", "")
                if _ans_text and _ans_text != "__streaming__":
                    _cb1, _cb2, _ = st.columns([1, 1, 3])
                    with _cb1:
                        _copy_btn(_ans_text, "📋 Copy")
                    with _cb2:
                        if st.button("🔊 Speak", key="t1_speak_ans"):
                            play_tts(_ans_text[:600], lang=tts_lang)
        else:
            _empty_state("🧠", T["t1_empty_title"], T["t1_empty_sub"])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Voice Quiz
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown(f'<div class="section-title">{T["t2_title"]}</div>', unsafe_allow_html=True)
    st.caption(T["t2_caption"])

    col_q1, col_q2 = st.columns([1, 1], gap="large")

    with col_q1:
        spoken_topic = record_and_transcribe(T["t2_record"])
        _chip_buttons(get_concept_topics(grade, subject, _lang), "chip_t2", "t2_text_input", auto_action="_t2_auto_quiz")
        typed_topic  = st.text_input(T["t2_type"], placeholder=T["t2_placeholder"],
                                     key="t2_text_input")
        topic_val = spoken_topic or typed_topic
        num_q = st.slider(T["t2_num_q"], 2, 8, 4)

        do_quiz = st.button(T["t2_btn"], key="quiz_gen_btn") or st.session_state.pop("_t2_auto_quiz", False)
        if do_quiz:
            if not topic_val:
                _warn(T["t2_warn"])
            else:
                with st.spinner(T["t2_spinner"]):
                    from utils.ai_helper import generate_quiz
                    questions = generate_quiz(model, topic_val, num_q, grade, subject, lang=_lang)
                    if questions:
                        st.session_state.quiz_questions  = questions
                        st.session_state.quiz_index      = 0
                        st.session_state.quiz_answered   = {}
                        st.session_state.quiz_score      = 0
                        st.session_state.quiz_saved      = False
                        st.session_state.quiz_topic_name = topic_val
                        st.session_state._show_confetti  = False
                        play_tts(
                            T["t2_tts_start"].format(n=len(questions), topic=topic_val),
                            lang=tts_lang)
                    else:
                        _err(T["t2_err"])

        qs = st.session_state.quiz_questions
        if qs:
            idx   = st.session_state.quiz_index
            total = len(qs)
            answered_count = len(st.session_state.quiz_answered)

            st.markdown(
                f'<div style="display:flex;justify-content:space-between;align-items:center;'
                f'margin:10px 0 4px;"><span style="color:{_TEXT2};font-size:0.88rem;">'
                f'{T["t2_progress"].format(idx=idx+1, total=total)}</span>'
                f'<span class="badge badge-done">'
                f'{T["t2_answered"].format(a=answered_count, t=total)}</span></div>',
                unsafe_allow_html=True)
            st.progress((idx + 1) / total)

            nav1, nav2 = st.columns(2)
            with nav1:
                if st.button(T["t2_prev"], key="prev_q") and idx > 0:
                    st.session_state.quiz_index -= 1
                    st.rerun()
            with nav2:
                if st.button(T["t2_next"], key="next_q") and idx < total - 1:
                    st.session_state.quiz_index += 1
                    st.rerun()

            if answered_count == total:
                score = st.session_state.quiz_score
                pct   = int(score / total * 100)
                col_c = "#10b981" if pct >= 70 else "#fbbf24" if pct >= 40 else "#ef4444"
                g_label = T["t2_excellent"] if pct >= 80 else T["t2_good"] if pct >= 60 else T["t2_practice"]

                if pct >= 60 and not st.session_state.get("_show_confetti"):
                    st.session_state["_show_confetti"] = True
                    _show_confetti()

                st.markdown(f"""
<div class="score-box" style="background:linear-gradient(135deg,{col_c}18,{col_c}28);
     border:2px solid {col_c};border-radius:16px;padding:22px;text-align:center;margin-top:14px;">
  <div style="font-size:3rem;font-weight:900;color:{col_c};line-height:1;">{score}/{total}</div>
  <div style="font-size:1.6rem;font-weight:700;color:{col_c};margin:4px 0;">{pct}%</div>
  <div style="color:{_TEXT2};font-size:1rem;margin-top:6px;">{g_label}</div>
</div>""", unsafe_allow_html=True)

                if not st.session_state.quiz_saved:
                    save_to_history("quiz", st.session_state.quiz_topic_name, score_pct=float(pct))
                    st.session_state.quiz_saved = True
                    st.toast(T.get("quiz_saved_toast", "Quiz saved!") + f" Score: {pct}% 🎯", icon="✅")
                    play_tts(
                        T["t2_tts_done"].format(
                            pct=pct,
                            label=g_label.replace("🎉","").replace("👍","").replace("📚","").strip()),
                        lang=tts_lang)

                st.markdown("---")
                try:
                    from services.pdf_gen import generate_quiz_pdf
                    pdf_bytes = generate_quiz_pdf(
                        st.session_state.quiz_topic_name, grade, subject, qs)
                    st.download_button(
                        label=T["t2_pdf"],
                        data=pdf_bytes,
                        file_name=f"ShikshAI_Quiz_{st.session_state.quiz_topic_name.replace(' ','_')[:30]}.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )
                except Exception as e:
                    _warn(f"{T['t2_pdf_err']} {e}")

    with col_q2:
        qs = st.session_state.quiz_questions
        if qs:
            idx  = st.session_state.quiz_index
            q    = qs[idx]
            from utils.visuals import create_quiz_card

            st.markdown(T["t2_board"])
            show_board_image(create_quiz_card(q, idx + 1, len(qs)))

            st.markdown(T["t2_choose"])
            answered = st.session_state.quiz_answered
            correct  = q.get("answer","A")
            opts     = q.get("options", {})

            for key, val in opts.items():
                if idx in answered:
                    if key == correct:
                        st.markdown(
                            f'<div class="answer-correct">✅ <b>{key})</b> {val}</div>',
                            unsafe_allow_html=True)
                    elif key == answered[idx]:
                        st.markdown(
                            f'<div class="answer-wrong">❌ <b>{key})</b> {val}</div>',
                            unsafe_allow_html=True)
                    else:
                        st.markdown(
                            f'<div class="answer-neutral"><b>{key})</b> {val}</div>',
                            unsafe_allow_html=True)
                else:
                    if st.button(f"{key}) {val}", key=f"opt_{idx}_{key}"):
                        answered[idx] = key
                        if key == correct:
                            st.session_state.quiz_score += 1
                            play_tts(T["t2_tts_correct"], lang=tts_lang)
                        else:
                            play_tts(T["t2_tts_wrong"].format(ans=correct), lang=tts_lang)
                        st.session_state.quiz_answered = answered
                        st.rerun()

            if idx in answered and q.get("explanation"):
                st.markdown(f"""
<div class="glass-card" style="border-left:4px solid #6366f1;margin-top:10px;">
  {T['t2_expl']} {q['explanation']}
</div>""", unsafe_allow_html=True)
        else:
            _empty_state("❓", T["t2_empty_title"], T["t2_empty_sub"])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — Bilingual Translation
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown(f'<div class="section-title">{T["t3_title"]}</div>', unsafe_allow_html=True)
    st.caption(T["t3_caption"])

    auto_detect = st.checkbox(T["t3_auto"], value=True, help=T["t3_auto_help"])
    if not auto_detect:
        direction = st.radio(T["t3_dir_label"],
                             [T["t3_en_hi"], T["t3_hi_en"]], horizontal=True)
        dir_code = "en_to_hi" if T["t3_en_hi"] in direction else "hi_to_en"
        in_label = T["t3_in_label_en"] if dir_code == "en_to_hi" else T["t3_in_label_hi"]
    else:
        dir_code, in_label = "auto", T["t3_in_label_auto"]

    col_t1, col_t2 = st.columns([1, 1], gap="large")

    with col_t1:
        spoken_text = record_and_transcribe(T["t3_record"].format(lang=in_label))
        _chip_buttons(T["t3_quick_list"], "chip_t3", "t3_text_input")
        typed_text  = st.text_input(T["t3_type"], placeholder=T["t3_placeholder"],
                                    key="t3_text_input")
        source_text = spoken_text or typed_text

        if st.button(T["t3_btn"], key="translate_btn"):
            if not source_text:
                _warn(T["t3_warn"])
            else:
                if dir_code == "auto":
                    detected_lang = detect_input_lang(source_text)
                    actual_dir    = "en_to_hi" if detected_lang == "en" else "hi_to_en"
                    dir_label     = T["t3_en_hi"] if actual_dir == "en_to_hi" else T["t3_hi_en"]
                    st.markdown(
                        f'<span class="badge badge-success">🔍 {T["t3_detected"]} {dir_label}</span>',
                        unsafe_allow_html=True)
                else:
                    actual_dir = dir_code
                with st.spinner(T["t3_spinner"]):
                    from utils.ai_helper import translate_content
                    result = translate_content(model, source_text, actual_dir)
                    st.session_state["trans_result"] = result
                    st.session_state["trans_actual_dir"] = actual_dir
                    save_to_history("translation", source_text[:60], result)

    with col_t2:
        result = st.session_state.get("trans_result", {})
        if result and "translation" in result:
            st.markdown(T["t3_board"])
            from utils.visuals import create_translation_card
            show_board_image(create_translation_card(result))

            st.markdown(T["t3_trans_label"])
            st.markdown(
                f'<div class="display-box" style="font-size:1.15rem;">'
                f'{result.get("translation","")}</div>',
                unsafe_allow_html=True)

            if result.get("transliteration"):
                st.markdown(
                    f'<div class="display-box" style="color:{_TEXT2};font-size:0.95rem;margin-top:8px;">'
                    f'{T["t3_pron"]} {result["transliteration"]}</div>',
                    unsafe_allow_html=True)

            _actual_dir = st.session_state.get("trans_actual_dir", dir_code)
            out_lang = "en" if _actual_dir == "hi_to_en" else "hi"
            play_tts(result.get("speak_text", result.get("translation","")), lang=out_lang)

            kws = result.get("key_words", [])
            if kws:
                with st.expander(T["t3_vocab"]):
                    col_kw1, col_kw2 = st.columns(2)
                    for i, kw in enumerate(kws[:6]):
                        if isinstance(kw, dict):
                            vals = list(kw.values())
                            col  = col_kw1 if i % 2 == 0 else col_kw2
                            pron = (f'<br><span style="color:#94a3b8;font-size:0.82rem;">{vals[2]}</span>'
                                    if len(vals) > 2 else "")
                            col.markdown(
                                f'<div class="glass-card" style="padding:10px 14px;margin:4px 0;">'
                                f'<b style="color:{_TITLE_C};">{vals[0]}</b> → {vals[1]}{pron}</div>',
                                unsafe_allow_html=True)
        else:
            _empty_state("🌐", T["t3_empty_title"], T["t3_empty_sub"])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — Activity Guide
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown(f'<div class="section-title">{T["t4_title"]}</div>', unsafe_allow_html=True)
    st.caption(T["t4_caption"])

    col_a1, col_a2 = st.columns([1, 1], gap="large")

    with col_a1:
        spoken_act    = record_and_transcribe(T["t4_record"])
        _chip_buttons(get_activity_topics(grade, subject, _lang), "chip_t4", "t4_text_input")
        typed_act     = st.text_input(T["t4_type"], placeholder=T["t4_placeholder"],
                                      key="t4_text_input")
        activity_text = spoken_act or typed_act
        duration = st.number_input(T["t4_duration"], min_value=5, max_value=60,
                                   value=10, step=5)

        if st.button(T["t4_btn"], key="activity_btn"):
            if not activity_text:
                _warn(T["t4_warn"])
            else:
                with st.spinner(T["t4_spinner"]):
                    from utils.ai_helper import generate_activity
                    act_data = generate_activity(model, activity_text, int(duration), grade, subject, lang=_lang)
                    st.session_state.activity_data = act_data
                    save_to_history("activity", activity_text[:60], act_data)
                    intro = act_data.get("speak_intro","")
                    if intro and not intro.startswith("AI error"):
                        play_tts(intro, lang=tts_lang)

        st.markdown("---")
        st.markdown(T["t4_timer_title"])
        timer_mins = st.number_input(T["t4_timer_dur"], 1, 60, int(duration),
                                     key="timer_mins")

        if st.button(T["t4_start_timer"], key="timer_start"):
            timer_secs = int(timer_mins) * 60
            import streamlit.components.v1 as components
            components.html(f"""<!DOCTYPE html><html><head>
<style>
  body{{margin:0;padding:16px;background:transparent;font-family:'Inter',sans-serif;}}
  #wrap{{background:rgba(22,28,60,0.85);border:2px solid rgba(99,102,241,0.4);
        border-radius:16px;padding:24px;text-align:center;}}
  #td{{font-size:5rem;font-weight:900;font-family:monospace;color:#10b981;
      text-shadow:0 0 30px rgba(16,185,129,0.5);transition:color 0.5s;}}
  #ts{{color:#94a3b8;font-size:1rem;margin-top:10px;}}
  #bw{{background:rgba(255,255,255,0.08);border-radius:50px;height:8px;
       margin-top:16px;overflow:hidden;}}
  #bar{{background:linear-gradient(90deg,#4f46e5,#10b981);height:100%;
        width:100%;border-radius:50px;transition:width 1s linear;}}
</style></head><body>
<div id="wrap">
  <div id="td">{int(timer_mins):02d}:00</div>
  <div id="ts">{T['t4_timer_run']}</div>
  <div id="bw"><div id="bar"></div></div>
</div>
<script>
var total={timer_secs},r=total;
var bar=document.getElementById('bar');
var iv=setInterval(function(){{
  r--;
  var m=Math.floor(r/60),s=r%60;
  document.getElementById('td').textContent=String(m).padStart(2,'0')+':'+String(s).padStart(2,'0');
  bar.style.width=(r/total*100)+'%';
  if(r<=60){{
    document.getElementById('td').style.color='#fbbf24';
    document.getElementById('td').style.textShadow='0 0 30px rgba(251,191,36,0.5)';
    bar.style.background='linear-gradient(90deg,#fbbf24,#f97316)';
  }}
  if(r<=0){{
    clearInterval(iv);
    document.getElementById('td').textContent='00:00';
    document.getElementById('td').style.color='#ef4444';
    document.getElementById('ts').textContent='{T["t4_time_up"]}';
    bar.style.width='0%';
  }}
}},1000);
</script></body></html>""", height=195)

    with col_a2:
        act = st.session_state.get("activity_data")
        if act:
            st.markdown(T["t4_board"])
            from utils.visuals import create_activity_card
            show_board_image(create_activity_card(act))

            title = act.get("title","Activity")
            st.markdown(f"""
<div class="grad-border" style="margin:14px 0;">
  <div style="font-size:1.3rem;font-weight:800;color:white;margin-bottom:6px;">{title}</div>
  <div style="color:rgba(255,255,255,0.8);">{act.get('objective','')}</div>
  <div style="display:flex;gap:16px;margin-top:10px;flex-wrap:wrap;">
    <span style="color:#94a3b8;font-size:0.84rem;">{T['t4_group']} {act.get('group_size','—')}</span>
    <span style="color:#94a3b8;font-size:0.84rem;">{T['t4_time_icon']} {int(duration)} min</span>
  </div>
</div>""", unsafe_allow_html=True)

            mats = act.get("materials",[])
            if mats:
                mat_html = "".join(
                    f'<span style="background:rgba(251,191,36,0.15);border:1px solid rgba(251,191,36,0.4);'
                    f'border-radius:8px;padding:4px 12px;font-size:0.85rem;color:#fbbf24;">{m}</span>'
                    for m in mats)
                st.markdown(
                    f'<div style="margin:8px 0 4px;font-weight:700;color:{_TEXT2};font-size:0.9rem;">'
                    f'{T["t4_materials"]}</div><div style="display:flex;flex-wrap:wrap;gap:6px;">{mat_html}</div>',
                    unsafe_allow_html=True)

            steps = act.get("steps",[])
            if steps:
                st.markdown(f'<div style="font-weight:700;color:{_TEXT2};margin:14px 0 8px;">{T["t4_steps"]}</div>',
                            unsafe_allow_html=True)
                for s in steps:
                    dur_txt = f"{T['t4_time_icon']} {s.get('duration_min','')} min" if s.get("duration_min") else ""
                    tip_txt = (f"<br><span style='color:{_TEXT2};font-size:0.82rem;'>💡 {s['teacher_tip']}</span>"
                               if s.get("teacher_tip") else "")
                    st.markdown(f"""<div class="step-card">
  <span style="background:linear-gradient(135deg,#4f46e5,#7c3aed);color:white;
     width:26px;height:26px;border-radius:50%;display:inline-flex;align-items:center;
     justify-content:center;font-weight:800;font-size:0.85rem;margin-right:10px;
     flex-shrink:0;">{s.get('step','')}</span>
  <b>{s.get('instruction','')}</b>
  <span style="color:{_TEXT2};font-size:0.84rem;margin-left:8px;">{dur_txt}</span>{tip_txt}
</div>""", unsafe_allow_html=True)

            if act.get("assessment"):
                st.markdown(f"""<div class="glass-card" style="border-left:4px solid #10b981;margin-top:10px;">
  {T['t4_check']} {act['assessment']}
</div>""", unsafe_allow_html=True)

            if act.get("teacher_note"):
                st.markdown(f"""<div class="glass-card" style="border-left:4px solid #fbbf24;margin-top:8px;">
  {T['t4_note']} {act['teacher_note']}
</div>""", unsafe_allow_html=True)

            if st.button(T["t4_speak"], key="speak_guide"):
                steps_text = " ".join(
                    f"Step {s.get('step','')}: {s.get('instruction','')}" for s in steps[:4])
                play_tts(f"{act.get('speak_intro','')} {steps_text}"[:500], lang=tts_lang)
        else:
            _empty_state("⏱️", T["t4_empty_title"], T["t4_empty_sub"])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — Teacher Dashboard
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown(f'<div class="section-title">{T["t5_title"]}</div>', unsafe_allow_html=True)
    st.caption(T["t5_caption"])

    try:
        import pandas as pd
        import matplotlib.pyplot as plt
        from services.history import stats as get_stats, recent as get_recent, clear_all

        s    = get_stats()
        feat = s.get("by_feature", {})

        # ── Metric cards ───────────────────────────────────────────────────────
        m_data = [
            (T["t5_total"],    s.get("total",0)),
            (T["t5_concepts"], feat.get("concept",0)),
            (T["t5_quizzes"],  feat.get("quiz",0)),
            (T["t5_trans"],    feat.get("translation",0)),
            (T["t5_avg"],      f"{s.get('avg_quiz_score',0):.0f}%"),
        ]
        cols = st.columns(5)
        for col, (label, val) in zip(cols, m_data):
            col.markdown(f"""
<div class="metric-card">
  <div class="metric-value">{val}</div>
  <div class="metric-label">{label}</div>
</div>""", unsafe_allow_html=True)

        st.markdown("---")
        col_d1, col_d2 = st.columns([1, 1], gap="large")

        with col_d1:
            if feat:
                fig, ax = plt.subplots(figsize=(5, 3.2))
                fig.patch.set_facecolor("#0a0f2e" if dark else "#f0f4ff")
                ax.set_facecolor("#0d1235" if dark else "#ffffff")
                labels = [{"concept":"Concept","quiz":"Quiz",
                           "translation":"Translation","activity":"Activity"}.get(k,k)
                          for k in feat]
                values = list(feat.values())
                colors = ["#6366f1","#10b981","#fbbf24","#f97316"]
                bars = ax.barh(labels, values, color=colors[:len(labels)],
                               height=0.55, edgecolor="none")
                for bar, v in zip(bars, values):
                    ax.text(bar.get_width()+0.05, bar.get_y()+bar.get_height()/2,
                            str(v), va='center', ha='left',
                            color="#e2e8f0" if dark else "#1e293b",
                            fontsize=10, fontweight='bold')
                ax.set_xlabel("Sessions", color="#94a3b8", fontsize=9)
                ax.tick_params(colors="#94a3b8", labelsize=9)
                for spine in ax.spines.values():
                    spine.set_visible(False)
                ax.xaxis.grid(True, color="rgba(255,255,255,0.06)",
                              linestyle='--', linewidth=0.8)
                plt.tight_layout(pad=1.5)
                st.markdown(T["t5_feat_chart"])
                st.pyplot(fig, use_container_width=True)
                plt.close(fig)

            recent_scores = s.get("recent_scores",[])
            if len(recent_scores) > 1:
                fig2, ax2 = plt.subplots(figsize=(5, 2.8))
                fig2.patch.set_facecolor("#0a0f2e" if dark else "#f0f4ff")
                ax2.set_facecolor("#0d1235" if dark else "#ffffff")
                scores_rev = recent_scores[::-1]
                x = range(1, len(scores_rev)+1)
                ax2.fill_between(x, scores_rev, alpha=0.25, color="#6366f1")
                ax2.plot(x, scores_rev, color="#818cf8", linewidth=2.5,
                         marker='o', markersize=6, markerfacecolor="#6366f1")
                ax2.axhline(60, color="#10b981", linestyle='--', linewidth=1, alpha=0.7)
                ax2.set_ylim(0, 105)
                ax2.set_ylabel("Score %", color="#94a3b8", fontsize=9)
                ax2.tick_params(colors="#94a3b8", labelsize=9)
                for spine in ax2.spines.values():
                    spine.set_visible(False)
                ax2.yaxis.grid(True, color="rgba(255,255,255,0.06)",
                               linestyle='--', linewidth=0.8)
                plt.tight_layout(pad=1.5)
                st.markdown(T["t5_score_chart"])
                st.pyplot(fig2, use_container_width=True)
                plt.close(fig2)

        with col_d2:
            top = s.get("top_topics",[])
            st.markdown(T["t5_topics"])
            if top:
                max_cnt  = max(c for _, c in top)
                bar_colors = ["#6366f1","#8b5cf6","#10b981","#fbbf24","#f97316","#06b6d4"]
                for i, (topic_name, cnt) in enumerate(top):
                    pct_w = min(100, int(cnt / max_cnt * 100))
                    bc = bar_colors[i % len(bar_colors)]
                    st.markdown(f"""<div style="margin:9px 0;">
  <div style="display:flex;justify-content:space-between;margin-bottom:5px;">
    <span style="color:{_TEXT};font-size:0.95rem;font-weight:600;">{topic_name[:38]}</span>
    <span style="color:{bc};font-size:0.88rem;font-weight:700;">{cnt}x</span>
  </div>
  <div style="background:rgba(255,255,255,0.07);border-radius:50px;height:8px;">
    <div style="background:{bc};width:{pct_w}%;height:100%;border-radius:50px;
         box-shadow:0 0 8px {bc}66;"></div>
  </div>
</div>""", unsafe_allow_html=True)
            else:
                _empty_state("📚", "", T["t5_no_topics"])

            sessions_all = get_recent(200)
            if sessions_all:
                df_export = pd.DataFrame(sessions_all)
                st.download_button(
                    label=T["t5_export"],
                    data=df_export.to_csv(index=False).encode(),
                    file_name="ShikshAI_sessions.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

        # ── Engagement tracker ─────────────────────────────────────────────────
        st.markdown("---")
        st.markdown(T["t5_engage_title"])
        st.caption(T["t5_engage_cap"])

        quiz_scores = s.get("recent_scores",[])
        topics_cnt  = len(s.get("top_topics",[]))
        quizzes_cnt = feat.get("quiz",0)
        avg_q       = s.get("avg_quiz_score",0)
        pass_rate   = int(sum(1 for sc in quiz_scores if sc >= 60) / max(len(quiz_scores),1) * 100)
        eng_score   = min(100, int(avg_q*0.55 + min(topics_cnt,10)*4 + min(quizzes_cnt,5)*4))
        eng_color   = "#10b981" if eng_score >= 70 else "#fbbf24" if eng_score >= 40 else "#ef4444"
        eng_label   = T["t5_excellent"] if eng_score >= 80 else T["t5_good"] if eng_score >= 60 else T["t5_developing"]

        e1, e2, e3, e4 = st.columns(4)
        for col, (label, val) in zip([e1,e2,e3,e4], [
            (T["t5_eng_score"],  f"{eng_score}/100"),
            (T["t5_pass"],       f"{pass_rate}%"),
            (T["t5_topics_cov"], topics_cnt),
            (T["t5_q_taken"],    quizzes_cnt),
        ]):
            col.markdown(f"""
<div class="metric-card">
  <div class="metric-value">{val}</div>
  <div class="metric-label">{label}</div>
</div>""", unsafe_allow_html=True)

        st.markdown("")
        import streamlit.components.v1 as _ec
        _ec.html(f"""
<div style="padding:8px 0;font-family:Inter,sans-serif;">
  <div style="font-size:0.78rem;color:#94a3b8;margin-bottom:6px;">{T['t5_eng_level']}</div>
  <div style="background:rgba(255,255,255,0.08);border-radius:50px;height:18px;overflow:hidden;">
    <div style="background:linear-gradient(90deg,#4f46e5,{eng_color});height:100%;
                width:{eng_score}%;border-radius:50px;box-shadow:0 0 12px {eng_color}66;
                transition:width 1.5s cubic-bezier(0.34,1.2,0.64,1);"></div>
  </div>
  <div style="font-size:1.4rem;font-weight:800;color:{eng_color};margin-top:8px;">
    {eng_score}% — {eng_label}
  </div>
</div>""", height=85)

        _top_topics = s.get("top_topics",[])
        if _top_topics:
            st.markdown(T["t5_topics_head"])
            tc_cols   = st.columns(min(4, len(_top_topics)))
            tc_colors = ["#6366f1","#8b5cf6","#10b981","#fbbf24","#f97316","#06b6d4","#ec4899","#14b8a6"]
            for ti, (tn, tc) in enumerate(_top_topics[:8]):
                bc = tc_colors[ti % len(tc_colors)]
                with tc_cols[ti % 4]:
                    st.markdown(f"""
<div style="background:{bc}18;border:1px solid {bc}55;border-radius:10px;
     padding:10px 12px;margin:4px 0;text-align:center;">
  <div style="font-weight:700;color:{bc};font-size:0.85rem;margin-bottom:2px;">{tn[:22]}</div>
  <div style="color:{_TEXT2};font-size:0.75rem;">{tc} session{"s" if tc>1 else ""}</div>
</div>""", unsafe_allow_html=True)

        # ── Recent sessions table ──────────────────────────────────────────────
        st.markdown("---")
        st.markdown(T["t5_recent"])
        sessions = get_recent(25)
        if sessions:
            icon_map = {"concept":"🧠","quiz":"❓","translation":"🌐","activity":"⏱️","ask_ai":"💬"}
            df = pd.DataFrame([{
                T["t5_col_time"]:    r["ts"],
                T["t5_col_feature"]: icon_map.get(r["feature"],"📌") + " " + r["feature"].capitalize(),
                T["t5_col_topic"]:   (r.get("topic") or "—")[:40],
                T["t5_col_grade"]:   r.get("grade","—"),
                T["t5_col_subject"]: r.get("subject","—"),
                T["t5_col_score"]:   f"{r['score_pct']:.0f}%" if r.get("score_pct") is not None else "—",
            } for r in sessions])
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            _empty_state("📊", "", T["t5_no_sess"])

        st.markdown("---")
        if st.button(T["t5_clear"], key="clear_hist"):
            clear_all()
            st.toast(T["t5_cleared"], icon="🗑️")
            st.rerun()

    except Exception as e:
        st.markdown(f"""
<div class="glass-card" style="border-left:4px solid #fbbf24;">
  ⚠️ <b>{T['t5_err']}</b> {e}<br>
  <span style="color:{_TEXT2};font-size:0.9rem;">{T['t5_err_sub']}</span>
</div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 6 — Ask AI  (streaming chat, gpt-4o)
# ══════════════════════════════════════════════════════════════════════════════
with tab6:
    from utils.ai_helper import stream_chat_answer

    # ── Header row ────────────────────────────────────────────────────────────
    _h1, _h2, _h3 = st.columns([5, 1, 1])
    with _h1:
        st.markdown(f'<div class="section-title">{T["t6_title"]}</div>',
                    unsafe_allow_html=True)
        st.caption(
            f'{T["t6_caption"]}  —  '
            f'📚 {T["t6_context"].format(grade=grade, subject=subject)}  '
            f'| 🤖 gpt-4o'
        )
    with _h2:
        if st.button(T["t6_new"], key="t6_clear_btn", use_container_width=True):
            st.session_state["t6_chat_history"] = []
            st.session_state["mic_key_t6"] = 0
            st.rerun()

    # ── Export conversation button ─────────────────────────────────────────────
    history = st.session_state.get("t6_chat_history", [])
    if history:
        _exp_text = "\n\n".join(
            f"{'You' if m['role']=='user' else 'ShikshAI'}: {m['content']}"
            for m in history
        )
        with _h3:
            st.download_button(
                "⬇️ Export",
                data=_exp_text.encode("utf-8"),
                file_name="ShikshAI_chat.txt",
                mime="text/plain",
                use_container_width=True,
            )

    # ── Render existing chat history ──────────────────────────────────────────
    if not history:
        _empty_state("💬", T["t6_empty_title"], T["t6_empty_sub"])

    for i, msg in enumerate(history):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
        # Speak + Copy buttons after each assistant message
        if msg["role"] == "assistant":
            _pa, _pb, _ = st.columns([1, 1, 5])
            with _pa:
                if st.button("🔊", key=f"t6_speak_{i}", help="Speak this answer"):
                    play_tts(msg["content"][:600], lang=tts_lang)
            with _pb:
                _copy_btn(msg["content"], "📋", height=40)

    # ── Chat input (appears at bottom of tab) ─────────────────────────────────
    spoken_q6 = record_and_transcribe(T["t6_record"], auto_clear=True, state_key="mic_key_t6")

    user_input = st.chat_input(T["t6_placeholder"]) or spoken_q6

    if user_input:
        # Show user bubble immediately
        with st.chat_message("user"):
            st.markdown(user_input)
        history.append({"role": "user", "content": user_input})

        # Stream AI response
        with st.chat_message("assistant"):
            response_text = st.write_stream(
                stream_chat_answer(model, history, grade, subject, _lang)
            )

        history.append({"role": "assistant", "content": response_text})
        st.session_state["t6_chat_history"] = history
        save_to_history("ask_ai", user_input, {"answer": response_text})


# ══════════════════════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div style="margin-top:36px;">
  <div style="height:1px;background:linear-gradient(90deg,transparent,{_BORDER},transparent);margin-bottom:20px;"></div>
  <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;margin-bottom:14px;">
    <div style="display:flex;align-items:center;gap:8px;font-size:1.1rem;font-weight:900;background:linear-gradient(135deg,#6366f1,#8b5cf6);-webkit-background-clip:text;-webkit-text-fill-color:transparent;"><img src="{FAVICON_B64}" style="height:28px;width:28px;border-radius:6px;flex-shrink:0;"> ShikshAI</div>
    <div style="display:flex;gap:6px;flex-wrap:wrap;align-items:center;">
      <span style="background:rgba(99,102,241,0.15);color:#818cf8;border:1px solid rgba(99,102,241,0.35);border-radius:50px;padding:3px 11px;font-size:0.73rem;font-weight:600;">🤖 GPT-4o</span>
      <span style="background:rgba(16,185,129,0.12);color:#34d399;border:1px solid rgba(16,185,129,0.3);border-radius:50px;padding:3px 11px;font-size:0.73rem;font-weight:600;">🎙️ Whisper</span>
      <span style="background:rgba(6,182,212,0.12);color:#67e8f9;border:1px solid rgba(6,182,212,0.3);border-radius:50px;padding:3px 11px;font-size:0.73rem;font-weight:600;">🔊 TTS Nova</span>
      <span style="background:rgba(251,191,36,0.12);color:#fbbf24;border:1px solid rgba(251,191,36,0.3);border-radius:50px;padding:3px 11px;font-size:0.73rem;font-weight:600;">🌐 EN + हिंदी</span>
    </div>
    <div style="width:120px;"></div>
  </div>
  <div style="text-align:center;padding-bottom:12px;">
    <span style="color:{_TEXT2};font-size:0.72rem;">© 2026 Connecting Dreams Foundation</span>
  </div>
</div>
""", unsafe_allow_html=True)

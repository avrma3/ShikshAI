"""
PDF quiz sheet generator for ShikshAI.
Produces a printable A4 question sheet + answer key using fpdf2.
"""
from fpdf import FPDF
import io
from datetime import datetime


# ── Colour palette ────────────────────────────────────────────────────────────
_INDIGO  = (63,  70,  229)
_EMERALD = (16,  185, 129)
_AMBER   = (245, 158,  11)
_RED     = (239,  68,  68)
_LIGHT   = (235, 237, 255)
_GREY    = ( 80,  80,  80)
_OPT_COL = {"A": _INDIGO, "B": _EMERALD, "C": _AMBER, "D": _RED}


def _safe(text) -> str:
    """Keep only Latin-1 characters so the default PDF font doesn't crash."""
    if not isinstance(text, str):
        text = str(text)
    return "".join(ch for ch in text if ord(ch) < 256).strip()


class _QuizPDF(FPDF):
    def __init__(self, topic: str, grade: str, subject: str):
        super().__init__()
        self._topic   = _safe(topic)
        self._grade   = _safe(grade)
        self._subject = _safe(subject)
        self.set_auto_page_break(auto=True, margin=16)
        self.set_margins(14, 14, 14)

    def header(self):
        self.set_fill_color(*_INDIGO)
        self.rect(0, 0, 220, 20, "F")
        self.set_text_color(255, 255, 255)
        self.set_font("Helvetica", "B", 12)
        self.set_y(4)
        self.cell(0, 12, "  ShikshAI  --  Smart Board Quiz", align="L")
        self.ln(18)
        self.set_text_color(0, 0, 0)

    def footer(self):
        self.set_y(-13)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(160, 160, 160)
        self.cell(
            0, 8,
            f"ShikshAI  |  Connecting Dreams Foundation  |"
            f"  Page {self.page_no()}  |  {datetime.now().strftime('%d %b %Y')}",
            align="C",
        )


def generate_quiz_pdf(topic: str, grade: str, subject: str, questions: list) -> bytes:
    """Return PDF bytes for a quiz sheet (questions + answer key)."""
    pdf = _QuizPDF(topic, grade, subject)
    pdf.add_page()

    # ── Title block ──────────────────────────────────────────────────────────
    pdf.set_fill_color(*_LIGHT)
    pdf.set_draw_color(*_INDIGO)
    pdf.set_line_width(0.4)
    pdf.rect(14, 22, 182, 24, "DF")

    pdf.set_font("Helvetica", "B", 17)
    pdf.set_text_color(*_INDIGO)
    pdf.set_y(25)
    pdf.cell(0, 9, f"Quiz: {_safe(topic)}", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(*_GREY)
    pdf.cell(
        0, 7,
        f"Class: {_safe(grade)}   |   Subject: {_safe(subject)}   |   Total: {len(questions)} Qs",
        align="C", new_x="LMARGIN", new_y="NEXT",
    )
    pdf.ln(5)

    # ── Student info row ─────────────────────────────────────────────────────
    pdf.set_fill_color(248, 249, 255)
    pdf.set_draw_color(200, 210, 240)
    pdf.rect(14, pdf.get_y(), 182, 12, "DF")
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(60, 60, 60)
    pdf.set_x(18)
    pdf.cell(72, 12, "Name: _________________________________")
    pdf.cell(56, 12, "Roll No: ________________")
    pdf.cell(44, 12, "Date: ____________")
    pdf.ln(16)

    # ── Questions ────────────────────────────────────────────────────────────
    for i, q in enumerate(questions, 1):
        q_text = _safe(q.get("question", ""))

        pdf.set_fill_color(245, 246, 255)
        pdf.set_draw_color(190, 195, 250)
        pdf.set_line_width(0.3)
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(20, 20, 20)
        pdf.multi_cell(0, 7, f"Q{i}.  {q_text}", border=0, fill=True)
        pdf.ln(2)

        opts = q.get("options", {})
        for key, val in opts.items():
            col = _OPT_COL.get(key, _INDIGO)
            pdf.set_fill_color(*col)
            pdf.set_text_color(255, 255, 255)
            pdf.set_font("Helvetica", "B", 9)
            pdf.set_x(22)
            pdf.cell(8, 7, key, align="C", fill=True)
            pdf.set_text_color(40, 40, 40)
            pdf.set_font("Helvetica", "", 10)
            pdf.multi_cell(0, 7, f"   {_safe(val)}")
        pdf.ln(5)

    # ── Answer key page ───────────────────────────────────────────────────────
    pdf.add_page()
    pdf.set_y(22)
    pdf.set_fill_color(*_EMERALD)
    pdf.rect(14, pdf.get_y(), 182, 14, "F")
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_x(18)
    pdf.cell(0, 14, "   Answer Key & Explanations")
    pdf.ln(18)

    for i, q in enumerate(questions, 1):
        ans      = q.get("answer", "")
        opts     = q.get("options", {})
        ans_text = _safe(opts.get(ans, ""))
        expl     = _safe(q.get("explanation", ""))

        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(20, 20, 20)
        pdf.cell(14, 8, f"Q{i}.")
        pdf.set_text_color(*_EMERALD)
        pdf.cell(18, 8, f"({ans})")
        pdf.set_text_color(20, 20, 20)
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(0, 8, ans_text)

        if expl:
            pdf.set_font("Helvetica", "I", 9)
            pdf.set_text_color(*_GREY)
            pdf.set_x(28)
            pdf.multi_cell(0, 6, f"-> {expl}")
        pdf.ln(3)

    buf = io.BytesIO()
    pdf.output(buf)
    return buf.getvalue()

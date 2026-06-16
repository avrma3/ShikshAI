def build(concept: str, grade: str, subject: str, lang: str = "en") -> str:

    if lang == "hi":
        lang_rule = """
LANGUAGE: Use Hindi (Devanagari script) for ALL labels, title, and annotations.
FONT SETUP — include this at the top of your code (before any text calls):
  import matplotlib.font_manager as _fm
  _hi_font = _fm.FontProperties(fname=r'C:\\Windows\\Fonts\\Nirmala.ttc', size=12)
  _hi_font_lg = _fm.FontProperties(fname=r'C:\\Windows\\Fonts\\Nirmala.ttc', size=15)
Use `fontproperties=_hi_font` in EVERY ax.text() / ax.annotate() call.
Title example: ax.set_title('प्रकाश संश्लेषण', fontproperties=_hi_font_lg, color='white')
Label example: ax.text(x, y, 'सूर्य का प्रकाश', fontproperties=_hi_font, color='yellow')
"""
    else:
        lang_rule = """
LANGUAGE: Use ONLY English text for ALL labels, titles, annotations.
NO Hindi, NO Devanagari, NO Unicode beyond basic ASCII.
"""

    return f"""You are an expert educational diagram generator.

Generate Python matplotlib code that draws a detailed, labeled educational diagram for: "{concept}"
Grade: {grade} | Subject: {subject}

REQUIREMENTS:
- Draw a proper scientific/educational diagram — NOT a flowchart or bar chart
- For anatomy (heart, eye, ear, cell): draw the actual anatomical shape with parts labeled
- For geometry (triangle, circle, angles): draw the actual geometric figure with measurements
- For physics (circuits, forces, lenses): draw the actual physics diagram
- For cycles (water, carbon, nitrogen): draw a circular/arrow process diagram
- For chemistry (atom, molecule, bonds): draw the actual structure
- All important parts must be labeled with leader lines or annotations
- Use color to distinguish different parts/regions

STYLE:
- Figure: plt.figure(figsize=(10, 7))
- Dark background: fig.patch.set_facecolor('#080c23') | ax.set_facecolor('#080c23')
- Bright colors for shapes and labels (white, yellow, cyan, lime, coral)
- Font size 11-14 for labels, 16-18 for title
- No grid unless it helps (like coordinate geometry)

{lang_rule}

CODE RULES:
- Import ONLY: matplotlib.pyplot as plt, matplotlib.patches as patches, numpy as np, math, matplotlib.font_manager
- End with: plt.tight_layout(); plt.savefig(_OUTPUT_PATH, dpi=100, bbox_inches='tight', facecolor=fig.get_facecolor())
- NO plt.show()
- NO other imports (no PIL, no cv2, no external libraries)
- Variable _OUTPUT_PATH is already defined — use it directly in savefig

Return ONLY the Python code. No explanation, no markdown fences, no ```python.
Start directly with import statements.
"""

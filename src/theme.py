"""
theme.py
--------
Single source of truth for the visual identity.

Direction: dark console. The page is a deep aubergine field, content sits on
raised cards, and violet is the only colour that carries data - so brightness
reads as importance instead of the eye hunting for meaning in a rainbow.

Palette (Vista Energy corporate purple, adapted for a dark surface):
    CANVAS    #150B26  page background, top of the gradient
    CANVAS_2  #1E1038  bottom of the gradient
    SURFACE   #241440  card background
    LINE      #35204F  card borders, gridlines
    VIOLET    #A96BEE  the data colour - reported figures
    VIOLET_L  #C9A6F2  secondary series
    VIOLET_D  #6B2FA0  the corporate purple: fills, active nav rail
    TEXT      #F3EEFA  headlines and figures
    MUTED     #9D8FB8  labels, captions, axis text

Semantics are the only exception to the purple rule: mint for cash generated,
coral for cash consumed. Two colours, used nowhere decorative.

Encoding rule applied across every chart:
    solid   = reported / audited history
    hatched = model projection, on a lighter band
"""

from __future__ import annotations

# --------------------------------------------------------------------------- #
# Colour tokens
# --------------------------------------------------------------------------- #

CANVAS = "#150B26"
CANVAS_2 = "#1E1038"
SURFACE = "#241440"
SURFACE_2 = "#2C1950"
LINE = "#35204F"

VIOLET = "#A96BEE"
VIOLET_LIGHT = "#C9A6F2"
VIOLET_DEEP = "#6B2FA0"
VIOLET_GLOW = "#D9BFF8"

TEXT = "#F3EEFA"
MUTED = "#9D8FB8"

POSITIVE = "#3FD5B0"
NEGATIVE = "#FF6B8A"

GRID = "#311C4A"

#: Heatmaps: dark canvas through to a bright violet.
PURPLE_SCALE = [
    [0.00, "#1E1038"],
    [0.25, "#3B1D63"],
    [0.50, "#6B2FA0"],
    [0.75, "#A96BEE"],
    [1.00, "#D9BFF8"],
]

FONT_DISPLAY = "'Space Grotesk', 'Segoe UI', sans-serif"
FONT_BODY = "'Inter', 'Segoe UI', sans-serif"


# --------------------------------------------------------------------------- #
# Streamlit CSS
# --------------------------------------------------------------------------- #

CUSTOM_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Space+Grotesk:wght@500;600;700&display=swap');

/* --- page frame ------------------------------------------------------- */
.stApp {{
    background: linear-gradient(135deg, {CANVAS} 0%, {CANVAS_2} 55%, #24124A 100%);
    background-attachment: fixed;
    color: {TEXT};
    font-family: {FONT_BODY};
}}
.block-container {{ padding: 1.8rem 2rem 3rem 2rem; max-width: 1500px; }}
h1, h2, h3, h4 {{ font-family: {FONT_DISPLAY}; color: {TEXT}; letter-spacing: -0.01em; }}
p, span, label, li {{ color: {TEXT}; }}

/* --- sidebar ---------------------------------------------------------- */
section[data-testid="stSidebar"] {{
    background: {CANVAS};
    border-right: 1px solid {LINE};
}}
section[data-testid="stSidebar"] .block-container {{ padding: 1.6rem 1rem; }}
.brand {{ font-family: {FONT_DISPLAY}; font-size: 1.45rem; font-weight: 600;
          letter-spacing: 0.02em; color: {TEXT}; line-height: 1.05; }}
.brand span {{ color: {VIOLET}; }}
.brand-sub {{ font-size: 0.66rem; letter-spacing: 0.22em; text-transform: uppercase;
              color: {VIOLET}; margin-top: 0.35rem; }}
.nav-heading {{ font-size: 0.64rem; letter-spacing: 0.18em; text-transform: uppercase;
                color: {MUTED}; margin: 1.7rem 0 0.5rem 0.2rem; }}

/* sidebar nav rendered as buttons; the active one uses type="primary" */
section[data-testid="stSidebar"] .stButton > button {{
    width: 100%; text-align: left; justify-content: flex-start;
    background: transparent; border: none; border-left: 3px solid transparent;
    border-radius: 0 6px 6px 0; color: {MUTED};
    font-family: {FONT_BODY}; font-size: 0.93rem; font-weight: 500;
    padding: 0.55rem 0.9rem; margin-bottom: 0.1rem; transition: all 120ms ease;
}}
section[data-testid="stSidebar"] .stButton > button:hover {{
    background: {SURFACE}; color: {TEXT}; border-left-color: {VIOLET_DEEP};
}}
section[data-testid="stSidebar"] .stButton > button[kind="primary"] {{
    background: {SURFACE_2}; color: {TEXT};
    border-left-color: {VIOLET}; font-weight: 600;
}}

/* --- page header ------------------------------------------------------ */
.page-head {{ display: flex; align-items: flex-end; justify-content: space-between;
              gap: 1rem; flex-wrap: wrap; margin-bottom: 1.1rem; }}
.page-title {{ font-family: {FONT_DISPLAY}; font-size: 1.85rem; font-weight: 600; margin: 0; }}
.page-sub {{ color: {MUTED}; font-size: 0.92rem; margin: 0.35rem 0 0 0; max-width: 72ch; }}
.stamp {{ font-family: {FONT_DISPLAY}; font-size: 1rem; color: {VIOLET_LIGHT}; }}

/* --- cards ------------------------------------------------------------ */
.card {{
    background: {SURFACE};
    border: 1px solid {LINE};
    border-radius: 12px;
    margin-bottom: 0.9rem;
    overflow: hidden;
}}
.card-head {{
    font-size: 0.72rem; letter-spacing: 0.13em; text-transform: uppercase;
    color: {MUTED}; font-weight: 600;
    padding: 0.8rem 1.05rem; border-bottom: 1px solid {LINE};
}}
.card-body {{ padding: 1.05rem; }}

.stat {{ font-family: {FONT_DISPLAY}; font-size: 2rem; font-weight: 700;
         color: {TEXT}; line-height: 1; font-variant-numeric: tabular-nums; }}
.stat-unit {{ font-size: 0.9rem; color: {MUTED}; font-weight: 500; margin-left: 0.3rem; }}
.stat-note {{ color: {MUTED}; font-size: 0.82rem; margin-top: 0.5rem; line-height: 1.45; }}
.stat-note b {{ color: {VIOLET_LIGHT}; font-weight: 600; }}
.up {{ color: {POSITIVE}; font-weight: 600; }}
.down {{ color: {NEGATIVE}; font-weight: 600; }}

/* progress rail */
.rail {{ background: {CANVAS}; border-radius: 99px; height: 8px; margin: 0.55rem 0 0.35rem 0; }}
.rail > div {{ background: linear-gradient(90deg, {VIOLET_DEEP}, {VIOLET}); height: 8px;
               border-radius: 99px; }}
.rail-labels {{ display: flex; justify-content: space-between; font-size: 0.75rem; color: {MUTED}; }}

/* --- explainer -------------------------------------------------------- */
.readme {{
    background: rgba(107, 47, 160, 0.16);
    border-left: 3px solid {VIOLET_DEEP};
    border-radius: 0 8px 8px 0;
    padding: 0.8rem 1rem; font-size: 0.89rem; color: {TEXT};
    margin-bottom: 1rem; line-height: 1.55;
}}
.readme b {{ color: {VIOLET_LIGHT}; }}

/* --- segmented control (horizontal st.radio) -------------------------- */
div[role="radiogroup"] {{ gap: 0 !important; background: {SURFACE};
    border: 1px solid {LINE}; border-radius: 99px; padding: 0.2rem; display: inline-flex; }}
div[role="radiogroup"] label {{
    margin: 0 !important; padding: 0.3rem 1rem; border-radius: 99px;
    color: {MUTED} !important; font-size: 0.78rem; letter-spacing: 0.06em;
    text-transform: uppercase; font-weight: 600; cursor: pointer;
}}
div[role="radiogroup"] label:has(input:checked) {{ background: {VIOLET_DEEP}; }}
div[role="radiogroup"] label:has(input:checked) p {{ color: {TEXT} !important; }}
div[role="radiogroup"] label > div:first-child {{ display: none; }}

/* --- widgets ---------------------------------------------------------- */
.stSelectbox div[data-baseweb="select"] > div,
.stTextInput input,
.stMultiSelect div[data-baseweb="select"] > div {{
    background: {SURFACE} !important; border-color: {LINE} !important; color: {TEXT} !important;
}}
[data-testid="stDataFrame"] {{ border: 1px solid {LINE}; border-radius: 10px; }}

/* --- misc ------------------------------------------------------------- */
hr {{ border: none; border-top: 1px solid {LINE}; margin: 1.3rem 0; }}
footer, #MainMenu, header[data-testid="stHeader"] {{ visibility: hidden; height: 0; }}
</style>
"""


# --------------------------------------------------------------------------- #
# Plotly template
# --------------------------------------------------------------------------- #


def plotly_layout(height: int = 300, **overrides) -> dict:
    """Shared layout: transparent background so figures sit inside the cards."""
    layout = dict(
        height=height,
        font=dict(family=FONT_BODY, size=12, color=MUTED),
        margin=dict(l=8, r=12, t=18, b=30),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        hoverlabel=dict(
            bgcolor=SURFACE_2,
            bordercolor=VIOLET,
            font=dict(family=FONT_BODY, size=12, color=TEXT),
        ),
        hovermode="x unified",
        legend=dict(
            orientation="h", yanchor="bottom", y=1.0, xanchor="left", x=0,
            font=dict(size=11, color=MUTED), bgcolor="rgba(0,0,0,0)",
        ),
        xaxis=dict(showgrid=False, linecolor=LINE, tickfont=dict(color=MUTED, size=11),
                   ticks="outside", tickcolor=LINE),
        yaxis=dict(showgrid=True, gridcolor=GRID, zerolinecolor=LINE,
                   linecolor="rgba(0,0,0,0)", tickfont=dict(color=MUTED, size=11)),
    )
    layout.update(overrides)
    return layout

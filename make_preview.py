"""
make_preview.py
---------------
Renders a **static** HTML preview of the dashboard: same data, same theme, same
Plotly figures, but no Streamlit runtime required. Useful for two things:

1. Checking the visual design without launching the app.
2. Producing a shareable artefact (or a screenshot source) for the README.

Usage:
    python make_preview.py            # writes preview.html
    python make_preview.py out.html
"""

from __future__ import annotations

import sys
from pathlib import Path

from src import charts
from src.data_loader import cagr, load_model
from src.theme import (
    CANVAS,
    CANVAS_2,
    FONT_BODY,
    FONT_DISPLAY,
    LINE,
    MUTED,
    SURFACE,
    TEXT,
    VIOLET,
    VIOLET_DEEP,
)

PLOTLY_CDN = "https://cdnjs.cloudflare.com/ajax/libs/plotly.js/2.35.2/plotly.min.js"
CONFIG = {"displayModeBar": False, "responsive": True}


def fig_html(fig) -> str:
    """Embed one figure without re-including the plotly.js bundle each time."""
    return fig.to_html(full_html=False, include_plotlyjs=False, config=CONFIG)


def build(output: Path) -> Path:
    data = load_model()

    last_actual = data.last_actual_year
    first_forecast = data.first_forecast_year
    final_year = data.years[-1]

    prod_start = data.value("Production", last_actual)
    prod_end = data.value("Production", final_year)
    prod_cagr = cagr(prod_start, prod_end, int(final_year[:4]) - int(last_actual[:4]))

    fcf = data.series("Free Cash Flow (levered)")
    positive = fcf[(fcf["value"] > 0) & (fcf["year"].str.endswith("E"))]
    turnaround = positive["year"].iloc[0] if not positive.empty else first_forecast

    price = data.valuation["share_price_current"]
    target = data.valuation["blended_price_target"]

    kpis = [
        ("Production growth", f"{prod_cagr:.1%}",
         f"per year, {last_actual[:4]}–{final_year[:4]} · {prod_start:,.0f} → {prod_end:,.0f} boe/d"),
        ("Profit margin", f"{data.value('EBITDA Margin', first_forecast):.0%}",
         f"of every sales dollar becomes operating profit in {first_forecast[:4]}"),
        ("Free cash flow", f"positive from {turnaround[:4]}",
         "after four years of outspending its own cash flow"),
        ("Debt burden",
         f"{data.value('Net Debt / EBITDA', last_actual):.1f}x → {data.value('Net Debt / EBITDA', final_year):.1f}x",
         f"years of earnings owed, {last_actual[:4]} vs {final_year[:4]}"),
        ("Estimated value", f"${target:,.0f}",
         f"per share vs <strong>${price:,.2f}</strong> today "
         f"({data.valuation['upside_downside']:+.0%})"),
    ]

    tabs = {
        "Growth": [
            ("The company is pumping more oil every year",
             "Output is measured in <b>barrels of oil equivalent per day</b> — gas converted into "
             "the amount of oil holding the same energy, so everything can be added up. The black "
             "line shows how fast production grows each year.",
             charts.production_mix(data.series("Oil production"),
                                   data.series("Gas & NGL production"),
                                   data.series("Production"))),
            ("Revenue follows the barrels",
             "Revenue depends on how much is sold and the price received. Because most costs are "
             "fixed per well, extra barrels arrive at a high margin — which is why the margin line "
             "stays flat as the company grows.",
             charts.revenue_and_margin(data.series("Revenue"), data.series("EBITDA Margin"))),
        ],
        "Profitability": [
            ("Each barrel is cheap to lift and sells for a lot more",
             f"The all-in cost is about <b>${data.value('Total cost per boe', last_actual):.2f} per "
             f"barrel</b> against a realised price near "
             f"<b>${data.value('Realized oil price', last_actual):.2f}</b>. The gap between the bars "
             "and the line is the profit on every barrel.",
             charts.unit_economics(data.series("EBITDA per boe"),
                                   data.series("Total cost per boe"))),
            ("Where the money goes",
             "Starting from every dollar of sales, this peels back one layer of cost at a time: "
             "production costs, then operating costs, then the charge for wells wearing out, then "
             "interest and tax.",
             charts.margin_ladder({
                 "Gross margin": data.series("Gross Margin"),
                 "EBITDA margin": data.series("EBITDA Margin"),
                 "Operating margin (EBIT)": data.series("EBIT Margin"),
                 "Net profit margin": data.series("Net Income Margin"),
             })),
        ],
        "Cash & debt": [
            ("From spending phase to harvest phase",
             "<b>Free cash flow</b> is what is left after running the business and drilling new "
             f"wells — the money genuinely available to repay debt. It turns positive in "
             f"{turnaround[:4]} and grows from there.",
             charts.cash_flow_story(fcf, data.series("of which CapEx"),
                                    data.series("Cash from Operations"))),
            ("The debt taken on to grow gets paid back",
             "<b>Net debt ÷ EBITDA</b> answers one question: how many years of earnings would it "
             "take to repay everything owed? Under 2x is generally comfortable for a producer.",
             charts.leverage(data.series("Net debt"), data.series("Net Debt / EBITDA"))),
        ],
        "What it's worth": [
            ("From future cash flows to today's equity value",
             "A <b>discounted cash flow</b> adds up the cash the business should produce and "
             "converts it into today's money, because a dollar received in 2030 is worth less than "
             "a dollar today.",
             charts.dcf_waterfall(data.dcf)),
            ("What the share is worth under each method",
             "Two independent methods, then the average of the two. The dashed line is where the "
             "share actually trades.",
             charts.price_targets(price, {
                 "Cash-flow method (DCF)": data.valuation["dcf_price_target"],
                 "Peer-multiple method": data.valuation["comps_price_target"],
                 "Blended target": data.valuation["blended_price_target"],
             })),
            ("Test the assumptions yourself",
             "In the live app these two inputs are sliders feeding a running valuation. Darker "
             "cells mean a higher value per share.",
             charts.sensitivity_heatmap(data.sensitivity, price)),
        ],
    }

    # ---------------------------------------------------------------- HTML -- #
    kpi_html = "".join(
        f'<div class="kpi"><div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}</div><div class="kpi-delta">{note}</div></div>'
        for label, value, note in kpis
    )

    buttons, panels = [], []
    for index, (name, blocks) in enumerate(tabs.items()):
        active = " active" if index == 0 else ""
        buttons.append(f'<button class="tab{active}" data-tab="{index}">{name}</button>')
        body = "".join(
            f'<h3>{title}</h3><div class="readme">{note}</div>{fig_html(fig)}'
            for title, note, fig in blocks
        )
        panels.append(f'<section class="panel{active}" data-panel="{index}">{body}</section>')

    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Vista Energy — Equity Story (static preview)</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Space+Grotesk:wght@500;600;700&display=swap" rel="stylesheet">
<script src="{PLOTLY_CDN}"></script>
<style>
  body {{ font-family:{FONT_BODY}; color:{TEXT}; margin:0; padding:2rem 1.5rem 4rem;
         background:linear-gradient(135deg,{CANVAS} 0%,{CANVAS_2} 55%,#24124A 100%); background-attachment:fixed; }}
  .wrap {{ max-width:1250px; margin:0 auto; }}
  h1,h2,h3 {{ font-family:{FONT_DISPLAY}; letter-spacing:-.015em; }}
  .hero {{ border-left:6px solid {VIOLET}; padding:.2rem 0 .2rem 1.1rem; margin-bottom:1.6rem; }}
  .hero-ticker {{ font-family:{FONT_DISPLAY}; font-size:.78rem; letter-spacing:.18em;
                 text-transform:uppercase; color:{VIOLET}; margin-bottom:.35rem; }}
  .hero h1 {{ font-size:2.35rem; font-weight:700; line-height:1.1; margin:0; }}
  .hero p {{ color:{MUTED}; font-size:1.02rem; margin-top:.5rem; max-width:62ch; }}
  .kpis {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(190px,1fr)); gap:.8rem; margin-bottom:1.8rem; }}
  .kpi {{ background:{SURFACE}; border:1px solid {LINE}; border-top:3px solid {VIOLET}; border-radius:10px; padding:1rem 1.1rem; }}
  .kpi-label {{ font-size:.74rem; text-transform:uppercase; letter-spacing:.09em; color:{MUTED}; font-weight:600; margin-bottom:.45rem; }}
  .kpi-value {{ font-family:{FONT_DISPLAY}; font-size:1.7rem; font-weight:700; line-height:1; font-variant-numeric:tabular-nums; }}
  .kpi-delta {{ font-size:.82rem; color:{MUTED}; margin-top:.42rem; }}
  .kpi-delta strong {{ color:{VIOLET}; }}
  .tabs {{ display:flex; gap:.35rem; border-bottom:1px solid {LINE}; margin-bottom:1.4rem; flex-wrap:wrap; }}
  .tab {{ font-family:{FONT_DISPLAY}; font-weight:600; font-size:.95rem; color:{MUTED};
          padding:.6rem 1rem; background:none; border:none; border-bottom:2px solid transparent; cursor:pointer; }}
  .tab.active {{ color:{VIOLET}; border-bottom-color:{VIOLET}; }}
  .panel {{ display:none; }} .panel.active {{ display:block; }}
  .panel h3 {{ font-size:1.15rem; margin:2rem 0 .6rem; }}
  .panel h3:first-child {{ margin-top:0; }}
  .readme {{ background:rgba(107,47,160,.16); border-left:3px solid {VIOLET_DEEP}; border-radius:0 8px 8px 0; padding:.85rem 1.05rem; font-size:.92rem; margin-bottom:1rem; }}
  .note {{ margin-top:2.5rem; padding-top:1.2rem; border-top:1px solid {LINE}; color:{MUTED}; font-size:.84rem; line-height:1.6; }}
  .badge {{ display:inline-block; background:{VIOLET_DEEP}; color:#fff; font-size:.7rem; letter-spacing:.08em;
            text-transform:uppercase; padding:.25rem .6rem; border-radius:4px; margin-bottom:1rem; }}
  .cta {{ display:inline-block; margin:0 0 1rem .6rem; font-family:{FONT_DISPLAY}; font-weight:600;
          font-size:.82rem; color:{VIOLET}; text-decoration:none; border-bottom:1px solid {VIOLET}; }}
  .cta:hover {{ color:{TEXT}; border-bottom-color:{TEXT}; }}
</style></head>
<body><div class="wrap">
  <div class="badge">Static preview</div>
  <a class="cta" href="./app.html">Open the interactive version &rarr;</a>
  <div class="hero">
    <div class="hero-ticker">NYSE · VIST &nbsp;|&nbsp; BMV · VISTA &nbsp;|&nbsp; Vaca Muerta, Argentina</div>
    <h1>Vista Energy: a producer turning drilling into cash</h1>
    <p>Vista spent the last three years spending heavily to grow production. This dashboard follows
       the money through that build-out — barrels produced, margins earned, cash returned, and what
       all of it is worth today.</p>
  </div>
  <div class="kpis">{kpi_html}</div>
  <div class="tabs">{''.join(buttons)}</div>
  {''.join(panels)}
  <p class="note">Historical figures from Vista Energy's published financial statements; projections
     are the author's own estimates. Portfolio project for educational purposes — not investment
     advice, and not affiliated with or endorsed by Vista Energy.</p>
</div>
<script>
  document.querySelectorAll('.tab').forEach(function (button) {{
    button.addEventListener('click', function () {{
      var id = button.dataset.tab;
      document.querySelectorAll('.tab').forEach(function (b) {{ b.classList.remove('active'); }});
      document.querySelectorAll('.panel').forEach(function (p) {{ p.classList.remove('active'); }});
      button.classList.add('active');
      var panel = document.querySelector('[data-panel="' + id + '"]');
      panel.classList.add('active');
      // Plotly needs a nudge to size charts that were hidden when first drawn.
      panel.querySelectorAll('.js-plotly-plot').forEach(function (chart) {{ Plotly.Plots.resize(chart); }});
    }});
  }});
</script>
</body></html>"""

    output.write_text(html, encoding="utf-8")
    return output


if __name__ == "__main__":
    destination = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("preview.html")
    print(f"Wrote {build(destination)}")

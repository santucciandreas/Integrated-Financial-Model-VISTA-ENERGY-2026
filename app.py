"""
Vista Energy (VIST) — Equity Story Dashboard
============================================
A dark-console dashboard that walks a DCF + comparables valuation model, written
for readers who do not work in finance.

Run locally:
    streamlit run app.py

Layout: a fixed left rail selects the section; content is a grid of cards, each
one a single idea with its figure. Repository layout is documented in README.md.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from src import charts
from src.data_loader import ModelData, cagr, load_model, resolve_model_path
from src.theme import CUSTOM_CSS, MUTED, NEGATIVE, POSITIVE

st.set_page_config(
    page_title="Vista Energy — Equity Dashboard",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

PLOTLY_CONFIG = {"displayModeBar": False, "scrollZoom": False}

#: Left rail. Key = internal id, value = label shown in the nav.
SECTIONS = {
    "overview": "Overview",
    "growth": "Production & growth",
    "margins": "Margins & costs",
    "cash": "Cash & debt",
    "valuation": "Valuation",
    "data": "Underlying data",
}


# --------------------------------------------------------------------------- #
# Data
# --------------------------------------------------------------------------- #


@st.cache_data(show_spinner="Reading the financial model…")
def get_data(path: str) -> ModelData:
    """Parse the workbook once per session (cached on the file path)."""
    return load_model(path)


@st.cache_data(show_spinner=False)
def default_path() -> str:
    """Where the model was found on this deployment."""
    return str(resolve_model_path())


# --------------------------------------------------------------------------- #
# Small HTML helpers — Streamlit has no card primitive, so cards are markup.
# --------------------------------------------------------------------------- #


def card_open(title: str) -> None:
    st.markdown(
        f'<div class="card"><div class="card-head">{title}</div><div class="card-body">',
        unsafe_allow_html=True,
    )


def card_close() -> None:
    st.markdown("</div></div>", unsafe_allow_html=True)


def stat_card(title: str, value: str, unit: str = "", note: str = "") -> None:
    """A card whose body is one headline figure."""
    st.markdown(
        f'<div class="card"><div class="card-head">{title}</div><div class="card-body">'
        f'<div class="stat">{value}<span class="stat-unit">{unit}</span></div>'
        f'<div class="stat-note">{note}</div></div></div>',
        unsafe_allow_html=True,
    )


def rail_card(title: str, done: float, left_label: str, right_label: str, note: str = "") -> None:
    """A card with a progress rail — used for deleveraging and reserve life."""
    pct = max(0.0, min(1.0, done)) * 100
    st.markdown(
        f'<div class="card"><div class="card-head">{title}</div><div class="card-body">'
        f'<div class="rail"><div style="width:{pct:.0f}%"></div></div>'
        f'<div class="rail-labels"><span>{left_label}</span><span>{right_label}</span></div>'
        f'<div class="stat-note">{note}</div></div></div>',
        unsafe_allow_html=True,
    )


def chart_card(title: str, figure, note: str = "") -> None:
    """A card wrapping a Plotly figure, with an optional caption underneath."""
    card_open(title)
    st.plotly_chart(figure, use_container_width=True, config=PLOTLY_CONFIG)
    if note:
        st.markdown(f'<div class="stat-note">{note}</div>', unsafe_allow_html=True)
    card_close()


def explain(text: str) -> None:
    st.markdown(f'<div class="readme">{text}</div>', unsafe_allow_html=True)


def page_head(title: str, subtitle: str, stamp: str = "") -> None:
    st.markdown(
        f'<div class="page-head"><div><h1 class="page-title">{title}</h1>'
        f'<p class="page-sub">{subtitle}</p></div>'
        f'<div class="stamp">{stamp}</div></div>',
        unsafe_allow_html=True,
    )


def window(frame: pd.DataFrame, mode: str) -> pd.DataFrame:
    """Apply the Reported / Projected / Full range segmented control."""
    if mode == "Reported":
        return frame[frame["period"] == "Actual"]
    if mode == "Projected":
        return frame[frame["period"] == "Forecast"]
    return frame


# --------------------------------------------------------------------------- #
# Sidebar: brand, navigation, source
# --------------------------------------------------------------------------- #

if "section" not in st.session_state:
    st.session_state.section = "overview"

with st.sidebar:
    st.markdown(
        '<div class="brand">VISTA <span>ENERGY</span></div>'
        '<div class="brand-sub">NYSE · VIST</div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="nav-heading">Sections</div>', unsafe_allow_html=True)

    for key, label in SECTIONS.items():
        active = st.session_state.section == key
        if st.button(label, key=f"nav_{key}", type="primary" if active else "secondary"):
            st.session_state.section = key
            st.rerun()

    st.markdown('<div class="nav-heading">Source</div>', unsafe_allow_html=True)
    model_path = st.text_input(
        "Model file", value=default_path(), label_visibility="collapsed",
        help="Path to the .xlsx workbook containing the 'Outputs' sheet.",
    )
    st.caption(
        "Reported figures from Vista's published statements. Projections are the "
        "author's own estimates — not investment advice."
    )

try:
    data = get_data(model_path)
except Exception as error:  # noqa: BLE001 — surfaced to the user on purpose
    st.error(f"Could not read the model. {error}")
    st.stop()

LAST_ACTUAL = data.last_actual_year
FIRST_FORECAST = data.first_forecast_year
FINAL_YEAR = data.years[-1]

production = data.series("Production")
fcf = data.series("Free Cash Flow (levered)")
prod_start = data.value("Production", LAST_ACTUAL)
prod_end = data.value("Production", FINAL_YEAR)
prod_cagr = cagr(prod_start, prod_end, int(FINAL_YEAR[:4]) - int(LAST_ACTUAL[:4]))

positive = fcf[(fcf["value"] > 0) & (fcf["year"].str.endswith("E"))]
turnaround = positive["year"].iloc[0] if not positive.empty else FIRST_FORECAST

price = data.valuation["share_price_current"]
target = data.valuation["blended_price_target"]
upside = data.valuation["upside_downside"]
debt_now = data.value("Net debt", LAST_ACTUAL)
debt_end = data.value("Net debt", FINAL_YEAR)

section = st.session_state.section


# --------------------------------------------------------------------------- #
# Overview — the card grid
# --------------------------------------------------------------------------- #

if section == "overview":
    page_head(
        "Equity Dashboard",
        "Vista is the largest independent oil producer in Argentina's Vaca Muerta shale. "
        "It spent three years drilling heavily; this dashboard follows the money through "
        "that build-out and out the other side.",
        f"{LAST_ACTUAL[:4]} reported · {FINAL_YEAR[:4]} projected",
    )

    row = st.columns([1, 1, 1.35], gap="medium")
    with row[0]:
        chart_card(
            f"Production mix · {LAST_ACTUAL[:4]}",
            charts.production_donut(
                data.value("Oil production", LAST_ACTUAL),
                data.value("Gas & NGL production", LAST_ACTUAL),
                LAST_ACTUAL,
            ),
        )
    with row[1]:
        change = data.value("Revenue", FINAL_YEAR) / data.value("Revenue", LAST_ACTUAL) - 1
        chart_card(
            "Revenue, then and later",
            charts.compare_pair(
                (LAST_ACTUAL, FINAL_YEAR),
                (data.value("Revenue", LAST_ACTUAL), data.value("Revenue", FINAL_YEAR)),
            ),
            f'<span class="up">▲ {change:.0%}</span> projected growth in annual revenue, '
            f"in millions of dollars.",
        )
    with row[2]:
        chart_card(
            "Production trajectory",
            charts.trajectory(production, "boe/d"),
            f"Output compounds at <b>{prod_cagr:.1%}</b> a year from {LAST_ACTUAL[:4]} "
            f"to {FINAL_YEAR[:4]}.",
        )

    row = st.columns([1, 1, 1.35], gap="medium")
    with row[0]:
        chart_card(
            f"Operating margin · {FIRST_FORECAST[:4]}",
            charts.margin_gauge(data.value("EBITDA Margin", FIRST_FORECAST), "of every sales dollar"),
        )
    with row[1]:
        stat_card(
            "Cost to lift one barrel",
            f"${data.value('Lifting cost', LAST_ACTUAL):.2f}",
            "/ boe",
            f"All-in, including royalties and transport: "
            f"<b>${data.value('Total cost per boe', LAST_ACTUAL):.2f}</b> against a realised "
            f"price of <b>${data.value('Realized oil price', LAST_ACTUAL):.2f}</b> per barrel.",
        )
        repaid = 1 - max(debt_end, 0) / debt_now if debt_now else 1.0
        rail_card(
            "Debt repayment path",
            repaid,
            f"{LAST_ACTUAL[:4]}: ${debt_now:,.0f}M owed",
            f"{FINAL_YEAR[:4]}: " + (f"${debt_end:,.0f}M" if debt_end > 0 else "net cash"),
            f"Leverage falls from <b>{data.value('Net Debt / EBITDA', LAST_ACTUAL):.1f}x</b> "
            f"to <b>{data.value('Net Debt / EBITDA', FINAL_YEAR):.1f}x</b> years of earnings.",
        )
    with row[2]:
        chart_card(
            "Free cash flow",
            charts.trajectory(fcf, "$M", fill=True),
            f"Deeply negative during the drilling push, turning positive in "
            f"<b>{turnaround[:4]}</b> as capital spending levels off.",
        )

    row = st.columns([1, 1, 1.35], gap="medium")
    with row[0]:
        stat_card(
            "Trading at",
            f"${price:,.2f}",
            "/ share",
            f"Market capitalisation <b>${data.valuation['market_cap']:,.0f}M</b> · "
            f"enterprise value <b>${data.valuation['enterprise_value']:,.0f}M</b>.",
        )
    with row[1]:
        arrow = "▲" if upside >= 0 else "▼"
        css = "up" if upside >= 0 else "down"
        stat_card(
            "Blended price target",
            f"${target:,.2f}",
            "/ share",
            f'<span class="{css}">{arrow} {upside:+.1%}</span> against the current price. '
            f"Average of a cash-flow model and a peer-multiple approach.",
        )
    with row[2]:
        chart_card(
            "Value per share by method",
            charts.price_targets(
                price,
                {
                    "Cash-flow (DCF)": data.valuation["dcf_price_target"],
                    "Peer multiple": data.valuation["comps_price_target"],
                    "Blended": data.valuation["blended_price_target"],
                },
            ),
        )


# --------------------------------------------------------------------------- #
# Growth
# --------------------------------------------------------------------------- #

elif section == "growth":
    page_head(
        "Production & growth",
        "How many barrels come out of the ground each day, and how that turns into revenue.",
    )
    mode = st.radio("Range", ["Reported", "Projected", "Full range"], index=2,
                    horizontal=True, label_visibility="collapsed")

    explain(
        "Output is measured in <b>barrels of oil equivalent per day (boe/d)</b> — gas is "
        "converted into the amount of oil holding the same energy, so everything can be added "
        f"up. Production more than doubled between 2022 and {LAST_ACTUAL[:4]}, and is projected "
        f"to reach {prod_end:,.0f} boe/d by {FINAL_YEAR[:4]}."
    )
    chart_card(
        "Daily production, split by product",
        charts.production_mix(
            window(data.series("Oil production"), mode),
            window(data.series("Gas & NGL production"), mode),
            window(production, mode),
        ),
        "Bars stack to the daily total. The pale line is growth against the prior year.",
    )

    left, right = st.columns([1.6, 1], gap="medium")
    with left:
        chart_card(
            "Revenue and operating margin",
            charts.revenue_and_margin(
                window(data.series("Revenue"), mode), window(data.series("EBITDA Margin"), mode)
            ),
        )
    with right:
        card_open("Why revenue outruns production")
        st.markdown(
            f"""
            Revenue depends on two things: **how much you sell** and **the price you get**.

            - Volumes rise about **{prod_cagr:.0%} a year** through {FINAL_YEAR[:4]}.
            - The crude is light shale oil priced off Brent, so revenue moves with the global
              oil price even when production is flat.
            - Most costs are fixed per well, so extra barrels arrive at a high margin — which is
              why the margin line stays flat instead of falling as the company grows.
            """
        )
        card_close()


# --------------------------------------------------------------------------- #
# Margins
# --------------------------------------------------------------------------- #

elif section == "margins":
    page_head(
        "Margins & costs",
        "What a barrel costs to produce, what it sells for, and how much survives to the bottom line.",
    )
    explain(
        "This is the heart of the investment case. The cost to pull a barrel out of the ground — "
        f"the <b>lifting cost</b> — is roughly <b>${data.value('Lifting cost', LAST_ACTUAL):.2f}</b>, "
        "among the lowest in the industry. Add royalties, taxes and transport and the all-in cost "
        f"is about <b>${data.value('Total cost per boe', LAST_ACTUAL):.2f} per barrel</b>, against "
        f"a realised price near <b>${data.value('Realized oil price', LAST_ACTUAL):.2f}</b>."
    )

    top = st.columns([1, 1, 1], gap="medium")
    with top[0]:
        stat_card("Lifting cost", f"${data.value('Lifting cost', LAST_ACTUAL):.2f}", "/ boe",
                  f"Falling to <b>${data.value('Lifting cost', FINAL_YEAR):.2f}</b> by "
                  f"{FINAL_YEAR[:4]} as wells get more productive.")
    with top[1]:
        stat_card("All-in cost", f"${data.value('Total cost per boe', LAST_ACTUAL):.2f}", "/ boe",
                  "Includes royalties, export duties and selling expenses.")
    with top[2]:
        stat_card("Profit per barrel", f"${data.value('EBITDA per boe', LAST_ACTUAL):.2f}", "/ boe",
                  f"Projected at <b>${data.value('EBITDA per boe', FINAL_YEAR):.2f}</b> "
                  f"in {FINAL_YEAR[:4]}.")

    chart_card(
        "What a barrel earns versus what it costs",
        charts.unit_economics(data.series("EBITDA per boe"), data.series("Total cost per boe")),
        "The gap between the bars and the pale line is the profit on every barrel produced.",
    )
    chart_card(
        "Where each sales dollar goes",
        charts.margin_ladder(
            {
                "Gross margin": data.series("Gross Margin"),
                "EBITDA margin": data.series("EBITDA Margin"),
                "Operating margin (EBIT)": data.series("EBIT Margin"),
                "Net profit margin": data.series("Net Income Margin"),
            }
        ),
        "Each line peels back one layer of cost: production, then operating, then the charge "
        "for wells wearing out, then interest and tax.",
    )


# --------------------------------------------------------------------------- #
# Cash & debt
# --------------------------------------------------------------------------- #

elif section == "cash":
    page_head(
        "Cash & debt",
        "The transition from spending phase to harvest phase, and how the debt gets repaid.",
    )
    explain(
        "<b>Free cash flow</b> is the cash left after running the business and drilling new wells "
        "— the money genuinely available to repay debt or return to shareholders. It was deeply "
        f"negative in {LAST_ACTUAL[:4]} because Vista invested far more than it earned. As "
        f"drilling spend levels off while production keeps rising, it turns positive in "
        f"<b>{turnaround[:4]}</b>."
    )

    top = st.columns([1, 1, 1], gap="medium")
    with top[0]:
        stat_card("Free cash flow", f"${data.value('Free Cash Flow (levered)', LAST_ACTUAL):,.0f}M",
                  f"in {LAST_ACTUAL[:4]}",
                  f"Projected at <b>${data.value('Free Cash Flow (levered)', FINAL_YEAR):,.0f}M</b> "
                  f"by {FINAL_YEAR[:4]}.")
    with top[1]:
        stat_card("Capital spending", f"${abs(data.value('of which CapEx', FIRST_FORECAST)):,.0f}M",
                  f"in {FIRST_FORECAST[:4]}",
                  f"Tapering to <b>${abs(data.value('of which CapEx', FINAL_YEAR)):,.0f}M</b> "
                  f"as the field matures.")
    with top[2]:
        stat_card("Return on capital", f"{data.value('ROACE', LAST_ACTUAL):.1%}", "ROACE",
                  "Profit earned on every dollar of capital employed in the business.")

    chart_card(
        "Cash in, cash out, and what is left over",
        charts.cash_flow_story(fcf, data.series("of which CapEx"), data.series("Cash from Operations")),
        "Bars above zero are cash generated by operations; bars below are cash invested in new "
        "wells. The line is the net result.",
    )
    chart_card(
        "Net debt and leverage",
        charts.leverage(data.series("Net debt"), data.series("Net Debt / EBITDA")),
        "<b>Net debt ÷ EBITDA</b> answers one question: how many years of earnings would it take "
        "to repay everything owed? Under 2x is generally comfortable for an energy producer.",
    )


# --------------------------------------------------------------------------- #
# Valuation
# --------------------------------------------------------------------------- #

elif section == "valuation":
    page_head(
        "Valuation",
        "Two independent methods, and a grid showing how the answer moves with the assumptions.",
        f"Trading at ${price:,.2f}",
    )
    explain(
        "A <b>discounted cash flow (DCF)</b> adds up all the cash the business is expected to "
        "produce and converts it into today's money, because a dollar received in 2030 is worth "
        "less than a dollar today. A <b>comparables</b> approach asks what investors currently pay "
        "for similar producers and applies that to Vista's earnings."
    )

    left, right = st.columns([1.5, 1], gap="medium")
    with left:
        chart_card("From future cash flows to equity value", charts.dcf_waterfall(data.dcf))
    with right:
        card_open("Key assumptions")
        st.markdown(
            f"""
            | Input | Value |
            |---|---|
            | Discount rate (WACC) | {data.dcf['wacc']:.1%} |
            | Exit multiple (EV/EBITDA) | {data.dcf.get('exit_multiple_ev_ebitda', float('nan')):.1f}x |
            | Peer multiple applied | {data.dcf.get('comps_ev_ebitda_mult', float('nan')):.1f}x |
            | Shares outstanding | {data.valuation['shares_outstanding']:,.1f} M |
            | EV / EBITDA ({FIRST_FORECAST[:4]}) | {data.valuation['ev_ebitda_2026e']:.1f}x |
            """
        )
        card_close()

    st.markdown("### Test the assumptions yourself")
    explain(
        "Any valuation is only as good as its inputs. The two that matter most are the "
        "<b>oil price</b> and the <b>discount rate</b> — the return investors demand for taking "
        "the risk. Pick a combination to see what a share would be worth."
    )

    grid = data.sensitivity
    a, b, c = st.columns([1, 1, 1.4], gap="medium")
    with a:
        brent = st.select_slider(
            "Brent oil price ($/barrel)", options=list(grid.index),
            value=float(grid.index[len(grid.index) // 2]), format_func=lambda v: f"${v:,.0f}",
        )
    with b:
        wacc_options = list(grid.columns)
        wacc = st.select_slider(
            "Discount rate (WACC)", options=wacc_options,
            value=float(data.dcf["wacc"]) if data.dcf["wacc"] in wacc_options
            else wacc_options[len(wacc_options) // 2],
            format_func=lambda v: f"{v:.0%}",
        )
    implied = float(grid.loc[brent, wacc])
    move = implied / price - 1
    with c:
        css = "up" if move >= 0 else "down"
        arrow = "▲" if move >= 0 else "▼"
        stat_card(
            "Implied value per share", f"${implied:,.2f}", "/ share",
            f'<span class="{css}">{arrow} {move:+.1%}</span> against today\'s ${price:,.2f}, '
            f"at ${brent:,.0f} oil and a {wacc:.0%} discount rate.",
        )

    chart_card(
        "Value per share across assumptions",
        charts.sensitivity_heatmap(grid, price),
        "Brighter cells mean a higher value per share. Read across for a tougher discount rate, "
        "down for a stronger oil price.",
    )


# --------------------------------------------------------------------------- #
# Data
# --------------------------------------------------------------------------- #

elif section == "data":
    page_head("Underlying data", "Every figure behind the charts, exactly as parsed from the model.")

    sections = sorted(data.tidy["section"].unique())
    chosen = st.multiselect("Filter by statement", sections, default=sections)
    view = data.tidy[data.tidy["section"].isin(chosen)]

    wide = view.pivot_table(
        index=["section", "metric", "unit"], columns="year", values="value", sort=False
    ).reindex(columns=data.years)
    st.dataframe(wide.style.format("{:,.2f}", na_rep="—"), use_container_width=True, height=560)

    st.download_button(
        "Download tidy dataset (CSV)",
        data=data.tidy.to_csv(index=False).encode("utf-8"),
        file_name="vista_model_output.csv",
        mime="text/csv",
    )

    if data.notes:
        st.markdown("#### Source notes")
        for note in data.notes:
            st.caption(note)


# --------------------------------------------------------------------------- #
# Footer
# --------------------------------------------------------------------------- #

st.markdown("<hr>", unsafe_allow_html=True)
st.markdown(
    f"""<p style="color:{MUTED}; font-size:0.8rem; line-height:1.6;">
    Built with Streamlit and Plotly. Reported figures are taken from Vista Energy's published
    financial statements; all forward-looking figures are the author's own estimates produced by
    an independent financial model. Portfolio project for educational purposes — <b>not investment
    advice</b>, not a recommendation to buy or sell any security, and not affiliated with or
    endorsed by Vista Energy.</p>""",
    unsafe_allow_html=True,
)

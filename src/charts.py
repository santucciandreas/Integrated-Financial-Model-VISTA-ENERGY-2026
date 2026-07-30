"""
charts.py
---------
Every Plotly figure lives here so app.py stays a layout file.

Figures are drawn on a transparent background: the card behind them supplies the
surface colour, exactly as in a dark console UI. Two conventions hold throughout:

  1. Reported years are solid violet; projected years are hatched and sit on a
     lighter band, so fact and forecast are never confused.
  2. Hover text is written in full sentences with units, because the reader may
     not know oil and gas reporting conventions.
"""

from __future__ import annotations

from typing import Sequence

import pandas as pd
import plotly.graph_objects as go

from .theme import (
    CANVAS,
    GRID,
    LINE,
    MUTED,
    NEGATIVE,
    POSITIVE,
    PURPLE_SCALE,
    SURFACE_2,
    TEXT,
    VIOLET,
    VIOLET_DEEP,
    VIOLET_GLOW,
    VIOLET_LIGHT,
    plotly_layout,
)

#: Hatch applied to every projected bar.
_HATCH = dict(size=6, solidity=0.22, fgcolor=CANVAS)


def _pattern(periods: Sequence[str]) -> dict:
    """Marker pattern with the hatch switched on only for forecast bars."""
    return dict(shape=["" if p == "Actual" else "/" for p in periods], **_HATCH)


def _colours(periods: Sequence[str], actual: str = VIOLET, forecast: str = VIOLET_DEEP) -> list[str]:
    return [actual if p == "Actual" else forecast for p in periods]


def _forecast_band(fig: go.Figure, years: Sequence[str], label: bool = True) -> go.Figure:
    """Shade the projected years and mark where reported history stops."""
    forecasts = [y for y in years if y.endswith("E")]
    if not forecasts:
        return fig

    boundary = list(years).index(forecasts[0]) - 0.5
    fig.add_vrect(
        x0=boundary, x1=len(years) - 0.5,
        fillcolor="rgba(169,107,238,0.07)", layer="below", line_width=0,
    )
    fig.add_vline(x=boundary, line_width=1, line_dash="dot", line_color=VIOLET_DEEP)
    if label:
        fig.add_annotation(
            x=boundary, y=1.0, yref="paper", text="PROJECTED", showarrow=False,
            xanchor="left", yanchor="bottom",
            font=dict(size=9, color=VIOLET, family="'Space Grotesk', sans-serif"),
        )
    return fig


# --------------------------------------------------------------------------- #
# Single-figure cards (the donut / gauge / rail family from the reference)
# --------------------------------------------------------------------------- #


def production_donut(oil: float, gas: float, year_label: str) -> go.Figure:
    """Oil vs gas split, with the daily total in the middle of the ring."""
    total = oil + gas
    fig = go.Figure(
        go.Pie(
            labels=["Oil", "Gas & NGL"],
            values=[oil, gas],
            hole=0.68,
            sort=False,
            direction="clockwise",
            marker=dict(colors=[VIOLET, VIOLET_DEEP], line=dict(color=CANVAS, width=2)),
            textinfo="none",
            hovertemplate="%{label}: %{value:,.0f} boe/d (%{percent})<extra></extra>",
        )
    )
    fig.add_annotation(
        text=(
            f"<span style='font-size:13px;color:{MUTED}'>{year_label}</span><br>"
            f"<span style='font-size:26px;color:{TEXT}'><b>{total:,.0f}</b></span><br>"
            f"<span style='font-size:11px;color:{MUTED}'>boe per day</span>"
        ),
        showarrow=False, font=dict(family="'Space Grotesk', sans-serif"),
    )
    fig.update_layout(
        **plotly_layout(
            height=250, hovermode="closest",
            margin=dict(l=6, r=6, t=6, b=6),
            legend=dict(orientation="h", y=-0.02, x=0.5, xanchor="center",
                        font=dict(size=11, color=MUTED)),
        )
    )
    return fig


def margin_gauge(value: float, label: str) -> go.Figure:
    """A percentage shown as a partial ring with the number inside."""
    fig = go.Figure(
        go.Pie(
            values=[value, max(0.0, 1 - value)],
            hole=0.74,
            sort=False,
            direction="clockwise",
            rotation=0,
            marker=dict(colors=[VIOLET, "rgba(255,255,255,0.06)"], line=dict(width=0)),
            textinfo="none",
            hoverinfo="skip",
        )
    )
    fig.add_annotation(
        text=(
            f"<span style='font-size:34px;color:{TEXT}'><b>{value:.0%}</b></span><br>"
            f"<span style='font-size:11px;color:{MUTED}'>{label}</span>"
        ),
        showarrow=False, font=dict(family="'Space Grotesk', sans-serif"),
    )
    fig.update_layout(
        **plotly_layout(height=230, showlegend=False, hovermode=False,
                        margin=dict(l=6, r=6, t=6, b=6))
    )
    return fig


def compare_pair(labels: tuple[str, str], values: tuple[float, float], prefix: str = "$") -> go.Figure:
    """Two bars side by side — the 'May vs Jun' device from the reference."""
    fig = go.Figure(
        go.Bar(
            x=list(labels),
            y=list(values),
            width=0.45,
            marker=dict(color=[VIOLET_DEEP, VIOLET],
                        line=dict(color=VIOLET_LIGHT, width=1)),
            text=[f"{prefix}{v:,.0f}" for v in values],
            textposition="outside",
            textfont=dict(color=TEXT, size=13, family="'Space Grotesk', sans-serif"),
            hovertemplate="%{x}: " + prefix + "%{y:,.0f}<extra></extra>",
        )
    )
    fig.update_layout(
        **plotly_layout(
            height=230, hovermode="closest", showlegend=False,
            margin=dict(l=6, r=6, t=26, b=24),
            xaxis=dict(showgrid=False, linecolor="rgba(0,0,0,0)", ticks="",
                       tickfont=dict(color=MUTED, size=12)),
            yaxis=dict(visible=False, range=[0, max(values) * 1.28]),
        )
    )
    return fig


def trajectory(frame: pd.DataFrame, unit: str, fill: bool = True) -> go.Figure:
    """A single series as a gradient area — used for the headline trend card."""
    actual = frame[frame["period"] == "Actual"]
    forecast = frame[frame["period"] == "Forecast"]
    # Repeat the last reported point so the two segments join without a gap.
    bridge = pd.concat([actual.tail(1), forecast])

    fig = go.Figure()
    fig.add_scatter(
        name="Reported", x=actual["year"], y=actual["value"],
        mode="lines+markers", line=dict(color=VIOLET, width=3, shape="spline"),
        marker=dict(size=7, color=VIOLET, line=dict(color=CANVAS, width=1.5)),
        fill="tozeroy" if fill else None, fillcolor="rgba(169,107,238,0.20)",
        hovertemplate="%{y:,.0f} " + unit + "<extra>Reported</extra>",
    )
    fig.add_scatter(
        name="Projected", x=bridge["year"], y=bridge["value"],
        mode="lines+markers", line=dict(color=VIOLET_GLOW, width=2.5, dash="dot", shape="spline"),
        marker=dict(size=7, color=VIOLET_GLOW, line=dict(color=CANVAS, width=1.5)),
        fill="tozeroy" if fill else None, fillcolor="rgba(217,191,248,0.10)",
        hovertemplate="%{y:,.0f} " + unit + "<extra>Projected</extra>",
    )
    fig.update_layout(**plotly_layout(height=250, yaxis=dict(showgrid=True, gridcolor=GRID,
                                                            tickfont=dict(color=MUTED, size=11))))
    return fig


# --------------------------------------------------------------------------- #
# Full-width analytical charts
# --------------------------------------------------------------------------- #


def production_mix(oil: pd.DataFrame, gas: pd.DataFrame, total: pd.DataFrame) -> go.Figure:
    """Stacked oil vs gas production with the year-on-year growth rate on top."""
    years = total["year"].tolist()
    growth = total["value"].pct_change() * 100

    fig = go.Figure()
    fig.add_bar(
        name="Oil", x=oil["year"], y=oil["value"],
        marker=dict(color=VIOLET, pattern=_pattern(oil["period"])),
        hovertemplate="Oil: %{y:,.0f} barrels per day<extra></extra>",
    )
    fig.add_bar(
        name="Gas & NGL", x=gas["year"], y=gas["value"],
        marker=dict(color=VIOLET_DEEP, pattern=_pattern(gas["period"])),
        hovertemplate="Gas & NGL: %{y:,.0f} boe per day<extra></extra>",
    )
    fig.add_scatter(
        name="Growth vs prior year", x=years, y=growth, yaxis="y2",
        mode="lines+markers", line=dict(color=VIOLET_GLOW, width=2),
        marker=dict(size=6, color=VIOLET_GLOW),
        hovertemplate="Growth vs prior year: %{y:.1f}%<extra></extra>",
    )
    fig.update_layout(
        **plotly_layout(
            height=380, barmode="stack",
            yaxis=dict(title="boe per day", showgrid=True, gridcolor=GRID,
                       tickfont=dict(color=MUTED, size=11), titlefont=dict(color=MUTED, size=11)),
            yaxis2=dict(title="Growth (%)", overlaying="y", side="right", showgrid=False,
                        ticksuffix="%", tickfont=dict(color=MUTED, size=11),
                        titlefont=dict(color=MUTED, size=11)),
        )
    )
    return _forecast_band(fig, years)


def revenue_and_margin(revenue: pd.DataFrame, margin: pd.DataFrame) -> go.Figure:
    """Revenue bars with the EBITDA margin line — growth plus quality."""
    years = revenue["year"].tolist()

    fig = go.Figure()
    fig.add_bar(
        name="Revenue", x=revenue["year"], y=revenue["value"],
        marker=dict(color=_colours(revenue["period"]), pattern=_pattern(revenue["period"])),
        hovertemplate="Revenue: $%{y:,.0f} million<extra></extra>",
    )
    fig.add_scatter(
        name="EBITDA margin", x=margin["year"], y=margin["value"] * 100, yaxis="y2",
        mode="lines+markers", line=dict(color=VIOLET_GLOW, width=2.5),
        marker=dict(size=6), hovertemplate="EBITDA margin: %{y:.1f}% of revenue<extra></extra>",
    )
    fig.update_layout(
        **plotly_layout(
            height=380,
            yaxis=dict(title="$ millions", showgrid=True, gridcolor=GRID,
                       tickfont=dict(color=MUTED, size=11), titlefont=dict(color=MUTED, size=11)),
            yaxis2=dict(title="Margin (%)", overlaying="y", side="right", showgrid=False,
                        range=[0, 100], ticksuffix="%", tickfont=dict(color=MUTED, size=11),
                        titlefont=dict(color=MUTED, size=11)),
        )
    )
    return _forecast_band(fig, years)


def unit_economics(ebitda_per_boe: pd.DataFrame, cost_per_boe: pd.DataFrame) -> go.Figure:
    """What one barrel earns versus what it costs."""
    years = ebitda_per_boe["year"].tolist()

    fig = go.Figure()
    fig.add_bar(
        name="Profit per barrel", x=ebitda_per_boe["year"], y=ebitda_per_boe["value"],
        marker=dict(color=_colours(ebitda_per_boe["period"]),
                    pattern=_pattern(ebitda_per_boe["period"])),
        hovertemplate="Earns $%{y:.2f} per barrel<extra></extra>",
    )
    fig.add_scatter(
        name="Cost per barrel", x=cost_per_boe["year"], y=cost_per_boe["value"],
        mode="lines+markers", line=dict(color=VIOLET_GLOW, width=2.5),
        marker=dict(size=6), hovertemplate="Costs $%{y:.2f} per barrel<extra></extra>",
    )
    fig.update_layout(
        **plotly_layout(height=360, yaxis=dict(title="US$ per barrel", showgrid=True,
                                               gridcolor=GRID, tickfont=dict(color=MUTED, size=11),
                                               titlefont=dict(color=MUTED, size=11)))
    )
    return _forecast_band(fig, years)


def margin_ladder(frames: dict[str, pd.DataFrame]) -> go.Figure:
    """Gross / EBITDA / EBIT / net margins as parallel lines."""
    shades = [VIOLET_GLOW, VIOLET, VIOLET_LIGHT, VIOLET_DEEP]
    fig = go.Figure()
    years: list[str] = []
    for (label, frame), colour in zip(frames.items(), shades):
        years = frame["year"].tolist()
        fig.add_scatter(
            name=label, x=frame["year"], y=frame["value"] * 100,
            mode="lines+markers", line=dict(color=colour, width=2.5), marker=dict(size=6),
            hovertemplate=f"{label}: %{{y:.1f}}% of revenue<extra></extra>",
        )
    fig.update_layout(
        **plotly_layout(height=360, yaxis=dict(title="Share of revenue (%)", ticksuffix="%",
                                               showgrid=True, gridcolor=GRID,
                                               tickfont=dict(color=MUTED, size=11),
                                               titlefont=dict(color=MUTED, size=11)))
    )
    return _forecast_band(fig, years)


def cash_flow_story(fcf: pd.DataFrame, capex: pd.DataFrame, ocf: pd.DataFrame) -> go.Figure:
    """Operating cash in, capital spending out, free cash flow as the result."""
    years = fcf["year"].tolist()

    fig = go.Figure()
    fig.add_bar(
        name="Cash from operations", x=ocf["year"], y=ocf["value"],
        marker=dict(color=VIOLET_DEEP),
        hovertemplate="Cash from operations: $%{y:,.0f} million<extra></extra>",
    )
    fig.add_bar(
        name="Invested in new wells", x=capex["year"], y=capex["value"],
        marker=dict(color="rgba(169,107,238,0.45)"),
        hovertemplate="Capital spending: $%{y:,.0f} million<extra></extra>",
    )
    fig.add_scatter(
        name="Free cash flow", x=fcf["year"], y=fcf["value"],
        mode="lines+markers", line=dict(color=VIOLET_GLOW, width=3),
        marker=dict(size=10, color=[POSITIVE if v >= 0 else NEGATIVE for v in fcf["value"]],
                    line=dict(width=1.5, color=CANVAS)),
        hovertemplate="Free cash flow: $%{y:,.0f} million<extra></extra>",
    )
    fig.add_hline(y=0, line_width=1, line_color=MUTED)
    fig.update_layout(
        **plotly_layout(height=390, barmode="relative",
                        yaxis=dict(title="$ millions", showgrid=True, gridcolor=GRID,
                                   tickfont=dict(color=MUTED, size=11),
                                   titlefont=dict(color=MUTED, size=11)))
    )
    return _forecast_band(fig, years)


def leverage(net_debt: pd.DataFrame, ratio: pd.DataFrame) -> go.Figure:
    """Net debt in dollars, with debt-to-earnings as the reader's yardstick."""
    years = net_debt["year"].tolist()

    fig = go.Figure()
    fig.add_bar(
        name="Net debt", x=net_debt["year"], y=net_debt["value"],
        marker=dict(color=_colours(net_debt["period"]), pattern=_pattern(net_debt["period"])),
        hovertemplate="Net debt: $%{y:,.0f} million<extra></extra>",
    )
    fig.add_scatter(
        name="Net debt / EBITDA", x=ratio["year"], y=ratio["value"], yaxis="y2",
        mode="lines+markers", line=dict(color=VIOLET_GLOW, width=2.5), marker=dict(size=6),
        hovertemplate="Debt equals %{y:.2f} years of earnings<extra></extra>",
    )
    fig.add_hline(y=0, line_width=1, line_color=MUTED)
    fig.update_layout(
        **plotly_layout(height=360,
                        yaxis=dict(title="$ millions", showgrid=True, gridcolor=GRID,
                                   tickfont=dict(color=MUTED, size=11),
                                   titlefont=dict(color=MUTED, size=11)),
                        yaxis2=dict(title="Years of earnings", overlaying="y", side="right",
                                    showgrid=False, tickfont=dict(color=MUTED, size=11),
                                    titlefont=dict(color=MUTED, size=11)))
    )
    return _forecast_band(fig, years)


def dcf_waterfall(dcf: dict) -> go.Figure:
    """Bridge from discounted cash flows to the value of one share."""
    steps = [
        ("Cash flows 2026-2030", dcf["sum_pv_of_fcf_m"], "relative"),
        ("Value beyond 2030", dcf["pv_of_terminal_value_m"], "relative"),
        ("Company value", None, "total"),
        ("Less: net debt", -dcf["less_net_debt_2025a_m"], "relative"),
        ("Value for shareholders", None, "total"),
    ]
    fig = go.Figure(
        go.Waterfall(
            orientation="v",
            measure=[m for _, _, m in steps],
            x=[label for label, _, _ in steps],
            y=[0 if v is None else v for _, v, _ in steps],
            connector=dict(line=dict(color=LINE)),
            increasing=dict(marker=dict(color=VIOLET_DEEP)),
            decreasing=dict(marker=dict(color=NEGATIVE)),
            totals=dict(marker=dict(color=VIOLET)),
            texttemplate="$%{y:,.0f}M",
            textposition="outside",
            textfont=dict(color=TEXT, size=11),
            hovertemplate="%{x}: $%{y:,.0f} million<extra></extra>",
        )
    )
    fig.update_layout(
        **plotly_layout(height=380, hovermode="closest", showlegend=False,
                        yaxis=dict(title="$ millions", showgrid=True, gridcolor=GRID,
                                   tickfont=dict(color=MUTED, size=11),
                                   titlefont=dict(color=MUTED, size=11)))
    )
    return fig


def price_targets(current: float, targets: dict[str, float]) -> go.Figure:
    """The share price today versus each valuation method."""
    labels, values = list(targets.keys()), list(targets.values())
    fig = go.Figure()
    fig.add_bar(
        x=values, y=labels, orientation="h",
        marker=dict(color=[VIOLET_DEEP, VIOLET_LIGHT, VIOLET][: len(labels)]),
        texttemplate="$%{x:,.2f}", textposition="outside",
        textfont=dict(color=TEXT, size=12),
        hovertemplate="%{y}: $%{x:,.2f} per share<extra></extra>", showlegend=False,
    )
    fig.add_vline(
        x=current, line_width=2, line_dash="dash", line_color=VIOLET_GLOW,
        annotation_text=f"Trading today ${current:,.2f}", annotation_position="top",
        annotation_font=dict(color=VIOLET_GLOW, size=11),
    )
    fig.update_layout(
        **plotly_layout(
            height=300, hovermode="closest",
            margin=dict(l=8, r=90, t=30, b=30),
            xaxis=dict(title="US$ per share", showgrid=True, gridcolor=GRID,
                       tickfont=dict(color=MUTED, size=11), titlefont=dict(color=MUTED, size=11)),
            yaxis=dict(showgrid=False, autorange="reversed", tickfont=dict(color=TEXT, size=12)),
        )
    )
    return fig


def sensitivity_heatmap(grid: pd.DataFrame, current_price: float) -> go.Figure:
    """Value per share across oil-price and discount-rate assumptions."""
    fig = go.Figure(
        go.Heatmap(
            z=grid.values,
            x=[f"{c:.0%}" for c in grid.columns],
            y=[f"${i:,.0f}" for i in grid.index],
            colorscale=PURPLE_SCALE,
            texttemplate="%{z:.0f}",
            textfont=dict(size=11, color=TEXT),
            xgap=2, ygap=2,
            hovertemplate=("Oil %{y}/barrel, discount rate %{x}"
                           "<br>Value per share: $%{z:,.2f}<extra></extra>"),
            colorbar=dict(title=dict(text="$/share", side="right", font=dict(color=MUTED, size=11)),
                          thickness=12, outlinewidth=0, tickfont=dict(color=MUTED, size=10)),
        )
    )
    fig.update_layout(
        **plotly_layout(
            height=380, hovermode="closest",
            xaxis=dict(title="Discount rate (WACC)", showgrid=False,
                       tickfont=dict(color=MUTED, size=11), titlefont=dict(color=MUTED, size=11)),
            yaxis=dict(title="Brent oil price", showgrid=False,
                       tickfont=dict(color=MUTED, size=11), titlefont=dict(color=MUTED, size=11)),
        )
    )
    return fig

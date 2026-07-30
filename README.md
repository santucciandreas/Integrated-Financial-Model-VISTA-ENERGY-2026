# Vista Energy (VIST) – 5-Year Integrated Financial Model

## Overview

This project consists of a fully integrated three-statement financial model for **Vista Energy, S.A.B. de C.V.**
(NYSE: VIST · BMV: VISTA), the largest independent shale oil producer in Vaca Muerta, Argentina, including:

- Income Statement
- Balance Sheet
- Cash Flow Statement

The model projects financial performance over a 5-year horizon (2026E–2030E) on top of four years of audited
history (2022A–2025A), using operating drivers — Brent price, production growth, lifting cost and capital
expenditure — under three switchable scenarios. A set of KPIs evaluates growth, profitability, cash
generation, solvency, returns on capital and valuation.

Two interactive web dashboards sit on top of the model's outputs: one that presents the conclusions, and one
that lets the reader test them.

## Dashboards

Both are published on GitHub Pages and readable without installing anything.

### Summary dashboard

A single-page visual read on the company, designed to be absorbed in under four minutes: a headline take,
four key metrics, and five themed sections, each with a chart and a short interpretive note.

▶ **[Open the summary dashboard](https://santucciandreas.github.io/Integrated-Financial-Model-VISTA-ENERGY-2026/)**

| Section | Focus |
|---|---|
| 01 · Scale & Growth | Production per day and proved reserves |
| 02 · Growth & Profitability | Revenue, adjusted EBITDA and margin stability |
| 03 · Cash Generation | Unlevered free cash flow against capital expenditure |
| 04 · Solvency & Deleveraging | Net debt / EBITDA and interest coverage |
| 05 · Valuation & Scenarios | DCF vs. comparable multiple, and Brent sensitivity |

A dashed gold line in every chart marks the boundary between actuals (2022–2025) and projections
(2026E–2030E).

### Interactive dashboard

A full Streamlit application compiled to WebAssembly, so it runs entirely inside the browser with no server
and no installation. Where the summary dashboard presents conclusions, this one lets the reader test them:
the valuation section exposes the Brent × WACC sensitivity grid as live controls, so any combination of oil
price and discount rate can be priced on the spot.

▶ **[Open the interactive dashboard](https://santucciandreas.github.io/Integrated-Financial-Model-VISTA-ENERGY-2026/app.html)**
— the first load takes about a minute while the Python runtime downloads; it is cached from then on.

| Section | Focus |
|---|---|
| Overview | Headline card grid: production mix, margin, deleveraging, price target |
| Production & growth | Daily output by product, and how volumes translate into revenue |
| Margins & costs | Unit economics per barrel and the full margin ladder |
| Cash & debt | The shift from investment phase to cash generation |
| Valuation | DCF bridge, method comparison, and the live sensitivity grid |
| Underlying data | Every parsed figure, filterable and downloadable as CSV |

Solid bars are reported results; hatched bars on a shaded band are projections. The distinction is driven by
the `A`/`E` suffix in the model's own year headers, so extending the forecast horizon extends the shading
automatically.

### Running the interactive dashboard locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

The app opens at `http://localhost:8501`. After editing any Python source, regenerate the published page with
`python build_standalone.py`.

## Project Structure

| Sheet | Description |
|---|---|
| Cover | Model metadata, navigation and colour legend |
| Imputs Drivers | Brent price, production growth, lifting cost, CAPEX, tax, interest and debt assumptions |
| Imput Historical | Audited historicals 2022–2025, transcribed from SEC filings |
| Model | Integrated 3-statement forecast, debt and revolver schedule, balance-sheet reconciliation |
| Outputs | Operating KPIs, summarised financials, valuation, DCF and sensitivity |
| Dashboard | Summary of results |

| File | Description |
|---|---|
| `index.html` | Summary dashboard — open directly or host on GitHub Pages |
| `generate_dashboard.py` | Generator that turns the Outputs sheet into the summary dashboard |
| `app.html` | Interactive dashboard — self-contained Streamlit / WebAssembly build |
| `app.py` | Streamlit application: layout and page structure |
| `src/data_loader.py` | Parses the Outputs sheet into tidy pandas objects |
| `src/theme.py` | Colour tokens, typography and the shared Plotly layout |
| `src/charts.py` | One function per figure |
| `build_standalone.py` | Rebuilds `app.html` after any change to the Python sources |
| `requirements.txt` | Pinned dependencies for running the app locally |

## Tools Used

- Microsoft Excel 365
- Claude (Anthropic), running inside Excel, for model auditing and refactoring
- Python (openpyxl) + Plotly for the interactive dashboards
- Streamlit, compiled to WebAssembly with stlite, for the interactive build
- Financial Modeling best-practice references (FMVA methodology)

## Key Assumptions

### Scenarios

| Driver | Scenario | 2026E | 2027E | 2028E | 2029E | 2030E |
|---|---|---|---|---|---|---|
| Brent (US$/bbl) | Best | 95.0 | 92.0 | 90.0 | 88.0 | 85.0 |
| | Base | 85.0 | 82.0 | 80.0 | 78.0 | 75.0 |
| | Worst | 61.5 | 64.0 | 65.3 | 63.4 | 63.4 |
| Production growth | Best | 25% | 20% | 15% | 12% | 10% |
| | Base | 15% | 12% | 10% | 8% | 6% |
| | Worst | 5% | 5% | 4% | 4% | 3% |
| Lifting cost (US$/boe) | Best | 3.8 | 3.6 | 3.4 | 3.2 | 3.0 |
| | Base | 4.3 | 4.1 | 3.9 | 3.7 | 3.5 |
| | Worst | 5.0 | 4.8 | 4.6 | 4.4 | 4.2 |
| CAPEX (US$M) | Best | 1,400 | 1,300 | 1,200 | 1,100 | 1,000 |
| | Base | 1,550 | 1,500 | 1,400 | 1,300 | 1,200 |
| | Worst | 1,700 | 1,650 | 1,600 | 1,500 | 1,400 |

The downside case deliberately pairs the lowest prices with the **highest** capital expenditure — it spends
more and gets less, which is what makes it a genuine stress test rather than a softer version of the base case.

### Financial and tax

- Effective Tax Rate: 30.0% (2022–2025 average 28.2%; Argentine statutory rate 35%)
- Interest rate on gross debt: 7.5% (7.1% implied by 2025 interest expense)
- Depletion rate: US$17.5/boe, volume-based (2025 rate per Form 20-F)
- Realised oil price: 92.2% of Brent, held constant at the 2025 differential

### Capital structure

- Debt repayment of US$350M per year, no new borrowings
- Minimum cash balance of US$200M, maintained by a revolving facility
- No dividends and no equity issuance

### Valuation

- WACC: 13.0%
- Terminal exit multiple: 4.5x EBITDA
- Comparable multiple cross-check: 5.0x EV / 2026E EBITDA

## Validation

The model includes automated balance checks for every projected period:

**Assets = Liabilities + Equity**

The check holds in all nine periods **and under all three scenarios**. Cash is an output of the cash flow
statement rather than a balancing plug, so the check is a genuine test rather than an identity that is true
by construction. Interest is calculated on opening balances, so the model contains no circular references
and requires no iterative calculation. All financial statements are dynamically linked with no manual
balancing plugs.

Every historical figure was verified against the FY2025 Form 20-F: revenue, operating profit, net income,
total assets, cash flow subtotals, unit operating costs, production volumes and realised prices all tie.

## Key Insights

- **Vista is a growth story that funds itself.** Roughly US$7.0 billion of capital expenditure over five
  years, with positive unlevered free cash flow in every single year (~US$3.8 billion cumulative).
- **Deleveraging comes from growth, not from austerity.** Net debt / EBITDA falls from 1.66x in 2025A to
  1.08x in 2026E and inverts to a net cash position by 2030E, with no equity issuance. Interest coverage
  improves from 6.2x to 13.0x.
- **Growth does not erode profitability.** Production rises 62% to 2030E while the adjusted EBITDA margin
  holds near 65% and lifting cost falls from US$4.3 to US$3.5 per barrel.
- **ROACE of ~17% sits above the 13% assumed WACC**, indicating the company creates economic value rather
  than merely generating accounting profit — the spread holds across the projection period.
- **The equity is highly asymmetric to the oil price.** DCF value per share ranges from US$129 in the
  upside case to US$10 in the downside, against a share price of US$64.64. Vista is a leveraged bet on
  Brent, not a defensive compounder.
- **Caveat:** roughly 73% of the DCF enterprise value sits in the terminal value, which is inherent to a
  five-year window on a capital-intensive producer, and worth keeping in mind.

## Sources

All historical financial and operating data transcribed from Vista's **Form 20-F annual reports filed with
the U.S. Securities and Exchange Commission** — audited financial statements and the "Production Results and
Other Operating Data" disclosures. Market data as of June 2026.

## Disclaimer

This model was developed for educational and analytical purposes only and should not be considered
investment advice.

**Author:** Andreas Santucci · **Date:** July 2026

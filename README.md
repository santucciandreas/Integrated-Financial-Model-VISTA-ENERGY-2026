Vista Energy (VIST) – 5-Year Integrated Financial Model
Overview

This project consists of a fully integrated three-statement financial model for Vista Energy, S.A.B. de C.V. (NYSE: VIST · BMV: VISTA), the largest independent shale oil producer in Vaca Muerta, Argentina, including:

Income Statement
Balance Sheet
Cash Flow Statement

The model projects financial performance over a 5-year horizon (2026E–2030E) on top of four years of audited history (2022A–2025A), using operating drivers — Brent price, production growth, lifting cost and capital expenditure — under three switchable scenarios. A set of KPIs evaluates growth, profitability, cash generation, solvency, returns on capital and valuation.

An interactive Tableau dashboard sits on top of the model's outputs, presenting the investment thesis at a glance.

Dashboard

Built in Tableau Public and viewable in the browser without installing anything. The design is deliberately minimal — the headline valuation metrics and the production trajectory that drives the whole thesis, with no visual clutter.

▶ Open the Tableau dashboard

The dashboard leads with four headline metrics — blended price target, 2030E production, upside to the current share price, and 2030E adjusted EBITDA — above a single production ramp-up curve. Actual years (2022–2025) are drawn in grey and projected years (2026E–2030E) in colour, so the ~4x production growth driven by Vaca Muerta reads in a single glance.

Headline metric	Value	Context
Price target	US$74.2 / share	Blended DCF + comparables
Production 2030E	187,301 boe/d	From 48,560 in 2022 — ~4x growth
Upside	+14.9%	vs. US$64.64 current share price
Adjusted EBITDA 2030E	US$2,904M	From US$741M in 2022 — ~4x growth
Project Structure
Sheet	Description
Cover	Model metadata, navigation and colour legend
Imputs Drivers	Brent price, production growth, lifting cost, CAPEX, tax, interest and debt assumptions
Imput Historical	Audited historicals 2022–2025, transcribed from SEC filings
Model	Integrated 3-statement forecast, debt and revolver schedule, balance-sheet reconciliation
Outputs	Operating KPIs, summarised financials, valuation, DCF and sensitivity
Production_Curve	Tidy production series (2022–2030) feeding the Tableau curve
KPI_Cards	Headline valuation metrics feeding the Tableau cards
Tools Used
Microsoft Excel 365
Claude (Anthropic), running inside Excel, for model auditing and refactoring
Tableau Public for the interactive dashboard
Financial Modeling best-practice references (FMVA methodology)
Key Assumptions
Scenarios
Driver	Scenario	2026E	2027E	2028E	2029E	2030E
Brent (US$/bbl)	Best	95.0	92.0	90.0	88.0	85.0
	Base	85.0	82.0	80.0	78.0	75.0
	Worst	61.5	64.0	65.3	63.4	63.4
Production growth	Best	25%	20%	15%	12%	10%
	Base	15%	12%	10%	8%	6%
	Worst	5%	5%	4%	4%	3%
Lifting cost (US$/boe)	Best	3.8	3.6	3.4	3.2	3.0
	Base	4.3	4.1	3.9	3.7	3.5
	Worst	5.0	4.8	4.6	4.4	4.2
CAPEX (US$M)	Best	1,400	1,300	1,200	1,100	1,000
	Base	1,550	1,500	1,400	1,300	1,200
	Worst	1,700	1,650	1,600	1,500	1,400

The downside case deliberately pairs the lowest prices with the highest capital expenditure — it spends more and gets less, which is what makes it a genuine stress test rather than a softer version of the base case.

Financial and tax
Effective Tax Rate: 30.0% (2022–2025 average 28.2%; Argentine statutory rate 35%)
Interest rate on gross debt: 7.5% (7.1% implied by 2025 interest expense)
Depletion rate: US$17.5/boe, volume-based (2025 rate per Form 20-F)
Realised oil price: 92.2% of Brent, held constant at the 2025 differential
Capital structure
Debt repayment of US$350M per year, no new borrowings
Minimum cash balance of US$200M, maintained by a revolving facility
No dividends and no equity issuance
Valuation
WACC: 13.0%
Terminal exit multiple: 4.5x EBITDA
Comparable multiple cross-check: 5.0x EV / 2026E EBITDA
Validation

The model includes automated balance checks for every projected period:

Assets = Liabilities + Equity

The check holds in all nine periods and under all three scenarios. Cash is an output of the cash flow statement rather than a balancing plug, so the check is a genuine test rather than an identity that is true by construction. Interest is calculated on opening balances, so the model contains no circular references and requires no iterative calculation. All financial statements are dynamically linked with no manual balancing plugs.

Every historical figure was verified against the FY2025 Form 20-F: revenue, operating profit, net income, total assets, cash flow subtotals, unit operating costs, production volumes and realised prices all tie.

Key Insights
Vista is a growth story that funds itself. Roughly US$7.0 billion of capital expenditure over five years, with positive unlevered free cash flow in every single year (~US$3.8 billion cumulative).
Deleveraging comes from growth, not from austerity. Net debt / EBITDA falls from 1.66x in 2025A to 1.08x in 2026E and inverts to a net cash position by 2030E, with no equity issuance. Interest coverage improves from 6.2x to 13.0x.
Growth does not erode profitability. Production rises ~4x from 2022A to 2030E while the adjusted EBITDA margin holds near 65% and lifting cost falls from US$4.3 to US$3.5 per barrel.
ROACE of ~17% sits above the 13% assumed WACC, indicating the company creates economic value rather than merely generating accounting profit — the spread holds across the projection period.
The equity is highly asymmetric to the oil price. DCF value per share ranges from US$129 in the upside case to US$10 in the downside, against a share price of US$64.64. Vista is a leveraged bet on Brent, not a defensive compounder.
Caveat: roughly 73% of the DCF enterprise value sits in the terminal value, which is inherent to a five-year window on a capital-intensive producer, and worth keeping in mind.
Sources

All historical financial and operating data transcribed from Vista's Form 20-F annual reports filed with the U.S. Securities and Exchange Commission — audited financial statements and the "Production Results and Other Operating Data" disclosures. Market data as of June 2026.

Disclaimer

This model was developed for educational and analytical purposes only and should not be considered investment advice.

Author: Andreas Santucci · Date: July 2026

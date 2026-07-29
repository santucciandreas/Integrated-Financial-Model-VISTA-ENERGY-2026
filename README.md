## Dashboard 

<!-- Replace with your screenshot: save it as docs/dashboard.png -->
![Vista Energy dashboard](docs/dashboard.png)

📥 [Download the model](Vista_Energy_Financial_Model_v1.xlsx) · 🔗 [Open the dashboard](#)

## Potential

Vista grew from 24.5 thousand barrels of oil equivalent per day in 2018 to 135.4 in the fourth quarter
of 2025. The model projects that trajectory to 2030 and asks three questions: can it continue, does it 
pay for itself, and what is it worth.

The short answer, in the base case: production compounds at ~10% a year with margins holding near 65%,
the capital plan is funded entirely from operating cash flow, leverage inverts to a net cash position,
and proved reserves of 588 MMboe support roughly 14 years at the current rate.

## Assumptions

| Assumption | Value | Basis |
|---|---|---|
| WACC | 13.0% | Argentine E&P risk premium |
| Terminal exit multiple | 4.5x EBITDA | Below the 5.0x peer multiple |
| Effective tax rate | 30.0% | 28.2% historical average; 35% statutory |
| Interest rate on gross debt | 7.5% | 7.1% implied by 2025 |
| Depletion rate | US$17.5/boe | 2025 rate per Form 20-F |
| Debt repayment | US$350M/year | 2025 current portion |
| Minimum cash | US$200M | Revolver trigger |

Three scenarios — Best, Base, Worst — differ in Brent price, production growth and capital expenditure.

## Structure

| Sheet | Contents |
|---|---|
| **Dashboard** | Summary of results. |
| **Cover** | Contents, colour legend, sources. |
| **Outputs** | KPIs, summarised financials, valuation, DCF, sensitivity. |
| **Model** | Three-statement model 2022A–2030E, debt schedule, drivers. |
| **Imputs Drivers** | Every assumption. Blue cells are the only inputs. |
| **Imput Historical** | Audited historicals 2022–2025 from SEC filings. |

## How it was built

Cash is an output of the cash flow statement, not a balancing plug — so the balance-sheet check is a real
test, and it balances in all nine periods under all three scenarios.

Claude, running inside Excel, was used to audit and refactor the model. It found and fixed a circular cash
plug that made that check meaningless, a missing interest expense on US$3.2 billion of debt, a depletion
rate driven by the oil price instead of by barrels produced, a scenario that broke because prices were
stored as text, and a US$10 thousand transcription error traced back to the filing. It also verified every
historical figure against the Form 20-F and built the debt and revolver schedule.

## Sources

All historicals transcribed from Vista's **Form 20-F annual reports filed with the SEC** (audited
financial statements and production disclosures). Market data as of June 2026. Revenue, operating profit,
net income, total assets, cash flow subtotals, unit costs, production volumes and realised prices all tie
to the FY2025 filing.

## Disclaimer

Educational and illustrative purposes only. Not investment advice or a recommendation. The author holds no
position in Vista Energy.

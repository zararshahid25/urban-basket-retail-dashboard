# Urban Basket Retail Sales Dashboard

**PostgreSQL • Excel • Power Query • Power BI**

A simulated retail reporting training project for a 2026 analytics portfolio. It converts five raw CSVs into constrained relational tables and reports sales, margins, product contribution and order-status returns across 2024–2025.

![Excel dashboard preview](assets/excel_dashboard.png)

*Delivered Excel workbook preview. Power BI Desktop screenshots await local refresh and visual acceptance.*

## Start here

1. Download the whole repository and follow [the rebuild manual](docs/REBUILD_MANUAL.md).
2. Open [the Excel workbook](excel/Urban_Basket_Retail.xlsx) and change its channel selector.
3. Create database `urban_basket`. From the project root, run `psql -h localhost -U postgres -d urban_basket -f sql/run_all.psql`.
4. Open [UrbanBasket.pbip](powerbi/UrbanBasket.pbip), set the PostgreSQL connection parameters, refresh and complete the Desktop checklist.

No Python or Streamlit installation is required. Earlier implementation history remains in Git history.

## Business questions and implementation

- Monthly sales and profit: line arithmetic, date grouping and LAG comparisons.
- Category contribution: weighted margins and non-additive distinct order counts.
- Product performance: DENSE_RANK, CTEs and correlated subqueries.
- Channel/customer behavior: completed-order AOV and status-based return rates.
- Data trust: deterministic duplicates, city mapping, quantity quarantine and decimal rounding.

Five constrained business tables feed four Power BI tables with three single-direction relationships. The project includes nine SQL questions, a seven-sheet Excel workbook with four KPIs and three charts, and 17 DAX measures across three Power BI pages with 26 visual definitions. All accepted enriched rows are compared against a prepared reference fixture; see [validation](docs/VALIDATION.md).

## Baseline results

| Measure | All channels, 2024–2025 |
|---|---:|
| Prepared orders | 9,000 |
| Accepted items | 20,124 |
| Net sales | PKR 19,245,467.69 |
| Gross profit | PKR 4,887,184.34 |
| Gross margin | 25.39% |
| Completed AOV | PKR 2,579.92 |
| Returned-order rate | 7.00% |

Completed activity is positive, Returned activity negative and Cancelled activity zero. This is a simulated status-snapshot policy using order dates, not a financial ledger or linked return-event model. AOV uses completed sales / distinct completed orders. Category distinct order counts cannot be summed to obtain the overall count.

## Documentation and verification limits

- [Run and rebuild manual](docs/REBUILD_MANUAL.md)
- [Metric definitions](docs/KPI_DEFINITIONS.md)
- [Data model](docs/DATA_MODEL.md)
- [Validation record](docs/VALIDATION.md)
- [Portfolio notes](docs/PORTFOLIO_NOTES.md)

PBIP/PBIR structures were schema-checked. Power BI Desktop opening, refresh, DAX execution and rendering have **not** been verified in the authoring environment. Complete the Windows checklist before sharing Power BI screenshots or claiming native runtime validation. Excel was recalculated and rendered with the workbook authoring engine; native Excel checks remain local.

All records are simulated. This project does not establish employment, client delivery, production use or measured commercial impact. Source dates are 2024–2025; 2026 is the project year.

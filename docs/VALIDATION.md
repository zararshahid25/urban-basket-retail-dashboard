# Validation record

Revision: Excel, PostgreSQL and Power BI, 21 September 2026.

- Power BI: 35 project/report files validated against official Microsoft JSON schemas. Four tables, three relationships, 17 measures and 26 visual definitions.
- PostgreSQL: assertions cover counts, accepted-item grain, cancellations, decimal arithmetic, calendar coverage and bidirectional full-row reconciliation. CI runs the complete loader twice and all nine SQL questions. See the handoff's GitHub Actions link for executed results; a workflow definition alone is not evidence of passing execution.
- Excel: four headline KPIs reconciled against independent reference calculations; Web net sales and AOV recalculated, selector restored to All; formula-error scan and seven-sheet visual inspection.

## Native application checks still required

Power BI Desktop is unavailable in the authoring environment. Opening, refresh, DAX execution and rendering have not been tested in Desktop. JSON schema validation cannot establish runtime compatibility. Follow the manual's acceptance checklist before sharing Power BI screenshots.

Excel was recalculated and rendered using the workbook authoring engine, not the Excel desktop application. Check recalculation and the channel selector in Excel. The workbook has a prepared snapshot, with no embedded live PostgreSQL/Power Query connection.

The fixture cannot validate real revenue recognition, refund timing, inventory valuation or business impact.

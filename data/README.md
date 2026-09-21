# Data provenance

The five raw CSVs are synthetic training fixtures retained from the original Urban Basket exercise. They contain simulated customer/order identifiers and deliberate anomalies. No real customer records are included. Source dates cover 2024–2025.

The current workflow starts with these static fixtures and requires no data generator. `sql/run_all.psql` reproduces prepared data from the raw CSVs. `reference/` contains the expected prepared snapshot and KPI controls. `sql/export_reference.psql` can export PostgreSQL results after validation; do not replace the reference solely to hide a failed comparison.

Current metrics use exact decimal per-line rounding and may differ from the earlier floating-point implementation. The raw data is preserved unchanged.

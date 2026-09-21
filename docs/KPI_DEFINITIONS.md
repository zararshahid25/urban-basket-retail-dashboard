# KPI definitions

The reporting grain is one accepted order item. Currency is PKR. Round per line to two decimals using SQL NUMERIC, half away from zero. Discounts are stored in 0–100 units.

| Measure | Definition | Behavior |
|---|---|---|
| Line revenue | ROUND(quantity × unit_price × (1 − discount_pct/100), 2) | Recomputed from accepted inputs |
| Line cost | ROUND(quantity × reference unit_cost, 2) | Static scenario cost |
| Net sales | Sum(line revenue × status sign) | Completed +1, Returned −1, Cancelled 0 |
| Gross profit | Sum((line revenue − line cost) × sign) | Same status policy |
| Gross margin | Gross profit / net sales | Ratio of totals; zero denominator gives blank |
| Completed sales | Sum line revenue for Completed | Positive contribution |
| Returned value | Sum line revenue for Returned | Positive magnitude |
| Completed AOV | Completed sales / distinct Completed order IDs | Same filters in numerator and denominator |
| Return rate | Distinct Returned orders / distinct Completed-or-Returned orders | Cancels excluded |
| Orders | Distinct order IDs in filtered lines | Category counts are non-additive |
| Net units | Sum(quantity × sign) | Cancelled = 0 |
| Category share | Category net sales / sales among selected categories | Other filters retained |
| MoM / YoY | (Current month − comparison month sales) / comparison | Single month context; missing comparison gives blank |

An order spanning two categories appears in both category counts but once in the all-category total. Category AOV is the category's completed revenue per completed order containing it, not the total basket value of those orders. Excel filters by channel and uses the unique Orders sheet for denominators.

There is no separate refund date or original-sale link. Returned activity is assigned to recorded order month. Do not call it recognized accounting revenue or a cohort return rate. Shipping, tax, overhead and acquisition costs are absent; gross profit is not net profit.

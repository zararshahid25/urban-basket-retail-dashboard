# KPI definitions

| KPI | Formula | Important treatment |
|---|---|---|
| Net revenue | Completed line revenue − returned line revenue | Cancelled orders contribute zero. |
| Gross profit | Signed line revenue − signed line cost | Returned margins are reversed. |
| Gross margin | Total gross profit ÷ total net revenue × 100 | Calculated from totals, not averaged category margins. |
| Net units | Completed quantity − returned quantity | Cancelled quantity contributes zero. |
| Orders | Distinct order IDs in the selected population | An order may span several product categories. |
| Average order value | Net revenue ÷ completed orders | Returned and cancelled orders are excluded from the denominator. |
| Return rate | Returned orders ÷ (completed + returned orders) × 100 | Cancelled orders are excluded. |

For category return rates, the query first creates distinct category–order pairs so a multi-item order is not counted twice within the same category.


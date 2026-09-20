# Data model

```mermaid
erDiagram
    CATEGORIES ||--o{ PRODUCTS : contains
    CUSTOMERS ||--o{ ORDERS : places
    ORDERS ||--|{ ORDER_ITEMS : contains
    PRODUCTS ||--o{ ORDER_ITEMS : appears_in

    CATEGORIES {
        int category_id PK
        varchar category_name
    }
    PRODUCTS {
        int product_id PK
        int category_id FK
        varchar product_name
        numeric unit_cost
        numeric list_price
    }
    CUSTOMERS {
        varchar customer_id PK
        varchar customer_segment
        varchar city
        date signup_date
    }
    ORDERS {
        varchar order_id PK
        varchar customer_id FK
        date order_date
        varchar order_status
        varchar sales_channel
    }
    ORDER_ITEMS {
        int order_item_id PK
        varchar order_id FK
        int product_id FK
        int quantity
        numeric line_revenue
        numeric line_cost
    }
```

## Grain

- `orders`: one row per order.
- `order_items`: one row per product within an order.
- `vw_sales_enriched`: one row per order item with order, customer, product, and category attributes.

The schema keeps category, product, customer, order, and item attributes in separate related tables. Analytical views provide a convenient denormalised surface without duplicating source entities.


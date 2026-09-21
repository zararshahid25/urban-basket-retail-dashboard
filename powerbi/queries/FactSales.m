let
    Source = PostgreSQL.Database(Server, Database),
    Data = Source{[Schema="retail", Item="sales_enriched"]}[Data],
    Typed = Table.TransformColumnTypes(Data, {{"order_date", type date}, {"order_month", type date}})
in
    Typed

let
    Source = PostgreSQL.Database(Server, Database),
    Data = Source{[Schema="retail", Item="dim_products"]}[Data]
in
    Data

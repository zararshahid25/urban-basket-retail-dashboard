let
    Source = PostgreSQL.Database(Server, Database),
    Data = Source{[Schema="retail", Item="customers"]}[Data],
    Typed = Table.TransformColumnTypes(Data, {{"signup_date", type date}})
in
    Typed

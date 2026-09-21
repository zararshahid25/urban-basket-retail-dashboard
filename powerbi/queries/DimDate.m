let
    Source = PostgreSQL.Database(Server, Database),
    Data = Source{[Schema="retail", Item="dim_date"]}[Data],
    Typed = Table.TransformColumnTypes(Data, {{"date", type date}, {"month", type date}})
in
    Typed

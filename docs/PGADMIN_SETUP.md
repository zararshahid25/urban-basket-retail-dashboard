# PostgreSQL and pgAdmin setup

## Option A: Docker Compose

1. Copy `.env.example` to `.env` and replace the two example passwords.
2. Start PostgreSQL and pgAdmin:

   ```bash
   docker compose up -d
   ```

3. Generate and prepare the CSVs:

   ```bash
   python -m src.generate_data
   python -m src.prepare_data
   ```

4. Set `DATABASE_URL` to match your `.env`, then load the tables:

   ```bash
   python -m src.load_postgres
   ```

5. Open pgAdmin at `http://localhost:5050` and sign in with the pgAdmin credentials in `.env`.
6. Register a server with host `postgres`, port `5432`, database `urban_basket`, and the PostgreSQL user/password from `.env`.

## Query order in pgAdmin

If you prefer running SQL manually, open the Query Tool and execute:

1. `sql/01_schema.sql`
2. import the five processed CSVs in relational order: categories, products, customers, orders, order_items;
3. `sql/02_indexes.sql`
4. `sql/03_views.sql`
5. `sql/05_data_quality_checks.sql`
6. individual questions from `sql/04_analysis_queries.sql`.

The data-quality queries should return no exception rows after a successful load.


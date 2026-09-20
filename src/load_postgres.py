"""Load prepared CSVs into PostgreSQL using the repository SQL schema."""

from __future__ import annotations

import os
from pathlib import Path

import psycopg


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data" / "processed"
SQL_DIR = PROJECT_ROOT / "sql"
TABLES = ["categories", "products", "customers", "orders", "order_items"]


def run_sql_file(connection: psycopg.Connection, path: Path) -> None:
    with connection.cursor() as cursor:
        cursor.execute(path.read_text(encoding="utf-8"))


def main() -> None:
    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql://urban_user:urban_dev_password@localhost:5432/urban_basket",
    )
    with psycopg.connect(database_url) as connection:
        run_sql_file(connection, SQL_DIR / "01_schema.sql")
        with connection.cursor() as cursor:
            for table in reversed(TABLES):
                cursor.execute(f"TRUNCATE TABLE {table} CASCADE")
            for table in TABLES:
                csv_path = DATA_DIR / f"{table}.csv"
                with csv_path.open("r", encoding="utf-8") as file:
                    columns = file.readline().strip().split(",")
                    file.seek(0)
                    column_sql = ", ".join(columns)
                    with cursor.copy(
                        f"COPY {table} ({column_sql}) FROM STDIN WITH (FORMAT CSV, HEADER TRUE)"
                    ) as copy:
                        while data := file.read(1024 * 1024):
                            copy.write(data)
        run_sql_file(connection, SQL_DIR / "02_indexes.sql")
        run_sql_file(connection, SQL_DIR / "03_views.sql")
        connection.commit()
    print("Loaded Urban Basket tables and views into PostgreSQL.")


if __name__ == "__main__":
    main()


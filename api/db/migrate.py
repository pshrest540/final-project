from pathlib import Path

from sqlalchemy import text

from api.db.session import engine


ROOT_DIR = Path(__file__).resolve().parents[2]
MIGRATIONS_DIR = ROOT_DIR / "supabase" / "migrations"


REQUIRED_PREDICTION_COLUMNS = [
    "cv_wellness",
    "wb_wellness",
    "brk_wellness",
    "bat_wellness",
    "alt_wellness",
    "sta_wellness",
    "coolant_wellness",
    "ignition_wellness",
    "fuel_wellness",
]

REQUIRED_COLUMNS = {
    "wellness_predictions": REQUIRED_PREDICTION_COLUMNS,
    "users": ["share_code"],
    "vehicles": ["share_enabled"],
}

REQUIRED_TABLES = ["business_customer_links"]


def run_migrations() -> None:
    migration_paths = sorted(MIGRATIONS_DIR.glob("*.sql"))
    if not migration_paths:
        raise FileNotFoundError(f"No migration files found in {MIGRATIONS_DIR}")

    for path in migration_paths:
        print(f"Running migration: {path}")
        sql = path.read_text(encoding="utf-8")
        raw_connection = engine.raw_connection()
        try:
            with raw_connection.cursor() as cursor:
                cursor.execute(sql)
            raw_connection.commit()
        except Exception:
            raw_connection.rollback()
            raise
        finally:
            raw_connection.close()


def verify_schema() -> list[str]:
    missing: list[str] = []
    with engine.connect() as conn:
        for table_name, required_columns in REQUIRED_COLUMNS.items():
            rows = conn.execute(
                text(
                    """
                select column_name
                from information_schema.columns
                where table_schema = 'public'
                  and table_name = :table_name
                """
                ),
                {"table_name": table_name},
            ).scalars()
            existing = set(rows)
            missing.extend(
                f"{table_name}.{column}"
                for column in required_columns
                if column not in existing
            )

        table_rows = conn.execute(
            text(
                """
                select table_name
                from information_schema.tables
                where table_schema = 'public'
                  and table_type = 'BASE TABLE'
                """
            )
        ).scalars()
        existing_tables = set(table_rows)
        missing.extend(
            f"{table_name} table"
            for table_name in REQUIRED_TABLES
            if table_name not in existing_tables
        )
    return missing


if __name__ == "__main__":
    run_migrations()
    missing = verify_schema()
    if missing:
        raise SystemExit(f"Migrations finished, but schema items are still missing: {missing}")
    print("Migration complete. Required app schema is present.")

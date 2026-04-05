"""
Seed script to populate the meals database with sample data.
Run: python backend/seed.py
"""

import argparse
import csv
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from models.database import get_db_connection
from pull import init_db

SEED_CSV_PATH = os.path.join(os.path.dirname(__file__), "data", "meals_seed.csv")
SEED_SQL_PATH = os.path.join(os.path.dirname(__file__), "data", "seed.sql")
BASE_REQUIRED_FIELDS = {
    "id",
    "name",
    "category",
    "instructions",
    "ingredients",
    "thumbnail",
}
SEED_COLUMNS = [
    "id",
    "name",
    "category",
    "instructions",
    "ingredients",
    "thumbnail",
    "estimated_price",
    "currency",
    "price_source",
    "price_last_updated",
]


def _parse_float(value):
    """Safely parse floats from CSV values."""
    text = (value or "").strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def _load_seed_from_csv(cursor):
    """Load seed data from CSV and upsert into meals table."""
    if not os.path.exists(SEED_CSV_PATH):
        return False

    inserted_rows = 0
    with open(SEED_CSV_PATH, "r", encoding="utf-8", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        if not BASE_REQUIRED_FIELDS.issubset(set(reader.fieldnames or [])):
            missing = sorted(BASE_REQUIRED_FIELDS - set(reader.fieldnames or []))
            raise ValueError(f"CSV seed file is missing fields: {', '.join(missing)}")

        for row in reader:
            cursor.execute(
                """
                INSERT OR REPLACE INTO meals (
                    id, name, category, instructions, ingredients, thumbnail,
                    estimated_price, currency, price_source, price_last_updated
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    (row.get("id") or "").strip(),
                    (row.get("name") or "").strip().lower(),
                    (row.get("category") or "").strip() or None,
                    (row.get("instructions") or "").strip() or None,
                    (row.get("ingredients") or "").strip() or None,
                    (row.get("thumbnail") or "").strip() or None,
                    _parse_float(row.get("estimated_price")),
                    (row.get("currency") or "").strip() or "USD",
                    (row.get("price_source") or "").strip() or None,
                    (row.get("price_last_updated") or "").strip() or None,
                ),
            )
            inserted_rows += 1

    print(f"Loaded {inserted_rows} rows from meals_seed.csv")
    return True


def _load_seed_from_sql(cursor):
    """Fallback loader for existing SQL seed script."""
    if not os.path.exists(SEED_SQL_PATH):
        return False

    with open(SEED_SQL_PATH, "r", encoding="utf-8") as sql_file:
        cursor.executescript(sql_file.read())

    print("Loaded seed data from seed.sql")
    return True


def export_seed_csv(csv_path=SEED_CSV_PATH):
    """Export meals from SQLite into a CSV seed file."""
    try:
        # Ensure schema exists before exporting.
        init_db()

        with get_db_connection() as conn:
            cursor = conn.cursor()
            rows = cursor.execute(
                """
                SELECT
                    id,
                    name,
                    category,
                    instructions,
                    ingredients,
                    thumbnail,
                    estimated_price,
                    currency,
                    price_source,
                    price_last_updated
                FROM meals
                ORDER BY name
                """
            ).fetchall()

        os.makedirs(os.path.dirname(csv_path), exist_ok=True)
        with open(csv_path, "w", encoding="utf-8", newline="") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(SEED_COLUMNS)
            for row in rows:
                writer.writerow([row[column] for column in SEED_COLUMNS])

        print(f"✅ Exported {len(rows)} rows to {csv_path}")
        return True
    except Exception as e:
        print(f"❌ Error exporting CSV: {e}")
        return False


def seed_database():
    """Seed meals data from CSV (preferred) or SQL fallback."""
    
    # Initialize the database schema first
    print("📋 Initializing database schema...")
    init_db()
    
    if not os.path.exists(SEED_CSV_PATH) and not os.path.exists(SEED_SQL_PATH):
        print(
            f"❌ No seed file found. Expected one of: {SEED_CSV_PATH} or {SEED_SQL_PATH}"
        )
        return False
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            loaded = _load_seed_from_csv(cursor)
            if not loaded:
                loaded = _load_seed_from_sql(cursor)

            if not loaded:
                print("❌ Failed to load seed data.")
                return False

            conn.commit()
            
            # Verify data was inserted
            cursor.execute("SELECT COUNT(*) as count FROM meals")
            count = cursor.fetchone()['count']
        
        print(f"✅ Database seeded successfully!")
        print(f"📊 Total meals in database: {count}")
        return True
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Seed meals DB from CSV/SQL or export DB meals to CSV."
    )
    parser.add_argument(
        "--export-csv",
        action="store_true",
        help="Export current meals table to backend/data/meals_seed.csv",
    )
    args = parser.parse_args()

    success = export_seed_csv() if args.export_csv else seed_database()
    sys.exit(0 if success else 1)

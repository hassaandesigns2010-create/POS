
from sqlalchemy import create_engine, text
from pos_app.database.connection import Database

def drop_deprecated_columns():
    db = Database()
    with db.engine.connect() as conn:
        print("Dropping deprecated columns...")
        try:
            conn.execute(text("ALTER TABLE products DROP COLUMN IF EXISTS warehouse_stock"))
            conn.execute(text("ALTER TABLE products DROP COLUMN IF EXISTS retail_stock"))
            conn.commit()
            print("[SUCCESS] Columns 'warehouse_stock' and 'retail_stock' dropped.")
        except Exception as e:
            print(f"[ERROR] Failed to drop columns: {e}")

if __name__ == "__main__":
    drop_deprecated_columns()

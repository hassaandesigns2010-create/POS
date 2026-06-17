
from sqlalchemy import create_engine, text
from pos_app.database.connection import Database

def check_stock_values():
    db = Database()
    with db.engine.connect() as conn:
        result = conn.execute(text("SELECT id, name, warehouse_stock, retail_stock, stock_level FROM products WHERE warehouse_stock > 0 OR retail_stock > 0 LIMIT 10"))
        rows = result.fetchall()
        print(f"{'ID':<5} {'Name':<30} {'WH':<10} {'Retail':<10} {'Level':<10}")
        for r in rows:
            print(f"{r[0]:<5} {r[1]:<30} {r[2]:<10} {r[3]:<10} {r[4]:<10}")

if __name__ == "__main__":
    check_stock_values()

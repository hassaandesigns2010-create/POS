
from sqlalchemy import create_engine, inspect
from pos_app.database.connection import Database

def check_columns():
    db = Database()
    inspector = inspect(db.engine)
    columns = [c['name'] for c in inspector.get_columns('products')]
    print("Columns in 'products' table:")
    for col in columns:
        print(f" - {col}")
    
    if 'warehouse_stock' in columns or 'retail_stock' in columns:
        print("\n[WARNING] Deprecated columns found!")
    else:
        print("\n[SUCCESS] No deprecated columns found.")

if __name__ == "__main__":
    check_columns()

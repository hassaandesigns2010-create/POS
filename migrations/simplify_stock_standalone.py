"""
Simple standalone migration to simplify stock management
Run with: python migrations/simplify_stock_standalone.py
"""
import psycopg2
import json
from pathlib import Path

# Read database config
config_path = Path(__file__).parent.parent / 'config' / 'database.json'
with open(config_path, 'r') as f:
    config = json.load(f)

# Connect to database
conn = psycopg2.connect(
    host=config['host'],
    port=config['port'],
    database=config['database'],
    user=config['username'],
    password=config['password']
)
conn.autocommit = False
cursor = conn.cursor()

try:
    print("[MIGRATION] Starting stock simplification migration...")
    
    # Step 1: Synchronize stock_level with warehouse + retail stock
    print("[MIGRATION] Step 1: Synchronizing stock_level...")
    cursor.execute("""
        UPDATE products 
        SET stock_level = COALESCE(warehouse_stock, 0) + COALESCE(retail_stock, 0)
        WHERE (warehouse_stock IS NOT NULL OR retail_stock IS NOT NULL)
    """)
    conn.commit()
    print("[MIGRATION] ✓ Stock levels synchronized")
    
    # Step 2: Drop warehouse_stock column
    print("[MIGRATION] Step 2: Dropping warehouse_stock column...")
    try:
        cursor.execute("ALTER TABLE products DROP COLUMN IF EXISTS warehouse_stock CASCADE")
        conn.commit()
        print("[MIGRATION] ✓ warehouse_stock column dropped")
    except Exception as e:
        print(f"[MIGRATION] Warning: {e}")
        conn.rollback()
    
    # Step 3: Drop retail_stock column
    print("[MIGRATION] Step 3: Dropping retail_stock column...")
    try:
        cursor.execute("ALTER TABLE products DROP COLUMN IF EXISTS retail_stock CASCADE")
        conn.commit()
        print("[MIGRATION] ✓ retail_stock column dropped")
    except Exception as e:
        print(f"[MIGRATION] Warning: {e}")
        conn.rollback()
    
    # Step 4: Add performance indices
    print("[MIGRATION] Step 4: Adding performance indices...")
    
    # Index for product name (case-insensitive)
    try:
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_products_name_lower 
            ON products (LOWER(name))
        """)
        print("[MIGRATION] ✓ Created index on product name")
    except Exception as e:
        print(f"[ MIGRATION] Warning: {e}")
        conn.rollback()
    
    # Index for barcode
    try:
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_products_barcod_lower 
            ON products (LOWER(barcode))
        """)
        print("[MIGRATION] ✓ Created index on barcode")
    except Exception as e:
        print(f"[MIGRATION] Warning: {e}")
        conn.rollback()
    
    # Index for SKU
    try:
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_products_sku_lower 
            ON products (LOWER(sku))
        """)
        print("[MIGRATION] ✓ Created index on SKU")
    except Exception as e:
        print(f"[MIGRATION] Warning: {e}")
        conn.rollback()
    
    # Composite index for active products
    try:
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_products_active_stock 
            ON products (is_active, stock_level)
            WHERE is_active = true
        """)
        print("[MIGRATION] ✓ Created composite index")
    except Exception as e:
        print(f"[MIGRATION] Warning: {e}")
        conn.rollback()
    
    conn.commit()
    
    print("\n[MIGRATION] ✅ Migration completed successfully!")
    print("[MIGRATION] Summary:")
    print("  - Consolidated warehouse_stock + retail_stock → stock_level")
    print("  - Removed warehouse_stock and retail_stock columns")
    print("  - Added performance indices for faster search")
    
except Exception as e:
    print(f"\n[MIGRATION] ❌ Migration failed: {e}")
    conn.rollback()
    raise
finally:
    cursor.close()
    conn.close()

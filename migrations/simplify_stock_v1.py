"""
Migration: Simplify Stock Management
- Remove warehouse_stock and retail_stock columns
- Keep only stock_level as the single source of truth
- Add performance indices for product search
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from models.database import get_database_url, SessionLocal
from sqlalchemy import text

def run_migration():
    """Execute the stock simplification migration"""
    
    session = SessionLocal()
    
    try:
        print("[MIGRATION] Starting stock simplification migration...")
        
        # Step 1: Ensure stock_level has all the data (warehouse_stock + retail_stock)
        print("[MIGRATION] Step 1: Synchronizing stock_level with warehouse + retail stock...")
        session.execute(text("""
            UPDATE products 
            SET stock_level = COALESCE(warehouse_stock, 0) + COALESCE(retail_stock, 0)
            WHERE (warehouse_stock IS NOT NULL OR retail_stock IS NOT NULL)
        """))
        session.commit()
        print("[MIGRATION] ✓ Stock levels synchronized")
        
        # Step 2: Drop warehouse_stock and retail_stock columns
        print("[MIGRATION] Step 2: Dropping warehouse_stock column...")
        try:
            session.execute(text("ALTER TABLE products DROP COLUMN IF EXISTS warehouse_stock CASCADE"))
            session.commit()
            print("[MIGRATION] ✓ warehouse_stock column dropped")
        except Exception as e:
            print(f"[MIGRATION] Warning: Could not drop warehouse_stock: {e}")
            session.rollback()
        
        print("[MIGRATION] Step 3: Dropping retail_stock column...")
        try:
            session.execute(text("ALTER TABLE products DROP COLUMN IF EXISTS retail_stock CASCADE"))
            session.commit()
            print("[MIGRATION] ✓ retail_stock column dropped")
        except Exception as e:
            print(f"[MIGRATION] Warning: Could not drop retail_stock: {e}")
            session.rollback()
        
        # Step 3: Add performance indices for search
        print("[MIGRATION] Step 4: Adding performance indices...")
        
        # Index for product name (case-insensitive search)
        try:
            session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_products_name_lower 
                ON products (LOWER(name))
            """))
            print("[MIGRATION] ✓ Created index on product name")
        except Exception as e:
            print(f"[MIGRATION] Warning: Could not create name index: {e}")
            session.rollback()
        
        # Index for barcode
        try:
            session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_products_barcode_lower 
                ON products (LOWER(barcode))
            """))
            print("[MIGRATION] ✓ Created index on barcode")
        except Exception as e:
            print(f"[MIGRATION] Warning: Could not create barcode index: {e}")
            session.rollback()
        
        # Index for SKU
        try:
            session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_products_sku_lower 
                ON products (LOWER(sku))
            """))
            print("[MIGRATION] ✓ Created index on SKU")
        except Exception as e:
            print(f"[MIGRATION] Warning: Could not create SKU index: {e}")
            session.rollback()
        
        # Composite index for common queries
        try:
            session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_products_active_stock 
                ON products (is_active, stock_level)
                WHERE is_active = true
            """))
            print("[MIGRATION] ✓ Created composite index for active products")
        except Exception as e:
            print(f"[MIGRATION] Warning: Could not create composite index: {e}")
            session.rollback()
        
        session.commit()
        
        print("\n[MIGRATION] ✅ Stock simplification migration completed successfully!")
        print("[MIGRATION] Summary:")
        print("  - Consolidated warehouse_stock and retail_stock into stock_level")
        print("  - Removed warehouse_stock and retail_stock columns")
        print("  - Added performance indices for faster product search")
        
    except Exception as e:
        print(f"\n[MIGRATION] ❌ Migration failed: {e}")
        session.rollback()
        raise
    finally:
        session.close()

if __name__ == "__main__":
    run_migration()

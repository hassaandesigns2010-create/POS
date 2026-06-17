
import os
import sys
import logging
from datetime import datetime
from sqlalchemy import text

# Add current directory to path so we can import pos_app
sys.path.append(os.getcwd())

try:
    from pos_app.database.connection import Database
    from pos_app.models.database import Product
except ImportError:
    # Try parent directory if running from f:\pos_app
    sys.path.append(os.path.dirname(os.getcwd()))
    from pos_app.database.connection import Database
    from pos_app.models.database import Product

def run_cleanup():
    print("--- Database Cleanup Utility ---")
    print(f"Time: {datetime.now()}")
    
    try:
        db = Database()
        # Connect to engine directly to run DDL
        with db.engine.connect() as conn:
            print("1. Checking for deprecated columns...")
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            columns = [c['name'] for c in inspector.get_columns('products')]
            
            to_drop = [c for c in ['warehouse_stock', 'retail_stock'] if c in columns]
            
            if not to_drop:
                print("   ✅ No deprecated columns found.")
            else:
                print(f"   ⚠️ Found deprecated columns: {', '.join(to_drop)}")
                print("   🚀 Attempting to drop columns (this requires no other active connections)...")
                try:
                    for col in to_drop:
                        conn.execute(text(f"ALTER TABLE products DROP COLUMN IF EXISTS {col}"))
                    conn.commit()
                    print("   ✅ Successfully removed deprecated columns.")
                except Exception as e:
                    print(f"   ❌ FAILED to drop columns: {e}")
                    print("   💡 TIP: Close the POS application on ALL PCs before running this cleanup.")

            print("\n2. Verifying Stock Levels...")
            total_zero = conn.execute(text("SELECT COUNT(*) FROM products WHERE stock_level = 0")).scalar()
            total_prod = conn.execute(text("SELECT COUNT(*) FROM products")).scalar()
            print(f"   📊 Products with zero stock: {total_zero} out of {total_prod}")
            
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")

if __name__ == "__main__":
    run_cleanup()

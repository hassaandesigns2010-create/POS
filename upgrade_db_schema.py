
import logging
import sys
import os
# Add parent directory (f:/) to path so we can import 'pos_app'
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sqlalchemy import text
from pos_app.database.connection import Database

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('SchemaUpgrade')

def upgrade_schema():
    logger.info("Starting database schema upgrade to Numeric types...")
    db = Database()
    session = db.session
    
    try:
        # Terminate other connections to release locks
        try:
            logger.info("🔪 Terminating other connections to ensure exclusive access...")
            session.execute(text("SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'pos_network' AND pid <> pg_backend_pid()"))
            session.commit()
            logger.info("✅ Connections terminated")
        except Exception as e:
            logger.warning(f"⚠️ Could not terminate connections: {e}")

        # Check current state first (optional, but good for logging)
        
        # Define ALTER statements
        statements = [
            # Products
            "ALTER TABLE products ALTER COLUMN stock_level TYPE NUMERIC(12, 4)",
            "ALTER TABLE products ALTER COLUMN retail_price TYPE NUMERIC(12, 2)",
            "ALTER TABLE products ALTER COLUMN wholesale_price TYPE NUMERIC(12, 2)",
            "ALTER TABLE products ALTER COLUMN purchase_price TYPE NUMERIC(12, 2)",
            
            # Sales
            "ALTER TABLE sales ALTER COLUMN total_amount TYPE NUMERIC(12, 2)",
            
            # Sale Items
            "ALTER TABLE sale_items ALTER COLUMN quantity TYPE NUMERIC(12, 4)",
            "ALTER TABLE sale_items ALTER COLUMN unit_price TYPE NUMERIC(12, 2)",
            "ALTER TABLE sale_items ALTER COLUMN total TYPE NUMERIC(12, 2)",
            
            # Purchases
            "ALTER TABLE purchases ALTER COLUMN total_amount TYPE NUMERIC(12, 2)",
             "ALTER TABLE purchases ALTER COLUMN paid_amount TYPE NUMERIC(12, 2)",
            
            # Purchase Items
            "ALTER TABLE purchase_items ALTER COLUMN quantity TYPE NUMERIC(12, 4)",
            "ALTER TABLE purchase_items ALTER COLUMN unit_cost TYPE NUMERIC(12, 2)",
            "ALTER TABLE purchase_items ALTER COLUMN total_cost TYPE NUMERIC(12, 2)",

            # Expenses
            "ALTER TABLE expenses ALTER COLUMN amount TYPE NUMERIC(12, 2)",

            # Payments
            "ALTER TABLE payments ALTER COLUMN amount TYPE NUMERIC(12, 2)",
            "ALTER TABLE purchase_payments ALTER COLUMN amount TYPE NUMERIC(12, 2)",
            
            # Cash Drawer
             "ALTER TABLE cash_drawer_sessions ALTER COLUMN opening_balance TYPE NUMERIC(12, 2)",
             "ALTER TABLE cash_drawer_sessions ALTER COLUMN closing_balance TYPE NUMERIC(12, 2)",
             "ALTER TABLE cash_movements ALTER COLUMN amount TYPE NUMERIC(12, 2)",
        ]
        
        for stmt in statements:
            try:
                logger.info(f"Executing: {stmt}")
                session.execute(text(stmt))
                session.commit()
                logger.info("✅ Success")
            except Exception as e:
                session.rollback()
                logger.warning(f"⚠️ Failed (might already be correct or table missing): {e}")
        
        logger.info("Schema upgrade completed.")
        return True
    except Exception as e:
        logger.error(f"❌ Critical error during upgrade: {e}")
        return False
    finally:
        session.close()

if __name__ == "__main__":
    upgrade_schema()

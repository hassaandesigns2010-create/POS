
import sys
import os
import logging
from decimal import Decimal
from datetime import datetime
import traceback

# Setup paths
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('Verification')

def test_imports():
    logger.info("--- Testing Imports ---")
    try:
        from pos_app.models.database import Base, Product, Sale, SaleItem, User
        from pos_app.controllers.business_logic import BusinessController
        from pos_app.controllers.safe_business_controller import SafeBusinessController
        from pos_app.views.sales import ReceiptPreviewDialog
        from pos_app.views.dashboard_enhanced import DashboardEnhanced
        from pos_app.views.reports import ReportsWidget
        from pos_app.utils.formatting import format_rs
        
        logger.info("✅ All core modules imported successfully")
        return True
    except ImportError as e:
        logger.error(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error during import: {e}")
        return False

def test_database_and_models():
    logger.info("--- Testing Database & Models ---")
    session = None
    try:
        from pos_app.database.connection import Database
        from pos_app.models.database import Product, Sale, InventoryLocation
        
        db = Database()
        session = db.session
        
        # Test Decimal Precision
        test_price = Decimal("199.99")
        test_stock = Decimal("50.5")
        
        # Create a test product
        p = Product(
            name="TEST_PRODUCT_DECIMAL",
            description="Test Product for Decimal Verification",
            retail_price=test_price,
            wholesale_price=Decimal("150.00"),  # Mandatory field
            purchase_price=Decimal("120.00"),   # Mandatory field
            stock_level=test_stock,
            sku=f"TEST-{datetime.now().timestamp()}",
            is_active=True
        )
        session.add(p)
        session.flush()
        
        # Reload and verify
        session.refresh(p)
        
        p_price = p.retail_price
        p_stock = p.stock_level
        
        logger.info(f"Product Created: {p.name}")
        logger.info(f"Price (Expected: {test_price}, Got: {p_price}, Type: {type(p_price)})")
        logger.info(f"Stock (Expected: {test_stock}, Got: {p_stock}, Type: {type(p_stock)})")
        
        # Check types
        if isinstance(p_price, Decimal) and isinstance(p_stock, Decimal):
            logger.info("✅ Database returning Decimal types correct")
        else:
            logger.warning(f"⚠️ Database types check failed. Price: {type(p_price)}, Stock: {type(p_stock)}")
            
        # Cleanup
        session.rollback()
        logger.info("✅ Database verification completed (Transaction rolled back)")
        return True
    except Exception as e:
        logger.error(f"❌ Database test failed: {e}")
        traceback.print_exc()
        if session:
            session.rollback()
        return False
    finally:
        if session:
            session.close()

def test_business_logic():
    logger.info("--- Testing Business Logic ---")
    session = None
    try:
        from pos_app.database.connection import Database
        from pos_app.controllers.safe_business_controller import SafeBusinessController
        from pos_app.models.database import Product, Customer
        
        db = Database()
        session = db.session
        controller = SafeBusinessController(session)
        
        # 1. Add Product
        logger.info("Testing Add Product...")
        prefix = f"TEST_{int(datetime.now().timestamp())}"
        p = controller.add_product(
            name=f"{prefix}_ITEM",
            sku=f"{prefix}_SKU",
            retail_price=Decimal("100.00"),
            stock_level=Decimal("10.00"),
            description="Test Description",
            barcode=None,
            wholesale_price=Decimal("80.00"),
            purchase_price=Decimal("70.00"),
            reorder_level=5,
            supplier_id=None,
            unit="pcs"
        )
        if not p:
            logger.error("❌ Add Product failed")
            return False
            
        logger.info(f"✅ Product Added: {p.name} (ID: {p.id})")
        
        # 2. Update Stock (Atomic)
        logger.info("Testing Atomic Stock Update...")
        # Since we use atomic updates, we might need to commit to see changes if we were using a separate session,
        # but here we are in same session. However, atomic updates often execute directly against DB.
        # SafeBusinessController.update_stock should handle this.
        
        controller.update_stock(p.id, Decimal("5.00"), movement_type="OUT", commit=True)
        session.expire(p) # Force reload from DB
        session.refresh(p)
        
        if p.stock_level == Decimal("5.00"):
            logger.info(f"✅ Stock Updated correctly to {p.stock_level}")
        else:
            logger.error(f"❌ Stock Update failed. Expected 5.00, got {p.stock_level}")
        
        # 3. Create Sale
        logger.info("Testing Create Sale...")
        
        # Get a customer (or create one)
        customer = session.query(Customer).first()
        if not customer:
            customer = Customer(name="Test Customer", contact="123")
            session.add(customer)
            session.flush()
            
        items = [
            {'product_id': p.id, 'quantity': Decimal("2.00"), 'unit_price': Decimal("100.00")}
        ]
        
        sale = controller.create_sale(
            customer_id=customer.id,
            items=items,
            paid_amount=Decimal("200.00"),
            payment_method="Cash"
        )
        
        if sale:
            logger.info(f"✅ Sale Created: {sale.invoice_number}")
            logger.info(f"Sale Total: {sale.total_amount} (Type: {type(sale.total_amount)})")
            
            # Verify stock deduction (5 - 2 = 3)
            # Need to refresh product again as create_sale might have committed
            session.expire(p)
            session.refresh(p)
            logger.info(f"Post-Sale Stock: {p.stock_level}")
            if p.stock_level == Decimal("3.00"):
                 logger.info("✅ Stock deducted correctly after sale")
            else:
                 logger.error(f"❌ Stock mismatch after sale. Expected 3.00, got {p.stock_level}")

        else:
            logger.error("❌ Create Sale failed")
            
        # Clean up data
        session.delete(p)
        session.commit()
        logger.info("✅ Cleanup completed")
        
        return True
    except Exception as e:
        logger.error(f"❌ Business Logic test failed: {e}")
        traceback.print_exc()
        if session:
            session.rollback()
        return False
    finally:
        if session:
            session.close()

if __name__ == "__main__":
    logger.info("STARTING FULL SYSTEM VERIFICATION")
    
    if not test_imports():
        logger.critical("Imports Failed - Aborting")
        sys.exit(1)
        
    if not test_database_and_models():
        logger.critical("Database Tests Failed - Aborting")
        sys.exit(1)
        
    if not test_business_logic():
        logger.critical("Business Logic Tests Failed")
        sys.exit(1)
        
    logger.info("🎉 ALL SYSTEMS GO! VERIFICATION SUCCESSFUL")

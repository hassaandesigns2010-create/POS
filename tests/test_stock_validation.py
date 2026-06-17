"""Reliable stock validation tests with proper isolation"""
import pytest
from pos_app.models.database import Product

# Use existing controller fixture
pytestmark = pytest.mark.usefixtures("business_controller")

class TestStockValidation:
    """Stock validation tests with fresh product per test"""
    
    @pytest.fixture
    def test_product(self, business_controller):
        """Create fresh test product"""
        product = Product(
            name="Test Product",
            retail_price=100.0,
            wholesale_price=80.0,
            purchase_price=60.0,
            retail_stock=10,
            warehouse_stock=20,
            stock_level=30,
            is_active=True
        )
        business_controller.session.add(product)
        business_controller.session.commit()
        yield product
        # Teardown
        business_controller.session.delete(product)
        business_controller.session.commit()
    
    def test_stock_reduction(self, business_controller, test_product):
        """Test valid stock reduction"""
        items = [{'product_id': test_product.id, 'quantity': 2, 'unit_price': 100}]
        sale = business_controller.create_sale(None, items)
        assert sale is not None
        
        # Verify stock updated
        business_controller.session.commit()
        updated = business_controller.session.query(Product).get(test_product.id)
        assert updated.retail_stock == 8
    
    def test_insufficient_stock(self, business_controller, test_product):
        """Test insufficient stock validation"""
        items = [{'product_id': test_product.id, 'quantity': 50, 'unit_price': 100}]
        with pytest.raises(ValueError, match="Stock validation failed"):
            business_controller.create_sale(None, items)
        
        # Verify stock unchanged
        unchanged = business_controller.session.query(Product).get(test_product.id)
        assert unchanged.retail_stock == 10

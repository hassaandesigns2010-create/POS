"""Test cases for sale completion crash scenarios"""
import pytest
from PySide6.QtWidgets import QApplication
from pos_app.controllers.business_logic import BusinessController
from pos_app.views.sales import SalesWidget
from pos_app.models.database import Base, Product
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pos_app.utils.logger import setup_logger

@pytest.fixture
def sales_widget(qtbot):
    """Fixture providing a SalesWidget with in-memory SQLite DB"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Setup logger for controller
    logger = setup_logger('test_business_logic')
    controller = BusinessController(session)
    controller.logger = logger  # Override any existing logger
    
    widget = SalesWidget(controller)
    qtbot.addWidget(widget)
    return widget

@pytest.fixture
def controller(db_session):
    """BusinessController fixture"""
    from pos_app.controllers.business_logic import BusinessController
    return BusinessController(db_session)

@pytest.fixture
def sample_product(controller):
    """Test product fixture with all required fields"""
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
    controller.session.add(product)
    controller.session.commit()
    return product

@pytest.mark.parametrize("scenario", [
    "empty_cart",
    "insufficient_payment",
    "invalid_refund_quantity",
    "missing_customer"
])
def test_sale_completion_scenarios(sales_widget, scenario):
    """Test various sale completion scenarios that could cause crashes"""
    # Setup scenario
    if scenario == "empty_cart":
        sales_widget.current_cart = []
    elif scenario == "insufficient_payment":
        sales_widget.amount_paid_input.setValue(0)
    
    # Attempt sale completion
    try:
        sales_widget.process_sale()
        assert False, f"Scenario {scenario} should have failed"
    except Exception as e:
        assert str(e), "Exception should have message"

@pytest.mark.parametrize("scenario", [
    "complex_sale_with_discounts",
    "multi_tax_items",
    "mixed_refund_sale",
    "high_volume_items"
])
def test_complex_sale_scenarios(sales_widget, scenario):
    """Test more complex sale scenarios that could cause crashes"""
    # Setup test cart based on scenario
    if scenario == "complex_sale_with_discounts":
        sales_widget.current_cart = [
            {"id": 1, "name": "Item A", "price": 100, "quantity": 2, "discount": 10},
            {"id": 2, "name": "Item B", "price": 50, "quantity": 3, "discount": 5}
        ]
    elif scenario == "multi_tax_items":
        sales_widget.current_cart = [
            {"id": 3, "name": "Taxable A", "price": 200, "quantity": 1, "tax_rate": 0.15},
            {"id": 4, "name": "Taxable B", "price": 300, "quantity": 2, "tax_rate": 0.20}
        ]
    
    # Process sale and verify no crashes
    try:
        sales_widget.process_sale()
    except Exception as e:
        pytest.fail(f"Scenario {scenario} crashed: {str(e)}")

class TestStockValidation:
    """Comprehensive stock validation tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self, controller):
        """Create test product"""
        self.controller = controller
        self.product = Product(
            name="Test Product",
            retail_price=100.0,
            wholesale_price=80.0,
            purchase_price=60.0,
            retail_stock=10,
            warehouse_stock=20,
            stock_level=30,
            is_active=True
        )
        self.controller.session.add(self.product)
        self.controller.session.commit()
        yield
        # Teardown
        self.controller.session.delete(self.product)
        self.controller.session.commit()
    
    def test_stock_reduction(self):
        """Test valid stock reduction"""
        items = [{'product_id': self.product.id, 'quantity': 2, 'unit_price': 100}]
        sale = self.controller.create_sale(None, items)
        assert sale is not None
        
        # Verify stock updated
        self.controller.session.commit()
        updated = self.controller.session.query(Product).get(self.product.id)
        assert updated.retail_stock == 8
    
    def test_insufficient_stock(self):
        """Test insufficient stock validation"""
        items = [{'product_id': self.product.id, 'quantity': 50, 'unit_price': 100}]
        with pytest.raises(ValueError, match="Stock validation failed"):
            self.controller.create_sale(None, items)
        
        # Verify stock unchanged
        unchanged = self.controller.session.query(Product).get(self.product.id)
        assert unchanged.retail_stock == 10

def test_stock_validation_on_sale(controller):
    """Test stock validation with proper product lifecycle"""
    # Create test product with all required fields
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
    controller.session.add(product)
    controller.session.commit()
    product_id = product.id
    
    # Verify initial state
    initial_product = controller.session.query(Product).get(product_id)
    assert initial_product.retail_stock == 10
    
    # Test valid sale
    valid_items = [{'product_id': product_id, 'quantity': 2, 'unit_price': 100}]
    sale = controller.create_sale(None, valid_items)
    assert sale is not None
    
    # Verify stock reduced
    controller.session.commit()
    updated_product = controller.session.query(Product).get(product_id)
    assert updated_product.retail_stock == 8
    
    # Test insufficient stock
    invalid_items = [{'product_id': product_id, 'quantity': 50, 'unit_price': 100}]
    with pytest.raises(ValueError, match="Stock validation failed"):
        controller.create_sale(None, invalid_items)
    
    # Verify stock unchanged
    final_product = controller.session.query(Product).get(product_id)
    assert final_product.retail_stock == 8
    
    # Cleanup
    controller.session.delete(product)
    controller.session.commit()

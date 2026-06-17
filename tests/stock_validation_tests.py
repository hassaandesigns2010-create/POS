"""Reliable stock validation tests"""
import pytest
from pos_app.models.database import Product

def test_stock_reduction(business_controller):
    """Test valid stock reduction"""
    # Create test product
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
    
    # Test sale
    items = [{'product_id': product.id, 'quantity': 2, 'unit_price': 100}]
    sale = business_controller.create_sale(None, items)
    assert sale is not None
    
    # Verify stock
    updated = business_controller.session.query(Product).get(product.id)
    assert updated.retail_stock == 8

def test_insufficient_stock(business_controller):
    """Test insufficient stock validation"""
    # Create test product
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
    
    # Test sale with insufficient stock
    items = [{'product_id': product.id, 'quantity': 50, 'unit_price': 100}]
    with pytest.raises(ValueError, match="Stock validation failed"):
        business_controller.create_sale(None, items)

def test_reconcile_negative_stock(business_controller):
    """Test negative stock reconciliation with proper verification"""
    # Create test products with all required fields
    product1 = Product(
        name="Negative Retail",
        retail_price=100.0,
        wholesale_price=80.0,
        purchase_price=60.0,
        retail_stock=-5,
        warehouse_stock=10,
        stock_level=5,
        is_active=True
    )
    product2 = Product(
        name="Negative Warehouse",
        retail_price=100.0,
        wholesale_price=80.0,
        purchase_price=60.0,
        retail_stock=10,
        warehouse_stock=-3,
        stock_level=7,
        is_active=True
    )
    product3 = Product(
        name="Negative Both",
        retail_price=100.0,
        wholesale_price=80.0,
        purchase_price=60.0,
        retail_stock=-2,
        warehouse_stock=-1,
        stock_level=-3,
        is_active=True
    )
    
    business_controller.session.add_all([product1, product2, product3])
    business_controller.session.commit()
    
    # Run reconciliation
    fixed_count = business_controller.reconcile_negative_stock()
    assert fixed_count == 3
    
    # Refresh and verify
    business_controller.session.commit()
    
    updated1 = business_controller.session.query(Product).get(product1.id)
    assert updated1.retail_stock == 0
    assert updated1.stock_level == 10
    
    updated2 = business_controller.session.query(Product).get(product2.id)
    assert updated2.warehouse_stock == 0
    assert updated2.stock_level == 10
    
    updated3 = business_controller.session.query(Product).get(product3.id)
    assert updated3.retail_stock == 0
    assert updated3.warehouse_stock == 0
    assert updated3.stock_level == 0

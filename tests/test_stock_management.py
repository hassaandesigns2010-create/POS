"""Tests for stock management and negative value prevention"""
import pytest
from pos_app.controllers.business_logic import BusinessController
from pos_app.models.database import Product, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime

@pytest.fixture
def db_session():
    """Test database session fixture with valid Product"""
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Create valid Product with all required fields
    product = Product(
        name="Test Product",
        product_type="SIMPLE",
        retail_price=100.0,
        wholesale_price=80.0,
        purchase_price=60.0,
        retail_stock=10,
        warehouse_stock=20,
        stock_level=30,
        created_at=datetime.datetime.now(),
        updated_at=datetime.datetime.now()
    )
    session.add(product)
    session.commit()
    
    yield session
    session.close()

@pytest.fixture
def controller(db_session):
    """BusinessController fixture"""
    return BusinessController(db_session)

def test_normal_stock_reduction(controller):
    """Test normal stock reduction"""
    product = controller.session.query(Product).first()
    
    # Reduce stock by 5
    assert controller.update_stock(product.id, 5, 'OUT') == True
    
    # Verify updated stock
    controller.session.refresh(product)
    assert product.retail_stock == 5
    assert product.stock_level == 25

def test_insufficient_stock(controller):
    """Test attempt to reduce beyond available stock"""
    product = controller.session.query(Product).first()
    
    with pytest.raises(ValueError) as e:
        controller.update_stock(product.id, 50, 'OUT')
    
    assert "Insufficient stock" in str(e.value)

def test_negative_input_prevention(controller):
    """Test that negative quantities are rejected immediately"""
    # Test direct negative input
    with pytest.raises(ValueError, match="must be positive"):
        controller.update_stock(1, -5, 'OUT')
    
    # Test zero quantity
    with pytest.raises(ValueError, match="must be positive"):
        controller.update_stock(1, 0, 'OUT')

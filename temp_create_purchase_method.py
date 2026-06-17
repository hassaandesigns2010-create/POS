def create_purchase(self, supplier_id, items):
    """Create a purchase order and update stock levels
    
    Args:
        supplier_id: ID of the supplier
        items: List of dicts with keys: product_id, quantity, unit_cost
        
    Returns:
        Purchase object
    """
    try:
        from pos_app.models.database import Purchase, PurchaseItem, Product
        
        # Validate inputs
        if not supplier_id:
            raise ValueError("Supplier ID is required")
        if not items or len(items) == 0:
            raise ValueError("At least one item is required")
        
        # Calculate totals
        total_amount = sum(item['quantity'] * item['unit_cost'] for item in items)
        
        # Generate purchase number
        purchase_number = self.generate_code('PO')
        
        # Create purchase
        purchase = Purchase(
            supplier_id=supplier_id,
            purchase_number=purchase_number,
            total_amount=total_amount,
            paid_amount=0.0,
            tax_amount=0.0,
            discount_amount=0.0,
            status='ORDERED',
            order_date=datetime.now()
        )
        
        self.session.add(purchase)
        self.session.flush()  # Get purchase ID
        
        # Create purchase items and update stock
        for item in items:
            product_id = item['product_id']
            quantity = item['quantity']
            unit_cost = item['unit_cost']
            
            # Create purchase item
            purchase_item = PurchaseItem(
                purchase_id=purchase.id,
                product_id=product_id,
                quantity=quantity,
                unit_cost=unit_cost,
                total_cost=quantity * unit_cost,
                received_quantity=quantity  # Mark as received immediately
            )
            self.session.add(purchase_item)
            
            # Update product stock
            product = self.session.get(Product, product_id)
            if product:
                # Increase stock level
                from decimal import Decimal
                current_stock = Decimal(str(product.stock_level or 0))
                new_stock = current_stock + Decimal(str(quantity))
                product.stock_level = new_stock
                
                # Update purchase price
                product.purchase_price = unit_cost
        
        # Mark purchase as received
        purchase.status = 'RECEIVED'
        purchase.delivery_date = datetime.now()
        
        self.session.commit()
        return purchase
        
    except Exception as e:
        self.session.rollback()
        raise ValueError(f"Purchase creation failed: {str(e)}")

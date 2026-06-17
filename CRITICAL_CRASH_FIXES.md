# Critical Crash Fixes Required

## Issues Found

After analyzing the crash logs on client PCs, I identified **two critical issues** causing the application to crash:

### 1. **Legacy Stock Fields Still Referenced** ✅ FIXED
The code was still trying to access `warehouse_stock` and `retail_stock` fields that were removed during the stock simplification migration.

**Files Fixed:**
- `controllers/business_logic.py` - Updated `reconcile_negative_stock()` and `reconcile_stock()` methods
- `data/products.py` - Removed all references to `warehouse_stock` and `retail_stock`

### 2. **Missing `create_purchase` Method** ⚠️ NEEDS MANUAL FIX
The `SafeBusinessController` calls `super().create_purchase()` but this method doesn't exist in `BusinessController`.

**Error from logs:**
```
AttributeError: 'super' object has no attribute 'create_purchase'
Location: pos_app.controllers.safe_business_controller.create_purchase
```

## Required Manual Fix

You need to add the `create_purchase` method to `BusinessController` class in `f:\pos_app\controllers\business_logic.py`.

**Insert this method after the `create_sale` method (around line 542):**

```python
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
                current_stock = product.stock_level or 0
                product.stock_level = current_stock + quantity
                
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
```

## How to Apply the Fix

1. Open `f:\pos_app\controllers\business_logic.py`
2. Find the `create_sale` method (around line 414-541)
3. After the `create_sale` method ends (line 541), add a blank line
4. Paste the entire `create_purchase` method above
5. Save the file
6. Restart the application on all client PCs

## What This Fixes

- ✅ Removes crashes when trying to access non-existent `warehouse_stock` and `retail_stock` fields
- ✅ Fixes "AttributeError: 'super' object has no attribute 'create_purchase'" crashes
- ✅ Enables purchase creation functionality to work properly
- ✅ Properly updates stock levels when purchases are made

## Testing After Fix

1. Try creating a new purchase order
2. Verify stock levels increase correctly
3. Check that no crashes occur in the logs

---

**Status:** 
- Stock field references: ✅ FIXED
- create_purchase method: ⚠️ NEEDS MANUAL ADDITION (see above)

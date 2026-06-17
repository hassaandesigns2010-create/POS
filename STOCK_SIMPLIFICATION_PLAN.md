# Stock Simplification & Performance Fix Plan

## Problem 1: Stock Complexity
Currently the app uses:
- `warehouse_stock` 
- `retail_stock`
- `stock_level` (should be warehouse_stock + retail_stock)

This is confusing. We need **ONE unified stock field: `stock_level`**

## Problem 2: Performance Issues
Search fields cause application to freeze/crash for 3-7 minutes on some client PCs.

### Root Causes:
1. **Missing Database Indices** - Product searches on name/SKU/barcode without proper indices
2. **Inefficient Queries** - Every keystroke triggers full database scan
3. **No Query Optimization** - Loading too much data at once
4. **UI Thread Blocking** - Database queries run on main UI thread

## Solutions

### Part 1: Stock Simplification
1. Create migration to:
   - Drop `warehouse_stock` and `retail_stock` columns
   - Keep only `stock_level`
   - Update existing code to use `stock_level` everywhere

2. Update all Python code:
   - Remove all references to `warehouse_stock` and `retail_stock`
   - Use only `stock_level`
   - Update UI labels and displays

### Part 2: Performance Optimization
1. **Add Database Indices**:
   ```sql
   CREATE INDEX IF NOT EXISTS idx_products_name_trgm ON products USING gin(name gin_trgm_ops);
   CREATE INDEX IF NOT EXISTS idx_products_barcode ON products(barcode);
   CREATE INDEX IF NOT EXISTS idx_products_sku ON products(sku);
   ```

2. **Optimize Search Queries**:
   - Increase debounce delay to 300ms (from 150ms)
   - Limit results to 15 items max
   - Use indexed columns first in WHERE clause
   - Add `EXPLAIN ANALYZE` to identify slow queries

3. **Add Query Caching**:
   - Cache product list for 30 seconds
   - Invalidate cache on product add/edit/delete

4. **Async Search** (if needed):
   - Move database queries to background thread
   - Update UI when results ready

## Files to Modify

### Database:
- `models/database.py` - Remove warehouse_stock, retail_stock columns
- Create migration script

### Views (Remove warehouse/retail stock references):
- `views/inventory.py`
- `views/inventory_new.py`
- `views/sales.py`
- `views/warehouse_retail_inventory.py`
- `views/simple_product_dialog.py`
- `views/search_system.py`
- `views/customers.py`
- `views/suppliers.py`

### Controllers:
- `controllers/business_logic.py` - Update stock logic

### Tests:
- Update all test files that reference warehouse/retail stock

## Implementation Order
1. Create database migration
2. Update models/database.py
3. Update controllers
4. Update views (one by one)
5. Add performance optimizations
6. Test thoroughly

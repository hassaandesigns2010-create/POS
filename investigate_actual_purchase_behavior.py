#!/usr/bin/env python3
"""
Investigate actual purchase behavior - stock IS updating
"""

import os
import sys
import psycopg2
import json
from datetime import datetime

def load_db_config():
    """Load database configuration"""
    config_file = os.path.join(os.path.dirname(__file__), 'config', 'database.json')
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except:
        return {
            'host': 'localhost',
            'port': 5432,
            'database': 'pos_network',
            'username': 'postgres',
            'password': 'admin'
        }

def connect_to_postgres():
    """Connect to PostgreSQL"""
    config = load_db_config()
    try:
        conn = psycopg2.connect(
            host=config['host'],
            port=config['port'],
            database=config['database'],
            user=config['username'],
            password=config['password']
        )
        return conn
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        return None

def investigate_purchase_399():
    """Investigate purchase #399 that updated DUMY PRODUCT stock"""
    print("=" * 80)
    print("🔍 INVESTIGATING PURCHASE #399")
    print("=" * 80)
    
    conn = connect_to_postgres()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # Get purchase #399 details
        cursor.execute("""
            SELECT id, purchase_number, supplier_id, status, total_amount, 
                   order_date, delivery_date, created_at, updated_at
            FROM purchases 
            WHERE id = 399
        """)
        
        purchase = cursor.fetchone()
        if not purchase:
            print("❌ Purchase #399 not found")
            return
        
        purchase_id, purchase_number, supplier_id, status, total_amount, order_date, delivery_date, created_at, updated_at = purchase
        print(f"📋 Purchase #399 Details:")
        print(f"  ID: {purchase_id}")
        print(f"  Purchase Number: {purchase_number}")
        print(f"  Supplier ID: {supplier_id}")
        print(f"  Status: {status}")
        print(f"  Total Amount: {total_amount}")
        print(f"  Order Date: {order_date}")
        print(f"  Delivery Date: {delivery_date}")
        print(f"  Created: {created_at}")
        print(f"  Updated: {updated_at}")
        
        # Get purchase items for #399
        cursor.execute("""
            SELECT id, product_id, quantity, unit_cost, total_cost, 
                   received_quantity, created_at
            FROM purchase_items 
            WHERE purchase_id = 399
        """)
        
        items = cursor.fetchall()
        print(f"\n📦 Purchase Items ({len(items)} items):")
        
        total_ordered = 0
        total_received = 0
        
        for item in items:
            item_id, product_id, quantity, unit_cost, total_cost, received_quantity, item_created = item
            total_ordered += quantity
            total_received += received_quantity
            
            print(f"  Item {item_id}:")
            print(f"    Product ID: {product_id}")
            print(f"    Ordered: {quantity}")
            print(f"    Received: {received_quantity}")
            print(f"    Unit Cost: {unit_cost}")
            print(f"    Total Cost: {total_cost}")
            print(f"    Created: {item_created}")
            print()
        
        print(f"📊 Summary:")
        print(f"  Total Ordered: {total_ordered}")
        print(f"  Total Received: {total_received}")
        
        # Check DUMY PRODUCT (ID 429) stock history
        print(f"\n🔍 DUMY PRODUCT (ID 429) Stock Analysis:")
        
        # Current stock values
        cursor.execute("""
            SELECT stock_level, warehouse_stock, retail_stock
            FROM products 
            WHERE id = 429
        """)
        
        stock_values = cursor.fetchone()
        if stock_values:
            stock_level, warehouse_stock, retail_stock = stock_values
            print(f"  Current stock_level: {stock_level}")
            print(f"  Current warehouse_stock: {warehouse_stock}")
            print(f"  Current retail_stock: {retail_stock}")
        
        # Check stock movements for DUMY PRODUCT
        cursor.execute("""
            SELECT date, movement_type, quantity, reference, notes
            FROM stock_movements 
            WHERE product_id = 429
            ORDER BY date DESC
            LIMIT 10
        """)
        
        movements = cursor.fetchall()
        if movements:
            print(f"\n📦 Recent Stock Movements for DUMY PRODUCT:")
            for movement in movements:
                date, movement_type, quantity, reference, notes = movement
                print(f"  {date}: {movement_type} {quantity}")
                print(f"    Reference: {reference}")
                if notes:
                    print(f"    Notes: {notes}")
        else:
            print(f"\n❓ No stock movements found for DUMY PRODUCT")
        
        # Check recent sales for DUMY PRODUCT
        cursor.execute("""
            SELECT si.quantity, si.unit_price, si.created_at, s.invoice_number, s.sale_date
            FROM sale_items si
            JOIN sales s ON si.sale_id = s.id
            WHERE si.product_id = 429
            ORDER BY si.created_at DESC
            LIMIT 5
        """)
        
        sales = cursor.fetchall()
        if sales:
            print(f"\n🛒 Recent Sales for DUMY PRODUCT:")
            for sale in sales:
                quantity, unit_price, created_at, invoice, sale_date = sale
                print(f"  {created_at}: Sold {quantity} @ {unit_price}")
                print(f"    Invoice: {invoice}")
        else:
            print(f"\n❓ No sales found for DUMY PRODUCT")
        
        # Check if there are any other purchases for DUMY PRODUCT
        cursor.execute("""
            SELECT p.id, p.purchase_number, p.status, p.created_at,
                   pi.quantity, pi.received_quantity
            FROM purchases p
            JOIN purchase_items pi ON p.id = pi.purchase_id
            WHERE pi.product_id = 429
            ORDER BY p.created_at DESC
            LIMIT 5
        """)
        
        other_purchases = cursor.fetchall()
        if other_purchases:
            print(f"\n📋 All Purchases for DUMY PRODUCT:")
            for purchase in other_purchases:
                p_id, p_number, p_status, p_created, quantity, received = purchase
                print(f"  Purchase {p_id} ({p_number}):")
                print(f"    Status: {p_status}")
                print(f"    Ordered: {quantity}, Received: {received}")
                print(f"    Created: {p_created}")
        else:
            print(f"\n❓ No other purchases found for DUMY PRODUCT")
        
    except Exception as e:
        print(f"❌ Error investigating purchase: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

def check_business_logic_file():
    """Check if business_logic.py actually has content"""
    print(f"\n" + "=" * 80)
    print("🔍 CHECKING business_logic.py FILE")
    print("=" * 80)
    
    business_file = os.path.join(os.path.dirname(__file__), 'controllers', 'business_logic.py')
    
    try:
        with open(business_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        lines = content.split('\n')
        non_empty_lines = [line for line in lines if line.strip() and not line.strip().startswith('#')]
        
        print(f"📊 File Analysis:")
        print(f"  Total lines: {len(lines)}")
        print(f"  Non-empty lines: {len(non_empty_lines)}")
        print(f"  File size: {len(content)} characters")
        
        if len(non_empty_lines) > 0:
            print(f"\n📋 First 10 non-empty lines:")
            for i, line in enumerate(non_empty_lines[:10]):
                print(f"  {i+1}: {line}")
        else:
            print(f"\n❌ File appears to be empty!")
        
        # Look for receive_purchase method
        receive_purchase_found = False
        for i, line in enumerate(lines, 1):
            if 'def receive_purchase' in line:
                print(f"\n✅ Found receive_purchase method at line {i}:")
                print(f"  {line}")
                receive_purchase_found = True
                break
        
        if not receive_purchase_found:
            print(f"\n❌ No receive_purchase method found")
        
    except Exception as e:
        print(f"❌ Error reading business_logic.py: {e}")

def main():
    investigate_purchase_399()
    check_business_logic_file()

if __name__ == "__main__":
    main()

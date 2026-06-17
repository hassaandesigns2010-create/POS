#!/usr/bin/env python3
"""
Analyze DUMY PRODUCT stock issue - had too much stock but became zero
NO CODE CHANGES - INVESTIGATION ONLY
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
            'database': 'pos_system',
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

def analyze_dummy_product():
    """Analyze DUMY PRODUCT stock history"""
    print("=" * 70)
    print("🔍 DUMY PRODUCT STOCK ANALYSIS")
    print("=" * 70)
    print("Issue: Had too much stock but somehow became zero")
    print(f"Analysis started at: {datetime.now()}")
    
    conn = connect_to_postgres()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # Find DUMY PRODUCT in database
        print("\n=== SEARCHING FOR DUMY PRODUCT ===")
        cursor.execute("""
            SELECT id, name, stock_level, barcode, retail_price, wholesale_price, purchase_price
            FROM products 
            WHERE name ILIKE '%DUMY%' OR name ILIKE '%dummy%'
            ORDER BY id
        """)
        
        dummy_products = cursor.fetchall()
        
        if not dummy_products:
            print("❌ No 'DUMY PRODUCT' found in database")
            return
        
        print(f"📋 Found {len(dummy_products)} DUMY products:")
        for product in dummy_products:
            prod_id, name, stock, barcode, retail, wholesale, purchase = product
            print(f"  ID:{prod_id} | {name}")
            print(f"    Stock: {stock} | Barcode: {barcode}")
            print(f"    Prices: Retail={retail}, Wholesale={wholesale}, Purchase={purchase}")
            print()
        
        # Analyze each DUMY product
        for product in dummy_products:
            prod_id, name, stock, barcode, retail, wholesale, purchase = product
            print(f"=== ANALYZING: {name} (ID: {prod_id}) ===")
            
            # Current stock status
            print(f"📊 Current Stock: {stock}")
            
            # Get all sales for this product
            cursor.execute(f"""
                SELECT 
                    si.id,
                    si.quantity,
                    si.unit_price,
                    si.total,
                    si.created_at,
                    s.invoice_number,
                    s.sale_date,
                    s.total_amount as sale_total,
                    s.discount_amount
                FROM sale_items si
                JOIN sales s ON si.sale_id = s.id
                WHERE si.product_id = {prod_id}
                ORDER BY si.created_at DESC
                LIMIT 20
            """)
            
            sales = cursor.fetchall()
            print(f"🛒 Recent Sales (last 20):")
            
            if not sales:
                print("  ❌ No sales found for this product")
            else:
                total_sold = 0
                for sale in sales:
                    sale_id, quantity, unit_price, item_total, created_at, invoice, sale_date, sale_total, discount = sale
                    total_sold += quantity
                    print(f"  📅 {created_at}")
                    print(f"     Invoice: {invoice}")
                    print(f"     Quantity: {quantity} @ {unit_price} = {item_total}")
                    print(f"     Sale Total: {sale_total} | Discount: {discount}")
                    print()
                
                print(f"📈 Total Sold (last 20 sales): {total_sold}")
            
            # Check for very large quantity sales (the bug we found earlier)
            cursor.execute(f"""
                SELECT 
                    si.quantity,
                    si.unit_price,
                    si.created_at,
                    s.invoice_number
                FROM sale_items si
                JOIN sales s ON si.sale_id = s.id
                WHERE si.product_id = {prod_id}
                AND si.quantity > 10
                ORDER BY si.quantity DESC
                LIMIT 10
            """)
            
            large_sales = cursor.fetchall()
            if large_sales:
                print(f"🚨 LARGE QUANTITY SALES (Potential Bug Source):")
                for sale in large_sales:
                    quantity, unit_price, created_at, invoice = sale
                    print(f"  📅 {created_at} | Invoice: {invoice}")
                    print(f"     Quantity: {quantity} @ {unit_price} = {quantity * unit_price}")
                print()
            
            # Check stock movements if table exists
            try:
                cursor.execute(f"""
                    SELECT 
                        date,
                        movement_type,
                        quantity,
                        location,
                        reference,
                        notes
                    FROM stock_movements
                    WHERE product_id = {prod_id}
                    ORDER BY date DESC
                    LIMIT 10
                """)
                
                movements = cursor.fetchall()
                if movements:
                    print(f"📦 Recent Stock Movements:")
                    for movement in movements:
                        date, mov_type, quantity, location, reference, notes = movement
                        print(f"  📅 {date} | {mov_type}")
                        print(f"     Quantity: {quantity} | Location: {location}")
                        print(f"     Reference: {reference} | Notes: {notes}")
                    print()
                else:
                    print("📦 No stock movements found")
                    print()
            except Exception as e:
                print(f"📦 Could not check stock movements: {e}")
                print()
            
            # Check for any refunds or returns
            cursor.execute(f"""
                SELECT 
                    s.id,
                    s.invoice_number,
                    s.sale_date,
                    s.total_amount,
                    s.is_refund,
                    s.refund_of_sale_id,
                    si.quantity
                FROM sales s
                JOIN sale_items si ON s.id = si.sale_id
                WHERE si.product_id = {prod_id}
                AND (s.is_refund = true OR s.refund_of_sale_id IS NOT NULL)
                ORDER BY s.sale_date DESC
                LIMIT 5
            """)
            
            refunds = cursor.fetchall()
            if refunds:
                print(f"🔄 Refunds/Returns:")
                for refund in refunds:
                    sale_id, invoice, sale_date, total, is_refund, refund_of_id, quantity = refund
                    print(f"  📅 {sale_date} | Invoice: {invoice}")
                    print(f"     Refund: {is_refund} | Of Sale: {refund_of_id}")
                    print(f"     Quantity: {quantity} | Total: {total}")
                print()
            else:
                print("🔄 No refunds found")
                print()
            
            # Calculate theoretical stock based on sales
            cursor.execute(f"""
                SELECT COALESCE(SUM(si.quantity), 0) as total_sold
                FROM sale_items si
                JOIN sales s ON si.sale_id = s.id
                WHERE si.product_id = {prod_id}
                AND s.is_refund != true
            """)
            
            total_sold_result = cursor.fetchone()
            total_sold_all = total_sold_result[0] if total_sold_result else 0
            
            cursor.execute(f"""
                SELECT COALESCE(SUM(si.quantity), 0) as total_refunded
                FROM sale_items si
                JOIN sales s ON si.sale_id = s.id
                WHERE si.product_id = {prod_id}
                AND s.is_refund = true
            """)
            
            total_refunded_result = cursor.fetchone()
            total_refunded_all = total_refunded_result[0] if total_refunded_result else 0
            
            print(f"🧮 Stock Calculation:")
            print(f"  Total Sold: {total_sold_all}")
            print(f"  Total Refunded: {total_refunded_all}")
            print(f"  Net Sold: {total_sold_all - total_refunded_all}")
            print(f"  Current Stock: {stock}")
            
            # Check if current stock makes sense
            if stock == 0 and total_sold_all > 0:
                print(f"🚨 ISSUE CONFIRMED: Stock is 0 but {total_sold_all} items were sold!")
                print(f"   This suggests the stock calculation bug we identified earlier")
                
                # Look for the specific large quantity sales that could have caused this
                if large_sales:
                    print(f"🎯 LIKELY CAUSE: Large quantity sales found above")
                    print(f"   These sales probably exceeded available stock and set it to 0")
            
            elif stock < 0:
                print(f"🚨 NEGATIVE STOCK: {stock} (shouldn't happen)")
                print(f"   This indicates a serious stock calculation issue")
            
            elif stock > 0 and total_sold_all > 0:
                print(f"✅ Stock seems reasonable: {stock} remaining after selling {total_sold_all}")
            
            print("\n" + "="*50 + "\n")
        
    except Exception as e:
        print(f"❌ Error analyzing DUMY PRODUCT: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

def main():
    analyze_dummy_product()

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Check if the actual purchase system updates stock correctly
"""

import os
import sys
import re

def check_purchase_file():
    """Check the main purchases.py file for stock updates"""
    print("=" * 80)
    print("🔍 CHECKING MAIN PURCHASE SYSTEM FOR STOCK UPDATES")
    print("=" * 80)
    
    purchases_file = os.path.join(os.path.dirname(__file__), 'views', 'purchases.py')
    
    if not os.path.exists(purchases_file):
        print(f"❌ Purchases file not found: {purchases_file}")
        return
    
    try:
        with open(purchases_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Could not read purchases file: {e}")
        return
    
    lines = content.split('\n')
    
    # Look for stock updates
    stock_updates = []
    stock_level_updates = []
    warehouse_stock_updates = []
    retail_stock_updates = []
    generic_stock_updates = []
    
    for i, line in enumerate(lines, 1):
        line_stripped = line.strip()
        
        # Skip comments
        if line_stripped.startswith('#'):
            continue
        
        # Look for specific stock column updates
        if 'stock_level' in line and ('=' in line or '+=' in line or '-=' in line):
            stock_level_updates.append(f"Line {i}: {line_stripped}")
        
        if 'warehouse_stock' in line and ('=' in line or '+=' in line or '-=' in line):
            warehouse_stock_updates.append(f"Line {i}: {line_stripped}")
        
        if 'retail_stock' in line and ('=' in line or '+=' in line or '-=' in line):
            retail_stock_updates.append(f"Line {i}: {line_stripped}")
        
        # Look for generic stock updates
        stock_patterns = [
            r'\.stock\s*=',  # .stock = 
            r'\.stock\s*\+',  # .stock +
            r'stock\s*=',     # stock = 
            r'stock\s*\+',    # stock +
        ]
        
        for pattern in stock_patterns:
            if re.search(pattern, line):
                generic_stock_updates.append(f"Line {i}: {line_stripped}")
                break
    
    print(f"📊 Stock update analysis for purchases.py:")
    
    if stock_level_updates:
        print(f"\n✅ stock_level updates found:")
        for update in stock_level_updates:
            print(f"  {update}")
    else:
        print(f"\n❌ No stock_level updates found")
    
    if warehouse_stock_updates:
        print(f"\n📦 warehouse_stock updates found:")
        for update in warehouse_stock_updates:
            print(f"  {update}")
    else:
        print(f"\n❓ No warehouse_stock updates found")
    
    if retail_stock_updates:
        print(f"\n🏪 retail_stock updates found:")
        for update in retail_stock_updates:
            print(f"  {update}")
    else:
        print(f"\n❓ No retail_stock updates found")
    
    if generic_stock_updates:
        print(f"\n🔧 Generic stock updates found:")
        for update in generic_stock_updates[:10]:
            print(f"  {update}")
        if len(generic_stock_updates) > 10:
            print(f"  ... and {len(generic_stock_updates) - 10} more")
    else:
        print(f"\n❓ No generic stock updates found")
    
    # Look for receive purchase functions
    print(f"\n🔍 Looking for purchase receive functions:")
    
    receive_functions = []
    current_function = None
    
    for i, line in enumerate(lines, 1):
        # Track function context
        if re.match(r'^\s*def\s+', line):
            current_function = line.strip()
        
        # Look for receive-related functions
        if any(keyword in line.lower() for keyword in ['receive', 'complete', 'finish', 'deliver']):
            if 'def' in line:
                receive_functions.append(f"Line {i}: {line.strip()}")
    
    if receive_functions:
        print(f"📋 Receive-related functions found:")
        for func in receive_functions:
            print(f"  {func}")
    else:
        print(f"❓ No receive-related functions found")

def check_for_temp_purchase_method():
    """Check if temp_create_purchase_method.py is actually used"""
    print(f"\n" + "=" * 80)
    print("🔍 CHECKING IF temp_create_purchase_method.py IS USED")
    print("=" * 80)
    
    base_dir = os.path.dirname(__file__)
    
    # Search for references to temp_create_purchase_method
    python_files = []
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    references = []
    
    for file_path in python_files:
        if any(skip in file_path for skip in ['__pycache__', '.git', 'venv', 'env']):
            continue
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception:
            continue
        
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            if 'temp_create_purchase_method' in line or 'create_purchase' in line:
                rel_path = os.path.relpath(file_path, base_dir)
                references.append(f"{rel_path} Line {i}: {line.strip()}")
    
    if references:
        print(f"🚨 Found {len(references)} references to purchase methods:")
        for ref in references:
            print(f"  {ref}")
    else:
        print(f"❓ No references to temp_create_purchase_method found")
        print(f"   This means the stock update in temp_create_purchase_method.py")
        print(f"   might not be the actual purchase method being used!")

def check_database_purchase_stock_movements():
    """Check if purchases create stock movements"""
    print(f"\n" + "=" * 80)
    print("🗄️  CHECKING PURCHASE STOCK MOVEMENTS")
    print("=" * 80)
    
    import psycopg2
    import json
    
    def load_db_config():
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
    
    conn = connect_to_postgres()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # Check recent purchases
        cursor.execute("""
            SELECT id, purchase_number, status, order_date, delivery_date
            FROM purchases
            ORDER BY created_at DESC
            LIMIT 10
        """)
        
        recent_purchases = cursor.fetchall()
        
        if recent_purchases:
            print(f"📋 Recent purchases:")
            for purchase in recent_purchases:
                purchase_id, purchase_number, status, order_date, delivery_date = purchase
                print(f"  ID: {purchase_id} | {purchase_number} | Status: {status}")
                print(f"     Order: {order_date} | Delivery: {delivery_date}")
        else:
            print(f"❓ No purchases found")
        
        # Check if purchases create stock movements
        try:
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM stock_movements
                WHERE reference ILIKE '%purchase%'
                OR reference ILIKE '%PURCHASE%'
            """)
            
            purchase_movements = cursor.fetchone()
            if purchase_movements and purchase_movements[0] > 0:
                print(f"\n📦 Found {purchase_movements[0]} purchase-related stock movements")
                
                # Get some examples
                cursor.execute("""
                    SELECT product_id, quantity, movement_type, reference, date
                    FROM stock_movements
                    WHERE reference ILIKE '%purchase%'
                    OR reference ILIKE '%PURCHASE%'
                    ORDER BY date DESC
                    LIMIT 5
                """)
                
                movements = cursor.fetchall()
                print(f"📋 Recent purchase stock movements:")
                for movement in movements:
                    product_id, quantity, movement_type, reference, date = movement
                    print(f"  Product: {product_id} | Qty: {quantity} | Type: {movement_type}")
                    print(f"     Reference: {reference} | Date: {date}")
            else:
                print(f"\n❓ No purchase-related stock movements found")
                print(f"   This suggests purchases might not be updating stock!")
        
        except Exception as e:
            print(f"❓ Could not check stock movements: {e}")
        
    except Exception as e:
        print(f"❌ Error checking database: {e}")
    finally:
        conn.close()

def main():
    check_purchase_file()
    check_for_temp_purchase_method()
    check_database_purchase_stock_movements()

if __name__ == "__main__":
    main()

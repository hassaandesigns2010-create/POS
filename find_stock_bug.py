#!/usr/bin/env python3
"""
Find the exact stock bug - selling 1 item makes stock go from 10 to 0
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

def test_stock_calculation():
    """Test the exact stock calculation logic"""
    print("=== TESTING STOCK CALCULATION LOGIC ===")
    
    # Simulate the business logic calculation
    from decimal import Decimal
    
    # Test case 1: Normal sale
    print("🧪 Test Case 1: Normal sale")
    old_stock = Decimal('10')
    quantity = Decimal('1')
    new_stock = old_stock - quantity
    print(f"  Old stock: {old_stock}")
    print(f"  Quantity: {quantity}")
    print(f"  New stock: {new_stock}")
    print(f"  Expected: 9, Got: {new_stock}")
    print(f"  ✅ Correct" if new_stock == 9 else f"  ❌ BUG!")
    
    # Test case 2: Decimal conversion
    print("\n🧪 Test Case 2: Decimal conversion")
    old_stock = Decimal(str(10))
    quantity = Decimal(str(1))
    new_stock = old_stock - quantity
    print(f"  Old stock: {old_stock}")
    print(f"  Quantity: {quantity}")
    print(f"  New stock: {new_stock}")
    print(f"  Expected: 9, Got: {new_stock}")
    print(f"  ✅ Correct" if new_stock == 9 else f"  ❌ BUG!")
    
    # Test case 3: Float to Decimal conversion (potential bug)
    print("\n🧪 Test Case 3: Float to Decimal conversion")
    old_stock = Decimal(str(10.0))
    quantity = Decimal(str(1.0))
    new_stock = old_stock - quantity
    print(f"  Old stock: {old_stock}")
    print(f"  Quantity: {quantity}")
    print(f"  New stock: {new_stock}")
    print(f"  Expected: 9, Got: {new_stock}")
    print(f"  ✅ Correct" if new_stock == 9 else f"  ❌ BUG!")
    
    # Test case 4: Check for precision issues
    print("\n🧪 Test Case 4: Precision issues")
    old_stock = Decimal('10.0000')
    quantity = Decimal('1.0000')
    new_stock = old_stock - quantity
    print(f"  Old stock: {old_stock}")
    print(f"  Quantity: {quantity}")
    print(f"  New stock: {new_stock}")
    print(f"  Expected: 9.0000, Got: {new_stock}")
    print(f"  ✅ Correct" if new_stock == Decimal('9.0000') else f"  ❌ BUG!")

def check_database_stock_types():
    """Check how stock is stored in database"""
    print("\n=== DATABASE STOCK TYPE ANALYSIS ===")
    
    conn = connect_to_postgres()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # Check the actual data type
        cursor.execute("""
            SELECT column_name, data_type, numeric_precision, numeric_scale
            FROM information_schema.columns 
            WHERE table_name = 'products' AND column_name = 'stock_level'
        """)
        
        column_info = cursor.fetchone()
        if column_info:
            col_name, data_type, precision, scale = column_info
            print(f"📋 Stock level column info:")
            print(f"  Column: {col_name}")
            print(f"  Data type: {data_type}")
            print(f"  Precision: {precision}")
            print(f"  Scale: {scale}")
        
        # Check some actual values
        cursor.execute("""
            SELECT stock_level, COUNT(*) as count
            FROM products 
            GROUP BY stock_level
            ORDER BY count DESC
            LIMIT 10
        """)
        
        stock_values = cursor.fetchall()
        print(f"\n📊 Most common stock values:")
        for stock_val, count in stock_values:
            print(f"  {stock_val:>8} : {count:>4} products")
        
        # Check for any weird values
        cursor.execute("""
            SELECT stock_level, COUNT(*) as count
            FROM products 
            WHERE stock_level < 0 OR stock_level > 10000
            GROUP BY stock_level
            ORDER BY stock_level
        """)
        
        weird_values = cursor.fetchall()
        if weird_values:
            print(f"\n⚠️  Unusual stock values:")
            for stock_val, count in weird_values:
                print(f"  {stock_val:>8} : {count:>4} products")
        else:
            print(f"\n✅ No unusual stock values found")
        
    except Exception as e:
        print(f"❌ Error checking database types: {e}")
    finally:
        conn.close()

def find_potential_bug_sources():
    """Look for potential bug sources in the code"""
    print("\n=== POTENTIAL BUG SOURCES ===")
    
    # Check business logic for issues
    business_file = os.path.join(os.path.dirname(__file__), 'controllers', 'business_logic.py')
    
    try:
        with open(business_file, 'r') as f:
            lines = f.readlines()
        
        print("🔍 Checking for potential issues in business_logic.py...")
        
        # Look for specific patterns
        for i, line in enumerate(lines, 1):
            line_content = line.strip()
            
            # Check for suspicious patterns
            if 'stock_level' in line_content and '=' in line_content:
                # Look for direct assignment of quantity to stock
                if 'stock_level = quantity' in line_content:
                    print(f"  ❌ Line {i}: {line_content} (SETTING STOCK TO QUANTITY!)")
                
                # Look for multiplication/division
                elif any(op in line_content for op in ['stock_level *=', 'stock_level /=', 'stock_level **=']):
                    print(f"  ⚠️  Line {i}: {line_content} (Math operation on stock)")
                
                # Look for setting to zero
                elif 'stock_level = 0' in line_content:
                    print(f"  ⚠️  Line {i}: {line_content} (Setting stock to zero)")
                
                # Look for potential type issues
                elif 'Decimal(' in line_content and 'stock_level' in line_content:
                    print(f"  📝 Line {i}: {line_content} (Decimal conversion)")
        
        # Check for transaction issues
        print(f"\n🔍 Checking transaction handling...")
        commit_count = 0
        rollback_count = 0
        
        for i, line in enumerate(lines, 1):
            if 'self.session.commit()' in line:
                commit_count += 1
            if 'self.session.rollback()' in line:
                rollback_count += 1
        
        print(f"  Commits found: {commit_count}")
        print(f"  Rollbacks found: {rollback_count}")
        
        if rollback_count < commit_count:
            print(f"  ⚠️  More commits than rollbacks - potential transaction issues")
        
    except Exception as e:
        print(f"❌ Error analyzing business logic: {e}")

def check_for_race_conditions():
    """Check for potential race conditions"""
    print("\n=== RACE CONDITION ANALYSIS ===")
    
    # Look for concurrent access patterns
    business_file = os.path.join(os.path.dirname(__file__), 'controllers', 'business_logic.py')
    
    try:
        with open(business_file, 'r') as f:
            content = f.read()
        
        # Check for locking mechanisms
        if 'SELECT FOR UPDATE' in content:
            print("✅ Found SELECT FOR UPDATE - good for preventing race conditions")
        else:
            print("⚠️  No SELECT FOR UPDATE found - potential race condition risk")
        
        if 'with_for_update()' in content:
            print("✅ Found with_for_update() - good for preventing race conditions")
        else:
            print("⚠️  No with_for_update() found - potential race condition risk")
        
        # Check for transaction isolation
        if 'isolation_level' in content:
            print("✅ Found transaction isolation configuration")
        else:
            print("⚠️  No explicit transaction isolation found")
        
    except Exception as e:
        print(f"❌ Error checking race conditions: {e}")

def create_debug_scenario():
    """Create a debug scenario to reproduce the bug"""
    print("\n=== DEBUG SCENARIO ===")
    
    conn = connect_to_postgres()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # Find a product with decent stock
        cursor.execute("""
            SELECT id, name, stock_level
            FROM products 
            WHERE stock_level >= 5
            ORDER BY stock_level DESC
            LIMIT 5
        """)
        
        products = cursor.fetchall()
        
        if products:
            print("🧪 Products available for testing:")
            for prod in products:
                prod_id, name, stock = prod
                print(f"  ID:{prod_id} | {name[:40]:40s} | Stock:{stock}")
            
            # Choose the first product for testing
            test_product = products[0]
            product_id, product_name, original_stock = test_product
            
            print(f"\n🔬 Testing with: {product_name}")
            print(f"   Original stock: {original_stock}")
            
            # Simulate what happens in a sale
            quantity = 1
            
            # Step 1: Get current stock
            cursor.execute(f"SELECT stock_level FROM products WHERE id = {product_id}")
            current_stock = cursor.fetchone()[0]
            print(f"   Current stock from DB: {current_stock}")
            
            # Step 2: Calculate new stock (using business logic)
            from decimal import Decimal
            old_stock = Decimal(str(current_stock))
            quantity_decimal = Decimal(str(quantity))
            new_stock = old_stock - quantity_decimal
            print(f"   Calculated new stock: {new_stock}")
            
            # Step 3: Check if this matches expected
            expected = original_stock - quantity
            print(f"   Expected new stock: {expected}")
            
            if float(new_stock) != expected:
                print(f"   ❌ BUG DETECTED! Calculation error!")
                print(f"   Expected: {expected}, Got: {new_stock}")
            else:
                print(f"   ✅ Calculation is correct")
            
            # Check if there are any recent sales for this product
            cursor.execute(f"""
                SELECT quantity, created_at
                FROM sale_items 
                WHERE product_id = {product_id}
                ORDER BY created_at DESC
                LIMIT 3
            """)
            
            recent_sales = cursor.fetchall()
            if recent_sales:
                print(f"   Recent sales for this product:")
                for sale_qty, sale_date in recent_sales:
                    print(f"     Sold: {sale_qty} at {sale_date}")
            else:
                print(f"   No recent sales found for this product")
        
        else:
            print("❌ No products with sufficient stock found for testing")
        
    except Exception as e:
        print(f"❌ Error creating debug scenario: {e}")
    finally:
        conn.close()

def main():
    print("=" * 70)
    print("🐛 FINDING THE EXACT STOCK BUG")
    print("=" * 70)
    print("Issue: Selling 1 item makes stock go from 10 to 0")
    print(f"Started at: {datetime.now()}")
    
    # Test the calculation logic
    test_stock_calculation()
    
    # Check database types
    check_database_stock_types()
    
    # Find potential bug sources
    find_potential_bug_sources()
    
    # Check for race conditions
    check_for_race_conditions()
    
    # Create debug scenario
    create_debug_scenario()
    
    print(f"\n" + "=" * 70)
    print(f"📋 BUG ANALYSIS SUMMARY")
    print(f"=" * 70)
    
    print(f"\n🎯 Most Likely Causes:")
    print(f"1. **Race condition** - Multiple sales processing simultaneously")
    print(f"2. **Transaction issue** - Stock update not properly committed")
    print(f"3. **Exception handling** - Stock update exception not caught")
    print(f"4. **Type conversion** - Decimal/float precision issues")
    print(f"5. **Concurrent access** - No row locking during stock updates")
    
    print(f"\n🔧 Recommended Fixes:")
    print(f"1. Add row locking: SELECT ... FOR UPDATE")
    print(f"2. Add stock validation before/after updates")
    print(f"3. Improve exception handling in stock updates")
    print(f"4. Add detailed logging for stock changes")
    print(f"5. Implement proper transaction isolation")
    
    print(f"\n✅ Analysis completed at: {datetime.now()}")

if __name__ == "__main__":
    main()

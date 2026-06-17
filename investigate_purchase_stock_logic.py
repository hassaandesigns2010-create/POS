#!/usr/bin/env python3
"""
Investigate purchase logic - which stock column gets updated during purchases
"""

import os
import sys
import re

def find_purchase_stock_logic():
    """Find which stock column purchase logic uses"""
    print("=" * 80)
    print("🔍 INVESTIGATING PURCHASE STOCK LOGIC")
    print("=" * 80)
    print("Finding which stock column gets updated during purchases...")
    
    base_dir = os.path.dirname(__file__)
    
    # Look for purchase-related files
    purchase_files = []
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.py') and ('purchase' in file.lower() or 'procurement' in file.lower()):
                purchase_files.append(os.path.join(root, file))
    
    print(f"📁 Found {len(purchase_files)} purchase-related files:")
    for file_path in purchase_files:
        rel_path = os.path.relpath(file_path, base_dir)
        print(f"  • {rel_path}")
    
    # Analyze each purchase file
    for file_path in purchase_files:
        rel_path = os.path.relpath(file_path, base_dir)
        print(f"\n" + "=" * 60)
        print(f"🔍 ANALYZING: {rel_path}")
        print("=" * 60)
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            print(f"❌ Could not read file: {e}")
            continue
        
        lines = content.split('\n')
        
        # Look for stock updates in purchase logic
        stock_updates = []
        current_function = None
        
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # Skip comments
            if line_stripped.startswith('#'):
                continue
            
            # Track function context
            if re.match(r'^\s*def\s+', line):
                current_function = line_stripped
            
            # Look for stock column usage
            if any(col in line for col in ['stock_level', 'warehouse_stock', 'retail_stock']):
                context = ""
                if current_function:
                    context = f" in {current_function}"
                
                stock_updates.append(f"Line {i}{context}: {line_stripped}")
        
        if stock_updates:
            print("📊 Stock column usage found:")
            for update in stock_updates:
                print(f"  {update}")
        else:
            print("❓ No stock column usage found")
        
        # Look for generic stock updates
        print(f"\n🔍 Generic stock updates:")
        generic_updates = []
        
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # Look for stock update patterns
            stock_patterns = [
                r'\.stock\s*=',  # .stock = 
                r'\.stock\s*\+',  # .stock +
                r'stock\s*=',     # stock = 
                r'stock\s*\+',    # stock +
                r'add_stock',     # add_stock function
                r'update_stock',  # update_stock function
                r'increase_stock', # increase_stock function
            ]
            
            for pattern in stock_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    generic_updates.append(f"Line {i}: {line_stripped}")
                    break
        
        if generic_updates:
            for update in generic_updates[:10]:  # Show first 10
                print(f"  {update}")
            if len(generic_updates) > 10:
                print(f"  ... and {len(generic_updates) - 10} more")
        else:
            print("  ❓ No generic stock updates found")

def find_business_logic_purchases():
    """Check business logic for purchase-related stock updates"""
    print(f"\n" + "=" * 80)
    print("🔍 CHECKING BUSINESS LOGIC FOR PURCHASE STOCK UPDATES")
    print("=" * 80)
    
    base_dir = os.path.dirname(__file__)
    
    # Check all files for purchase-related functions
    python_files = []
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    purchase_stock_updates = []
    
    for file_path in python_files:
        if any(skip in file_path for skip in ['__pycache__', '.git', 'venv', 'env', 'tests']):
            continue
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception:
            continue
        
        lines = content.split('\n')
        
        # Look for purchase-related stock updates
        for i, line in enumerate(lines, 1):
            line_lower = line.lower()
            
            # Check for purchase-related stock updates
            if any(keyword in line_lower for keyword in ['purchase', 'procurement', 'buy', 'add_stock', 'receive']):
                if any(stock_col in line for stock_col in ['stock_level', 'warehouse_stock', 'retail_stock', '.stock']):
                    rel_path = os.path.relpath(file_path, base_dir)
                    purchase_stock_updates.append(f"{rel_path} Line {i}: {line.strip()}")
    
    if purchase_stock_updates:
        print(f"🚨 Found {len(purchase_stock_updates)} purchase-related stock updates:")
        for update in purchase_stock_updates:
            print(f"  {update}")
    else:
        print("❓ No purchase-related stock updates found")

def check_database_schema_for_purchases():
    """Check if there are purchase-related tables that might affect stock"""
    print(f"\n" + "=" * 80)
    print("🗄️  CHECKING DATABASE FOR PURCHASE-RELATED TABLES")
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
        
        # Look for purchase-related tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND (table_name ILIKE '%purchase%' OR table_name ILIKE '%procurement%')
            ORDER BY table_name
        """)
        
        purchase_tables = cursor.fetchall()
        
        if purchase_tables:
            print(f"📋 Purchase-related tables found:")
            for table in purchase_tables:
                table_name = table[0]
                print(f"  • {table_name}")
                
                # Check columns in this table
                cursor.execute(f"""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = '{table_name}' 
                    AND table_schema = 'public'
                    ORDER BY ordinal_position
                """)
                
                columns = cursor.fetchall()
                print(f"    Columns:")
                for col in columns:
                    col_name, data_type = col
                    print(f"      - {col_name}: {data_type}")
                print()
        else:
            print("❓ No purchase-related tables found")
        
        # Check for stock movements that might be purchase-related
        cursor.execute("""
            SELECT DISTINCT reference_type 
            FROM stock_movements 
            WHERE reference_type ILIKE '%purchase%' 
            OR reference_type ILIKE '%procurement%'
            OR reference_type ILIKE '%buy%'
            ORDER BY reference_type
        """)
        
        try:
            purchase_references = cursor.fetchall()
            if purchase_references:
                print(f"📦 Purchase-related stock movements:")
                for ref in purchase_references:
                    print(f"  • {ref[0]}")
            else:
                print("❓ No purchase-related stock movements found")
        except Exception as e:
            print(f"❓ Could not check stock movements: {e}")
        
    except Exception as e:
        print(f"❌ Error checking database: {e}")
    finally:
        conn.close()

def main():
    find_purchase_stock_logic()
    find_business_logic_purchases()
    check_database_schema_for_purchases()

if __name__ == "__main__":
    main()

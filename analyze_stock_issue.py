#!/usr/bin/env python3
"""
Analyze stock issue: 730+ items have zero stock when they shouldn't
Compare current database with backups to identify the problem
"""

import os
import sys
import sqlite3
import tempfile
from datetime import datetime
from collections import defaultdict

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def analyze_sql_backup(backup_file):
    """Analyze a SQL backup file for stock information"""
    print(f"\n=== Analyzing backup: {backup_file} ===")
    
    try:
        with open(backup_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Look for products table data
        lines = content.split('\n')
        products_data = []
        in_products_insert = False
        
        for line in lines:
            if 'INSERT INTO products' in line.upper():
                in_products_insert = True
                # Extract the values part
                if 'VALUES' in line.upper():
                    values_part = line.split('VALUES')[1].strip()
                    if values_part.endswith(';'):
                        values_part = values_part[:-1]
                    products_data.extend(parse_insert_values(values_part))
            elif in_products_insert and line.strip().startswith('('):
                # Continue parsing multi-line insert
                values_part = line.strip()
                if values_part.endswith(';'):
                    values_part = values_part[:-1]
                    in_products_insert = False
                products_data.extend(parse_insert_values(values_part))
        
        print(f"Found {len(products_data)} products in backup")
        
        # Analyze stock levels
        zero_stock = 0
        low_stock = 0
        normal_stock = 0
        stock_distribution = defaultdict(int)
        
        for product in products_data:
            if len(product) >= 8:  # Ensure we have enough columns
                try:
                    stock = float(product[7]) if product[7] else 0
                    if stock == 0:
                        zero_stock += 1
                    elif stock < 10:
                        low_stock += 1
                    else:
                        normal_stock += 1
                    
                    # Stock distribution
                    if stock == 0:
                        stock_distribution['Zero'] += 1
                    elif stock <= 5:
                        stock_distribution['1-5'] += 1
                    elif stock <= 10:
                        stock_distribution['6-10'] += 1
                    elif stock <= 50:
                        stock_distribution['11-50'] += 1
                    elif stock <= 100:
                        stock_distribution['51-100'] += 1
                    else:
                        stock_distribution['100+'] += 1
                        
                except (ValueError, IndexError):
                    continue
        
        print(f"Stock Analysis:")
        print(f"  Zero stock: {zero_stock}")
        print(f"  Low stock (1-9): {low_stock}")
        print(f"  Normal stock (10+): {normal_stock}")
        print(f"  Stock distribution: {dict(stock_distribution)}")
        
        return {
            'total_products': len(products_data),
            'zero_stock': zero_stock,
            'low_stock': low_stock,
            'normal_stock': normal_stock,
            'stock_distribution': dict(stock_distribution)
        }
        
    except Exception as e:
        print(f"Error analyzing backup {backup_file}: {e}")
        return None

def parse_insert_values(values_str):
    """Parse INSERT VALUES string into individual records"""
    records = []
    current_record = []
    in_quotes = False
    current_value = ""
    
    i = 0
    while i < len(values_str):
        char = values_str[i]
        
        if char == "'" and (i == 0 or values_str[i-1] != '\\'):
            in_quotes = not in_quotes
            current_value += char
        elif char == ',' and not in_quotes:
            current_record.append(current_value.strip())
            current_value = ""
        elif char == '(' and not in_quotes:
            # Start of new record
            current_record = []
            current_value = ""
        elif char == ')' and not in_quotes:
            # End of record
            current_record.append(current_value.strip())
            records.append(current_record)
            current_value = ""
        else:
            current_value += char
        
        i += 1
    
    return records

def get_current_stock_from_db():
    """Get current stock information from the database"""
    print("\n=== Analyzing Current Database ===")
    
    try:
        # Try to connect to the current database
        from pos_app.database.connection import Database
        
        db = Database()
        if db._is_offline:
            print("Database is in offline mode, using SQLite")
        
        # Query current stock levels
        query = """
        SELECT 
            id,
            name,
            stock,
            purchase_price,
            sale_price,
            barcode,
            category_id
        FROM products 
        ORDER BY id
        """
        
        result = db.session.execute(query)
        products = result.fetchall()
        
        print(f"Found {len(products)} products in current database")
        
        # Analyze current stock
        zero_stock = 0
        low_stock = 0
        normal_stock = 0
        stock_distribution = defaultdict(int)
        detailed_zero_stock = []
        
        for product in products:
            try:
                stock = float(product[2]) if product[2] is not None else 0
                if stock == 0:
                    zero_stock += 1
                    detailed_zero_stock.append({
                        'id': product[0],
                        'name': product[1],
                        'barcode': product[5],
                        'category_id': product[6]
                    })
                elif stock < 10:
                    low_stock += 1
                else:
                    normal_stock += 1
                
                # Stock distribution
                if stock == 0:
                    stock_distribution['Zero'] += 1
                elif stock <= 5:
                    stock_distribution['1-5'] += 1
                elif stock <= 10:
                    stock_distribution['6-10'] += 1
                elif stock <= 50:
                    stock_distribution['11-50'] += 1
                elif stock <= 100:
                    stock_distribution['51-100'] += 1
                else:
                    stock_distribution['100+'] += 1
                    
            except (ValueError, IndexError):
                continue
        
        print(f"Current Stock Analysis:")
        print(f"  Zero stock: {zero_stock}")
        print(f"  Low stock (1-9): {low_stock}")
        print(f"  Normal stock (10+): {normal_stock}")
        print(f"  Stock distribution: {dict(stock_distribution)}")
        
        # Show first 10 zero-stock items as examples
        print(f"\nFirst 10 zero-stock items:")
        for i, item in enumerate(detailed_zero_stock[:10]):
            print(f"  {i+1}. ID: {item['id']}, Name: {item['name']}, Barcode: {item['barcode']}")
        
        if len(detailed_zero_stock) > 10:
            print(f"  ... and {len(detailed_zero_stock) - 10} more items")
        
        return {
            'total_products': len(products),
            'zero_stock': zero_stock,
            'low_stock': low_stock,
            'normal_stock': normal_stock,
            'stock_distribution': dict(stock_distribution),
            'zero_stock_details': detailed_zero_stock
        }
        
    except Exception as e:
        print(f"Error connecting to current database: {e}")
        return None

def compare_with_backups(current_data, backup_dir):
    """Compare current stock data with backups"""
    print("\n=== Comparing with Backups ===")
    
    backup_files = [f for f in os.listdir(backup_dir) if f.endswith('.sql') and f.startswith('pos_backup_')]
    backup_files.sort()
    
    if not backup_files:
        print("No backup files found")
        return
    
    print(f"Found {len(backup_files)} backup files")
    
    for backup_file in backup_files[-5:]:  # Check last 5 backups
        backup_path = os.path.join(backup_dir, backup_file)
        backup_data = analyze_sql_backup(backup_path)
        
        if backup_data and current_data:
            print(f"\nComparison with {backup_file}:")
            print(f"  Current total products: {current_data['total_products']}")
            print(f"  Backup total products: {backup_data['total_products']}")
            print(f"  Current zero stock: {current_data['zero_stock']}")
            print(f"  Backup zero stock: {backup_data['zero_stock']}")
            
            if current_data['zero_stock'] > backup_data['zero_stock']:
                increase = current_data['zero_stock'] - backup_data['zero_stock']
                print(f"  ⚠️  ZERO STOCK INCREASED by {increase} items!")
            elif current_data['zero_stock'] < backup_data['zero_stock']:
                decrease = backup_data['zero_stock'] - current_data['zero_stock']
                print(f"  ✅ Zero stock decreased by {decrease} items")
            else:
                print(f"  ➡️  Zero stock unchanged")

def main():
    print("=== STOCK ISSUE ANALYSIS ===")
    print(f"Analysis started at: {datetime.now()}")
    
    # Get current stock data
    current_data = get_current_stock_from_db()
    
    if not current_data:
        print("❌ Could not get current stock data")
        return
    
    # Check if there's really a stock issue
    if current_data['zero_stock'] < 700:
        print(f"✅ Current zero stock count ({current_data['zero_stock']}) is less than 700")
        print("   The reported issue may have been resolved or was temporary")
        return
    
    print(f"⚠️  CONFIRMED: {current_data['zero_stock']} items have zero stock!")
    
    # Compare with backups
    backup_dir = os.path.join(os.path.dirname(__file__), 'backups')
    if os.path.exists(backup_dir):
        compare_with_backups(current_data, backup_dir)
    else:
        print("❌ Backups directory not found")
    
    # Generate recommendations
    print("\n=== RECOMMENDATIONS ===")
    print("1. Check recent sales/purchase operations that might have affected stock")
    print("2. Review stock calculation logic in the application")
    print("3. Consider restoring from the most recent backup with better stock levels")
    print("4. Run stock reconciliation process")
    print("5. Check for any data corruption issues")
    
    # Save detailed report
    report_file = f"stock_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_file, 'w') as f:
        f.write(f"Stock Analysis Report\n")
        f.write(f"Generated: {datetime.now()}\n")
        f.write(f"Current zero stock items: {current_data['zero_stock']}\n")
        f.write(f"Total products: {current_data['total_products']}\n")
        f.write(f"\nZero stock items:\n")
        for item in current_data.get('zero_stock_details', []):
            f.write(f"ID: {item['id']}, Name: {item['name']}, Barcode: {item['barcode']}\n")
    
    print(f"\n📄 Detailed report saved to: {report_file}")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Script to analyze backup files and compare stock data with current database
"""

import os
import re
import sqlite3
from datetime import datetime
from pathlib import Path

def parse_sql_backup(file_path):
    """Parse SQL backup file and extract product stock data"""
    products = []
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Find INSERT statements for products table
        # Look for patterns like: INSERT INTO products (id, name, stock_level, ...) VALUES (1, 'Product Name', 100, ...);
        insert_pattern = r'INSERT\s+INTO\s+products\s*\([^)]*\)\s*VALUES\s*\(([^;]+)\);'
        matches = re.findall(insert_pattern, content, re.IGNORECASE | re.MULTILINE)
        
        for match in matches:
            # Parse the values
            values = []
            current_value = ""
            in_quotes = False
            quote_char = None
            
            i = 0
            while i < len(match):
                char = match[i]
                
                if not in_quotes:
                    if char in ("'", '"'):
                        in_quotes = True
                        quote_char = char
                        current_value += char
                    elif char == ',':
                        values.append(current_value.strip())
                        current_value = ""
                    else:
                        current_value += char
                else:
                    current_value += char
                    if char == quote_char and (i == 0 or match[i-1] != '\\'):
                        in_quotes = False
                        quote_char = None
                
                i += 1
            
            # Add the last value
            if current_value.strip():
                values.append(current_value.strip())
            
            # Extract product info (adjust indices based on actual table structure)
            if len(values) >= 3:
                product_id = values[0].strip("'\"")
                product_name = values[1].strip("'\"") if len(values) > 1 else ""
                
                # Find stock_level in the values (it might be at different positions)
                stock_level = "0"
                for i, val in enumerate(values):
                    if val.replace('.', '').replace('-', '').isdigit():
                        # This could be stock_level, purchase_price, wholesale_price, or retail_price
                        # We'll need to identify which one based on column order
                        pass
                
                products.append({
                    'id': product_id,
                    'name': product_name,
                    'raw_values': values
                })
    
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
    
    return products

def extract_stock_from_values(values, column_names):
    """Extract stock level from values based on column names"""
    try:
        # Find stock_level column index
        stock_index = None
        for i, col in enumerate(column_names):
            if 'stock' in col.lower():
                stock_index = i
                break
        
        if stock_index is not None and stock_index < len(values):
            stock_val = values[stock_index].strip("'\"")
            try:
                return float(stock_val) if stock_val else 0.0
            except:
                return 0.0
    except:
        pass
    
    return 0.0

def get_current_database_stock():
    """Get current stock data from the database"""
    try:
        # Connect to the current database
        import sys
        sys.path.append('C:/Users/pc/Music/pos_app')
        
        from pos_app.models.database import get_session
        
        session = get_session()
        products = session.query(Product).all()
        
        current_stock = {}
        for product in products:
            current_stock[product.id] = {
                'name': product.name,
                'stock_level': float(product.stock_level) if product.stock_level else 0.0,
                'sku': product.sku,
                'barcode': product.barcode
            }
        
        session.close()
        return current_stock
    
    except Exception as e:
        print(f"Error getting current database stock: {e}")
        return {}

def analyze_backup_stocks():
    """Main analysis function"""
    backup_dir = Path("C:/Users/pc/Documents/backups")
    backup_files = sorted(backup_dir.glob("pos_backup_*.sql"))
    
    print(f"Found {len(backup_files)} backup files")
    print("=" * 80)
    
    # Get current database stock
    print("Getting current database stock...")
    current_stock = get_current_database_stock()
    print(f"Current database has {len(current_stock)} products")
    
    # Analyze each backup
    backup_analysis = {}
    
    for backup_file in backup_files:
        print(f"\nAnalyzing: {backup_file.name}")
        print("-" * 60)
        
        # Extract date from filename
        date_match = re.search(r'(\d{8})_(\d{6})', backup_file.name)
        if date_match:
            date_str = f"{date_match.group(1)} {date_match.group(2)}"
            backup_date = datetime.strptime(date_str, "%Y%m%d %H%M%S")
        else:
            backup_date = datetime.fromtimestamp(backup_file.stat().st_mtime)
        
        print(f"Backup date: {backup_date}")
        
        # Parse the backup
        products = parse_sql_backup(backup_file)
        print(f"Found {len(products)} products in backup")
        
        # Store analysis
        backup_analysis[backup_file.name] = {
            'date': backup_date,
            'product_count': len(products),
            'products': products[:10]  # Store first 10 for sample
        }
    
    # Compare stocks over time
    print("\n" + "=" * 80)
    print("STOCK COMPARISON ANALYSIS")
    print("=" * 80)
    
    # Show backup timeline
    print("\nBackup Timeline:")
    for name, data in sorted(backup_analysis.items(), key=lambda x: x[1]['date']):
        print(f"  {data['date']}: {name} ({data['product_count']} products)")
    
    print(f"\nCurrent Database: {len(current_stock)} products")
    
    # Find significant stock changes (if we could parse properly)
    print("\nNote: Detailed stock comparison requires proper SQL parsing.")
    print("The backup files contain complex SQL that needs specialized parsing.")
    print("Recommendation: Use PostgreSQL restore tools for accurate analysis.")

if __name__ == "__main__":
    analyze_backup_stocks()

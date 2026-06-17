#!/usr/bin/env python3
"""
PostgreSQL Backup Analysis Script - Focus on Stock Data
"""

import os
import re
from datetime import datetime
from pathlib import Path

def extract_products_from_copy(file_path):
    """Extract product data from PostgreSQL COPY format"""
    products = []
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        in_copy_section = False
        copy_start_line = 0
        
        for i, line in enumerate(lines):
            if "COPY public.products" in line:
                in_copy_section = True
                copy_start_line = i
                # Extract column names from the COPY line
                columns_match = re.search(r'COPY public\.products\s*\(([^)]+)\)', line)
                if columns_match:
                    columns_str = columns_match.group(1)
                    columns = [col.strip().strip('"') for col in columns_str.split(',')]
                    print(f"Found products table columns: {columns}")
                continue
            
            if in_copy_section and line.strip() == "\\.":
                # End of COPY section
                break
            
            if in_copy_section and line.strip():
                # Parse product data line
                try:
                    # Split by tab (PostgreSQL COPY default delimiter)
                    values = line.strip().split('\t')
                    
                    # Create product dict
                    product = {}
                    for j, value in enumerate(values):
                        if j < len(columns):
                            col_name = columns[j]
                            # Clean up the value
                            clean_value = value.strip()
                            if clean_value == '\\N':  # PostgreSQL NULL
                                clean_value = None
                            elif clean_value.startswith('"') and clean_value.endswith('"'):
                                clean_value = clean_value[1:-1]  # Remove quotes
                            
                            product[col_name] = clean_value
                    
                    products.append(product)
                    
                except Exception as e:
                    print(f"Error parsing line {i}: {e}")
                    continue
    
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
    
    return products

def get_current_stock_data():
    """Get current stock data from database"""
    try:
        import sys
        sys.path.append('C:/Users/pc/Music/pos_app')
        
        from pos_app.models.database import Product, get_session
        
        session = get_session()
        products = session.query(Product).all()
        
        current_data = {}
        for product in products:
            current_data[product.id] = {
                'name': product.name,
                'stock_level': float(product.stock_level) if product.stock_level else 0.0,
                'sku': product.sku,
                'barcode': product.barcode,
                'purchase_price': float(product.purchase_price) if product.purchase_price else 0.0,
                'wholesale_price': float(product.wholesale_price) if product.wholesale_price else 0.0,
                'retail_price': float(product.retail_price) if product.retail_price else 0.0,
            }
        
        session.close()
        return current_data
    
    except Exception as e:
        print(f"Error getting current database data: {e}")
        return {}

def analyze_stock_changes():
    """Main analysis function"""
    backup_dir = Path("C:/Users/pc/Documents/backups")
    backup_files = sorted(backup_dir.glob("pos_backup_*.sql"))
    
    print("=" * 80)
    print("POSTGRESQL BACKUP STOCK ANALYSIS")
    print("=" * 80)
    
    # Get current database data
    print("Getting current database data...")
    current_data = get_current_stock_data()
    print(f"Current database: {len(current_data)} products")
    
    # Analyze backups
    backup_data = {}
    
    for backup_file in backup_files:
        print(f"\n{'='*60}")
        print(f"Analyzing: {backup_file.name}")
        print('='*60)
        
        # Extract date from filename
        date_match = re.search(r'(\d{8})_(\d{6})', backup_file.name)
        if date_match:
            date_str = f"{date_match.group(1)} {date_match.group(2)}"
            backup_date = datetime.strptime(date_str, "%Y%m%d %H%M%S")
        else:
            backup_date = datetime.fromtimestamp(backup_file.stat().st_mtime)
        
        print(f"Backup date: {backup_date}")
        
        # Extract products
        products = extract_products_from_copy(backup_file)
        print(f"Products found: {len(products)}")
        
        if products:
            # Calculate stock statistics
            total_stock = 0
            stock_values = []
            
            for product in products:
                stock_level = 0
                if 'stock_level' in product and product['stock_level']:
                    try:
                        stock_level = float(product['stock_level'])
                    except:
                        pass
                
                total_stock += stock_level
                if stock_level > 0:
                    stock_values.append(stock_level)
            
            avg_stock = sum(stock_values) / len(stock_values) if stock_values else 0
            
            print(f"Total stock: {total_stock:,.0f}")
            print(f"Products with stock: {len(stock_values)}")
            print(f"Average stock per product: {avg_stock:.2f}")
            
            # Show sample products
            print("\nSample products:")
            for i, product in enumerate(products[:5]):
                stock = product.get('stock_level', '0')
                name = product.get('name', 'Unknown')[:30]
                print(f"  {product.get('id', '?')}: {name} - Stock: {stock}")
        
        backup_data[backup_file.name] = {
            'date': backup_date,
            'products': products,
            'total_products': len(products)
        }
    
    # Compare with current database
    print(f"\n{'='*80}")
    print("COMPARISON WITH CURRENT DATABASE")
    print('='*80)
    
    if current_data:
        current_total_stock = sum(p['stock_level'] for p in current_data.values())
        current_stock_values = [p['stock_level'] for p in current_data.values() if p['stock_level'] > 0]
        current_avg_stock = sum(current_stock_values) / len(current_stock_values) if current_stock_values else 0
        
        print(f"Current Database:")
        print(f"  Total products: {len(current_data)}")
        print(f"  Total stock: {current_total_stock:,.0f}")
        print(f"  Products with stock: {len(current_stock_values)}")
        print(f"  Average stock per product: {current_avg_stock:.2f}")
    
    # Show timeline
    print(f"\n{'='*80}")
    print("BACKUP TIMELINE")
    print('='*80)
    
    for name, data in sorted(backup_data.items(), key=lambda x: x[1]['date']):
        print(f"{data['date']}: {name} ({data['total_products']} products)")

if __name__ == "__main__":
    analyze_stock_changes()

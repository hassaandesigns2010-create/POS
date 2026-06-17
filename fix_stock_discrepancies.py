#!/usr/bin/env python3
"""
Script to identify and fix stock discrepancies between current database and backups
"""

import sys
import os
from pathlib import Path

# Add the app path
sys.path.append('C:/Users/pc/Music/pos_app')

def extract_products_from_copy(file_path):
    """Extract product data from PostgreSQL COPY format"""
    products = {}
    
    try:
        import re
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        in_copy_section = False
        columns = []
        
        for i, line in enumerate(lines):
            if "COPY public.products" in line:
                in_copy_section = True
                # Extract column names
                columns_match = re.search(r'COPY public\.products\s*\(([^)]+)\)', line)
                if columns_match:
                    columns_str = columns_match.group(1)
                    columns = [col.strip().strip('"') for col in columns_str.split(',')]
                continue
            
            if in_copy_section and line.strip() == "\\.":
                break
            
            if in_copy_section and line.strip():
                try:
                    values = line.strip().split('\t')
                    
                    product = {}
                    for j, value in enumerate(values):
                        if j < len(columns):
                            col_name = columns[j]
                            clean_value = value.strip()
                            if clean_value == '\\N':
                                clean_value = None
                            elif clean_value.startswith('"') and clean_value.endswith('"'):
                                clean_value = clean_value[1:-1]
                            product[col_name] = clean_value
                    
                    # Store by ID for easy lookup
                    if 'id' in product:
                        products[product['id']] = product
                    
                except Exception as e:
                    print(f"Error parsing line {i}: {e}")
                    continue
    
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
    
    return products

def get_current_stock_data():
    """Get current stock data from database"""
    try:
        from pos_app.models.database import Product, get_session
        
        session = get_session()
        products = session.query(Product).all()
        
        current_data = {}
        for product in products:
            current_data[str(product.id)] = {
                'name': product.name,
                'stock_level': float(product.stock_level) if product.stock_level else 0.0,
                'sku': product.sku,
                'barcode': product.barcode,
            }
        
        session.close()
        return current_data
    
    except Exception as e:
        print(f"Error getting current database data: {e}")
        return {}

def find_stock_discrepancies():
    """Find products that should have stock but currently show zero"""
    
    print("=" * 80)
    print("STOCK DISCREPANCY ANALYSIS")
    print("=" * 80)
    
    # Get current data
    print("Getting current database data...")
    current_data = get_current_stock_data()
    print(f"Current database: {len(current_data)} products")
    
    # Get the latest backup data
    backup_dir = Path("C:/Users/pc/Documents/backups")
    backup_files = sorted(backup_dir.glob("pos_backup_*.sql"))
    
    if not backup_files:
        print("No backup files found!")
        return
    
    # Use the latest backup
    latest_backup = max(backup_files, key=lambda x: x.stat().st_mtime)
    print(f"Using latest backup: {latest_backup.name}")
    
    backup_products = extract_products_from_copy(latest_backup)
    print(f"Backup contains: {len(backup_products)} products")
    
    # Find discrepancies
    print("\n" + "=" * 80)
    print("PRODUCTS WITH ZERO STOCK THAT SHOULDN'T BE ZERO")
    print("=" * 80)
    
    discrepancies = []
    
    for product_id, current_info in current_data.items():
        if current_info['stock_level'] == 0:
            # Check if this product had stock in backup
            if product_id in backup_products:
                backup_product = backup_products[product_id]
                backup_stock = 0
                
                if 'stock_level' in backup_product and backup_product['stock_level']:
                    try:
                        backup_stock = float(backup_product['stock_level'])
                    except:
                        pass
                
                if backup_stock > 0:
                    discrepancies.append({
                        'id': product_id,
                        'name': current_info['name'],
                        'current_stock': 0,
                        'backup_stock': backup_stock,
                        'sku': current_info['sku'],
                        'barcode': current_info['barcode'],
                    })
    
    # Display discrepancies
    if discrepancies:
        print(f"Found {len(discrepancies)} products with incorrect zero stock:\n")
        
        for i, disc in enumerate(discrepancies, 1):
            print(f"{i}. Product ID: {disc['id']}")
            print(f"   Name: {disc['name']}")
            print(f"   Current Stock: {disc['current_stock']}")
            print(f"   Should Be: {disc['backup_stock']}")
            print(f"   SKU: {disc['sku']}")
            print(f"   Barcode: {disc['barcode']}")
            print()
        
        # Ask if user wants to fix them
        print("Do you want to fix these stock discrepancies? (y/n)")
        # In automated mode, we'll proceed with fixes
        
        return discrepancies
    else:
        print("No stock discrepancies found. All products with zero stock should be zero.")
        return []

def fix_stock_discrepancies(discrepancies):
    """Fix the stock discrepancies by updating the database"""
    
    if not discrepancies:
        print("No discrepancies to fix.")
        return
    
    print("\n" + "=" * 80)
    print("FIXING STOCK DISCREPANCIES")
    print("=" * 80)
    
    try:
        from pos_app.models.database import Product, get_session
        
        session = get_session()
        fixed_count = 0
        
        for disc in discrepancies:
            try:
                product = session.query(Product).filter(Product.id == int(disc['id'])).first()
                if product:
                    old_stock = product.stock_level or 0
                    product.stock_level = disc['backup_stock']
                    
                    print(f"Fixed: {disc['name']} (ID: {disc['id']})")
                    print(f"  Stock: {old_stock} → {disc['backup_stock']}")
                    print()
                    
                    fixed_count += 1
                else:
                    print(f"Product not found: ID {disc['id']}")
            
            except Exception as e:
                print(f"Error fixing product {disc['id']}: {e}")
        
        # Commit all changes
        session.commit()
        session.close()
        
        print(f"Successfully fixed {fixed_count} products!")
        
    except Exception as e:
        print(f"Error during database update: {e}")

if __name__ == "__main__":
    discrepancies = find_stock_discrepancies()
    
    if discrepancies:
        print(f"\nFound {len(discrepancies)} products that need stock fixes.")
        print("Proceeding with automatic fixes...")
        fix_stock_discrepancies(discrepancies)
    else:
        print("No stock fixes needed.")

"""
Compare all backup files and restore the best stock levels for products with zero stock.

This script:
1. Reads ALL backup files in the backups folder
2. For each product, finds the maximum stock level across all backups
3. Updates products that currently have zero stock with the best backup value
"""

import re
import psycopg2
import os
from datetime import datetime
from pathlib import Path

# Database connection parameters
DB_CONFIG = {
    'dbname': 'pos_network',
    'user': 'admin',
    'password': 'admin',
    'host': 'localhost',
    'port': '5432'
}

BACKUP_DIR = r'F:\pos_app\backups'

def parse_backup_file(backup_file):
    """Extract product stock data from a single backup file"""
    print(f"  Reading: {os.path.basename(backup_file)}")
    
    try:
        with open(backup_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"    ❌ Error reading file: {e}")
        return {}
    
    # Find the COPY products section
    copy_pattern = r'COPY public\.products \((.*?)\) FROM stdin;(.*?)\\\\.'
    match = re.search(copy_pattern, content, re.DOTALL)
    
    if not match:
        print(f"    ⚠️  No products data found")
        return {}
    
    columns_str = match.group(1)
    data_str = match.group(2)
    
    # Parse column names
    columns = [col.strip() for col in columns_str.split(',')]
    
    # Find indices for important columns
    try:
        id_idx = columns.index('id')
        name_idx = columns.index('name')
        warehouse_idx = columns.index('warehouse_stock') if 'warehouse_stock' in columns else None
        retail_idx = columns.index('retail_stock') if 'retail_stock' in columns else None
        stock_idx = columns.index('stock_level') if 'stock_level' in columns else None
    except ValueError:
        print(f"    ⚠️  Missing required columns")
        return {}
    
    # Parse data rows
    stock_data = {}
    lines = [line.strip() for line in data_str.strip().split('\n') if line.strip()]
    
    for line in lines:
        values = line.split('\t')
        
        if len(values) <= max(id_idx, name_idx):
            continue
        
        try:
            product_id = int(values[id_idx])
            product_name = values[name_idx]
            
            # Calculate total stock from backup
            warehouse_stock = 0
            retail_stock = 0
            stock_level = 0
            
            if warehouse_idx is not None and warehouse_idx < len(values):
                try:
                    ws = values[warehouse_idx]
                    warehouse_stock = int(ws) if ws and ws != '\\N' else 0
                except (ValueError, IndexError):
                    warehouse_stock = 0
            
            if retail_idx is not None and retail_idx < len(values):
                try:
                    rs = values[retail_idx]
                    retail_stock = int(rs) if rs and rs != '\\N' else 0
                except (ValueError, IndexError):
                    retail_stock = 0
            
            if stock_idx is not None and stock_idx < len(values):
                try:
                    sl = values[stock_idx]
                    stock_level = int(sl) if sl and sl != '\\N' else 0
                except (ValueError, IndexError):
                    stock_level = 0
            
            # Use the maximum of all three values
            backup_stock = max(warehouse_stock + retail_stock, stock_level)
            
            stock_data[product_id] = {
                'name': product_name,
                'stock': backup_stock
            }
            
        except (ValueError, IndexError):
            continue
    
    print(f"    ✓ Found {len(stock_data)} products")
    return stock_data

def get_all_backups():
    """Get all backup files sorted by date (newest first)"""
    backup_files = []
    
    for file in Path(BACKUP_DIR).glob('*.sql'):
        backup_files.append(str(file))
    
    # Sort by filename (which includes timestamp)
    backup_files.sort(reverse=True)
    return backup_files

def merge_backup_data(backup_files):
    """Merge stock data from all backups, keeping the maximum stock for each product"""
    print(f"\n📂 Processing {len(backup_files)} backup files...")
    
    merged_data = {}
    
    for backup_file in backup_files:
        stock_data = parse_backup_file(backup_file)
        
        for product_id, data in stock_data.items():
            if product_id not in merged_data:
                merged_data[product_id] = data
            else:
                # Keep the maximum stock value
                if data['stock'] > merged_data[product_id]['stock']:
                    merged_data[product_id] = data
    
    print(f"\n✓ Merged data for {len(merged_data)} unique products")
    return merged_data

def fix_zero_stock_products(merged_data):
    """Update products with zero stock using the best backup value"""
    print(f"\n🔄 Connecting to database...")
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Get products with zero or null stock
        cursor.execute("""
            SELECT id, name, stock_level 
            FROM products 
            WHERE stock_level IS NULL OR stock_level = 0
            ORDER BY id
        """)
        zero_stock_products = cursor.fetchall()
        
        print(f"✓ Found {len(zero_stock_products)} products with zero/null stock")
        
        if len(zero_stock_products) == 0:
            print("\n✅ No products with zero stock found!")
            cursor.close()
            conn.close()
            return True
        
        # Statistics
        updated_count = 0
        no_backup_count = 0
        
        print(f"\n📊 Fixing zero stock products...")
        print(f"{'ID':<6} {'Product Name':<40} {'Current':<10} {'Best Backup':<12} {'Action':<15}")
        print("=" * 90)
        
        for product_id, product_name, current_stock in zero_stock_products:
            current_stock = current_stock or 0
            
            if product_id in merged_data:
                backup_stock = merged_data[product_id]['stock']
                
                if backup_stock > 0:
                    # Update stock level
                    cursor.execute(
                        "UPDATE products SET stock_level = %s WHERE id = %s",
                        (backup_stock, product_id)
                    )
                    updated_count += 1
                    print(f"{product_id:<6} {product_name[:38]:<40} {current_stock:<10} {backup_stock:<12} ✓ Updated")
                else:
                    print(f"{product_id:<6} {product_name[:38]:<40} {current_stock:<10} {backup_stock:<12} ⊘ Also zero")
            else:
                # No backup data for this product
                no_backup_count += 1
                print(f"{product_id:<6} {product_name[:38]:<40} {current_stock:<10} {'N/A':<12} ⊕ New product")
        
        # Commit changes
        conn.commit()
        
        print("\n" + "=" * 90)
        print(f"\n✅ Zero stock fix complete!")
        print(f"   • Updated: {updated_count} products")
        print(f"   • No backup data: {no_backup_count} products")
        print(f"   • Total processed: {len(zero_stock_products)}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

def main():
    """Main execution"""
    print("=" * 90)
    print("🔧 FIX ZERO STOCK PRODUCTS FROM ALL BACKUPS")
    print("=" * 90)
    print(f"Backup Directory: {BACKUP_DIR}")
    print(f"Database: {DB_CONFIG['dbname']} @ {DB_CONFIG['host']}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 90)
    
    # Step 1: Get all backup files
    backup_files = get_all_backups()
    
    if not backup_files:
        print("\n❌ No backup files found!")
        return False
    
    print(f"\n✓ Found {len(backup_files)} backup files")
    
    # Step 2: Merge data from all backups
    merged_data = merge_backup_data(backup_files)
    
    if not merged_data:
        print("\n❌ Failed to extract stock data from backups")
        return False
    
    # Step 3: Fix zero stock products
    success = fix_zero_stock_products(merged_data)
    
    if success:
        print(f"\n✅ All done! Zero stock products have been fixed using the best backup values.")
    else:
        print(f"\n❌ Fix failed. Please check the error messages above.")
    
    return success

if __name__ == '__main__':
    main()

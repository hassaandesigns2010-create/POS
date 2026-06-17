"""
Restore stock levels from the latest PostgreSQL backup
while preserving new products in the current database.

This script:
1. Reads the latest backup file
2. Extracts stock data (warehouse_stock + retail_stock) for each product
3. Updates only existing products in the current database
4. Preserves all new products that weren't in the backup
"""

import re
import psycopg2
from datetime import datetime

# Database connection parameters
DB_CONFIG = {
    'dbname': 'pos_network',
    'user': 'admin',
    'password': 'admin',
    'host': 'localhost',
    'port': '5432'
}

BACKUP_FILE = r'F:\pos_app\backups\pos_backup_20260126_192834.sql'

def parse_backup_stock_data(backup_file):
    """Extract product stock data from backup file"""
    print(f"\n📂 Reading backup file: {backup_file}")
    
    with open(backup_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the COPY products section
    copy_pattern = r'COPY public\.products \((.*?)\) FROM stdin;(.*?)\\\\.'
    match = re.search(copy_pattern, content, re.DOTALL)
    
    if not match:
        print("❌ Could not find products data in backup")
        return {}
    
    columns_str = match.group(1)
    data_str = match.group(2)
    
    # Parse column names
    columns = [col.strip() for col in columns_str.split(',')]
    print(f"✓ Found {len(columns)} columns in backup")
    
    # Find indices for important columns
    try:
        id_idx = columns.index('id')
        name_idx = columns.index('name')
        warehouse_idx = columns.index('warehouse_stock') if 'warehouse_stock' in columns else None
        retail_idx = columns.index('retail_stock') if 'retail_stock' in columns else None
        stock_idx = columns.index('stock_level') if 'stock_level' in columns else None
    except ValueError as e:
        print(f"❌ Missing required column: {e}")
        return {}
    
    print(f"✓ Column indices - ID: {id_idx}, Name: {name_idx}, Warehouse: {warehouse_idx}, Retail: {retail_idx}, Stock: {stock_idx}")
    
    # Parse data rows
    stock_data = {}
    lines = [line.strip() for line in data_str.strip().split('\n') if line.strip()]
    
    for line in lines:
        # Split by tab
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
            
            # Use the maximum of all three values as the backup stock
            backup_stock = max(warehouse_stock + retail_stock, stock_level)
            
            stock_data[product_id] = {
                'name': product_name,
                'stock': backup_stock
            }
            
        except (ValueError, IndexError) as e:
            continue
    
    print(f"✓ Extracted stock data for {len(stock_data)} products from backup")
    return stock_data

def restore_stock_levels(stock_data):
    """Update stock levels in current database"""
    print(f"\n🔄 Connecting to database...")
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Get current products
        cursor.execute("SELECT id, name, stock_level FROM products ORDER BY id")
        current_products = cursor.fetchall()
        
        print(f"✓ Found {len(current_products)} products in current database")
        
        # Statistics
        updated_count = 0
        skipped_new = 0
        skipped_same = 0
        
        print(f"\n📊 Processing stock updates...")
        print(f"{'ID':<6} {'Product Name':<40} {'Current':<10} {'Backup':<10} {'Action':<15}")
        print("=" * 85)
        
        for product_id, product_name, current_stock in current_products:
            current_stock = current_stock or 0
            
            if product_id in stock_data:
                backup_stock = stock_data[product_id]['stock']
                
                if current_stock != backup_stock:
                    # Update stock level
                    cursor.execute(
                        "UPDATE products SET stock_level = %s WHERE id = %s",
                        (backup_stock, product_id)
                    )
                    updated_count += 1
                    action = f"✓ {current_stock} → {backup_stock}"
                    print(f"{product_id:<6} {product_name[:38]:<40} {current_stock:<10} {backup_stock:<10} {action:<15}")
                else:
                    skipped_same += 1
            else:
                # Product not in backup - it's a new product, keep current stock
                skipped_new += 1
                print(f"{product_id:<6} {product_name[:38]:<40} {current_stock:<10} {'N/A':<10} {'⊕ New Product':<15}")
        
        # Commit changes
        conn.commit()
        
        print("\n" + "=" * 85)
        print(f"\n✅ Stock restoration complete!")
        print(f"   • Updated: {updated_count} products")
        print(f"   • Unchanged (same stock): {skipped_same} products")
        print(f"   • Preserved (new products): {skipped_new} products")
        print(f"   • Total products: {len(current_products)}")
        
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
    print("=" * 85)
    print("🔧 STOCK LEVEL RESTORATION FROM BACKUP")
    print("=" * 85)
    print(f"Backup File: {BACKUP_FILE}")
    print(f"Database: {DB_CONFIG['dbname']} @ {DB_CONFIG['host']}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 85)
    
    # Step 1: Parse backup
    stock_data = parse_backup_stock_data(BACKUP_FILE)
    
    if not stock_data:
        print("\n❌ Failed to extract stock data from backup")
        return False
    
    # Step 2: Restore stock levels
    success = restore_stock_levels(stock_data)
    
    if success:
        print(f"\n✅ All done! Stock levels have been restored from backup.")
        print(f"   New products added after the backup have been preserved.")
    else:
        print(f"\n❌ Stock restoration failed. Please check the error messages above.")
    
    return success

if __name__ == '__main__':
    main()

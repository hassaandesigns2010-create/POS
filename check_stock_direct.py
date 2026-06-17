#!/usr/bin/env python3
"""
Direct PostgreSQL stock analysis - bypass import issues
"""

import os
import sys
import psycopg2
import json
from datetime import datetime
from collections import defaultdict

def load_db_config():
    """Load database configuration from config file"""
    config_file = os.path.join(os.path.dirname(__file__), 'config', 'database.json')
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except:
        # Default config
        return {
            'host': 'localhost',
            'port': 5432,
            'database': 'pos_system',
            'username': 'postgres',
            'password': 'admin'
        }

def connect_to_postgres():
    """Connect to PostgreSQL database"""
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
        print(f"❌ Failed to connect to PostgreSQL: {e}")
        print(f"Config: {config}")
        return None

def analyze_current_stock(conn):
    """Analyze current stock in PostgreSQL"""
    print("\n=== ANALYZING CURRENT POSTGRESQL DATABASE ===")
    
    try:
        cursor = conn.cursor()
        
        # Get total products count
        cursor.execute("SELECT COUNT(*) FROM products")
        total_products = cursor.fetchone()[0]
        print(f"Total products in database: {total_products}")
        
        # Get stock analysis
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN stock = 0 OR stock IS NULL THEN 1 END) as zero_stock,
                COUNT(CASE WHEN stock > 0 AND stock < 10 THEN 1 END) as low_stock,
                COUNT(CASE WHEN stock >= 10 THEN 1 END) as normal_stock,
                MIN(stock) as min_stock,
                MAX(stock) as max_stock,
                AVG(stock) as avg_stock
            FROM products
        """)
        
        stats = cursor.fetchone()
        print(f"\n📊 STOCK STATISTICS:")
        print(f"  Total products: {stats[0]}")
        print(f"  🔴 Zero stock: {stats[1]}")
        print(f"  🟡 Low stock (1-9): {stats[2]}")
        print(f"  🟢 Normal stock (10+): {stats[3]}")
        print(f"  Min stock: {stats[4]}")
        print(f"  Max stock: {stats[5]}")
        print(f"  Average stock: {stats[6]:.2f}")
        
        # Get stock distribution
        cursor.execute("""
            SELECT 
                CASE 
                    WHEN stock = 0 OR stock IS NULL THEN 'Zero'
                    WHEN stock <= 5 THEN '1-5'
                    WHEN stock <= 10 THEN '6-10'
                    WHEN stock <= 50 THEN '11-50'
                    WHEN stock <= 100 THEN '51-100'
                    ELSE '100+'
                END as stock_range,
                COUNT(*) as count
            FROM products
            GROUP BY stock_range
            ORDER BY 
                CASE stock_range
                    WHEN 'Zero' THEN 1
                    WHEN '1-5' THEN 2
                    WHEN '6-10' THEN 3
                    WHEN '11-50' THEN 4
                    WHEN '51-100' THEN 5
                    ELSE 6
                END
        """)
        
        distribution = cursor.fetchall()
        print(f"\n📈 STOCK DISTRIBUTION:")
        for range_name, count in distribution:
            emoji = "🔴" if range_name == "Zero" else "🟡" if range_name in ["1-5", "6-10"] else "🟢"
            print(f"  {emoji} {range_name}: {count} items")
        
        # Get sample of zero-stock items
        if stats[1] > 0:
            cursor.execute("""
                SELECT id, name, barcode, category_id, stock, sale_price
                FROM products 
                WHERE stock = 0 OR stock IS NULL
                ORDER BY id
                LIMIT 15
            """)
            
            zero_stock_items = cursor.fetchall()
            print(f"\n🔍 SAMPLE ZERO-STOCK ITEMS (first 15 of {stats[1]}):")
            for i, item in enumerate(zero_stock_items, 1):
                print(f"  {i:2d}. ID:{item[0]:4d} | Name:{item[1][:30]:30s} | Barcode:{item[2]:12s} | Price:{item[5]:8.2f}")
        
        return {
            'total_products': stats[0],
            'zero_stock': stats[1],
            'low_stock': stats[2],
            'normal_stock': stats[3],
            'min_stock': stats[4],
            'max_stock': stats[5],
            'avg_stock': stats[6],
            'distribution': dict(distribution)
        }
        
    except Exception as e:
        print(f"❌ Error analyzing stock: {e}")
        return None

def check_recent_transactions(conn):
    """Check recent transactions that might have affected stock"""
    print("\n=== CHECKING RECENT TRANSACTIONS ===")
    
    try:
        cursor = conn.cursor()
        
        # Check recent sales
        cursor.execute("""
            SELECT COUNT(*) as total_sales, 
                   MAX(created_at) as latest_sale,
                   SUM(total_amount) as total_sales_amount
            FROM sales 
            WHERE created_at >= NOW() - INTERVAL '7 days'
        """)
        
        sales_data = cursor.fetchone()
        print(f"📅 Recent Sales (last 7 days):")
        print(f"  Total sales: {sales_data[0]}")
        print(f"  Latest sale: {sales_data[1]}")
        print(f"  Total amount: {sales_data[2]:.2f}" if sales_data[2] else "  Total amount: 0.00")
        
        # Check recent purchases
        cursor.execute("""
            SELECT COUNT(*) as total_purchases,
                   MAX(created_at) as latest_purchase,
                   SUM(total_amount) as total_purchase_amount
            FROM purchases 
            WHERE created_at >= NOW() - INTERVAL '7 days'
        """)
        
        purchase_data = cursor.fetchone()
        print(f"\n📦 Recent Purchases (last 7 days):")
        print(f"  Total purchases: {purchase_data[0]}")
        print(f"  Latest purchase: {purchase_data[1]}")
        print(f"  Total amount: {purchase_data[2]:.2f}" if purchase_data[2] else "  Total amount: 0.00")
        
        # Check for any stock adjustment operations
        cursor.execute("""
            SELECT COUNT(*) as adjustments
            FROM stock_adjustments 
            WHERE created_at >= NOW() - INTERVAL '7 days'
        """)
        
        adj_data = cursor.fetchone()
        print(f"\n🔧 Recent Stock Adjustments (last 7 days): {adj_data[0]}")
        
    except Exception as e:
        print(f"❌ Error checking transactions: {e}")

def analyze_backup_comparison(conn):
    """Compare current stock with backup data"""
    print("\n=== BACKUP COMPARISON ===")
    
    backup_dir = os.path.join(os.path.dirname(__file__), 'backups')
    if not os.path.exists(backup_dir):
        print("❌ No backups directory found")
        return
    
    backup_files = [f for f in os.listdir(backup_dir) if f.endswith('.sql')]
    backup_files.sort()
    
    if not backup_files:
        print("❌ No backup files found")
        return
    
    print(f"📁 Found {len(backup_files)} backup files")
    
    # Check the most recent backup
    latest_backup = backup_files[-1]
    backup_path = os.path.join(backup_dir, latest_backup)
    
    print(f"🔍 Analyzing latest backup: {latest_backup}")
    
    try:
        with open(backup_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Count products in backup
        product_inserts = content.count("INSERT INTO products")
        print(f"📊 Backup contains {product_inserts} product insert operations")
        
        # Look for stock values in backup
        lines = content.split('\n')
        zero_stock_in_backup = 0
        total_products_in_backup = 0
        
        for line in lines:
            if 'INSERT INTO products' in line and 'VALUES' in line:
                # Simple parsing for stock values (assuming stock is 8th column)
                values_part = line.split('VALUES')[1]
                if values_part:
                    # Count records in this insert
                    records = values_part.count('(')
                    total_products_in_backup += records
                    
                    # Look for zero stock patterns (simplified)
                    zero_patterns = values_part.count(', 0,') + values_part.count(', NULL,')
                    zero_stock_in_backup += zero_patterns
        
        print(f"📈 Backup stock analysis:")
        print(f"  Estimated total products: {total_products_in_backup}")
        print(f"  Estimated zero stock: {zero_stock_in_backup}")
        
    except Exception as e:
        print(f"❌ Error analyzing backup: {e}")

def generate_recommendations(stock_data):
    """Generate recommendations based on analysis"""
    print("\n=== 📋 RECOMMENDATIONS ===")
    
    if not stock_data:
        print("❌ No stock data available for recommendations")
        return
    
    zero_stock_pct = (stock_data['zero_stock'] / stock_data['total_products']) * 100
    
    print(f"🔍 Current Situation:")
    print(f"  • {stock_data['zero_stock']} items have zero stock ({zero_stock_pct:.1f}%)")
    print(f"  • {stock_data['low_stock']} items have low stock")
    print(f"  • {stock_data['normal_stock']} items have normal stock")
    
    if zero_stock_pct > 50:
        print(f"\n⚠️  CRITICAL: More than 50% of products have zero stock!")
        print(f"   Recommendations:")
        print(f"   1. 🚨 IMMEDIATE ACTION REQUIRED")
        print(f"   2. Check for data corruption or calculation errors")
        print(f"   3. Restore from recent backup if available")
        print(f"   4. Review stock calculation logic")
        print(f"   5. Check for recent bulk operations")
    elif zero_stock_pct > 25:
        print(f"\n⚠️  HIGH: More than 25% of products have zero stock!")
        print(f"   Recommendations:")
        print(f"   1. Investigate recent stock changes")
        print(f"   2. Check purchase/sale operations")
        print(f"   3. Consider partial restoration")
        print(f"   4. Review stock adjustment logs")
    elif zero_stock_pct > 10:
        print(f"\n⚠️  MEDIUM: More than 10% of products have zero stock")
        print(f"   Recommendations:")
        print(f"   1. Monitor stock levels closely")
        print(f"   2. Check for systematic issues")
        print(f"   3. Review inventory management process")
    else:
        print(f"\n✅ LOW: Zero stock percentage is within normal range")
        print(f"   Recommendations:")
        print(f"   1. Regular stock monitoring")
        print(f"   2. Preventive inventory management")
    
    print(f"\n🔧 IMMEDIATE ACTIONS:")
    print(f"   1. Check recent sales that might have depleted stock")
    print(f"   2. Verify stock calculation formulas")
    print(f"   3. Review database integrity")
    print(f"   4. Check for any failed purchase operations")
    print(f"   5. Consider running stock reconciliation")

def main():
    print("=" * 60)
    print("🔍 POSTGRESQL STOCK ISSUE ANALYSIS")
    print("=" * 60)
    print(f"Started at: {datetime.now()}")
    
    # Connect to database
    conn = connect_to_postgres()
    if not conn:
        print("❌ Cannot proceed without database connection")
        return
    
    try:
        # Analyze current stock
        stock_data = analyze_current_stock(conn)
        
        # Check recent transactions
        check_recent_transactions(conn)
        
        # Compare with backups
        analyze_backup_comparison(conn)
        
        # Generate recommendations
        generate_recommendations(stock_data)
        
        # Save report
        report_file = f"stock_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_file, 'w') as f:
            f.write(f"PostgreSQL Stock Analysis Report\n")
            f.write(f"Generated: {datetime.now()}\n")
            f.write(f"{'='*50}\n")
            if stock_data:
                f.write(f"Total Products: {stock_data['total_products']}\n")
                f.write(f"Zero Stock: {stock_data['zero_stock']}\n")
                f.write(f"Low Stock: {stock_data['low_stock']}\n")
                f.write(f"Normal Stock: {stock_data['normal_stock']}\n")
        
        print(f"\n📄 Report saved to: {report_file}")
        
    finally:
        conn.close()
        print(f"\n✅ Analysis completed at: {datetime.now()}")

if __name__ == "__main__":
    main()

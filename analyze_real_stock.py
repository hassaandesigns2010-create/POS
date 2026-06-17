#!/usr/bin/env python3
"""
Analyze actual stock columns in PostgreSQL database
"""

import os
import sys
import psycopg2
import json
from datetime import datetime
from collections import defaultdict

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

def analyze_all_stock_columns(conn):
    """Analyze all stock-related columns"""
    print("=== COMPREHENSIVE STOCK ANALYSIS ===")
    
    stock_columns = ['warehouse_stock', 'retail_stock', 'stock_level']
    
    try:
        cursor = conn.cursor()
        
        # Get total products
        cursor.execute("SELECT COUNT(*) FROM products")
        total_products = cursor.fetchone()[0]
        print(f"📦 Total products in database: {total_products}")
        
        # Analyze each stock column
        stock_analysis = {}
        
        for col in stock_columns:
            print(f"\n📊 Analyzing {col}:")
            
            cursor.execute(f"""
                SELECT 
                    COUNT(*) as total_with_data,
                    COUNT(CASE WHEN {col} = 0 OR {col} IS NULL THEN 1 END) as zero_stock,
                    COUNT(CASE WHEN {col} > 0 AND {col} < 10 THEN 1 END) as low_stock,
                    COUNT(CASE WHEN {col} >= 10 THEN 1 END) as normal_stock,
                    MIN({col}) as min_stock,
                    MAX({col}) as max_stock,
                    AVG({col}) as avg_stock
                FROM products
            """)
            
            stats = cursor.fetchone()
            
            # Calculate percentages
            zero_pct = (stats[1] / total_products) * 100 if total_products > 0 else 0
            low_pct = (stats[2] / total_products) * 100 if total_products > 0 else 0
            normal_pct = (stats[3] / total_products) * 100 if total_products > 0 else 0
            
            print(f"  📈 With data: {stats[0]} ({(stats[0]/total_products)*100:.1f}%)")
            print(f"  🔴 Zero stock: {stats[1]} ({zero_pct:.1f}%)")
            print(f"  🟡 Low stock (1-9): {stats[2]} ({low_pct:.1f}%)")
            print(f"  🟢 Normal stock (10+): {stats[3]} ({normal_pct:.1f}%)")
            print(f"  📏 Range: {stats[4]} to {stats[5]}")
            print(f"  📊 Average: {stats[6]:.2f}" if stats[6] else "  📊 Average: N/A")
            
            stock_analysis[col] = {
                'total_with_data': stats[0],
                'zero_stock': stats[1],
                'low_stock': stats[2],
                'normal_stock': stats[3],
                'min_stock': stats[4],
                'max_stock': stats[5],
                'avg_stock': stats[6],
                'zero_percentage': zero_pct,
                'low_percentage': low_pct,
                'normal_percentage': normal_pct
            }
        
        # Determine which stock column should be used
        print(f"\n🎯 RECOMMENDED STOCK COLUMN:")
        
        best_column = None
        best_score = 0
        
        for col, analysis in stock_analysis.items():
            # Score based on data coverage and reasonable stock levels
            coverage_score = analysis['total_with_data'] / total_products
            zero_penalty = analysis['zero_percentage'] / 100  # Lower zero stock is better
            
            score = coverage_score - zero_penalty
            print(f"  {col}: Score {score:.3f} (Coverage: {coverage_score:.3f}, Zero penalty: {zero_penalty:.3f})")
            
            if score > best_score:
                best_score = score
                best_column = col
        
        if best_column:
            print(f"\n✅ Best column to use: {best_column}")
            return best_column, stock_analysis
        else:
            print(f"\n❌ No suitable stock column found")
            return None, stock_analysis
        
    except Exception as e:
        print(f"❌ Error analyzing stock: {e}")
        return None, {}

def show_zero_stock_details(conn, stock_column):
    """Show details of zero-stock items"""
    print(f"\n🔍 ZERO STOCK DETAILS (using {stock_column}):")
    
    try:
        cursor = conn.cursor()
        
        # Get zero stock items
        cursor.execute(f"""
            SELECT id, name, barcode, retail_price, {stock_column}
            FROM products 
            WHERE {stock_column} = 0 OR {stock_column} IS NULL
            ORDER BY id
            LIMIT 20
        """)
        
        zero_items = cursor.fetchall()
        
        # Count total zero stock items
        cursor.execute(f"""
            SELECT COUNT(*) FROM products 
            WHERE {stock_column} = 0 OR {stock_column} IS NULL
        """)
        total_zero = cursor.fetchone()[0]
        
        print(f"📊 Total zero-stock items: {total_zero}")
        print(f"\n📋 First 20 zero-stock items:")
        
        for i, item in enumerate(zero_items, 1):
            product_id = item[0]
            name = item[1][:40] if item[1] else "No Name"
            barcode = item[2] if item[2] else "No Barcode"
            price = item[3] if item[3] else 0
            stock = item[4] if item[4] is not None else "NULL"
            
            print(f"  {i:2d}. ID:{product_id:4d} | {name:40s} | {barcode:12s} | Price:{price:8.2f} | Stock:{stock}")
        
        if total_zero > 20:
            print(f"  ... and {total_zero - 20} more items")
        
        return total_zero
        
    except Exception as e:
        print(f"❌ Error getting zero stock details: {e}")
        return 0

def check_stock_calculation_logic(conn, stock_column):
    """Check how stock should be calculated"""
    print(f"\n🔧 STOCK CALCULATION ANALYSIS:")
    
    try:
        cursor = conn.cursor()
        
        # Check if there are sales/purchases that affect stock
        cursor.execute("SELECT COUNT(*) FROM sales")
        sales_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM purchases")
        purchases_count = cursor.fetchone()[0]
        
        print(f"📊 Sales records: {sales_count}")
        print(f"📦 Purchase records: {purchases_count}")
        
        # Check for stock adjustment tables
        cursor.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND (table_name LIKE '%stock%' OR table_name LIKE '%adjustment%' OR table_name LIKE '%inventory%')
        """)
        
        stock_tables = cursor.fetchall()
        if stock_tables:
            print(f"📋 Stock-related tables:")
            for table in stock_tables:
                print(f"  • {table[0]}")
                
                # Check if this table has recent data
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
                    count = cursor.fetchone()[0]
                    print(f"    Records: {count}")
                except:
                    print(f"    Unable to count records")
        
        # Determine the correct stock calculation logic
        print(f"\n💡 STOCK CALCULATION RECOMMENDATIONS:")
        
        if stock_column == 'stock_level':
            print(f"  ✅ 'stock_level' appears to be the main stock column")
            print(f"     This should be used for all stock operations")
        elif stock_column == 'retail_stock':
            print(f"  ✅ 'retail_stock' has good data coverage")
            print(f"     Use this for retail operations")
        elif stock_column == 'warehouse_stock':
            print(f"  ⚠️  'warehouse_stock' has mostly zero values")
            print(f"     This might be for warehouse inventory only")
        
        print(f"\n🔧 SUGGESTED FIXES:")
        print(f"  1. Update application to use '{stock_column}' instead of 'stock'")
        print(f"  2. Ensure stock calculations update the correct column")
        print(f"  3. Verify sales/purchase operations affect stock properly")
        print(f"  4. Consider data migration if needed")
        
    except Exception as e:
        print(f"❌ Error checking stock logic: {e}")

def compare_with_backups(stock_column):
    """Compare current stock with backup data"""
    print(f"\n📁 BACKUP COMPARISON:")
    
    backup_dir = os.path.join(os.path.dirname(__file__), 'backups')
    if not os.path.exists(backup_dir):
        print("❌ No backups directory found")
        return
    
    backup_files = [f for f in os.listdir(backup_dir) if f.endswith('.sql')]
    backup_files.sort()
    
    if not backup_files:
        print("❌ No backup files found")
        return
    
    # Check the most recent backup
    latest_backup = backup_files[-1]
    backup_path = os.path.join(backup_dir, latest_backup)
    
    print(f"🔍 Analyzing latest backup: {latest_backup}")
    
    try:
        with open(backup_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Look for the stock column in backup
        if stock_column in content:
            print(f"✅ Found '{stock_column}' column in backup")
            
            # Simple count of stock values in backup
            lines = content.split('\n')
            stock_values = []
            
            for line in lines:
                if 'INSERT INTO products' in line and stock_column in line:
                    # This is a simplified analysis
                    parts = line.split(stock_column)
                    if len(parts) > 1:
                        # Extract the value after the column name
                        remaining = parts[1]
                        if remaining.startswith(','):
                            remaining = remaining[1:]
                        # Get the value up to the next comma
                        if ',' in remaining:
                            value_str = remaining.split(',')[0].strip()
                            try:
                                value = float(value_str)
                                stock_values.append(value)
                            except:
                                pass
            
            if stock_values:
                zero_in_backup = sum(1 for v in stock_values if v == 0)
                print(f"📊 Backup stock analysis:")
                print(f"  Total stock values found: {len(stock_values)}")
                print(f"  Zero stock in backup: {zero_in_backup}")
                print(f"  Zero percentage: {(zero_in_backup/len(stock_values))*100:.1f}%")
            else:
                print(f"⚠️  Could not extract stock values from backup")
        else:
            print(f"❌ '{stock_column}' not found in backup")
            print(f"   This might indicate a schema change occurred")
        
    except Exception as e:
        print(f"❌ Error analyzing backup: {e}")

def main():
    print("=" * 70)
    print("🔍 REAL STOCK COLUMN ANALYSIS")
    print("=" * 70)
    print(f"Started at: {datetime.now()}")
    
    conn = connect_to_postgres()
    if not conn:
        print("❌ Cannot connect to database")
        return
    
    try:
        # Analyze all stock columns
        best_column, stock_analysis = analyze_all_stock_columns(conn)
        
        if best_column:
            # Show zero stock details
            total_zero = show_zero_stock_details(conn, best_column)
            
            # Check stock calculation logic
            check_stock_calculation_logic(conn, best_column)
            
            # Compare with backups
            compare_with_backups(best_column)
            
            # Final recommendations
            print(f"\n" + "="*70)
            print(f"📋 FINAL ANALYSIS & RECOMMENDATIONS")
            print(f"="*70)
            
            print(f"\n🎯 ISSUE IDENTIFIED:")
            print(f"  • The application is looking for 'stock' column")
            print(f"  • But the database has: {list(stock_analysis.keys())}")
            print(f"  • Best column to use: '{best_column}'")
            print(f"  • Total zero-stock items: {total_zero}")
            
            zero_pct = (total_zero / 4679) * 100  # Total products from schema check
            
            if zero_pct > 50:
                print(f"\n🚨 CRITICAL SITUATION:")
                print(f"  • {zero_pct:.1f}% of products have zero stock!")
                print(f"  • This indicates a serious data or calculation issue")
            elif zero_pct > 25:
                print(f"\n⚠️  HIGH PRIORITY:")
                print(f"  • {zero_pct:.1f}% of products have zero stock")
                print(f"  • Immediate attention required")
            else:
                print(f"\n✅ MANAGEABLE:")
                print(f"  • {zero_pct:.1f}% of products have zero stock")
                print(f"  • Normal inventory situation")
            
            print(f"\n🔧 IMMEDIATE ACTIONS:")
            print(f"  1. Update all SQL queries to use '{best_column}' instead of 'stock'")
            print(f"  2. Update Python models to reference the correct column")
            print(f"  3. Test stock calculation in sales/purchase operations")
            print(f"  4. Verify stock updates are working correctly")
            
            print(f"\n📄 FILES TO CHECK:")
            print(f"  • models/product.py - Update Product model")
            print(f"  • controllers/business_logic.py - Update stock calculations")
            print(f"  • views/sales.py - Update stock display logic")
            print(f"  • Any SQL queries using 'stock' column")
        
        else:
            print(f"\n❌ CRITICAL ERROR:")
            print(f"  No suitable stock column found!")
            print(f"  The database schema needs immediate attention")
        
        # Save detailed report
        report_file = f"real_stock_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_file, 'w') as f:
            f.write(f"Real Stock Analysis Report\n")
            f.write(f"Generated: {datetime.now()}\n")
            f.write(f"Best stock column: {best_column}\n")
            f.write(f"Total zero-stock items: {total_zero}\n")
            if stock_analysis:
                f.write(f"\nStock column analysis:\n")
                for col, data in stock_analysis.items():
                    f.write(f"{col}: {data}\n")
        
        print(f"\n📄 Detailed report saved to: {report_file}")
        
    finally:
        conn.close()
        print(f"\n✅ Analysis completed at: {datetime.now()}")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Check PostgreSQL database schema directly
"""

import os
import sys
import psycopg2
import json

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

def check_schema(conn):
    """Check database schema"""
    print("=== POSTGRESQL SCHEMA ANALYSIS ===")
    
    try:
        cursor = conn.cursor()
        
        # Check if products table exists
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name = 'products'
        """)
        
        if not cursor.fetchone():
            print("❌ Products table does not exist!")
            return
        
        print("✅ Products table exists")
        
        # Get columns in products table
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'products' AND table_schema = 'public'
            ORDER BY ordinal_position
        """)
        
        columns = cursor.fetchall()
        print(f"\n📋 Products table has {len(columns)} columns:")
        
        stock_columns = []
        for col in columns:
            col_name = col[0]
            data_type = col[1]
            nullable = col[2]
            default = col[3]
            
            print(f"  • {col_name}: {data_type} ({'NULL' if nullable == 'YES' else 'NOT NULL'})")
            
            # Look for stock-related columns
            if 'stock' in col_name.lower():
                stock_columns.append(col_name)
        
        print(f"\n🔍 Stock-related columns found: {stock_columns}")
        
        if not stock_columns:
            print("⚠️  No stock columns found! This explains the issue.")
            print("   The stock column may have been renamed or removed.")
        
        # Check for any stock data in existing columns
        for col_name in stock_columns:
            cursor.execute(f"""
                SELECT 
                    COUNT(*) as total_rows,
                    COUNT(CASE WHEN {col_name} = 0 OR {col_name} IS NULL THEN 1 END) as zero_stock,
                    MIN({col_name}) as min_stock,
                    MAX({col_name}) as max_stock,
                    AVG({col_name}) as avg_stock
                FROM products
                WHERE {col_name} IS NOT NULL
            """)
            
            try:
                stats = cursor.fetchone()
                print(f"\n📊 Stock analysis for column '{col_name}':")
                print(f"  Total rows with data: {stats[0]}")
                print(f"  Zero stock: {stats[1]}")
                print(f"  Min stock: {stats[2]}")
                print(f"  Max stock: {stats[3]}")
                print(f"  Average stock: {stats[4]:.2f}" if stats[4] else "  Average stock: N/A")
            except Exception as e:
                print(f"  ❌ Error analyzing {col_name}: {e}")
        
        # If no stock columns, check what happened to stock
        if not stock_columns:
            print(f"\n🔍 INVESTIGATION: What happened to stock column?")
            
            # Check for any recent schema changes
            cursor.execute("""
                SELECT column_name, data_type
                FROM information_schema.columns 
                WHERE table_name = 'products' 
                AND table_schema = 'public'
                AND (column_name LIKE '%quantity%' OR column_name LIKE '%amount%' OR column_name LIKE '%inventory%')
            """)
            
            related_cols = cursor.fetchall()
            if related_cols:
                print(f"  Found related columns:")
                for col in related_cols:
                    print(f"    • {col[0]}: {col[1]}")
            else:
                print(f"  No related columns found")
            
            # Check if there are any stock-related tables
            cursor.execute("""
                SELECT table_name
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND (table_name LIKE '%stock%' OR table_name LIKE '%inventory%')
            """)
            
            stock_tables = cursor.fetchall()
            if stock_tables:
                print(f"\n  Found stock-related tables:")
                for table in stock_tables:
                    print(f"    • {table[0]}")
            else:
                print(f"\n  No stock-related tables found")
        
        return stock_columns
        
    except Exception as e:
        print(f"❌ Error checking schema: {e}")
        return []

def check_sample_data(conn, stock_columns):
    """Check sample data to understand the issue"""
    print(f"\n=== SAMPLE DATA ANALYSIS ===")
    
    if not stock_columns:
        print("⚠️  No stock columns to analyze")
        return
    
    try:
        cursor = conn.cursor()
        
        # Get sample of products
        cursor.execute("""
            SELECT id, name, barcode, sale_price, purchase_price
            FROM products 
            ORDER BY id 
            LIMIT 10
        """)
        
        products = cursor.fetchall()
        print(f"📦 Sample products:")
        
        for product in products:
            print(f"  ID:{product[0]:4d} | Name:{product[1][:30]:30s} | Price:{product[4]:8.2f}")
            
            # Check stock values for this product
            for col_name in stock_columns:
                cursor.execute(f"SELECT {col_name} FROM products WHERE id = {product[0]}")
                stock_val = cursor.fetchone()[0]
                print(f"    {col_name}: {stock_val}")
        
    except Exception as e:
        print(f"❌ Error checking sample data: {e}")

def main():
    print("=" * 60)
    print("🔍 POSTGRESQL SCHEMA CHECK")
    print("=" * 60)
    
    conn = connect_to_postgres()
    if not conn:
        print("❌ Cannot connect to database")
        return
    
    try:
        stock_columns = check_schema(conn)
        check_sample_data(conn, stock_columns)
        
        print(f"\n=== SUMMARY ===")
        if stock_columns:
            print(f"✅ Found stock columns: {stock_columns}")
            print(f"   The stock data exists, check the analysis above")
        else:
            print(f"❌ NO STOCK COLUMNS FOUND!")
            print(f"   This is why 730+ items appear to have zero stock")
            print(f"   The stock column may have been:")
            print(f"   • Renamed during schema migration")
            print(f"   • Accidentally dropped")
            print(f"   • Moved to a different table")
        
    finally:
        conn.close()

if __name__ == "__main__":
    main()

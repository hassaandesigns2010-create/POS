#!/usr/bin/env python3
"""
Comprehensive Stock Analysis Script
Analyzes ALL backup files, tracks stock movements, sales, purchases, and adjustments
"""

import os
import sys
import re
from datetime import datetime
from pathlib import Path
import psycopg2
from psycopg2.extras import RealDictCursor

class StockAnalyzer:
    def __init__(self):
        self.conn_params = {
            'host': 'localhost',
            'port': 5432,
            'database': 'pos_network',
            'user': 'admin',
            'password': 'admin'
        }
        self.backup_dir = Path("C:/Users/pc/Documents/backups")
        self.all_backups = []
        self.stock_timeline = {}
        self.current_stock = {}
        self.discrepancies = []
        
    def connect_database(self):
        """Connect to PostgreSQL database"""
        try:
            self.conn = psycopg2.connect(**self.conn_params)
            self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            print("✅ Database connected successfully")
            return True
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False
    
    def get_all_backup_files(self):
        """Get all backup files sorted by date"""
        backup_files = sorted(self.backup_dir.glob("pos_backup_*.sql"))
        self.all_backups = backup_files
        print(f"📁 Found {len(backup_files)} backup files")
        return backup_files
    
    def extract_products_from_backup(self, backup_file):
        """Extract product data from a single backup file"""
        products = {}
        
        try:
            with open(backup_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Extract date from filename
            date_match = re.search(r'(\d{8})_(\d{6})', backup_file.name)
            if date_match:
                date_str = f"{date_match.group(1)} {date_match.group(2)}"
                backup_date = datetime.strptime(date_str, "%Y%m%d %H%M%S")
            else:
                backup_date = datetime.fromtimestamp(backup_file.stat().st_mtime)
            
            # Find COPY section for products
            copy_pattern = r'COPY public\.products\s*\(([^)]+)\)\s*;\n(.*?)\n\\\.'
            copy_match = re.search(copy_pattern, content, re.DOTALL | re.IGNORECASE)
            
            if copy_match:
                columns_str = copy_match.group(1)
                columns = [col.strip().strip('"') for col in columns_str.split(',')]
                data_section = copy_match.group(2)
                
                # Parse each line of data
                lines = data_section.split('\n')
                for line in lines:
                    if line.strip():
                        values = line.strip().split('\t')
                        if len(values) >= len(columns):
                            product = {}
                            for i, value in enumerate(values):
                                if i < len(columns):
                                    col_name = columns[i]
                                    clean_value = value.strip()
                                    if clean_value == '\\N':
                                        clean_value = None
                                    elif clean_value.startswith('"') and clean_value.endswith('"'):
                                        clean_value = clean_value[1:-1]
                                    product[col_name] = clean_value
                            
                            if 'id' in product:
                                products[product['id']] = product
            
            return products, backup_date
            
        except Exception as e:
            print(f"❌ Error parsing {backup_file.name}: {e}")
            return {}, None
    
    def extract_stock_movements(self, backup_file):
        """Extract stock movements from backup file"""
        movements = []
        
        try:
            with open(backup_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Find COPY section for stock_movements
            copy_pattern = r'COPY public\.stock_movements\s*\(([^)]+)\)\s*;\n(.*?)\n\\\.'
            copy_match = re.search(copy_pattern, content, re.DOTALL | re.IGNORECASE)
            
            if copy_match:
                columns_str = copy_match.group(1)
                columns = [col.strip().strip('"') for col in columns_str.split(',')]
                data_section = copy_match.group(2)
                
                lines = data_section.split('\n')
                for line in lines:
                    if line.strip():
                        values = line.strip().split('\t')
                        if len(values) >= len(columns):
                            movement = {}
                            for i, value in enumerate(values):
                                if i < len(columns):
                                    col_name = columns[i]
                                    clean_value = value.strip()
                                    if clean_value == '\\N':
                                        clean_value = None
                                    elif clean_value.startswith('"') and clean_value.endswith('"'):
                                        clean_value = clean_value[1:-1]
                                    movement[col_name] = clean_value
                            
                            movements.append(movement)
            
            return movements
            
        except Exception as e:
            print(f"❌ Error extracting movements from {backup_file.name}: {e}")
            return []
    
    def extract_sales_data(self, backup_file):
        """Extract sales data from backup file"""
        sales = []
        
        try:
            with open(backup_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Find COPY section for sale_items
            copy_pattern = r'COPY public\.sale_items\s*\(([^)]+)\)\s*;\n(.*?)\n\\\.'
            copy_match = re.search(copy_pattern, content, re.DOTALL | re.IGNORECASE)
            
            if copy_match:
                columns_str = copy_match.group(1)
                columns = [col.strip().strip('"') for col in columns_str.split(',')]
                data_section = copy_match.group(2)
                
                lines = data_section.split('\n')
                for line in lines:
                    if line.strip():
                        values = line.strip().split('\t')
                        if len(values) >= len(columns):
                            sale_item = {}
                            for i, value in enumerate(values):
                                if i < len(columns):
                                    col_name = columns[i]
                                    clean_value = value.strip()
                                    if clean_value == '\\N':
                                        clean_value = None
                                    elif clean_value.startswith('"') and clean_value.endswith('"'):
                                        clean_value = clean_value[1:-1]
                                    sale_item[col_name] = clean_value
                            
                            sales.append(sale_item)
            
            return sales
            
        except Exception as e:
            print(f"❌ Error extracting sales from {backup_file.name}: {e}")
            return []
    
    def analyze_all_backups(self):
        """Analyze all backup files and build stock timeline"""
        print("\n🔍 Analyzing all backup files...")
        
        for backup_file in self.all_backups:
            print(f"📊 Processing: {backup_file.name}")
            
            # Extract products
            products, backup_date = self.extract_products_from_backup(backup_file)
            if not products:
                continue
            
            # Extract stock movements
            movements = self.extract_stock_movements(backup_file)
            
            # Extract sales data
            sales = self.extract_sales_data(backup_file)
            
            # Store timeline data
            self.stock_timeline[backup_file.name] = {
                'date': backup_date,
                'products': products,
                'movements': movements,
                'sales': sales,
                'total_products': len(products),
                'total_stock': sum(float(p.get('stock_level', 0) or 0) for p in products.values()),
                'products_with_stock': len([p for p in products.values() if float(p.get('stock_level', 0) or 0) > 0])
            }
        
        print(f"✅ Analyzed {len(self.stock_timeline)} backup files")
    
    def get_current_database_stock(self):
        """Get current stock from database"""
        try:
            query = """
            SELECT id, name, sku, barcode, stock_level, purchase_price, wholesale_price, retail_price
            FROM products 
            ORDER BY id
            """
            
            self.cursor.execute(query)
            products = self.cursor.fetchall()
            
            for product in products:
                self.current_stock[str(product['id'])] = {
                    'id': product['id'],
                    'name': product['name'],
                    'sku': product['sku'],
                    'barcode': product['barcode'],
                    'stock_level': float(product['stock_level'] or 0),
                    'purchase_price': float(product['purchase_price'] or 0),
                    'wholesale_price': float(product['wholesale_price'] or 0),
                    'retail_price': float(product['retail_price'] or 0)
                }
            
            print(f"📦 Current database: {len(self.current_stock)} products")
            
        except Exception as e:
            print(f"❌ Error getting current stock: {e}")
    
    def calculate_expected_stock(self, product_id):
        """Calculate expected stock based on timeline analysis"""
        if not self.stock_timeline:
            return 0
        
        # Get the latest backup stock as baseline
        latest_backup = max(self.stock_timeline.values(), key=lambda x: x['date'])
        latest_products = latest_backup['products']
        
        if product_id in latest_products:
            baseline_stock = float(latest_products[product_id].get('stock_level', 0) or 0)
        else:
            baseline_stock = 0
        
        # Calculate stock changes from movements and sales
        stock_change = 0
        
        # Process all movements after latest backup
        for backup_name, backup_data in self.stock_timeline.items():
            if backup_data['date'] > latest_backup['date']:
                # Add stock movements
                for movement in backup_data['movements']:
                    if movement.get('product_id') == product_id:
                        quantity = float(movement.get('quantity', 0) or 0)
                        movement_type = movement.get('movement_type', '').lower()
                        
                        if movement_type in ['purchase', 'adjustment_in', 'return_in']:
                            stock_change += quantity
                        elif movement_type in ['sale', 'adjustment_out', 'return_out']:
                            stock_change -= quantity
                
                # Subtract sales
                for sale in backup_data['sales']:
                    if sale.get('product_id') == product_id:
                        quantity = float(sale.get('quantity', 0) or 0)
                        stock_change -= quantity
        
        return baseline_stock + stock_change
    
    def identify_discrepancies(self):
        """Identify stock discrepancies between expected and actual"""
        print("\n🔍 Identifying stock discrepancies...")
        
        self.discrepancies = []
        
        for product_id, current_info in self.current_stock.items():
            current_stock = current_info['stock_level']
            
            # Calculate expected stock
            expected_stock = self.calculate_expected_stock(product_id)
            
            # Check if there's a significant discrepancy
            if abs(current_stock - expected_stock) > 0.01:  # Allow for small floating point differences
                self.discrepancies.append({
                    'id': product_id,
                    'name': current_info['name'],
                    'sku': current_info['sku'],
                    'current_stock': current_stock,
                    'expected_stock': expected_stock,
                    'difference': current_stock - expected_stock,
                    'percentage_diff': ((current_stock - expected_stock) / expected_stock * 100) if expected_stock > 0 else 0
                })
        
        # Sort by absolute difference
        self.discrepancies.sort(key=lambda x: abs(x['difference']), reverse=True)
        
        print(f"📊 Found {len(self.discrepancies)} stock discrepancies")
    
    def generate_report(self):
        """Generate comprehensive analysis report"""
        print("\n" + "="*100)
        print("📊 COMPREHENSIVE STOCK ANALYSIS REPORT")
        print("="*100)
        
        # Timeline summary
        print("\n📅 BACKUP TIMELINE SUMMARY:")
        print("-" * 50)
        
        for backup_name, data in sorted(self.stock_timeline.items(), key=lambda x: x[1]['date']):
            print(f"{data['date']}: {backup_name}")
            print(f"  Products: {data['total_products']}, Total Stock: {data['total_stock']:,.0f}")
            print(f"  Products with Stock: {data['products_with_stock']}")
            print()
        
        # Current database summary
        print("📦 CURRENT DATABASE SUMMARY:")
        print("-" * 50)
        
        total_current_stock = sum(p['stock_level'] for p in self.current_stock.values())
        products_with_current_stock = len([p for p in self.current_stock.values() if p['stock_level'] > 0])
        
        print(f"Total Products: {len(self.current_stock)}")
        print(f"Total Stock: {total_current_stock:,.0f}")
        print(f"Products with Stock: {products_with_current_stock}")
        print(f"Average Stock per Product: {total_current_stock / len(self.current_stock):.2f}")
        
        # Discrepancies
        print("\n🚨 STOCK DISCREPANCIES:")
        print("-" * 50)
        
        if self.discrepancies:
            print(f"Found {len(self.discrepancies)} products with stock discrepancies:")
            print()
            
            # Show top 20 discrepancies
            for i, disc in enumerate(self.discrepancies[:20], 1):
                print(f"{i}. ID: {disc['id']}")
                print(f"   Name: {disc['name'][:50]}")
                print(f"   Current Stock: {disc['current_stock']}")
                print(f"   Expected Stock: {disc['expected_stock']}")
                print(f"   Difference: {disc['difference']:+.2f} ({disc['percentage_diff']:+.1f}%)")
                print()
            
            if len(self.discrepancies) > 20:
                print(f"... and {len(self.discrepancies) - 20} more discrepancies")
        else:
            print("✅ No stock discrepancies found!")
        
        # Critical issues (products that should have stock but have zero)
        critical_issues = [d for d in self.discrepancies if d['current_stock'] == 0 and d['expected_stock'] > 0]
        
        if critical_issues:
            print("\n🚨 CRITICAL ISSUES (Products with zero stock that should have stock):")
            print("-" * 70)
            
            for issue in critical_issues[:10]:
                print(f"ID: {issue['id']} - {issue['name'][:40]}")
                print(f"  Should have: {issue['expected_stock']} units, Currently: 0")
                print()
        
        return self.discrepancies
    
    def fix_discrepancies(self, discrepancies_to_fix=None):
        """Fix stock discrepancies in database"""
        if not discrepancies_to_fix:
            discrepancies_to_fix = self.discrepancies
        
        if not discrepancies_to_fix:
            print("No discrepancies to fix.")
            return
        
        print(f"\n🔧 Fixing {len(discrepancies_to_fix)} stock discrepancies...")
        
        fixed_count = 0
        error_count = 0
        
        for disc in discrepancies_to_fix:
            try:
                update_query = """
                UPDATE products 
                SET stock_level = %s 
                WHERE id = %s
                """
                self.cursor.execute(update_query, (disc['expected_stock'], disc['id']))
                
                print(f"✅ Fixed: {disc['name'][:40]} (ID: {disc['id']})")
                print(f"   Stock: {disc['current_stock']} → {disc['expected_stock']}")
                print()
                
                fixed_count += 1
                
            except Exception as e:
                print(f"❌ Error fixing {disc['id']}: {e}")
                error_count += 1
        
        # Commit changes
        try:
            self.conn.commit()
            print(f"🎉 Successfully fixed {fixed_count} products!")
            if error_count > 0:
                print(f"⚠️  Failed to fix {error_count} products")
        except Exception as e:
            print(f"❌ Error committing changes: {e}")
    
    def run_full_analysis(self):
        """Run complete analysis"""
        print("🚀 Starting Comprehensive Stock Analysis...")
        
        # Connect to database
        if not self.connect_database():
            return
        
        # Get all backup files
        self.get_all_backup_files()
        
        # Analyze all backups
        self.analyze_all_backups()
        
        # Get current stock
        self.get_current_database_stock()
        
        # Identify discrepancies
        self.identify_discrepancies()
        
        # Generate report
        discrepancies = self.generate_report()
        
        # Ask if user wants to fix
        if discrepancies:
            print("\n" + "="*50)
            print("Do you want to fix these discrepancies? (y/n)")
            response = input("Enter choice: ").strip().lower()
            
            if response == 'y':
                # Fix critical issues first
                critical = [d for d in discrepancies if d['current_stock'] == 0 and d['expected_stock'] > 0]
                if critical:
                    print(f"\n🚨 Fixing {len(critical)} critical issues first...")
                    self.fix_discrepancies(critical)
                
                # Then fix other discrepancies
                other = [d for d in discrepancies if d not in critical]
                if other:
                    print(f"\n🔧 Fixing {len(other)} other discrepancies...")
                    self.fix_discrepancies(other[:50])  # Limit to 50 to avoid overwhelming
        
        # Close connection
        self.cursor.close()
        self.conn.close()
        print("\n✅ Analysis complete!")

if __name__ == "__main__":
    analyzer = StockAnalyzer()
    analyzer.run_full_analysis()

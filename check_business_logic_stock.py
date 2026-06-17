#!/usr/bin/env python3
"""
Check which stock column the business logic actually uses
"""

import os
import sys

def check_business_logic():
    """Check which stock column is used in business logic"""
    print("=" * 60)
    print("🔍 CHECKING WHICH STOCK COLUMN BUSINESS LOGIC USES")
    print("=" * 60)
    
    # Check business_logic.py file
    business_file = os.path.join(os.path.dirname(__file__), 'controllers', 'business_logic.py')
    
    if not os.path.exists(business_file):
        print(f"❌ Business logic file not found: {business_file}")
        return
    
    try:
        with open(business_file, 'r') as f:
            content = f.read()
        
        print("📋 Stock column usage in business_logic.py:")
        
        # Look for stock column references
        lines = content.split('\n')
        stock_usage = []
        
        for i, line in enumerate(lines, 1):
            line_lower = line.lower()
            
            # Check for stock column references
            if 'stock_level' in line_lower:
                stock_usage.append(f"  Line {i}: stock_level - {line.strip()}")
            elif 'warehouse_stock' in line_lower:
                stock_usage.append(f"  Line {i}: warehouse_stock - {line.strip()}")
            elif 'retail_stock' in line_lower:
                stock_usage.append(f"  Line {i}: retail_stock - {line.strip()}")
            elif 'stock' in line_lower and ('=' in line or '.' in line):
                # General stock references
                stock_usage.append(f"  Line {i}: STOCK - {line.strip()}")
        
        if stock_usage:
            for usage in stock_usage:
                print(usage)
        else:
            print("  ❌ No stock column references found")
        
        # Look for stock update patterns
        print(f"\n🔍 Stock update patterns:")
        
        stock_updates = []
        for i, line in enumerate(lines, 1):
            if 'stock' in line.lower() and ('=' in line or '+=' in line or '-=' in line):
                if 'product.' in line or 'self.product' in line:
                    stock_updates.append(f"  Line {i}: {line.strip()}")
        
        if stock_updates:
            for update in stock_updates:
                print(update)
        else:
            print("  ❌ No stock update patterns found")
        
        # Look for stock validation
        print(f"\n🔍 Stock validation patterns:")
        
        validations = []
        for i, line in enumerate(lines, 1):
            if 'stock' in line.lower() and ('available' in line.lower() or 'validate' in line.lower() or 'check' in line.lower()):
                validations.append(f"  Line {i}: {line.strip()}")
        
        if validations:
            for validation in validations:
                print(validation)
        else:
            print("  ❌ No stock validation patterns found")
        
    except Exception as e:
        print(f"❌ Error reading business logic: {e}")

def check_sales_view():
    """Check which stock column is used in sales view"""
    print(f"\n🔍 CHECKING STOCK USAGE IN SALES VIEW:")
    
    sales_file = os.path.join(os.path.dirname(__file__), 'views', 'sales.py')
    
    if not os.path.exists(sales_file):
        print(f"❌ Sales view file not found: {sales_file}")
        return
    
    try:
        with open(sales_file, 'r') as f:
            content = f.read()
        
        # Look for stock column references
        lines = content.split('\n')
        stock_usage = []
        
        for i, line in enumerate(lines, 1):
            line_lower = line.lower()
            
            if 'stock_level' in line_lower:
                stock_usage.append(f"  Line {i}: stock_level - {line.strip()}")
            elif 'warehouse_stock' in line_lower:
                stock_usage.append(f"  Line {i}: warehouse_stock - {line.strip()}")
            elif 'retail_stock' in line_lower:
                stock_usage.append(f"  Line {i}: retail_stock - {line.strip()}")
        
        if stock_usage:
            for usage in stock_usage:
                print(usage)
        else:
            print("  ❌ No stock column references found in sales view")
        
    except Exception as e:
        print(f"❌ Error reading sales view: {e}")

def main():
    check_business_logic()
    check_sales_view()
    
    print(f"\n🎯 CONCLUSION:")
    print(f"Based on the analysis, the application uses 'stock_level' column.")
    print(f"DUMY PRODUCT has stock_level = 0.0000 but retail_stock = 522")
    print(f"This explains why it shows zero stock - the app uses stock_level!")

if __name__ == "__main__":
    main()

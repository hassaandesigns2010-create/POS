#!/usr/bin/env python3
"""
Comprehensive analysis of ALL modules that use stock
Check which stock column each module actually uses
"""

import os
import sys
import re

def find_python_files(directory):
    """Find all Python files in directory"""
    python_files = []
    try:
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
    except Exception as e:
        print(f"Error walking directory {directory}: {e}")
    return python_files

def analyze_stock_usage(file_path):
    """Analyze a single Python file for stock column usage"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        return {"error": f"Could not read file: {e}"}
    
    lines = content.split('\n')
    stock_usage = {
        'stock_level': [],
        'warehouse_stock': [],
        'retail_stock': [],
        'stock_generic': [],
        'stock_updates': [],
        'stock_validation': []
    }
    
    for i, line in enumerate(lines, 1):
        line_stripped = line.strip()
        
        # Skip comments and empty lines
        if not line_stripped or line_stripped.startswith('#'):
            continue
        
        # Check for specific stock column usage
        if 'stock_level' in line:
            stock_usage['stock_level'].append(f"Line {i}: {line_stripped}")
        
        if 'warehouse_stock' in line:
            stock_usage['warehouse_stock'].append(f"Line {i}: {line_stripped}")
        
        if 'retail_stock' in line:
            stock_usage['retail_stock'].append(f"Line {i}: {line_stripped}")
        
        # Check for generic stock usage
        stock_patterns = [
            r'\.stock\s*=',  # .stock = 
            r'\.stock\s*\+',  # .stock +
            r'\.stock\s*-',  # .stock -
            r'stock\s*=',     # stock = 
            r'stock\s*\+',    # stock +
            r'stock\s*-',    # stock -
            r'available_stock',  # available_stock
            r'current_stock',     # current_stock
        ]
        
        for pattern in stock_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                stock_usage['stock_generic'].append(f"Line {i}: {line_stripped}")
                break
        
        # Check for stock updates
        update_patterns = [
            r'stock.*=.*\+',  # stock = stock + 
            r'stock.*=.*-',  # stock = stock - 
            r'stock.*\+=',   # stock +=
            r'stock.*-=',   # stock -=
        ]
        
        for pattern in update_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                stock_usage['stock_updates'].append(f"Line {i}: {line_stripped}")
                break
        
        # Check for stock validation
        validation_patterns = [
            r'stock.*<',
            r'stock.*>',
            r'stock.*<=',
            r'stock.*>=',
            r'insufficient.*stock',
            r'validate.*stock',
            r'check.*stock',
            r'stock.*available',
            r'stock.*insufficient',
        ]
        
        for pattern in validation_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                stock_usage['stock_validation'].append(f"Line {i}: {line_stripped}")
                break
    
    return stock_usage

def analyze_all_modules():
    """Analyze all Python modules for stock usage"""
    print("=" * 80)
    print("🔍 COMPREHENSIVE STOCK COLUMN ANALYSIS")
    print("=" * 80)
    print("Checking ALL modules that use stock...")
    
    # Find all Python files
    base_dir = os.path.dirname(__file__)
    python_files = find_python_files(base_dir)
    
    print(f"📁 Found {len(python_files)} Python files")
    
    # Analyze each file
    stock_modules = {}
    
    for file_path in python_files:
        # Skip some directories that are unlikely to have stock logic
        if any(skip in file_path for skip in ['__pycache__', '.git', 'venv', 'env']):
            continue
        
        usage = analyze_stock_usage(file_path)
        
        # Check if this file uses stock
        has_stock = any([
            usage['stock_level'],
            usage['warehouse_stock'],
            usage['retail_stock'],
            usage['stock_generic'],
            usage['stock_updates'],
            usage['stock_validation']
        ])
        
        if has_stock and not usage.get('error'):
            # Get relative path for display
            rel_path = os.path.relpath(file_path, base_dir)
            stock_modules[rel_path] = usage
    
    print(f"📊 Found {len(stock_modules)} files that use stock")
    
    # Analyze results
    print("\n" + "=" * 80)
    print("📋 STOCK COLUMN USAGE BY MODULE")
    print("=" * 80)
    
    stock_level_users = []
    warehouse_stock_users = []
    retail_stock_users = []
    generic_stock_users = []
    
    for file_path, usage in stock_modules.items():
        print(f"\n🔍 {file_path}")
        print("-" * 60)
        
        if usage['stock_level']:
            print("  📊 Uses stock_level:")
            for line in usage['stock_level'][:5]:  # Show first 5 lines
                print(f"    {line}")
            if len(usage['stock_level']) > 5:
                print(f"    ... and {len(usage['stock_level']) - 5} more lines")
            stock_level_users.append(file_path)
        
        if usage['warehouse_stock']:
            print("  📦 Uses warehouse_stock:")
            for line in usage['warehouse_stock'][:5]:
                print(f"    {line}")
            if len(usage['warehouse_stock']) > 5:
                print(f"    ... and {len(usage['warehouse_stock']) - 5} more lines")
            warehouse_stock_users.append(file_path)
        
        if usage['retail_stock']:
            print("  🏪 Uses retail_stock:")
            for line in usage['retail_stock'][:5]:
                print(f"    {line}")
            if len(usage['retail_stock']) > 5:
                print(f"    ... and {len(usage['retail_stock']) - 5} more lines")
            retail_stock_users.append(file_path)
        
        if usage['stock_generic']:
            print("  🔧 Generic stock usage:")
            for line in usage['stock_generic'][:3]:
                print(f"    {line}")
            if len(usage['stock_generic']) > 3:
                print(f"    ... and {len(usage['stock_generic']) - 3} more lines")
            generic_stock_users.append(file_path)
        
        if usage['stock_updates']:
            print("  📈 Stock updates:")
            for line in usage['stock_updates'][:3]:
                print(f"    {line}")
            if len(usage['stock_updates']) > 3:
                print(f"    ... and {len(usage['stock_updates']) - 3} more lines")
        
        if usage['stock_validation']:
            print("  ✅ Stock validation:")
            for line in usage['stock_validation'][:3]:
                print(f"    {line}")
            if len(usage['stock_validation']) > 3:
                print(f"    ... and {len(usage['stock_validation']) - 3} more lines")
        
        if not any([usage['stock_level'], usage['warehouse_stock'], usage['retail_stock'], 
                   usage['stock_generic'], usage['stock_updates'], usage['stock_validation']]):
            print("  ❓ No specific stock usage found")
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 SUMMARY: WHICH STOCK COLUMN IS USED?")
    print("=" * 80)
    
    print(f"\n📊 stock_level users ({len(stock_level_users)}):")
    for user in stock_level_users:
        print(f"  • {user}")
    
    print(f"\n📦 warehouse_stock users ({len(warehouse_stock_users)}):")
    for user in warehouse_stock_users:
        print(f"  • {user}")
    
    print(f"\n🏪 retail_stock users ({len(retail_stock_users)}):")
    for user in retail_stock_users:
        print(f"  • {user}")
    
    print(f"\n🔧 Generic stock users ({len(generic_stock_users)}):")
    for user in generic_stock_users:
        print(f"  • {user}")
    
    # Key modules analysis
    print("\n" + "=" * 80)
    print("🎯 KEY MODULES ANALYSIS")
    print("=" * 80)
    
    key_modules = [
        'controllers/business_logic.py',
        'views/sales.py',
        'models/database.py',
        'views/customers.py',
        'views/products.py'
    ]
    
    for module in key_modules:
        if module in stock_modules:
            print(f"\n🔍 {module}")
            usage = stock_modules[module]
            
            if usage['stock_level']:
                print("  ✅ Uses stock_level")
            if usage['warehouse_stock']:
                print("  ✅ Uses warehouse_stock")
            if usage['retail_stock']:
                print("  ✅ Uses retail_stock")
            if usage['stock_generic']:
                print("  ⚠️  Uses generic stock references")
            if usage['stock_updates']:
                print("  📈 Contains stock updates")
            if usage['stock_validation']:
                print("  ✅ Contains stock validation")
        else:
            print(f"\n❌ {module} - No stock usage found")
    
    print("\n" + "=" * 80)
    print("🎯 CONCLUSION")
    print("=" * 80)
    
    if stock_level_users:
        print(f"✅ Primary stock column: stock_level (used by {len(stock_level_users)} modules)")
    if warehouse_stock_users:
        print(f"📦 Secondary column: warehouse_stock (used by {len(warehouse_stock_users)} modules)")
    if retail_stock_users:
        print(f"🏪 Secondary column: retail_stock (used by {len(retail_stock_users)} modules)")
    if generic_stock_users:
        print(f"⚠️  Generic stock references found in {len(generic_stock_users)} modules")

def main():
    analyze_all_modules()

if __name__ == "__main__":
    main()

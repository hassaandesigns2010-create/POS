#!/usr/bin/env python3
"""
Find which specific functions use retail_stock instead of stock_level
"""

import os
import sys
import re

def find_retail_stock_usage():
    """Find all functions that use retail_stock column"""
    print("=" * 80)
    print("🔍 FINDING FUNCTIONS THAT USE retail_stock (WRONG COLUMN)")
    print("=" * 80)
    
    base_dir = os.path.dirname(__file__)
    
    # Find all Python files
    python_files = []
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    retail_stock_usage = {}
    
    for file_path in python_files:
        # Skip cache and test files for now
        if any(skip in file_path for skip in ['__pycache__', '.git', 'venv', 'env', 'tests']):
            continue
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            continue
        
        lines = content.split('\n')
        current_function = None
        in_function = False
        function_lines = []
        
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # Skip comments and empty lines
            if not line_stripped or line_stripped.startswith('#'):
                continue
            
            # Check for function definition
            if re.match(r'^\s*def\s+\w+', line):
                # Save previous function if it had retail_stock usage
                if current_function and function_lines:
                    if file_path not in retail_stock_usage:
                        retail_stock_usage[file_path] = []
                    retail_stock_usage[file_path].append({
                        'function': current_function,
                        'lines': function_lines
                    })
                
                # Start new function
                current_function = line_stripped
                function_lines = []
                in_function = True
                continue
            
            # Check for class definition (reset function tracking)
            if re.match(r'^\s*class\s+\w+', line):
                current_function = None
                in_function = False
                function_lines = []
                continue
            
            # Look for retail_stock usage
            if 'retail_stock' in line and in_function:
                function_lines.append(f"Line {i}: {line_stripped}")
    
        # Save last function
        if current_function and function_lines:
            if file_path not in retail_stock_usage:
                retail_stock_usage[file_path] = []
            retail_stock_usage[file_path].append({
                'function': current_function,
                'lines': function_lines
            })
    
    # Display results
    if not retail_stock_usage:
        print("✅ No retail_stock usage found in application code!")
        print("This means the application correctly uses stock_level everywhere.")
        return
    
    print(f"🚨 Found {len(retail_stock_usage)} files with retail_stock usage:")
    
    for file_path, functions in retail_stock_usage.items():
        rel_path = os.path.relpath(file_path, base_dir)
        print(f"\n🔍 {rel_path}")
        print("-" * 60)
        
        for func_data in functions:
            func_name = func_data['function']
            func_lines = func_data['lines']
            
            print(f"  📋 Function: {func_name}")
            for line in func_lines:
                print(f"    {line}")
            print()
    
    # Analysis of problematic usage
    print("\n" + "=" * 80)
    print("🎯 ANALYSIS: WHICH USAGE IS PROBLEMATIC?")
    print("=" * 80)
    
    problematic_files = []
    for file_path, functions in retail_stock_usage.items():
        rel_path = os.path.relpath(file_path, base_dir)
        
        # Check if this is a core application file
        if any(core in rel_path for core in ['controllers/', 'views/', 'models/']):
            problematic_files.append(rel_path)
            print(f"🚨 CORE FILE: {rel_path}")
            
            for func_data in functions:
                func_name = func_data['function']
                print(f"  ❌ Function: {func_name}")
                print(f"     This should use stock_level instead of retail_stock!")
            print()
    
    # Check if these are just analysis/backup scripts
    analysis_files = []
    for file_path, functions in retail_stock_usage.items():
        rel_path = os.path.relpath(file_path, base_dir)
        
        if any(analysis in rel_path for analysis in ['analyze_', 'check_', 'debug_', 'test_', 'backup_', 'migration']):
            analysis_files.append(rel_path)
    
    if analysis_files:
        print(f"📊 ANALYSIS FILES (retail_stock usage is OK here):")
        for file_path in analysis_files:
            print(f"  📋 {file_path}")
    
    print(f"\n🎯 CONCLUSION:")
    if problematic_files:
        print(f"❌ Found {len(problematic_files)} core application files using retail_stock")
        print(f"   These should be updated to use stock_level instead!")
    else:
        print(f"✅ No core application files use retail_stock")
        print(f"   The application correctly uses stock_level everywhere!")

def find_stock_level_usage_for_comparison():
    """Also check stock_level usage to confirm it's the primary column"""
    print(f"\n" + "=" * 80)
    print("📊 CONFIRMING stock_level USAGE (PRIMARY COLUMN)")
    print("=" * 80)
    
    base_dir = os.path.dirname(__file__)
    
    # Check key files for stock_level usage
    key_files = [
        'controllers/business_logic.py',
        'views/sales.py',
        'views/products.py',
        'views/inventory.py',
        'models/database.py'
    ]
    
    for key_file in key_files:
        file_path = os.path.join(base_dir, key_file)
        if not os.path.exists(file_path):
            continue
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            print(f"❌ Could not read {key_file}: {e}")
            continue
        
        lines = content.split('\n')
        stock_level_lines = []
        
        for i, line in enumerate(lines, 1):
            if 'stock_level' in line and not line.strip().startswith('#'):
                stock_level_lines.append(f"Line {i}: {line.strip()}")
        
        if stock_level_lines:
            print(f"\n✅ {key_file} uses stock_level:")
            for line in stock_level_lines[:5]:  # Show first 5
                print(f"    {line}")
            if len(stock_level_lines) > 5:
                print(f"    ... and {len(stock_level_lines) - 5} more lines")
        else:
            print(f"\n❓ {key_file} - No stock_level usage found")

def main():
    find_retail_stock_usage()
    find_stock_level_usage_for_comparison()

if __name__ == "__main__":
    main()

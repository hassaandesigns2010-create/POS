#!/usr/bin/env python3
"""
Find where the actual stock update is coming from
"""

import os
import sys
import re

def find_stock_update_logging():
    """Find where "Updated stock for product" logging comes from"""
    print("=" * 80)
    print("🔍 FINDING SOURCE OF STOCK UPDATE LOGGING")
    print("=" * 80)
    
    base_dir = os.path.dirname(__file__)
    
    # Search all Python files for the logging message
    python_files = []
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    stock_update_sources = []
    
    for file_path in python_files:
        if any(skip in file_path for skip in ['__pycache__', '.git', 'venv', 'env']):
            continue
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception:
            continue
        
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            if 'Updated stock for product' in line:
                rel_path = os.path.relpath(file_path, base_dir)
                stock_update_sources.append(f"{rel_path} Line {i}: {line.strip()}")
    
    if stock_update_sources:
        print(f"🚨 Found {len(stock_update_sources)} sources of stock update logging:")
        for source in stock_update_sources:
            print(f"  {source}")
    else:
        print(f"❓ No 'Updated stock for product' logging found")

def find_receive_purchase_alternatives():
    """Look for alternative receive_purchase implementations"""
    print(f"\n" + "=" * 80)
    print("🔍 LOOKING FOR ALTERNATIVE receive_purchase IMPLEMENTATIONS")
    print("=" * 80)
    
    base_dir = os.path.dirname(__file__)
    
    # Search for receive_purchase in all files
    python_files = []
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    receive_purchase_implementations = []
    
    for file_path in python_files:
        if any(skip in file_path for skip in ['__pycache__', '.git', 'venv', 'env', 'tests']):
            continue
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception:
            continue
        
        lines = content.split('\n')
        current_function = None
        function_lines = []
        
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # Skip comments
            if line_stripped.startswith('#'):
                continue
            
            # Check for receive_purchase method definition
            if re.match(r'^\s*def\s+receive_purchase', line):
                current_function = line_stripped
                function_lines.append(f"Line {i}: {line_stripped}")
                
                # Get the rest of the function
                for j in range(i, len(lines)):
                    line_j = lines[j]
                    if line_j.strip() and not line_j.strip().startswith('#'):
                        function_lines.append(f"Line {j+1}: {line_j.strip()}")
                    
                    # Stop at next method or class
                    if re.match(r'^\s*(def|class)\s+', line_j):
                        break
                
                rel_path = os.path.relpath(file_path, base_dir)
                receive_purchase_implementations.append({
                    'file': rel_path,
                    'function': current_function,
                    'lines': function_lines
                })
                break
    
    if receive_purchase_implementations:
        print(f"🚨 Found {len(receive_purchase_implementations)} receive_purchase implementations:")
        for impl in receive_purchase_implementations:
            print(f"\n📋 {impl['file']}")
            print(f"  Function: {impl['function']}")
            print(f"  Implementation:")
            for line in impl['lines'][:20]:  # Show first 20 lines
                print(f"    {line}")
            if len(impl['lines']) > 20:
                print(f"    ... and {len(impl['lines']) - 20} more lines")
    else:
        print(f"❓ No receive_purchase implementations found")

def check_for_dynamic_method_loading():
    """Check if receive_purchase is loaded dynamically"""
    print(f"\n" + "=" * 80)
    print("🔍 CHECKING FOR DYNAMIC METHOD LOADING")
    print("=" * 80)
    
    base_dir = os.path.dirname(__file__)
    
    # Look for patterns that might dynamically add methods
    python_files = []
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    dynamic_patterns = []
    
    for file_path in python_files:
        if any(skip in file_path for skip in ['__pycache__', '.git', 'venv', 'env']):
            continue
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception:
            continue
        
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            line_lower = line.lower()
            
            # Look for dynamic method addition patterns
            if any(pattern in line_lower for pattern in [
                'setattr.*receive_purchase',
                'exec.*receive_purchase',
                'eval.*receive_purchase',
                'types.MethodType.*receive_purchase',
                'add_method.*receive_purchase',
                'import.*receive_purchase',
                'from.*receive_purchase'
            ]):
                rel_path = os.path.relpath(file_path, base_dir)
                dynamic_patterns.append(f"{rel_path} Line {i}: {line.strip()}")
    
    if dynamic_patterns:
        print(f"🚨 Found {len(dynamic_patterns)} dynamic method patterns:")
        for pattern in dynamic_patterns:
            print(f"  {pattern}")
    else:
        print(f"❓ No dynamic method loading patterns found")

def check_for_method_resolution():
    """Check method resolution in controller classes"""
    print(f"\n" + "=" * 80)
    print("🔍 CHECKING METHOD RESOLUTION")
    print("=" * 80)
    
    # Check the controller hierarchy
    controller_files = [
        'controllers/safe_business_controller.py',
        'controllers/business_logic.py'
    ]
    
    base_dir = os.path.dirname(__file__)
    
    for controller_file in controller_files:
        file_path = os.path.join(base_dir, controller_file)
        if not os.path.exists(file_path):
            continue
        
        rel_path = os.path.relpath(file_path, base_dir)
        print(f"\n🔍 Checking {rel_path}:")
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            print(f"  ❌ Could not read: {e}")
            continue
        
        lines = content.split('\n')
        
        # Look for class definition
        for i, line in enumerate(lines, 1):
            if 'class' in line and 'Controller' in line:
                print(f"  Line {i}: {line.strip()}")
                
                # Look for inheritance
                if '(' in line and ')' in line:
                    inheritance = line[line.find('(')+1:line.find(')')]
                    print(f"    Inherits from: {inheritance}")
                break
        
        # Look for receive_purchase method
        for i, line in enumerate(lines, 1):
            if 'receive_purchase' in line:
                print(f"  Line {i}: {line.strip()}")

def main():
    find_stock_update_logging()
    find_receive_purchase_alternatives()
    check_for_dynamic_method_loading()
    check_for_method_resolution()

if __name__ == "__main__":
    main()

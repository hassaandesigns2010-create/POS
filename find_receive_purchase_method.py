#!/usr/bin/env python3
"""
Find the receive_purchase method and check which stock column it updates
"""

import os
import sys
import re

def find_receive_purchase_method():
    """Find the receive_purchase method in controllers"""
    print("=" * 80)
    print("🔍 FINDING receive_purchase METHOD")
    print("=" * 80)
    
    base_dir = os.path.dirname(__file__)
    
    # Check controllers directory
    controllers_dir = os.path.join(base_dir, 'controllers')
    if not os.path.exists(controllers_dir):
        print(f"❌ Controllers directory not found: {controllers_dir}")
        return
    
    # Find all controller files
    controller_files = []
    for file in os.listdir(controllers_dir):
        if file.endswith('.py'):
            controller_files.append(os.path.join(controllers_dir, file))
    
    print(f"📁 Found {len(controller_files)} controller files:")
    for file_path in controller_files:
        rel_path = os.path.relpath(file_path, base_dir)
        print(f"  • {rel_path}")
    
    # Search for receive_purchase method
    receive_purchase_found = False
    
    for file_path in controller_files:
        rel_path = os.path.relpath(file_path, base_dir)
        print(f"\n" + "=" * 60)
        print(f"🔍 CHECKING: {rel_path}")
        print("=" * 60)
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            print(f"❌ Could not read file: {e}")
            continue
        
        lines = content.split('\n')
        
        # Look for receive_purchase method
        method_found = False
        method_lines = []
        current_function = None
        
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # Skip comments
            if line_stripped.startswith('#'):
                continue
            
            # Check for receive_purchase method definition
            if re.match(r'^\s*def\s+receive_purchase', line):
                current_function = line_stripped
                method_found = True
                receive_purchase_found = True
                method_lines.append(f"Line {i}: {line_stripped}")
                continue
            
            # If we're inside the method, collect lines
            if method_found and current_function:
                # Stop at next method or class
                if re.match(r'^\s*(def|class)\s+', line):
                    break
                
                method_lines.append(f"Line {i}: {line_stripped}")
        
        if method_found:
            print(f"✅ Found receive_purchase method:")
            for line in method_lines:
                print(f"  {line}")
            
            # Check which stock column is used
            stock_usage = []
            for line in method_lines:
                if any(col in line for col in ['stock_level', 'warehouse_stock', 'retail_stock']):
                    stock_usage.append(line)
            
            if stock_usage:
                print(f"\n📊 Stock column usage in receive_purchase:")
                for usage in stock_usage:
                    print(f"  {usage}")
            else:
                print(f"\n❓ No specific stock column usage found")
                # Look for generic stock usage
                generic_stock = []
                for line in method_lines:
                    if '.stock' in line or 'stock =' in line:
                        generic_stock.append(line)
                
                if generic_stock:
                    print(f"🔧 Generic stock usage found:")
                    for usage in generic_stock:
                        print(f"  {usage}")
                else:
                    print(f"❌ No stock usage found at all!")
        else:
            print(f"❌ No receive_purchase method found")
    
    if not receive_purchase_found:
        print(f"\n" + "=" * 80)
        print(f"🚨 CRITICAL: No receive_purchase method found in any controller!")
        print(f"   This explains why purchases don't update stock!")
        print(f"   The ReceivePurchaseDialog calls controller.receive_purchase()")
        print(f"   but the method doesn't exist!")
        print("=" * 80)

def check_safe_business_controller():
    """Check the safe_business_controller for receive_purchase"""
    print(f"\n" + "=" * 80)
    print("🔍 CHECKING safe_business_controller")
    print("=" * 80)
    
    safe_controller_file = os.path.join(os.path.dirname(__file__), 'controllers', 'safe_business_controller.py')
    
    if not os.path.exists(safe_controller_file):
        print(f"❌ safe_business_controller.py not found")
        return
    
    try:
        with open(safe_controller_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Could not read safe_business_controller.py: {e}")
        return
    
    lines = content.split('\n')
    
    # Look for receive_purchase method
    for i, line in enumerate(lines, 1):
        if 'receive_purchase' in line:
            print(f"Line {i}: {line.strip()}")

def main():
    find_receive_purchase_method()
    check_safe_business_controller()

if __name__ == "__main__":
    main()

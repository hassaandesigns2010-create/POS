#!/usr/bin/env python3
"""
Check the inheritance chain to find where receive_purchase actually exists
"""

import os
import sys

def check_safe_business_controller_inheritance():
    """Check what SafeBusinessController actually inherits from"""
    print("=" * 80)
    print("🔍 CHECKING SafeBusinessController INHERITANCE")
    print("=" * 80)
    
    safe_controller_file = os.path.join(os.path.dirname(__file__), 'controllers', 'safe_business_controller.py')
    
    if not os.path.exists(safe_controller_file):
        print("❌ safe_business_controller.py not found")
        return
    
    try:
        with open(safe_controller_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Could not read safe_business_controller.py: {e}")
        return
    
    lines = content.split('\n')
    
    # Find the class definition
    for i, line in enumerate(lines, 1):
        if 'class SafeBusinessController' in line:
            print(f"📋 SafeBusinessController class definition:")
            print(f"  Line {i}: {line.strip()}")
            
            # Get inheritance
            if '(' in line and ')' in line:
                inheritance_part = line[line.find('(')+1:line.find(')')]
                print(f"  Inherits from: {inheritance_part}")
                
                # Check if it's multiple inheritance
                if ',' in inheritance_part:
                    parents = [p.strip() for p in inheritance_part.split(',')]
                    print(f"  Multiple inheritance from: {parents}")
            break

def check_for_base_classes():
    """Check for base classes that might have receive_purchase"""
    print(f"\n" + "=" * 80)
    print("🔍 CHECKING FOR BASE CLASSES")
    print("=" * 80)
    
    base_dir = os.path.dirname(__file__)
    
    # Common base class names
    base_class_names = [
        'BaseController',
        'Controller',
        'BusinessLogic',
        'PurchaseController',
        'StockController'
    ]
    
    for base_class in base_class_names:
        print(f"\n🔍 Looking for {base_class} class:")
        
        python_files = []
        for root, dirs, files in os.walk(base_dir):
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        
        found_classes = []
        
        for file_path in python_files:
            if any(skip in file_path for skip in ['__pycache__', '.git', 'venv', 'env', 'tests']):
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            except Exception:
                continue
            
            lines = content.split('\n')
            
            for i, line in enumerate(lines, 1):
                if f'class {base_class}' in line:
                    rel_path = os.path.relpath(file_path, base_dir)
                    found_classes.append(f"{rel_path} Line {i}: {line.strip()}")
                    
                    # Check for receive_purchase method in this class
                    receive_purchase_lines = []
                    for j in range(i, len(lines)):
                        line_j = lines[j]
                        if 'def receive_purchase' in line_j:
                            receive_purchase_lines.append(f"    Line {j+1}: {line_j.strip()}")
                        # Stop at next class
                        if line_j.strip().startswith('class ') and j > i:
                            break
                    
                    if receive_purchase_lines:
                        print(f"    ✅ receive_purchase method found:")
                        for line in receive_purchase_lines:
                            print(f"    {line}")
                    else:
                        print(f"    ❌ No receive_purchase method found")
                    
                    break
        
        if found_classes:
            print(f"📋 Found {len(found_classes)} {base_class} classes:")
            for found in found_classes:
                print(f"  {found}")
        else:
            print(f"❓ No {base_class} classes found")

def check_all_controller_classes():
    """Check all controller classes for receive_purchase"""
    print(f"\n" + "=" * 80)
    print("🔍 CHECKING ALL CONTROLLER CLASSES")
    print("=" * 80)
    
    controllers_dir = os.path.join(os.path.dirname(__file__), 'controllers')
    
    if not os.path.exists(controllers_dir):
        print("❌ Controllers directory not found")
        return
    
    controller_files = []
    for file in os.listdir(controllers_dir):
        if file.endswith('.py'):
            controller_files.append(os.path.join(controllers_dir, file))
    
    print(f"📁 Found {len(controller_files)} controller files:")
    
    for file_path in controller_files:
        rel_path = os.path.relpath(file_path, os.path.dirname(__file__))
        print(f"\n🔍 Checking {rel_path}:")
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            print(f"  ❌ Could not read: {e}")
            continue
        
        lines = content.split('\n')
        
        # Find all classes in this file
        classes_in_file = []
        for i, line in enumerate(lines, 1):
            if 'class ' in line and not line.strip().startswith('#'):
                classes_in_file.append(f"Line {i}: {line.strip()}")
        
        if classes_in_file:
            print(f"  📋 Classes found:")
            for class_line in classes_in_file:
                print(f"    {class_line}")
            
            # Check for receive_purchase in this file
            receive_purchase_in_file = []
            for i, line in enumerate(lines, 1):
                if 'def receive_purchase' in line:
                    receive_purchase_in_file.append(f"Line {i}: {line.strip()}")
            
            if receive_purchase_in_file:
                print(f"  ✅ receive_purchase method found:")
                for method_line in receive_purchase_in_file:
                    print(f"    {method_line}")
            else:
                print(f"  ❌ No receive_purchase method found")
        else:
            print(f"  ❓ No classes found")

def main():
    check_safe_business_controller_inheritance()
    check_for_base_classes()
    check_all_controller_classes()

if __name__ == "__main__":
    main()

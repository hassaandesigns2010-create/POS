#!/usr/bin/env python3
"""
Find the actual BusinessController class
"""

import os
import sys
import re

def find_business_controller():
    """Find where BusinessController class is defined"""
    print("=" * 80)
    print("🔍 FINDING BusinessController CLASS")
    print("=" * 80)
    
    base_dir = os.path.dirname(__file__)
    
    # Search all Python files for BusinessController
    python_files = []
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    business_controller_found = []
    
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
            if 'class BusinessController' in line:
                rel_path = os.path.relpath(file_path, base_dir)
                business_controller_found.append(f"{rel_path} Line {i}: {line.strip()}")
                
                # Get the class definition and some context
                print(f"\n📋 Found BusinessController in {rel_path}:")
                print(f"  Line {i}: {line.strip()}")
                
                # Show some context around the class
                start_line = max(0, i-2)
                end_line = min(len(lines), i+10)
                print(f"  Context (lines {start_line+1}-{end_line}):")
                for j in range(start_line, end_line):
                    print(f"    {j+1}: {lines[j]}")
                
                # Look for receive_purchase method in this file
                receive_purchase_lines = []
                for j in range(i, len(lines)):
                    line_j = lines[j]
                    if 'def receive_purchase' in line_j:
                        receive_purchase_lines.append(f"    Line {j+1}: {line_j.strip()}")
                    # Stop at next class
                    if re.match(r'^\s*class\s+', line_j):
                        break
                
                if receive_purchase_lines:
                    print(f"\n  ✅ receive_purchase method found:")
                    for line in receive_purchase_lines:
                        print(f"  {line}")
                else:
                    print(f"\n  ❌ No receive_purchase method found")
                
                break
    
    if not business_controller_found:
        print(f"❌ No BusinessController class found!")
    
    print(f"\n" + "=" * 80)
    print(f"📊 SUMMARY: {len(business_controller_found)} BusinessController classes found")
    for found in business_controller_found:
        print(f"  {found}")

def check_for_method_addition():
    """Check if receive_purchase is added dynamically"""
    print(f"\n" + "=" * 80)
    print(f"🔍 CHECKING FOR DYNAMIC METHOD ADDITION")
    print("=" * 80)
    
    base_dir = os.path.dirname(__file__)
    
    # Look for files that might add methods dynamically
    python_files = []
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    dynamic_additions = []
    
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
            
            # Look for patterns that add methods to classes
            if any(pattern in line_lower for pattern in [
                'setattr.*receive_purchase',
                'businesscontroller.*receive_purchase',
                'controller.*receive_purchase',
                'add_method.*receive_purchase',
                'type.*receive_purchase',
                'methodtype.*receive_purchase'
            ]):
                rel_path = os.path.relpath(file_path, base_dir)
                dynamic_additions.append(f"{rel_path} Line {i}: {line.strip()}")
    
    if dynamic_additions:
        print(f"🚨 Found {len(dynamic_additions)} potential dynamic additions:")
        for addition in dynamic_additions:
            print(f"  {addition}")
    else:
        print(f"❓ No dynamic method additions found")

def check_for_method_delegation():
    """Check if receive_purchase is delegated to another class"""
    print(f"\n" + "=" * 80)
    print(f"🔍 CHECKING FOR METHOD DELEGATION")
    print("=" * 80)
    
    base_dir = os.path.dirname(__file__)
    
    # Look for delegation patterns
    python_files = []
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    delegation_patterns = []
    
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
            
            # Look for delegation patterns
            if any(pattern in line_lower for pattern in [
                'delegate.*receive_purchase',
                'proxy.*receive_purchase',
                'wrapper.*receive_purchase',
                'fallback.*receive_purchase',
                'alternative.*receive_purchase',
                'backup.*receive_purchase'
            ]):
                rel_path = os.path.relpath(file_path, base_dir)
                delegation_patterns.append(f"{rel_path} Line {i}: {line.strip()}")
    
    if delegation_patterns:
        print(f"🚨 Found {len(delegation_patterns)} delegation patterns:")
        for pattern in delegation_patterns:
            print(f"  {pattern}")
    else:
        print(f"❓ No delegation patterns found")

def main():
    find_business_controller()
    check_for_method_addition()
    check_for_method_delegation()

if __name__ == "__main__":
    main()

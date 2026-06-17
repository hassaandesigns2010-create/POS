#!/usr/bin/env python3
"""
Fix sales.py to hide purchase price and profit columns for worker users
"""

import os

def fix_sales_file():
    file_path = r"C:\Users\pc\Music\pos_app\views\sales.py"
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and replace the cart table setup
    old_code = '''        # Replace the cart table with our custom one
        self.cart_table = CartTableWidget(self)
        self.cart_table.setColumnCount(10)
        self.cart_table.setHorizontalHeaderLabels([
            "Product Name", "Qty", "Purchase Price", "Sale Price", "Total", "Profit", "Remove", "Bought Qty", "Stock", "Item Disc"
        ])'''
    
    new_code = '''        # Replace the cart table with our custom one
        self.cart_table = CartTableWidget(self)
        self.cart_table.setColumnCount(10)
        
        # Set headers based on user role
        if self._is_worker_user():
            # Worker user - hide purchase price and profit columns
            self.cart_table.setHorizontalHeaderLabels([
                "Product Name", "Qty", "", "Sale Price", "Total", "", "Remove", "Bought Qty", "Stock", "Item Disc"
            ])
            # Hide purchase price (column 2) and profit (column 5) columns
            self.cart_table.setColumnHidden(2, True)  # Purchase Price
            self.cart_table.setColumnHidden(5, True)  # Profit
        else:
            # Admin user - show all columns
            self.cart_table.setHorizontalHeaderLabels([
                "Product Name", "Qty", "Purchase Price", "Sale Price", "Total", "Profit", "Remove", "Bought Qty", "Stock", "Item Disc"
            ])'''
    
    # Replace the code
    if old_code in content:
        content = content.replace(old_code, new_code)
        
        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Successfully updated sales.py to hide purchase price and profit for worker users")
        return True
    else:
        print("❌ Could not find the target code in sales.py")
        return False

if __name__ == "__main__":
    fix_sales_file()

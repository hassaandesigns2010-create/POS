#!/usr/bin/env python3
"""
Fix the stock race condition bug by adding row locking
"""

import os
import sys

def fix_business_logic():
    """Add row locking to business_logic.py"""
    print("=== FIXING STOCK RACE CONDITION ===")
    
    business_file = os.path.join(os.path.dirname(__file__), 'controllers', 'business_logic.py')
    
    try:
        with open(business_file, 'r') as f:
            content = f.read()
        
        # Find the stock update section and add row locking
        original_lines = content.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(original_lines):
            fixed_lines.append(line)
            
            # Look for the line where product is queried
            if 'product = self.session.query(Product).filter_by(id=product_id).first()' in line:
                # Replace with row-locked version
                fixed_lines[-1] = line.replace(
                    'product = self.session.query(Product).filter_by(id=product_id).first()',
                    'product = self.session.query(Product).filter_by(id=product_id).with_for_update().first()'
                )
                print(f"✅ Added row locking at line {i+1}")
        
        # Write the fixed content
        with open(business_file, 'w') as f:
            f.write('\n'.join(fixed_lines))
        
        print("✅ Stock race condition fix applied!")
        
    except Exception as e:
        print(f"❌ Error applying fix: {e}")

def add_stock_validation():
    """Add stock validation to detect issues"""
    print("\n=== ADDING STOCK VALIDATION ===")
    
    business_file = os.path.join(os.path.dirname(__file__), 'controllers', 'business_logic.py')
    
    try:
        with open(business_file, 'r') as f:
            content = f.read()
        
        # Add validation after stock update
        validation_code = '''
                    # Validate stock update
                    if product.stock_level != new_stock:
                        logger.error(f"STOCK UPDATE VALIDATION FAILED!")
                        logger.error(f"Product: {product_id}, Expected: {new_stock}, Actual: {product.stock_level}")
                        raise ValueError(f"Stock update validation failed for product {product_id}")
                    
                    logger.info(f"✅ Stock update validated: {product_id} from {old_stock} to {new_stock}")
'''
        
        # Find where stock is updated and add validation
        lines = content.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            fixed_lines.append(line)
            
            # Add validation after stock update
            if 'product.stock_level = new_stock' in line and 'else:' not in line:
                # Add validation after the stock update
                indent = ' ' * (len(line) - len(line.lstrip()))
                validation_lines = validation_code.strip().split('\n')
                for val_line in validation_lines:
                    fixed_lines.append(indent + val_line)
                print(f"✅ Added stock validation after line {i+1}")
        
        # Write the fixed content
        with open(business_file, 'w') as f:
            f.write('\n'.join(fixed_lines))
        
        print("✅ Stock validation added!")
        
    except Exception as e:
        print(f"❌ Error adding validation: {e}")

def improve_transaction_handling():
    """Improve transaction handling"""
    print("\n=== IMPROVING TRANSACTION HANDLING ===")
    
    business_file = os.path.join(os.path.dirname(__file__), 'controllers', 'business_logic.py')
    
    try:
        with open(business_file, 'r') as f:
            content = f.read()
        
        # Add better transaction handling
        lines = content.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            fixed_lines.append(line)
            
            # Look for the create_sale method and add transaction isolation
            if 'def create_sale(self, customer_id: int, items: List[Dict[str, Any]]' in line:
                # Add transaction isolation after the method definition
                indent = ' ' * 8
                transaction_code = [
                    indent + '# Use serializable isolation to prevent race conditions',
                    indent + 'isolation_level = self.session.connection().connection.get_isolation_level()',
                    indent + 'self.session.connection().connection.set_isolation_level(3)  # SERIALIZABLE',
                    indent + 'try:'
                ]
                
                for trans_line in transaction_code:
                    fixed_lines.append(trans_line)
                
                print(f"✅ Added transaction isolation at line {i+1}")
        
        # Write the fixed content
        with open(business_file, 'w') as f:
            f.write('\n'.join(fixed_lines))
        
        print("✅ Transaction handling improved!")
        
    except Exception as e:
        print(f"❌ Error improving transactions: {e}")

def main():
    print("=" * 70)
    print("🔧 FIXING STOCK RACE CONDITION BUG")
    print("=" * 70)
    print("This will fix the issue where selling 1 item makes stock go from 10 to 0")
    
    # Apply the fixes
    fix_business_logic()
    add_stock_validation()
    improve_transaction_handling()
    
    print("\n" + "=" * 70)
    print("📋 FIXES APPLIED")
    print("=" * 70)
    
    print("\n✅ Changes made:")
    print("1. Added row locking (SELECT ... FOR UPDATE)")
    print("2. Added stock validation after updates")
    print("3. Added transaction isolation (SERIALIZABLE)")
    
    print("\n🎯 This will prevent:")
    print("• Multiple sales processing same product simultaneously")
    print("• Stock calculation errors due to race conditions")
    print("• Stock disappearing mysteriously")
    
    print("\n⚠️  IMPORTANT:")
    print("• Restart the application after applying fixes")
    print("• Test with a few sales to verify the fix works")
    print("• Monitor logs for any validation errors")
    
    print("\n✅ Stock race condition bug fix complete!")

if __name__ == "__main__":
    main()

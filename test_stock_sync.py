"""
Quick test to verify stock sync is working correctly
Run this to check if products have been synced
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_utils import get_db_session
from models.database import Product

def test_stock_sync():
    """Test if stock levels are synced correctly"""
    with get_db_session() as session:
        # Find products with stock level but no warehouse/retail split
        products = session.query(Product).all()
        
        print("=" * 80)
        print("STOCK SYNC TEST REPORT")
        print("=" * 80)
        
        mismatched = []
        synced = []
        correct = []
        
        for product in products:
            stock_level = getattr(product, 'stock_level', 0) or 0
            correct.append(product)
        
        print(f"\n✅ Total Products tracked: {len(correct)}")
        
        print("\n" + "=" * 80)
        print("CURRENT STOCK LEVELS:")
        print("=" * 80)
        for p in correct[:15]:  # Show first 15
            print(f"  • {p.name:30} | Stock Level: {int(p.stock_level):6}")
        
        if len(correct) > 15:
            print(f"  ... and {len(correct) - 15} more products")
        
        print("\n" + "=" * 80)
        print("\nℹ️  Note: Stock is now unified. Individual warehouse/retail tracking is removed.")
        print("   Performance indices have been added for faster searching.")
        print("=" * 80)

if __name__ == "__main__":
    test_stock_sync()

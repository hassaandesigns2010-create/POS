#!/usr/bin/env python3
"""Test script to verify the customer statement HTML template"""

# Test the HTML template with discount data
test_data = {
    "total_sales": 150.0,
    "total_discounts": 2.0,
    "balance": 150.0
}

# Simulate the HTML template logic
def format_currency(value):
    try:
        return f"Rs {float(value):,.2f}"
    except Exception:
        return f"Rs {value}"

# Test the conditional discount row
discount_row = ""
if test_data.get("total_discounts", 0) > 0:
    discount_row = f'''<tr style="background: linear-gradient(135deg, #fef2f2, #fee2e2); border-top: 2px solid #dc2626;">
                <td colspan="6" style="text-align: right; font-weight: 700; font-size: 1.1rem; padding: 0.5rem 1rem; color: #dc2626;">DISCOUNT GIVEN:</td>
                <td style="text-align: center; font-weight: 800; font-size: 1.2rem; color: #dc2626; padding: 0.5rem 1rem;">{format_currency(-test_data["total_discounts"])}</td>
            </tr>'''

print("=== Customer Statement HTML Template Test ===")
print()
print("Test Data:")
print(f"  Total Sales: Rs {test_data['total_sales']}")
print(f"  Total Discounts: Rs {test_data['total_discounts']}")
print(f"  Balance: Rs {test_data['balance']}")
print()
print("Generated Discount Row:")
print("✅ Condition met (total_discounts > 0)" if test_data.get("total_discounts", 0) > 0 else "❌ Condition not met")
print()
if discount_row:
    print("HTML Output:")
    print(discount_row)
else:
    print("❌ No discount row generated")

print()
print("Expected in printed output:")
print("┌─────────────────────────────────────────────────┐")
print("│ TOTAL OF THAT SALE:                    Rs 150.00 │")
print("│ DISCOUNT GIVEN:                          Rs -2.00 │  ← RED ROW")
print("│ AMOUNT DUE:                             Rs 150.00 │")
print("└─────────────────────────────────────────────────┘")

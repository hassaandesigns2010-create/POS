"""
Script to add create_purchase method to BusinessController
"""

# Read the business logic file
with open(r'f:\pos_app\controllers\business_logic.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the line after create_sale method ends
insert_line = None
for i, line in enumerate(lines):
    if 'raise ValueError(f"Sale creation failed: {str(e)}")' in line:
        # Find the next blank line or method definition
        for j in range(i+1, len(lines)):
            if lines[j].strip() == '' or lines[j].strip().startswith('def '):
                insert_line = j
                break
        break

if insert_line is None:
    print("ERROR: Could not find insertion point")
    exit(1)

# Read the new method
with open(r'f:\pos_app\temp_create_purchase_method.py', 'r', encoding='utf-8') as f:
    method_content = f.read()

# Prepare the method with proper indentation
method_lines = []
method_lines.append('\n')
for line in method_content.split('\n'):
    if line.strip():
        method_lines.append('    ' + line + '\n')
    else:
        method_lines.append('\n')
method_lines.append('\n')

# Insert the method
lines[insert_line:insert_line] = method_lines

# Write back
with open(r'f:\pos_app\controllers\business_logic.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print(f"✓ Successfully added create_purchase method at line {insert_line}")

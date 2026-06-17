
import os

file_path = r"f:/pos_app/controllers/business_logic.py"

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # We want to keep lines up to line 566.
    # Lines are 0-indexed in list, so index 566 means keeping 566 lines (0 to 565).
    # Step 1694 showed line 566 as '        return False'.
    # Line 567 started duplication.
    
    keep_lines = lines[:566]
    
    # Verify the cut point
    last_line = keep_lines[-1].strip()
    print(f"Last kept line: {last_line}")
    
    if last_line != "return False":
        print(f"Warning: Line 566 is '{last_line}', expected 'return False'. Check indices.")
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(keep_lines)
        
    print(f"Successfully truncated {file_path} to {len(keep_lines)} lines.")
    
except Exception as e:
    print(f"Error: {e}")

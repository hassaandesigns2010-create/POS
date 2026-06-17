import os
import re

# Directory containing backup files
backup_dir = r"C:\Users\pc\Documents\backups"

# Search patterns
search_patterns = ["015", "15", "2015", "0150", "0151", "0152", "0153", "0154", "0155", "0156", "0157", "0158", "0159"]

# Check if directory exists
if not os.path.exists(backup_dir):
    print(f"Directory {backup_dir} does not exist")
    exit()

print(f"Searching for patterns containing '015' in SQL backup files...")
print("=" * 80)

# Get all SQL files
sql_files = [f for f in os.listdir(backup_dir) if f.endswith('.sql')]

# Categories for organizing results
categories = {
    "Product IDs": [],
    "Invoice Numbers": [],
    "Timestamps": [],
    "Stock IDs": [],
    "Other": []
}

for sql_file in sql_files:
    file_path = os.path.join(backup_dir, sql_file)
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
            # Search for each pattern
            for pattern in search_patterns:
                if pattern in content:
                    lines = content.split('\n')
                    for line_num, line in enumerate(lines, 1):
                        if pattern in line:
                            # Categorize the match
                            line_lower = line.lower()
                            
                            # Check for different contexts
                            if any(keyword in line_lower for keyword in ['product', 'item', 'sku']):
                                categories["Product IDs"].append((sql_file, line_num, pattern, line.strip()))
                            elif any(keyword in line_lower for keyword in ['invoice', 'sale', 'inv']):
                                categories["Invoice Numbers"].append((sql_file, line_num, pattern, line.strip()))
                            elif any(keyword in line_lower for keyword in ['timestamp', 'date', 'time']):
                                categories["Timestamps"].append((sql_file, line_num, pattern, line.strip()))
                            elif any(keyword in line_lower for keyword in ['stock', 'inventory']):
                                categories["Stock IDs"].append((sql_file, line_num, pattern, line.strip()))
                            else:
                                categories["Other"].append((sql_file, line_num, pattern, line.strip()))
    
    except Exception as e:
        print(f"Error reading {sql_file}: {e}")

# Display results by category
for category, matches in categories.items():
    if matches:
        print(f"\n🔍 {category.upper()}")
        print("-" * 60)
        
        # Show unique matches (avoid duplicates)
        unique_matches = list(set(matches))
        unique_matches.sort()
        
        for i, (file, line_num, pattern, line) in enumerate(unique_matches[:10]):  # Limit to 10 per category
            print(f"{i+1}. {file} - Line {line_num}")
            print(f"   Pattern: '{pattern}'")
            print(f"   Content: {line[:100]}...")
            print()
        
        if len(unique_matches) > 10:
            print(f"   ... and {len(unique_matches) - 10} more matches in this category")

# Summary
total_matches = sum(len(matches) for matches in categories.values())
print(f"\n📊 SUMMARY")
print("=" * 60)
print(f"Total matches found: {total_matches}")
for category, matches in categories.items():
    print(f"{category}: {len(matches)} matches")

# Look for specific remote-related entries
print(f"\n🔍 SEARCHING FOR REMOTE-RELATED ENTRIES")
print("=" * 60)

remote_keywords = ["remote", "branch", "store", "location"]
for sql_file in sql_files:
    file_path = os.path.join(backup_dir, sql_file)
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
            for keyword in remote_keywords:
                if keyword in content.lower():
                    lines = content.split('\n')
                    for line_num, line in enumerate(lines, 1):
                        if keyword in line.lower() and any(pattern in line for pattern in search_patterns):
                            print(f"📍 {sql_file} - Line {line_num}")
                            print(f"   {line.strip()}")
                            print()
    
    except Exception as e:
        print(f"Error reading {sql_file}: {e}")

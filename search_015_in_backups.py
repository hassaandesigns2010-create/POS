import os
import re

# Directory containing backup files
backup_dir = r"C:\Users\pc\Documents\backups"

# Search pattern
search_pattern = "015"

# Check if directory exists
if not os.path.exists(backup_dir):
    print(f"Directory {backup_dir} does not exist")
    exit()

print(f"Searching for '{search_pattern}' in SQL backup files...")
print("=" * 60)

# Get all SQL files
sql_files = [f for f in os.listdir(backup_dir) if f.endswith('.sql')]

matches_found = False

for sql_file in sql_files:
    file_path = os.path.join(backup_dir, sql_file)
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
            # Search for the pattern
            if search_pattern in content:
                matches_found = True
                print(f"\n📁 FILE: {sql_file}")
                print("-" * 40)
                
                # Find all lines containing the pattern
                lines = content.split('\n')
                for line_num, line in enumerate(lines, 1):
                    if search_pattern in line:
                        # Highlight the match
                        highlighted = line.replace(search_pattern, f"**{search_pattern}**")
                        print(f"Line {line_num}: {highlighted.strip()}")
                        
                        # If it's too long, show just the relevant part
                        if len(line) > 200:
                            start_pos = line.find(search_pattern)
                            if start_pos != -1:
                                start = max(0, start_pos - 50)
                                end = min(len(line), start_pos + len(search_pattern) + 50)
                                print(f"  -> Context: ...{line[start:end]}...")
                
                print()
    
    except Exception as e:
        print(f"Error reading {sql_file}: {e}")

if not matches_found:
    print(f"No matches found for '{search_pattern}' in any SQL backup files.")
else:
    print(f"Search completed. Found '{search_pattern}' in the files above.")

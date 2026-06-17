
import ast

def clean_duplicates(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        tree = ast.parse(content)

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == 'SalesWidget':
            methods = {}
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    if item.name in methods:
                        methods[item.name].append((item.lineno, item.end_lineno))
                    else:
                        methods[item.name] = [(item.lineno, item.end_lineno)]
            
            # Identify ranges to delete (all but the LAST one)
            to_delete = []
            for name, ranges in methods.items():
                if len(ranges) > 1:
                    print(f"Preserving last instance of '{name}' at line {ranges[-1][0]}")
                    to_delete.extend(ranges[:-1])
            
            # Delete from bottom up to avoid line shifting issues during deletion
            to_delete.sort(key=lambda x: x[0], reverse=True)
            
            for start, end in to_delete:
                print(f"Deleting duplicate method from line {start} to {end}")
                # Lines are 1-indexed, Python list is 0-indexed
                del lines[start-1:end]
                
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print("Cleanup complete.")

if __name__ == "__main__":
    clean_duplicates(r'f:\pos_app\views\sales.py')


import ast

def find_duplicates(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        tree = ast.parse(f.read())

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == 'SalesWidget':
            methods = {}
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    if item.name in methods:
                        methods[item.name].append(item.lineno)
                    else:
                        methods[item.name] = [item.lineno]
            
            for name, lines in methods.items():
                if len(lines) > 1:
                    print(f"Method '{name}' is defined multiple times: {lines}")

if __name__ == "__main__":
    find_duplicates(r'f:\pos_app\views\sales.py')

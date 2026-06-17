import os
import re

patterns = [
    re.compile(r'QTimer'),
    re.compile(r'Thread\('),
    re.compile(r'QThread')
]

for root, dirs, files in os.walk('.'):
    if 'venv' in root or '.git' in root or '__pycache__' in root:
        continue
    for file in files:
        if file.endswith('.py'):
            path = os.path.join(root, file)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, 1):
                        for pattern in patterns:
                            if pattern.search(line):
                                print(f"{path}:{line_num}: {line.strip()}")
                                break
            except Exception as e:
                pass

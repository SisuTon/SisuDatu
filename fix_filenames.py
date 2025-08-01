import os
from pathlib import Path

def lowercase_files(root_dir):
    for path in Path(root_dir).rglob('*.py'):
        if path.name != path.name.lower():
            new_path = path.with_name(path.name.lower())
            os.rename(path, new_path)
            print(f"Renamed: {path} -> {new_path}")

if __name__ == '__main__':
    lowercase_files('app') 
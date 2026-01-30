
import os
import sys

# To fix encoding issues on Windows
sys.stdout.reconfigure(encoding='utf-8')

def list_tree(startpath, indent=""):
    try:
        entries = sorted(os.listdir(startpath))
    except OSError:
        print(indent + "|-- [ACCESS DENIED]")
        return

    for item in entries:
        if item == ".git": continue # Skip git internal data
        if item == "__pycache__": continue

        path = os.path.join(startpath, item)
        print(indent + "|-- " + item)
        if os.path.isdir(path):
            list_tree(path, indent + "    ")

if __name__ == "__main__":
    start_dir = r"Q:\Dev\Google Avinity\geologix_knowledge_base"
    print(f"Listing all files in: {start_dir}")
    list_tree(start_dir)

import sys
from pathlib import Path
import json

# Adjust path to import core system
sys.path.append(str(Path(__file__).resolve().parent.parent))
from Core_System.file_storage import FileStorage
from Core_System.categorizer import Categorizer

def run_import():
    print("Initializing Geologix Knowledge DB Importer...")
    print("Target: Strategic Knowledge Database")
    
    storage = FileStorage()
    categorizer = Categorizer()
    
    files = storage.list_documents("knowledge")
    print(f"Found {len(files)} strategic documents.")
    
    index = []
    
    for idx, file_data in enumerate(files):
        # Read content for better indexing (small files)
        content_bytes = storage.read_file(file_data['path'])
        content_preview = ""
        if content_bytes:
            try:
                content_preview = content_bytes.decode('utf-8')[:1000] # First 1000 chars
            except:
                pass
        
        meta = categorizer.categorize_file(file_data['filename'], content_preview)
        
        entry = {
            "id": f"kb-{idx}",
            "filename": file_data['filename'],
            "path": file_data['path'],
            "category": "STRATEGIC_KNOWLEDGE",
            "tags": meta['tags'] + ["strategic", "verified"],
            "preview": content_preview[:200]
        }
        index.append(entry)
        
    # Save Index
    output_file = Path(__file__).parent.parent / "Data_Directories" / "knowledge_index.json"
    with open(output_file, 'w') as f:
        json.dump(index, f, indent=2)
        
    print(f"Import Complete. {len(index)} documents indexed.")

if __name__ == "__main__":
    run_import()

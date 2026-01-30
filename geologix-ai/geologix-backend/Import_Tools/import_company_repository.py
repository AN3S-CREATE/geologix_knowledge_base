import sys
from pathlib import Path
import json

# Adjust path to import core system
sys.path.append(str(Path(__file__).resolve().parent.parent))
from Core_System.file_storage import FileStorage
from Core_System.categorizer import Categorizer

def run_import():
    print("Initializing Geologix Knowledge Base Importer...")
    print("Target: Company Documents")
    
    storage = FileStorage()
    categorizer = Categorizer()
    
    # List all files
    files = storage.list_documents("documents")
    print(f"Found {len(files)} files in repository.")
    
    index = []
    
    # Process files
    for idx, file_data in enumerate(files):
        # Progress indicator
        if idx % 50 == 0:
            print(f"Processing {idx}/{len(files)}...")
            
        # Categorize
        meta = categorizer.categorize_file(file_data['filename'])
        
        # Build Index Entry
        entry = {
            "id": idx,
            "filename": file_data['filename'],
            "path": file_data['path'],
            "category": meta['category'],
            "tags": meta['tags'],
            "size": file_data['size']
        }
        index.append(entry)
        
    # Save Index (Mock Vector DB insertion)
    output_file = Path(__file__).parent.parent / "Data_Directories" / "company_index.json"
    with open(output_file, 'w') as f:
        json.dump(index, f, indent=2)
        
    print(f"\nImport Complete. Index saved to {output_file}")
    print(f"Successfully indexed {len(index)} items.")

if __name__ == "__main__":
    run_import()

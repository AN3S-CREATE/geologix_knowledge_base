import sys
from pathlib import Path

# Adjust path to import core system
sys.path.append(str(Path(__file__).resolve().parent.parent))
from Core_System.advanced_email_processor import AdvancedEmailProcessor

def run_import():
    print("Initializing Geologix Email Importer...")
    
    processor = AdvancedEmailProcessor()
    result = processor.process_all()
    
    if result:
        print("Email import successful.")
    else:
        print("Email import failed.")

if __name__ == "__main__":
    run_import()

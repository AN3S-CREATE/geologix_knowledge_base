import csv
import sys
import json
from pathlib import Path
from datetime import datetime
import re

# Adjust path to import config
sys.path.append(str(Path(__file__).resolve().parent.parent))
from geologix.config.config import SOURCE_EMAILS, DATA_DIR

class AdvancedEmailProcessor:
    """
    Parses legacy email exports (CSV/HTML) and creates a structured knowledge base index.
    """

    def __init__(self):
        self.source_dir = SOURCE_EMAILS
        self.index = []

    def clean_text(self, text):
        """Removes excessive whitespace and artifacts."""
        if not text:
            return ""
        return re.sub(r'\s+', ' ', text).strip()

    def parse_csv(self, file_path: Path):
        """
        Parses a single CSV email export.
        Assumes standard Outlook/Exchange export format.
        """
        print(f"Processing {file_path.name}...")
        count = 0
        
        try:
            # Try different encodings as email exports can be messy
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    # Normalize keys (handle case variations)
                    row_lower = {k.lower(): v for k, v in row.items() if k}
                    
                    # Extract fields
                    subject = row_lower.get('subject', 'No Subject')
                    sender = row_lower.get('from', row_lower.get('sender', 'Unknown'))
                    recipient = row_lower.get('to', row_lower.get('recipient', 'Unknown'))
                    body = row_lower.get('body', row_lower.get('description', ''))
                    date_str = row_lower.get('sent', row_lower.get('date', ''))

                    # Skip empty rows
                    if not body and not subject:
                        continue

                    entry = {
                        "source_file": file_path.name,
                        "subject": self.clean_text(subject),
                        "sender": self.clean_text(sender),
                        "recipient": self.clean_text(recipient),
                        "date": date_str, # Keep as string for now to avoid parsing errors
                        "preview": self.clean_text(body)[:200], # Store preview only for index
                        "full_body_offset": count # Could be used to seek in original file
                    }
                    
                    self.index.append(entry)
                    count += 1
                    
        except Exception as e:
            print(f"Error reading {file_path.name}: {e}")

        print(f"  -> Extracted {count} emails.")
        return count

    def process_all(self):
        """
        Scans source directory and processes all CSV files.
        """
        if not self.source_dir.exists():
            print(f"Source directory not found: {self.source_dir}")
            return

        total_emails = 0
        for file_path in self.source_dir.glob("*.csv"):
            total_emails += self.parse_csv(file_path)

        # Save Index
        output_file = DATA_DIR / "email_index.json"
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.index, f, indent=2, ensure_ascii=False)
            print(f"\nTotal Processed: {total_emails}")
            print(f"Index saved to: {output_file}")
            return output_file
        except Exception as e:
            print(f"Error saving index: {e}")
            return None

if __name__ == "__main__":
    processor = AdvancedEmailProcessor()
    processor.process_all()

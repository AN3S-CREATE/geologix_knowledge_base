"""
Compile all emails from CSV files into a single Markdown document.
"""
import csv
from pathlib import Path
from datetime import datetime

def compile_emails_to_md():
    """Read all CSV email files and compile into one markdown file."""
    
    emails_dir = Path(r"Q:\Dev\Google Avinity\geologix_knowledge_base\emails")
    output_file = emails_dir.parent / "All_Emails_Compiled.md"
    
    # Find all CSV files (excluding the compiled one)
    csv_files = sorted([f for f in emails_dir.glob("*.csv") if f.name != "All_Emails_Compiled.csv"])
    
    all_emails = []
    
    # Read each CSV file
    for csv_file in csv_files:
        print(f"Processing: {csv_file.name}")
        try:
            with open(csv_file, 'r', encoding='utf-8', errors='ignore') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Extract email data (field names may vary)
                    email_data = {
                        'source': csv_file.stem,  # File name without extension
                        'date': row.get('Date', row.get('Received', row.get('Sent', 'Unknown'))),
                        'from': row.get('From', row.get('Sender', 'Unknown')),
                        'to': row.get('To', row.get('Recipient', 'Unknown')),
                        'subject': row.get('Subject', 'No Subject'),
                        'body': row.get('Body', row.get('Content', row.get('Message', ''))),
                        'attachments': row.get('Attachments', 'None')
                    }
                    all_emails.append(email_data)
        except Exception as e:
            print(f"Error reading {csv_file.name}: {e}")
    
    # Sort emails by date (newest first)
    print(f"\nTotal emails found: {len(all_emails)}")
    
    # Write to markdown file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Complete Email Archive\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \n")
        f.write(f"**Total Emails:** {len(all_emails)}  \n")
        f.write(f"**Sources:** {len(csv_files)} CSV files\n\n")
        
        f.write("---\n\n")
        
        # Group by source file
        current_source = None
        for i, email in enumerate(all_emails, 1):
            # Add source header when it changes
            if email['source'] != current_source:
                current_source = email['source']
                f.write(f"\n## 📁 Source: {current_source}\n\n")
            
            # Write email
            f.write(f"### Email #{i}\n\n")
            f.write(f"**Date:** {email['date']}  \n")
            f.write(f"**From:** {email['from']}  \n")
            f.write(f"**To:** {email['to']}  \n")
            f.write(f"**Subject:** {email['subject']}  \n")
            if email['attachments'] and email['attachments'] != 'None':
                f.write(f"**Attachments:** {email['attachments']}  \n")
            f.write(f"\n**Message:**\n\n")
            f.write(f"{email['body']}\n\n")
            f.write("---\n\n")
    
    print(f"\n✅ Compiled {len(all_emails)} emails to: {output_file}")
    print(f"File size: {output_file.stat().st_size / 1024:.1f} KB")
    
    return str(output_file)

if __name__ == "__main__":
    output_path = compile_emails_to_md()
    print(f"\nOutput file: {output_path}")

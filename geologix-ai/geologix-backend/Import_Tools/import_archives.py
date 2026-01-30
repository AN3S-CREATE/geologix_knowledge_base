"""
Archive Indexer for GeoLogix AI
Indexes company archives for historical, operational, and strategic analysis.

Supports reporting types:
- Historical Reporting (past data analysis)
- Real-Time Performance (current metrics)
- Predictive Reporting (forecasting)
- Prescriptive Reporting (recommendations)
- Strategic/Operational/Management/Compliance Reporting
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime
import re

# Adjust path to import core system
sys.path.append(str(Path(__file__).resolve().parent.parent))
from Configuration.config import PROJECT_ROOT, DATA_DIR

# Archive location
ARCHIVE_DIR = PROJECT_ROOT / "archives"

# File type categories for reporting purposes
FILE_CATEGORIES = {
    # Financial & Reporting
    'financial': ['.xlsx', '.xls', '.csv'],
    # Documents & Reports
    'documents': ['.pdf', '.doc', '.docx', '.rtf', '.txt'],
    # Presentations
    'presentations': ['.ppt', '.pptx'],
    # Images & Media
    'media': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tif', '.tiff', '.mov', '.mp4'],
    # Data & Archives
    'data': ['.json', '.xml', '.zip', '.rar', '.7z'],
}

# Keywords for auto-tagging reports
REPORT_KEYWORDS = {
    'financial': ['invoice', 'payment', 'budget', 'cost', 'revenue', 'profit', 'expense', 'financial', 'accounting', 'tax', 'salary', 'wages'],
    'operational': ['production', 'output', 'logistics', 'transport', 'delivery', 'inventory', 'stock', 'mining', 'plant', 'maintenance'],
    'compliance': ['audit', 'compliance', 'safety', 'legal', 'regulation', 'certificate', 'license', 'permit', 'inspection'],
    'strategic': ['strategy', 'forecast', 'projection', 'analysis', 'trend', 'market', 'competitor', 'swot', 'kpi', 'dashboard'],
    'hr': ['employee', 'staff', 'hr', 'recruitment', 'performance', 'training', 'leave', 'payroll'],
    'sales': ['sales', 'customer', 'client', 'order', 'quote', 'tender', 'proposal', 'contract'],
}


def get_file_category(extension: str) -> str:
    """Determine file category based on extension."""
    ext = extension.lower()
    for category, extensions in FILE_CATEGORIES.items():
        if ext in extensions:
            return category
    return 'other'


def extract_report_tags(filename: str, path: str) -> list:
    """Extract relevant tags based on filename and path keywords."""
    tags = []
    text = (filename + " " + path).lower()
    
    for tag_category, keywords in REPORT_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text:
                tags.append(tag_category)
                break
    
    # Add year tags if found
    years = re.findall(r'20\d{2}', text)
    for year in set(years):
        tags.append(f"year_{year}")
    
    # Add month tags if found
    months = ['january', 'february', 'march', 'april', 'may', 'june', 
              'july', 'august', 'september', 'october', 'november', 'december',
              'jan', 'feb', 'mar', 'apr', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
    for month in months:
        if month in text:
            tags.append('monthly_report')
            break
    
    return list(set(tags))


def scan_archives(max_files: int = 50000) -> list:
    """Scan archive directories and build index."""
    print(f"Scanning archives at: {ARCHIVE_DIR}")
    
    if not ARCHIVE_DIR.exists():
        print(f"ERROR: Archive directory not found: {ARCHIVE_DIR}")
        return []
    
    index = []
    file_count = 0
    skipped = 0
    
    # Supported extensions for indexing
    indexable_extensions = set()
    for exts in FILE_CATEGORIES.values():
        indexable_extensions.update(exts)
    
    for root, dirs, files in os.walk(ARCHIVE_DIR):
        for filename in files:
            if file_count >= max_files:
                print(f"Reached max file limit: {max_files}")
                break
                
            filepath = Path(root) / filename
            ext = filepath.suffix.lower()
            
            # Skip non-indexable files
            if ext not in indexable_extensions:
                skipped += 1
                continue
            
            try:
                stat = filepath.stat()
                rel_path = str(filepath.relative_to(ARCHIVE_DIR))
                
                # Determine folder context
                parts = rel_path.split(os.sep)
                folder_context = parts[0] if parts else "root"
                
                entry = {
                    "id": f"arch-{file_count}",
                    "filename": filename,
                    "path": str(filepath),
                    "relative_path": rel_path,
                    "folder": folder_context,
                    "extension": ext,
                    "category": get_file_category(ext),
                    "size_bytes": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "tags": extract_report_tags(filename, rel_path),
                }
                
                index.append(entry)
                file_count += 1
                
                if file_count % 1000 == 0:
                    print(f"  Indexed {file_count} files...")
                    
            except Exception as e:
                skipped += 1
                continue
        
        if file_count >= max_files:
            break
    
    print(f"Scan complete: {file_count} files indexed, {skipped} skipped")
    return index


def generate_statistics(index: list) -> dict:
    """Generate statistics about the archive for AI context."""
    stats = {
        "total_files": len(index),
        "by_category": {},
        "by_folder": {},
        "by_extension": {},
        "by_tag": {},
        "date_range": {"earliest": None, "latest": None},
    }
    
    for entry in index:
        # Category counts
        cat = entry['category']
        stats['by_category'][cat] = stats['by_category'].get(cat, 0) + 1
        
        # Folder counts
        folder = entry['folder']
        stats['by_folder'][folder] = stats['by_folder'].get(folder, 0) + 1
        
        # Extension counts
        ext = entry['extension']
        stats['by_extension'][ext] = stats['by_extension'].get(ext, 0) + 1
        
        # Tag counts
        for tag in entry['tags']:
            stats['by_tag'][tag] = stats['by_tag'].get(tag, 0) + 1
        
        # Date range
        mod_date = entry['modified']
        if stats['date_range']['earliest'] is None or mod_date < stats['date_range']['earliest']:
            stats['date_range']['earliest'] = mod_date
        if stats['date_range']['latest'] is None or mod_date > stats['date_range']['latest']:
            stats['date_range']['latest'] = mod_date
    
    return stats


def run_import():
    """Main import function."""
    print("=" * 60)
    print("GeoLogix AI - Archive Indexer")
    print("=" * 60)
    print(f"Started at: {datetime.now().isoformat()}")
    print()
    
    # Scan archives
    index = scan_archives()
    
    if not index:
        print("No files indexed. Exiting.")
        return
    
    # Generate statistics
    stats = generate_statistics(index)
    
    # Save index
    output_file = DATA_DIR / "archive_index.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2)
    print(f"\nIndex saved to: {output_file}")
    
    # Save statistics
    stats_file = DATA_DIR / "archive_stats.json"
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2)
    print(f"Statistics saved to: {stats_file}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("ARCHIVE SUMMARY")
    print("=" * 60)
    print(f"Total Files Indexed: {stats['total_files']}")
    print(f"\nBy Category:")
    for cat, count in sorted(stats['by_category'].items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count}")
    print(f"\nBy Folder:")
    for folder, count in sorted(stats['by_folder'].items(), key=lambda x: -x[1]):
        print(f"  {folder}: {count}")
    print(f"\nTop Tags:")
    for tag, count in sorted(stats['by_tag'].items(), key=lambda x: -x[1])[:15]:
        print(f"  {tag}: {count}")
    print(f"\nDate Range: {stats['date_range']['earliest'][:10]} to {stats['date_range']['latest'][:10]}")
    print("=" * 60)
    print("Archive indexing complete!")


if __name__ == "__main__":
    run_import()

"""
Automated import updater for GeoLogix repository refactoring.
Updates all imports from old structure to new geologix package structure.
"""
import re
from pathlib import Path

# Define import replacements
IMPORT_REPLACEMENTS = [
    # Core_System imports
    (r'from Core_System\.(\w+)', r'from geologix.core.\1'),
    (r'import Core_System\.(\w+)', r'import geologix.core.\1'),
    
    # Configuration imports
    (r'from Configuration\.(\w+)', r'from geologix.config.\1'),
    (r'import Configuration\.(\w+)', r'import geologix.config.\1'),
    
    # Import_Tools imports
    (r'from Import_Tools\.(\w+)', r'from geologix.import_tools.\1'),
    (r'import Import_Tools\.(\w+)', r'import geologix.import_tools.\1'),
]

def update_imports_in_file(file_path: Path) -> tuple[int, list[str]]:
    """Update imports in a single file. Returns (count, changes_made)."""
    if not file_path.exists():
        return 0, []
    
    content = file_path.read_text(encoding='utf-8')
    original_content = content
    changes = []
    
    for pattern, replacement in IMPORT_REPLACEMENTS:
        matches = re.findall(pattern, content)
        if matches:
            new_content = re.sub(pattern, replacement, content)
            if new_content != content:
                changes.append(f"  {pattern} -> {replacement}")
                content = new_content
    
    if content != original_content:
        file_path.write_text(content, encoding='utf-8')
        return len(changes), changes
    
    return 0, []

def main():
    """Update imports in all Python files."""
    project_root = Path(__file__).parent.parent
    
    # Directories to process
    dirs_to_process = [
        project_root / "src" / "geologix" / "core",
        project_root / "src" / "geologix" / "import_tools",
        project_root / "src" / "geologix" / "config",
        project_root / "tests",
    ]
    
    total_files = 0
    total_changes = 0
    
    print("=" * 60)
    print("GeoLogix Import Updater")
    print("=" * 60)
    
    for directory in dirs_to_process:
        if not directory.exists():
            print(f"\n⚠️  Directory not found: {directory}")
            continue
        
        print(f"\n📁 Processing: {directory.relative_to(project_root)}")
        print("-" * 60)
        
        for py_file in directory.glob("*.py"):
            if py_file.name == "__init__.py":
                continue
            
            count, changes = update_imports_in_file(py_file)
            if count > 0:
                total_files += 1
                total_changes += count
                print(f"✓ {py_file.name} - {count} import(s) updated")
                for change in changes:
                    print(change)
            else:
                print(f"  {py_file.name} - no changes needed")
    
    print("\n" + "=" * 60)
    print(f"✅ Complete: Updated {total_changes} imports in {total_files} files")
    print("=" * 60)

if __name__ == "__main__":
    main()

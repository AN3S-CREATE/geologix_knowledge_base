import shutil
import os
from pathlib import Path
from typing import List, Dict, Optional
import sys

# Adjust path to import config
sys.path.append(str(Path(__file__).resolve().parent.parent))
from Configuration.config import SOURCE_DOCUMENTS, SOURCE_EMAILS, STORAGE_DIR, SOURCE_KNOWLEDGE_DB
from Core_System.categorizer import Categorizer

class FileStorage:
    """
    Handles read-only access to source documents and managed write access to internal storage.
    Strictly enforces NO MODIFICATION of source files.
    """

    def __init__(self):
        self.categorizer = Categorizer()

    def list_documents(self, source: str = "documents") -> List[Dict]:
        """
        List files from the specified source directory (recursive).
        """
        root_path = SOURCE_DOCUMENTS if source == "documents" else SOURCE_EMAILS
        if source == "knowledge":
            root_path = SOURCE_KNOWLEDGE_DB

        results = []
        if not root_path.exists():
            return []

        for path in root_path.rglob("*"):
            if path.is_file() and not path.name.startswith("."):
                stats = path.stat()
                results.append({
                    "filename": path.name,
                    "path": str(path),
                    "relative_path": str(path.relative_to(root_path)),
                    "size": stats.st_size,
                    "modified": stats.st_mtime,
                    "is_source": True
                })
        return results

    def read_file(self, file_path: str) -> Optional[bytes]:
        """
        Safely read a file from theallowed paths.
        """
        path = Path(file_path)
        # Security check: Ensure path is within allowed roots
        allowed_roots = [SOURCE_DOCUMENTS, SOURCE_EMAILS, STORAGE_DIR, SOURCE_KNOWLEDGE_DB]
        if not any(str(path.resolve()).startswith(str(root.resolve())) for root in allowed_roots):
            raise PermissionError("Access denied: File outside allowed directories.")

        if not path.exists():
            return None

        try:
            return path.read_bytes()
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return None

    def save_upload(self, file_content: bytes, filename: str) -> Dict:
        """
        Save a NEW file uploaded by the user to the internal storage.
        Does NOT touch source directories.
        """
        target_path = STORAGE_DIR / filename
        
        # Avoid overwriting
        counter = 1
        while target_path.exists():
            stem = Path(filename).stem
            suffix = Path(filename).suffix
            target_path = STORAGE_DIR / f"{stem}_{counter}{suffix}"
            counter += 1

        target_path.write_bytes(file_content)
        
        # Auto-categorize
        meta = self.categorizer.categorize_file(filename)
        
        return {
            "status": "saved",
            "path": str(target_path),
            "metadata": meta
        }

    def search_files(self, query: str) -> List[Dict]:
        """
        Basic filename search across all sources.
        """
        all_files = self.list_documents("documents") + \
                   self.list_documents("emails") + \
                   self.list_documents("knowledge")
        
        query_lower = query.lower()
        return [f for f in all_files if query_lower in f['filename'].lower()]

import re
from pathlib import Path

class Categorizer:
    """
    Auto-categorizes documents and data based on filename, content, and metadata.
    """
    
    CATEGORIES = {
        "FINANCIAL": ["invoice", "budget", "quote", "receipt", "ledger", "tax", "banking", "statement"],
        "LEGAL": ["contract", "agreement", "nda", "terms", "regulation", "compliance", "law"],
        "HR": ["resume", "cv", "employment", "offer", "salary", "leave", "personnel"],
        "TECHNICAL": ["spec", "datasheet", "manual", "guide", "diagram", "blueprint", "schematic"],
        "OPERATIONS": ["report", "status", "inventory", "log", "schedule", "daily", "ops", "site"],
        "COMMUNICATION": ["email", "correspondence", "letter", "memo", "minutes"]
    }

    PROJECT_CODES = [r"site-\d+", "project-[a-z]+", "mining-ops"]

    @staticmethod
    def categorize_file(filename: str, content_preview: str = "") -> dict:
        """
        Analyze a file and return its category, tags, and priority.
        """
        filename_lower = filename.lower()
        content_lower = content_preview.lower()
        
        assigned_category = "UNCATEGORIZED"
        tags = []
        
        # 1. Determine Category
        for category, keywords in Categorizer.CATEGORIES.items():
            if any(k in filename_lower for k in keywords):
                assigned_category = category
                break
        
        # 2. Extract Project Tags
        for pattern in Categorizer.PROJECT_CODES:
            matches = re.findall(pattern, filename_lower)
            tags.extend(matches)

        # 3. Detect Sensitivity (Simple Heuristic)
        sensitivity = "INTERNAL"
        if "confidential" in content_lower or "private" in content_lower:
            sensitivity = "CONFIDENTIAL"
            tags.append("confidential")

        return {
            "category": assigned_category,
            "tags": list(set(tags)),
            "sensitivity": sensitivity
        }

    @staticmethod
    def suggest_folder_path(category: str) -> str:
        """
        Returns the suggested standardized folder path for a category.
        """
        return f"organized/{category.lower()}/"

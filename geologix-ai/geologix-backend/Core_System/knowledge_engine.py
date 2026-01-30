import json
import logging
from pathlib import Path
import sys

# Adjust path configuration
sys.path.append(str(Path(__file__).resolve().parent.parent))
from Configuration.config import DATA_DIR, SOURCE_DOCUMENTS

class KnowledgeEngine:
    """
    Handles retrieval of information from the indexed knowledge base.
    Supports: documents, emails, strategic knowledge, and company archives.
    """
    
    def __init__(self):
        self.company_index_path = DATA_DIR / "company_index.json"
        self.email_index_path = DATA_DIR / "email_index.json"
        self.archive_index_path = DATA_DIR / "archive_index.json"
        self.archive_stats_path = DATA_DIR / "archive_stats.json"
        
        self.company_docs = self._load_json(self.company_index_path)
        self.email_docs = self._load_json(self.email_index_path)
        self.archive_docs = self._load_json(self.archive_index_path)
        self.archive_stats = self._load_json(self.archive_stats_path)
        
    def _load_json(self, path: Path):
        try:
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            logging.error(f"Failed to load index {path}: {e}")
            return []

    def search(self, query: str, limit: int = 10, sources: list = ["docs", "emails", "knowledge", "archives"]):
        """
        Performs a keyword search across specified sources.
        Sources: docs, emails, knowledge, archives
        """
        results = []
        query_lower = query.lower()
        
        # Tokenize query
        query_terms = [term for term in query_lower.split() if len(term) > 2] # Ignore short words
        if not query_terms:
            query_terms = [query_lower]

        # Search Company Documents
        if "docs" in sources:
            for doc in self.company_docs:
                score = 0
                content_str = (doc.get('filename', '') + " " + str(doc.get('tags', []))).lower()
                
                # Check for term matches
                matches = 0
                for term in query_terms:
                    if term in content_str:
                        matches += 1
                
                if matches > 0:
                    score = matches * 10
                    # Bonus for exact phrase match
                    if query_lower in content_str:
                        score += 20
                
                if score > 0:
                    doc['type'] = 'document'
                    doc['score'] = score
                    results.append(doc)

        # Search Emails
        if "emails" in sources:
            for email in self.email_docs:
                score = 0
                subject_lower = email.get('subject', '').lower()
                sender_lower = email.get('sender', '').lower()
                preview_lower = email.get('preview', '').lower()
                
                matches = 0
                for term in query_terms:
                    term_score = 0
                    if term in subject_lower:
                        term_score += 8
                    if term in sender_lower:
                        term_score += 5
                    if term in preview_lower:
                        term_score += 2
                    
                    if term_score > 0:
                        score += term_score
                        matches += 1
                
                # Bonus for exact phrase match
                if query_lower in (subject_lower + " " + sender_lower):
                     score += 15

                if score > 0:
                    email['type'] = 'email'
                    email['score'] = score
                    results.append(email)

        # Search Knowledge DB
        if "knowledge" in sources:
            knowledge_path = DATA_DIR / "knowledge_index.json"
            knowledge_docs = self._load_json(knowledge_path)
            
            for doc in knowledge_docs:
                score = 0
                content_str = (doc.get('filename', '') + " " + doc.get('preview', '')).lower()
                
                matches = 0
                for term in query_terms:
                    if term in content_str:
                        matches += 1
                        score += 5
                
                if score > 0:
                    doc['type'] = 'knowledge'
                    doc['score'] = score
                    results.append(doc)

        # Search Archives (Historical Data)
        if "archives" in sources:
            for doc in self.archive_docs:
                score = 0
                filename_lower = doc.get('filename', '').lower()
                path_lower = doc.get('relative_path', '').lower()
                tags = [t.lower() for t in doc.get('tags', [])]
                full_str = f"{filename_lower} {path_lower} {' '.join(tags)}"
                
                matches = 0
                for term in query_terms:
                    if term in full_str:
                        matches += 1
                        score += 5
                
                if score > 0:
                    doc['type'] = 'archive'
                    doc['score'] = score
                    results.append(doc)

        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:limit]

    def get_context(self, query: str) -> str:
        """
        Retrieves formatted context string for the AI model.
        """
        hits = self.search(query, limit=5)
        if not hits:
            return "No relevant internal documents found."
            
        context_parts = ["INTERNAL KNOWLEDGE BASE RESULTS:"]
        for hit in hits:
            if hit['type'] == 'document':
                context_parts.append(f"[DOC] {hit['filename']} (Category: {hit.get('category')})")
            elif hit['type'] == 'email':
                preview = hit.get('preview', '')[:300]  # Include up to 300 chars of content
                context_parts.append(f"[EMAIL] From: {hit['sender']} | Subj: {hit['subject']} | Content: {preview}")
            elif hit['type'] == 'knowledge':
                context_parts.append(f"[STRATEGY] {hit['filename']} : {hit.get('preview', '')[:100]}...")
            elif hit['type'] == 'archive':
                tags = ', '.join(hit.get('tags', [])[:3])
                context_parts.append(f"[ARCHIVE] {hit['filename']} ({hit.get('category')}) Tags: {tags}")
                
        return "\n".join(context_parts)
    
    def get_archive_summary(self) -> str:
        """Get a summary of available archive data for AI context."""
        if not self.archive_stats:
            return "No archive data indexed yet."
        
        summary = ["COMPANY ARCHIVE SUMMARY:"]
        summary.append(f"Total Files: {self.archive_stats.get('total_files', 0)}")
        
        if self.archive_stats.get('by_category'):
            summary.append("Categories: " + ", ".join(
                f"{k}({v})" for k, v in sorted(
                    self.archive_stats['by_category'].items(), 
                    key=lambda x: -x[1]
                )[:5]
            ))
        
        if self.archive_stats.get('by_tag'):
            top_tags = sorted(self.archive_stats['by_tag'].items(), key=lambda x: -x[1])[:8]
            summary.append("Top Tags: " + ", ".join(f"{k}" for k, v in top_tags))
        
        if self.archive_stats.get('date_range'):
            dr = self.archive_stats['date_range']
            if dr.get('earliest') and dr.get('latest'):
                summary.append(f"Date Range: {dr['earliest'][:10]} to {dr['latest'][:10]}")
        
        return "\n".join(summary)
    
    def search_archives(self, query: str = "", tags: list = None, limit: int = 20) -> list:
        query_lower = (query or "").lower()
        tags_lower = [t.lower() for t in (tags or []) if t]

        results = []
        for doc in self.archive_docs:
            doc_tags = [t.lower() for t in doc.get('tags', [])]
            if tags_lower and not any(t in doc_tags for t in tags_lower):
                continue

            score = 0
            if query_lower:
                filename_lower = doc.get('filename', '').lower()
                path_lower = doc.get('relative_path', '').lower()

                if query_lower in filename_lower:
                    score += 10
                if query_lower in path_lower:
                    score += 5
                if any(query_lower in tag for tag in doc_tags):
                    score += 8
                if query_lower in doc.get('category', '').lower():
                    score += 3

                if score <= 0:
                    continue
            else:
                score = 1

            doc['type'] = 'archive'
            doc['score'] = score
            results.append(doc)

        results.sort(key=lambda x: x.get('score', 0), reverse=True)
        return results[:limit]
     
    def search_archives_by_tag(self, tag: str, limit: int = 20) -> list:
        """Search archives by specific tag (financial, operational, compliance, etc.)."""
        results = []
        tag_lower = tag.lower()
        
        for doc in self.archive_docs:
            if any(tag_lower in t.lower() for t in doc.get('tags', [])):
                doc['type'] = 'archive'
                results.append(doc)
                if len(results) >= limit:
                    break
        
        return results

"""
GeoLogix AI - Long-Term Memory System
Provides persistent memory across chat sessions for context continuity.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path


class AIMemory:
    """
    Long-term memory system for GeoLogix AI.
    Stores facts, preferences, entities, and context across sessions.
    """
    
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            data_dir = Path(__file__).resolve().parent.parent / "Data_Directories"
        self.data_dir = Path(data_dir)
        self.memory_file = self.data_dir / "ai_memory.json"
        self.memory = self._load_memory()
    
    def _load_memory(self) -> Dict:
        """Load memory from disk."""
        if self.memory_file.exists():
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return self._create_default_memory()
    
    def _create_default_memory(self) -> Dict:
        """Create default memory structure."""
        return {
            "facts": [],
            "entities": {},
            "preferences": {},
            "context": {},
            "summaries": {},
            "important_dates": [],
            "metrics": {},
            "created": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }
    
    def _save_memory(self):
        """Save memory to disk."""
        self.memory["last_updated"] = datetime.now().isoformat()
        try:
            self.data_dir.mkdir(parents=True, exist_ok=True)
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.memory, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving memory: {e}")
    
    def remember_fact(self, fact: str, category: str = "general", 
                      confidence: float = 0.8, source: str = None) -> Dict:
        """Store a learned fact."""
        fact_entry = {
            "id": f"fact_{len(self.memory['facts']) + 1}",
            "fact": fact,
            "category": category,
            "confidence": confidence,
            "source": source,
            "learned_at": datetime.now().isoformat(),
            "access_count": 0
        }
        self.memory["facts"].append(fact_entry)
        self._save_memory()
        return fact_entry
    
    def recall_facts(self, query: str = None, category: str = None, 
                     limit: int = 10) -> List[Dict]:
        """Recall relevant facts."""
        facts = self.memory["facts"]
        if category:
            facts = [f for f in facts if f.get("category") == category]
        if query:
            query_lower = query.lower()
            facts = [f for f in facts if query_lower in f.get("fact", "").lower()]
        facts = sorted(facts, key=lambda x: (x.get("confidence", 0), x.get("learned_at", "")), reverse=True)
        return facts[:limit]
    
    def remember_entity(self, name: str, entity_type: str, 
                        attributes: Dict = None) -> Dict:
        """Store information about an entity."""
        entity_key = f"{entity_type}:{name.lower()}"
        if entity_key in self.memory["entities"]:
            existing = self.memory["entities"][entity_key]
            if attributes:
                existing["attributes"].update(attributes)
            existing["last_mentioned"] = datetime.now().isoformat()
            existing["mention_count"] = existing.get("mention_count", 0) + 1
        else:
            self.memory["entities"][entity_key] = {
                "name": name,
                "type": entity_type,
                "attributes": attributes or {},
                "first_seen": datetime.now().isoformat(),
                "last_mentioned": datetime.now().isoformat(),
                "mention_count": 1,
                "related_entities": []
            }
        self._save_memory()
        return self.memory["entities"][entity_key]
    
    def get_entity(self, name: str, entity_type: str = None) -> Optional[Dict]:
        """Retrieve entity information."""
        name_lower = name.lower()
        if entity_type:
            return self.memory["entities"].get(f"{entity_type}:{name_lower}")
        for key, entity in self.memory["entities"].items():
            if entity.get("name", "").lower() == name_lower:
                return entity
        return None
    
    def list_entities(self, entity_type: str = None) -> List[Dict]:
        """List all known entities."""
        entities = list(self.memory["entities"].values())
        if entity_type:
            entities = [e for e in entities if e.get("type") == entity_type]
        return sorted(entities, key=lambda x: x.get("mention_count", 0), reverse=True)
    
    def set_context(self, topic: str, context: Any):
        """Store persistent context for a topic."""
        self.memory["context"][topic] = {
            "data": context,
            "updated": datetime.now().isoformat()
        }
        self._save_memory()
    
    def get_context(self, topic: str) -> Optional[Any]:
        """Retrieve context for a topic."""
        ctx = self.memory["context"].get(topic)
        return ctx.get("data") if ctx else None
    
    def store_summary(self, chat_id: str, summary: str, key_points: List[str] = None):
        """Store a conversation summary."""
        self.memory["summaries"][chat_id] = {
            "summary": summary,
            "key_points": key_points or [],
            "created": datetime.now().isoformat()
        }
        self._save_memory()
    
    def track_metric(self, name: str, value: float, unit: str = None):
        """Track a metric value over time."""
        if name not in self.memory["metrics"]:
            self.memory["metrics"][name] = {"unit": unit, "history": []}
        self.memory["metrics"][name]["history"].append({
            "value": value,
            "timestamp": datetime.now().isoformat()
        })
        if len(self.memory["metrics"][name]["history"]) > 100:
            self.memory["metrics"][name]["history"] = self.memory["metrics"][name]["history"][-100:]
        self._save_memory()
    
    def get_metric_history(self, name: str, limit: int = 20) -> Optional[Dict]:
        """Get metric history."""
        metric = self.memory["metrics"].get(name)
        if metric:
            return {
                "name": name,
                "unit": metric.get("unit"),
                "history": metric["history"][-limit:],
                "current": metric["history"][-1]["value"] if metric["history"] else None
            }
        return None
    
    def get_stats(self) -> Dict:
        """Get memory statistics."""
        return {
            "facts_count": len(self.memory["facts"]),
            "entities_count": len(self.memory["entities"]),
            "contexts_count": len(self.memory["context"]),
            "summaries_count": len(self.memory["summaries"]),
            "metrics_tracked": len(self.memory["metrics"]),
            "last_updated": self.memory.get("last_updated")
        }
    
    def get_memory_context(self, query: str = None, limit: int = 5) -> str:
        """Get relevant memory context as a string for the AI."""
        context_parts = []
        facts = self.recall_facts(query, limit=limit)
        if facts:
            context_parts.append("REMEMBERED FACTS:")
            for f in facts:
                context_parts.append(f"- {f['fact']}")
        if query:
            for key, entity in self.memory["entities"].items():
                if entity.get("name", "").lower() in query.lower():
                    context_parts.append(f"\nKNOWN ENTITY: {entity['name']} ({entity['type']})")
                    for k, v in entity.get("attributes", {}).items():
                        context_parts.append(f"  {k}: {v}")
        return "\n".join(context_parts) if context_parts else ""

import sys
from pathlib import Path

# Adjust path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from Core_System.knowledge_engine import KnowledgeEngine

def test_knowledge_search():
    engine = KnowledgeEngine()
    print("Testing Strategic Knowledge Search...")
    
    # Query for a term likely in the strategic docs
    results = engine.search("Owners Mindset", limit=5, sources=["knowledge"])
    
    print(f"\nFound {len(results)} matches.")
    for r in results:
        print(f"[{r['type'].upper()}] {r['filename']} (Score: {r['score']})")

if __name__ == "__main__":
    test_knowledge_search()

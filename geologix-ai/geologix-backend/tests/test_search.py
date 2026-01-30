import sys
from pathlib import Path
import json

# Adjust path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from Core_System.knowledge_engine import KnowledgeEngine

def test_search():
    print("Testing Knowledge Engine...")
    engine = KnowledgeEngine()
    
    # Test Query 1: "invoice" (Financial)
    results = engine.search("invoice", limit=3, sources=["docs"])
    print(f"\nQuery: 'invoice' | Found: {len(results)}")
    for r in results:
        print(f" - {r['filename']} (Score: {r['score']})")
        
    # Test Query 2: "email" (Communication)
    results = engine.search("Jacques", limit=3, sources=["emails"])
    print(f"\nQuery: 'Jacques' | Found: {len(results)}")
    for r in results:
        print(f" - Email from {r['sender']} (Subj: {r['subject']})")

if __name__ == "__main__":
    try:
        test_search()
        print("\nSUCCESS: Knowledge Engine is operational.")
    except Exception as e:
        print(f"\nFAILURE: {e}")

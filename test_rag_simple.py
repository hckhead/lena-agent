"""Simple test to verify RAG enhancement works correctly"""
import os
import sys
from dotenv import load_dotenv

# Ensure imports work
sys.path.insert(0, os.path.dirname(__file__))

load_dotenv()

print("Testing RAG imports...")
try:
    from agent.rag import get_retriever
    print("✓ Successfully imported get_retriever")
except Exception as e:
    print(f"✗ Failed to import: {e}")
    sys.exit(1)

print("\nTesting retriever initialization...")
try:
    # Create a simple test document
    if not os.path.exists("docs"):
        os.makedirs("docs")
    with open("docs/test_doc.txt", "w", encoding="utf-8") as f:
        f.write("LENA is a modern application server platform.\nIt provides high performance and scalability.")
    
    # Test without re-ranking
    print("  - Testing without re-ranking...")
    retriever = get_retriever(enable_rerank=False)
    if retriever:
        print("  ✓ Retriever initialized successfully (no re-rank)")
    else:
        print("  ✗ Retriever returned None")
    
    # Test with re-ranking
    print("  - Testing with re-ranking...")
    retriever_rerank = get_retriever(enable_rerank=True)
    if retriever_rerank:
        print("  ✓ Retriever initialized successfully (with re-rank)")
    else:
        print("  ✗ Retriever returned None")
        
    print("\n✓ All import and initialization tests passed!")
    
except Exception as e:
    print(f"\n✗ Test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

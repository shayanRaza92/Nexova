from typing import List
import os

class KnowledgeBase:
    def __init__(self, data_path: str):
        self.data_path = data_path
        self.documents = []
        self.load_data()

    def load_data(self):
        if os.path.exists(self.data_path):
            with open(self.data_path, 'r', encoding='utf-8') as f:
                # Split by double newlines to get rough paragraphs
                content = f.read()
                self.documents = [doc.strip() for doc in content.split('\n\n') if doc.strip()]
        else:
            print(f"Warning: Data file not found at {self.data_path}")

    def search(self, query: str, top_k: int = 3) -> str:
        # Simple keyword matching for this prototype
        # In a real app, use vector embeddings (e.g., OpenAI embeddings + FAISS/Chroma)
        
        query_words = query.lower().split()
        scores = []
        
        for doc in self.documents:
            score = 0
            doc_lower = doc.lower()
            for word in query_words:
                if word in doc_lower:
                    score += 1
            scores.append((score, doc))
        
        # Sort by score desc
        scores.sort(key=lambda x: x[0], reverse=True)
        
        # Return top k relevant docs joined
        top_docs = [doc for score, doc in scores[:top_k] if score > 0]
        
        if not top_docs:
            return ""
            
        return "\n---\n".join(top_docs)

# Robust path resolution
current_dir = os.path.dirname(os.path.abspath(__file__))
kb = KnowledgeBase(os.path.join(current_dir, "..", "data", "dummy_data.txt"))

import os
import json
import numpy as np
from sentence_transformers import SentenceTransformer

class MisconceptionEmbedder:
    def __init__(self, taxonomy_path: str):
        """
        Initializes the embedder by loading the SentenceTransformer model
        and pre-embedding all taxonomy entries.
        """
        # Load the model locally. Will download it on first run.
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.taxonomy_path = taxonomy_path
        self.taxonomy = []
        self.cached_embeddings = None
        self.load_and_embed_taxonomy()

    def load_and_embed_taxonomy(self):
        """Loads the taxonomy file and pre-computes embeddings."""
        if not os.path.exists(self.taxonomy_path):
            raise FileNotFoundError(f"Taxonomy file not found at {self.taxonomy_path}")
            
        with open(self.taxonomy_path, 'r', encoding='utf-8') as f:
            self.taxonomy = json.load(f)

        texts_to_embed = []
        for entry in self.taxonomy:
            # Construct a rich text representation incorporating name, description, keywords, and code structure
            text = (
                f"Misconception: {entry['name']}\n"
                f"Description: {entry['description']}\n"
                f"Keywords: {', '.join(entry['keywords'])}\n"
                f"Example bad code:\n{entry['example_bad_code']}"
            )
            texts_to_embed.append(text)

        # Pre-embed and cache as numpy array
        self.cached_embeddings = self.model.encode(texts_to_embed, convert_to_numpy=True)

    def find_top_matches(self, code: str, error_msg: str, error_type: str, ast_flags: list[str], top_k: int = 3) -> list:
        """
        Embeds the student's submission and calculates cosine similarity
        against cached taxonomy embeddings.
        
        Returns the top 3 matching misconceptions with confidence scores.
        """
        # Prepare the query string representing the student's program and performance
        ast_str = ", ".join(ast_flags) if ast_flags else "None"
        error_str = f"{error_type}: {error_msg}" if error_type else "No runtime error"
        
        query_text = (
            f"Student Code:\n{code}\n\n"
            f"Error: {error_str}\n\n"
            f"AST Flaws: {ast_str}"
        )

        query_embedding = self.model.encode([query_text], convert_to_numpy=True)[0]

        # Calculate cosine similarity manually: (A . B) / (||A|| * ||B||)
        # Normalize vectors for dot product
        norm_query = query_embedding / (np.linalg.norm(query_embedding) + 1e-9)
        norms_cached = np.linalg.norm(self.cached_embeddings, axis=1, keepdims=True) + 1e-9
        normalized_cached = self.cached_embeddings / norms_cached

        similarities = np.dot(normalized_cached, norm_query)

        # Retrieve the indices of the top matches
        top_indices = np.argsort(similarities)[::-1][:top_k]

        results = []
        for idx in top_indices:
            score = float(similarities[idx])
            # Ensure the score is in the [0.0, 1.0] range
            score = max(0.0, min(1.0, score))
            
            results.append({
                "id": self.taxonomy[idx]["id"],
                "name": self.taxonomy[idx]["name"],
                "description": self.taxonomy[idx]["description"],
                "example_bad_code": self.taxonomy[idx]["example_bad_code"],
                "example_fix": self.taxonomy[idx]["example_fix"],
                "confidence": score
            })
            
        return results

# Shared global instance to be initialized at startup
_embedder_instance = None

def get_embedder(taxonomy_path: str = None) -> MisconceptionEmbedder:
    global _embedder_instance
    if _embedder_instance is None:
        if taxonomy_path is None:
            # Fallback path finding
            taxonomy_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'misconception_taxonomy.json')
        _embedder_instance = MisconceptionEmbedder(taxonomy_path)
    return _embedder_instance

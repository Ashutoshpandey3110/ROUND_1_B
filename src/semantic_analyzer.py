"""
Semantic Analyzer

This module contains the core machine learning logic for the application.
It handles loading the sentence-transformer model, encoding text into vectors,
and calculating relevance scores using cosine similarity.
"""

from sentence_transformers import SentenceTransformer, util
import torch
from typing import List, Dict, Any

from . import config
from .data_models import PersonaInput

class SemanticAnalyzer:
    """
    A class to encapsulate the sentence-transformer model and related logic.
    """
    def __init__(self, model_path: str):
        """
        Initializes the analyzer and loads the model into memory.
        This is a potentially slow operation and should only be done once.
        """
        print(f"Loading model from {model_path}...")
        # Ensure the model runs on CPU
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"Using device: {self.device}")
        self.model = SentenceTransformer(model_path, device=self.device)
        print("Model loaded successfully.")

    def create_query_vector(self, persona_data: PersonaInput) -> torch.Tensor:
        """
        Creates a single semantic vector representing the user's query.

        Args:
            persona_data (PersonaInput): The user's persona and job-to-be-done.

        Returns:
            torch.Tensor: A 1D tensor representing the query.
        """
        query_text = f"As a {persona_data.persona}, I need to {persona_data.job_to_be_done}"
        return self.model.encode(query_text, convert_to_tensor=True, device=self.device)

    def encode_corpus(self, chunks: List[Dict[str, Any]]) -> torch.Tensor:
        """
        Encodes a large list of text chunks into a 2D tensor.

        Args:
            chunks (List[Dict[str, Any]]): A list of document chunks.

        Returns:
            torch.Tensor: A 2D tensor where each row is a chunk's vector.
        """
        if not chunks:
            return torch.tensor([])
            
        chunk_texts = [chunk['text'] for chunk in chunks]
        return self.model.encode(
            chunk_texts,
            convert_to_tensor=True,
            show_progress_bar=True, # Useful for seeing progress on large corpora
            device=self.device,
            batch_size=32 # Tune this for optimal performance
        )

    def rank_chunks(self, query_vector: torch.Tensor, corpus_embeddings: torch.Tensor) -> torch.Tensor:
        """
        Calculates the cosine similarity between the query vector and all corpus vectors.

        Args:
            query_vector (torch.Tensor): The user's query vector.
            corpus_embeddings (torch.Tensor): The 2D tensor of document chunk vectors.

        Returns:
            torch.Tensor: A 1D tensor of similarity scores.
        """
        if corpus_embeddings.nelement() == 0:
            return torch.tensor([])
            
        # util.cos_sim is highly optimized for this calculation
        cosine_scores = util.cos_sim(query_vector, corpus_embeddings)
        return cosine_scores[0] # The result is a 2D tensor [[scores]], so we take the first row

    def refine_sub_section(self, text: str, query_vector: torch.Tensor) -> str:
        """
        Finds the single most relevant sentence within a block of text.

        Args:
            text (str): The text of a highly-ranked chunk.
            query_vector (torch.Tensor): The original user query vector.

        Returns:
            str: The most relevant sentence.
        """
        # A simple sentence splitter. For more complex cases, NLTK would be better.
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        if not sentences:
            return text # Fallback to returning the original text if no sentences found

        sentence_embeddings = self.model.encode(sentences, convert_to_tensor=True, device=self.device)
        scores = util.cos_sim(query_vector, sentence_embeddings)[0]
        
        # Find the sentence with the highest score
        best_sentence_idx = torch.argmax(scores).item()
        return sentences[best_sentence_idx]


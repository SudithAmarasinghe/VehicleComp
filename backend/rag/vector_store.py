"""
Vector store management using ChromaDB for RAG pipeline.
"""
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional
from config import config
import os


class VectorStore:
    """Manages vector database for vehicle information storage and retrieval."""
    
    def __init__(self):
        # Ensure data directory exists
        os.makedirs(config.VECTOR_STORE_PATH, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=config.VECTOR_STORE_PATH,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer(config.EMBEDDING_MODEL)
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="vehicle_knowledge",
            metadata={"description": "Vehicle market information and historical data"}
        )
    
    def add_documents(self, documents: List[str], metadatas: List[Dict], ids: List[str]):
        """
        Add documents to the vector store.
        
        Args:
            documents: List of text documents
            metadatas: List of metadata dictionaries
            ids: List of unique document IDs
        """
        try:
            # Generate embeddings
            embeddings = self.embedding_model.encode(documents).tolist()
            
            # Add to collection
            self.collection.add(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            
            print(f"Added {len(documents)} documents to vector store")
        
        except Exception as e:
            print(f"Error adding documents: {str(e)}")
    
    def query(self, query_text: str, n_results: int = None) -> Dict:
        """
        Query the vector store for similar documents.
        
        Args:
            query_text: Query string
            n_results: Number of results to return (default: config.RAG_TOP_K)
            
        Returns:
            Dictionary with documents, metadatas, and distances
        """
        if n_results is None:
            n_results = config.RAG_TOP_K
        
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query_text]).tolist()
            
            # Query collection
            results = self.collection.query(
                query_embeddings=query_embedding,
                n_results=n_results
            )
            
            return results
        
        except Exception as e:
            print(f"Error querying vector store: {str(e)}")
            return {'documents': [], 'metadatas': [], 'distances': []}
    
    def delete_collection(self):
        """Delete the collection (for testing/reset purposes)."""
        try:
            self.client.delete_collection("vehicle_knowledge")
            print("Collection deleted")
        except Exception as e:
            print(f"Error deleting collection: {str(e)}")
    
    def get_collection_count(self) -> int:
        """Get the number of documents in the collection."""
        try:
            return self.collection.count()
        except:
            return 0


# Singleton instance
_vector_store_instance = None

def get_vector_store() -> VectorStore:
    """Get or create vector store singleton instance."""
    global _vector_store_instance
    if _vector_store_instance is None:
        _vector_store_instance = VectorStore()
    return _vector_store_instance

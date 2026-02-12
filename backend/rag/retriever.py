"""
RAG retriever for querying vehicle knowledge base.
"""
from typing import List, Dict
from .vector_store import get_vector_store
from langchain.tools import tool


class VehicleRetriever:
    """Retrieves relevant vehicle information from knowledge base."""
    
    def __init__(self):
        self.vector_store = get_vector_store()
    
    def retrieve(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Retrieve relevant documents for a query.
        
        Args:
            query: Search query
            top_k: Number of results to return
            
        Returns:
            List of relevant documents with metadata
        """
        results = self.vector_store.query(query, n_results=top_k)
        
        # Format results
        formatted_results = []
        
        if results['documents'] and len(results['documents']) > 0:
            documents = results['documents'][0]
            metadatas = results['metadatas'][0] if results['metadatas'] else []
            distances = results['distances'][0] if results['distances'] else []
            
            for i, doc in enumerate(documents):
                formatted_results.append({
                    'content': doc,
                    'metadata': metadatas[i] if i < len(metadatas) else {},
                    'relevance_score': 1 - distances[i] if i < len(distances) else 0
                })
        
        return formatted_results
    
    def format_context(self, retrieved_docs: List[Dict]) -> str:
        """
        Format retrieved documents into context string for LLM.
        
        Args:
            retrieved_docs: List of retrieved documents
            
        Returns:
            Formatted context string
        """
        if not retrieved_docs:
            return "No relevant historical data found."
        
        context = "Relevant vehicle market information:\n\n"
        
        for i, doc in enumerate(retrieved_docs, 1):
            context += f"{i}. {doc['content']}\n"
            
            # Add metadata if available
            metadata = doc.get('metadata', {})
            if metadata:
                if 'source' in metadata:
                    context += f"   Source: {metadata['source']}\n"
                if 'date' in metadata:
                    context += f"   Date: {metadata['date']}\n"
            
            context += f"   Relevance: {doc.get('relevance_score', 0):.2f}\n\n"
        
        return context


# LangChain tool wrapper
@tool
def retrieve_vehicle_knowledge(query: str) -> str:
    """
    Retrieve relevant vehicle market knowledge from the knowledge base.
    Use this to get historical price trends, market insights, and vehicle information.
    
    Args:
        query: Query about vehicle market (e.g., "Toyota Aqua price trends", "Honda Fit reliability")
        
    Returns:
        Relevant information from knowledge base
    """
    retriever = VehicleRetriever()
    docs = retriever.retrieve(query)
    return retriever.format_context(docs)


# Export retriever instance
vehicle_retriever = VehicleRetriever()

"""
Agent state definition for LangGraph workflow.
"""
from typing import TypedDict, List, Dict, Annotated
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """State for the vehicle market agent."""
    
    # Conversation messages
    messages: Annotated[List[Dict], add_messages]
    
    # Current user query
    user_query: str
    
    # Classified intent
    intent: str  # 'price_check', 'comparison', 'general_info', 'unknown'
    
    # Scraped vehicle data
    scraped_data: List[Dict]
    
    # Retrieved context from RAG
    retrieved_context: str
    
    # Final response
    final_response: str
    
    # Comparison data (for multi-vehicle comparisons)
    comparison_data: Dict

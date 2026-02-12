"""
LangGraph workflow for vehicle market price agent.
"""
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from typing import Dict, List
import re

from .state import AgentState
from tools import search_vehicle_listings, compare_vehicle_prices, vehicle_scraper
from rag import retrieve_vehicle_knowledge, vehicle_retriever
from config import config


# Initialize LLM
llm = ChatOpenAI(
    model=config.LLM_MODEL,
    temperature=config.LLM_TEMPERATURE,
    api_key=config.OPENAI_API_KEY
)


def classify_intent(state: AgentState) -> AgentState:
    """Classify user's intent from their query."""
    query = state['user_query'].lower()
    
    # Check for comparison keywords
    comparison_keywords = ['compare', 'vs', 'versus', 'difference between', 'which is better']
    if any(keyword in query for keyword in comparison_keywords):
        state['intent'] = 'comparison'
    
    # Check for price check keywords
    elif any(word in query for word in ['price', 'cost', 'how much']):
        state['intent'] = 'price_check'
    
    # General information
    else:
        state['intent'] = 'general_info'
    
    return state


def extract_vehicle_query(user_query: str, intent: str) -> str:
    """Extract clean vehicle query from conversational input using LLM."""
    
    extraction_prompt = f"""Extract ONLY the vehicle information from this query in a clean format.

User query: "{user_query}"

Rules:
1. Extract brand, model, and year/year range ONLY
2. Format: "Brand Model YYYY" or "Brand Model YYYY-YYYY" (ALWAYS use full 4-digit years)
3. Remove all conversational words like "compare", "price", "buy", "need", "in sri lanka", etc.
4. Keep model variants (e.g., "Corolla 110", "Alto K10")
5. If comparing multiple vehicles, separate with " | " (pipe)
6. CRITICAL: Always use full 4-digit years (e.g., "1995-2003", NOT "19-20" or "95-03")

Examples:
- "Compare toyota corolla 110 with alto k10" → "Toyota Corolla 110 | Suzuki Alto K10"
- "I need to buy a corolla 2015-2023" → "Toyota Corolla 2015-2023"
- "What is the price of Honda Fit 2018?" → "Honda Fit 2018"
- "Toyota Corolla 1995-2003" → "Toyota Corolla 1995-2003"
- "Nissan Leaf from 2020 to 2022" → "Nissan Leaf 2020-2022"

Extracted vehicle query:"""
    
    try:
        messages = [HumanMessage(content=extraction_prompt)]
        response = llm.invoke(messages)
        extracted = response.content.strip()
        # Remove quotes if present
        extracted = extracted.strip('"\'')
        return extracted if extracted else user_query
    except Exception as e:
        print(f"Error extracting vehicle query: {e}")
        return user_query



def scrape_vehicles(state: AgentState) -> AgentState:
    """Scrape vehicle data from websites."""
    user_query = state['user_query']
    intent = state['intent']
    
    # Extract clean vehicle query from conversational input
    clean_query = extract_vehicle_query(user_query, intent)
    print(f"Original query: {user_query}")
    print(f"Extracted query: {clean_query}")
    
    if intent == 'comparison':
        # Extract vehicle models for comparison
        if ' | ' in clean_query:
            # Already separated by extraction
            models = [m.strip() for m in clean_query.split('|')]
        else:
            models = extract_vehicle_models(clean_query)
        
        if len(models) >= 2:
            comparison = vehicle_scraper.compare_vehicles(models)
            state['comparison_data'] = comparison
            state['scraped_data'] = []
            for model_vehicles in comparison['vehicles'].values():
                state['scraped_data'].extend(model_vehicles[:3])  # Top 3 from each
        else:
            # Fallback to single search
            vehicles = vehicle_scraper.search_all(clean_query)
            state['scraped_data'] = vehicles[:10]
    
    else:
        # Single vehicle search
        vehicles = vehicle_scraper.search_all(clean_query)
        state['scraped_data'] = vehicles[:10]
    
    return state


def retrieve_knowledge(state: AgentState) -> AgentState:
    """Retrieve relevant knowledge from RAG pipeline."""
    query = state['user_query']
    
    # Retrieve relevant documents
    docs = vehicle_retriever.retrieve(query, top_k=3)
    context = vehicle_retriever.format_context(docs)
    
    state['retrieved_context'] = context
    
    return state


def generate_response(state: AgentState) -> AgentState:
    """Generate conversational response using LLM."""
    
    # Build context for LLM
    system_prompt = """You are a helpful vehicle market assistant for Sri Lanka. 
You help users find vehicle prices, compare vehicles, and provide market insights.
Be conversational, friendly, and informative. Use the provided data to give accurate information.
When showing prices, format them nicely with commas (e.g., Rs 4,500,000).
If comparing vehicles, highlight key differences and provide recommendations."""
    
    # Prepare scraped data summary
    scraped_summary = ""
    if state.get('scraped_data'):
        scraped_summary = "\n\nCurrent Market Listings:\n"
        for i, vehicle in enumerate(state['scraped_data'][:5], 1):
            scraped_summary += f"{i}. {vehicle['title']} - Rs {vehicle['price']:,.0f} ({vehicle['source']})\n"
    
    # Prepare comparison summary
    comparison_summary = ""
    if state.get('comparison_data') and state['comparison_data'].get('summary'):
        comparison_summary = "\n\nPrice Comparison Summary:\n"
        for model, summary in state['comparison_data']['summary'].items():
            comparison_summary += f"\n{model}:\n"
            comparison_summary += f"  - Average: Rs {summary['avg_price']:,.0f}\n"
            comparison_summary += f"  - Range: Rs {summary['min_price']:,.0f} - Rs {summary['max_price']:,.0f}\n"
            comparison_summary += f"  - Listings: {summary['count']}\n"
    
    # Retrieved context
    context = state.get('retrieved_context', '')
    
    # Build messages
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"""User Query: {state['user_query']}

{context}
{scraped_summary}
{comparison_summary}

Please provide a helpful response to the user's query based on the above information.""")
    ]
    
    # Generate response
    response = llm.invoke(messages)
    state['final_response'] = response.content
    
    # Add to conversation messages
    state['messages'].append({
        'role': 'user',
        'content': state['user_query']
    })
    state['messages'].append({
        'role': 'assistant',
        'content': state['final_response'],
        'data': {
            'vehicles': state.get('scraped_data', [])[:5],
            'comparison': state.get('comparison_data', {})
        }
    })
    
    return state


def extract_vehicle_models(query: str) -> List[str]:
    """Extract vehicle models from comparison query."""
    # Simple extraction - split by common separators
    separators = [' vs ', ' versus ', ' and ', ' with ', ',']
    
    models = [query]
    for sep in separators:
        if sep in query.lower():
            models = query.lower().split(sep)
            break
    
    # Clean up models
    models = [m.strip() for m in models]
    
    # Remove common words
    remove_words = ['compare', 'price', 'of', 'the', 'between', 'in', 'sri', 'lanka', 'buy', 'need', 'want']
    cleaned_models = []
    for model in models:
        for word in remove_words:
            model = model.replace(word, '')
        model = model.strip()
        if model:
            cleaned_models.append(model)
    
    return cleaned_models[:5]  # Max 5 models


def should_scrape(state: AgentState) -> str:
    """Decide if we should scrape based on intent."""
    intent = state['intent']
    if intent in ['price_check', 'comparison']:
        return 'scrape'
    return 'skip_scrape'


# Build the graph
def create_agent_graph():
    """Create the LangGraph workflow."""
    
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("classify_intent", classify_intent)
    workflow.add_node("scrape_vehicles", scrape_vehicles)
    workflow.add_node("retrieve_knowledge", retrieve_knowledge)
    workflow.add_node("generate_response", generate_response)
    
    # Set entry point
    workflow.set_entry_point("classify_intent")
    
    # Add edges
    workflow.add_conditional_edges(
        "classify_intent",
        should_scrape,
        {
            "scrape": "scrape_vehicles",
            "skip_scrape": "retrieve_knowledge"
        }
    )
    
    workflow.add_edge("scrape_vehicles", "retrieve_knowledge")
    workflow.add_edge("retrieve_knowledge", "generate_response")
    workflow.add_edge("generate_response", END)
    
    # Compile
    app = workflow.compile()
    
    return app


# Create the agent
agent_graph = create_agent_graph()


def run_agent(user_query: str, conversation_history: List[Dict] = None) -> Dict:
    """
    Run the agent with a user query.
    
    Args:
        user_query: User's question
        conversation_history: Previous messages
        
    Returns:
        Agent response with data
    """
    initial_state = {
        'messages': conversation_history or [],
        'user_query': user_query,
        'intent': '',
        'scraped_data': [],
        'retrieved_context': '',
        'final_response': '',
        'comparison_data': {}
    }
    
    # Run the graph
    result = agent_graph.invoke(initial_state)
    
    return {
        'response': result['final_response'],
        'vehicles': result.get('scraped_data', [])[:5],
        'comparison': result.get('comparison_data', {}),
        'intent': result['intent']
    }

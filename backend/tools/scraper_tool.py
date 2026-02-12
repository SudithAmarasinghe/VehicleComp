"""
Unified scraper tool that aggregates results from all vehicle websites.
This tool is used by the LangGraph agent.
"""
from typing import List, Dict, Optional
from langchain.tools import tool
from .scrapers import RiyasewanaScraper, IkmanScraper, PatpatScraper
import asyncio
from concurrent.futures import ThreadPoolExecutor


class VehicleScraperTool:
    """Unified vehicle scraper tool for LangChain/LangGraph."""
    
    def __init__(self):
        self.scrapers = {
            'riyasewana': RiyasewanaScraper(),
            'ikman': IkmanScraper(),
            'patpat': PatpatScraper()
        }
    
    def search_all(self, query: str, sources: Optional[List[str]] = None) -> List[Dict]:
        """
        Search for vehicles across all or specified sources.
        
        Args:
            query: Search query (e.g., "Toyota Aqua 2018")
            sources: List of sources to search (default: all)
            
        Returns:
            Aggregated and deduplicated list of vehicles
        """
        if sources is None:
            sources = list(self.scrapers.keys())
        
        all_vehicles = []
        
        # Use ThreadPoolExecutor for parallel scraping
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {}
            
            for source in sources:
                if source in self.scrapers:
                    future = executor.submit(self.scrapers[source].search, query)
                    futures[future] = source
            
            for future in futures:
                try:
                    vehicles = future.result(timeout=60)
                    all_vehicles.extend(vehicles)
                except Exception as e:
                    print(f"Error scraping {futures[future]}: {str(e)}")
        
        # Deduplicate and sort
        deduplicated = self._deduplicate_vehicles(all_vehicles)
        sorted_vehicles = self._sort_vehicles(deduplicated)
        
        return sorted_vehicles
    
    def _deduplicate_vehicles(self, vehicles: List[Dict]) -> List[Dict]:
        """Remove duplicate listings based on title and price similarity."""
        seen = set()
        unique_vehicles = []
        
        for vehicle in vehicles:
            # Create a simple hash based on title and price
            key = (
                vehicle.get('title', '').lower().strip(),
                int(vehicle.get('price', 0))
            )
            
            if key not in seen and key[1] > 0:
                seen.add(key)
                unique_vehicles.append(vehicle)
        
        return unique_vehicles
    
    def _sort_vehicles(self, vehicles: List[Dict]) -> List[Dict]:
        """Sort vehicles by relevance and price."""
        # Sort by price (ascending) and then by year (descending)
        return sorted(
            vehicles,
            key=lambda x: (x.get('price', 0), -x.get('year', 0))
        )
    
    def compare_vehicles(self, queries: List[str]) -> Dict:
        """
        Compare multiple vehicle models.
        
        Args:
            queries: List of vehicle queries to compare
            
        Returns:
            Dictionary with comparison data
        """
        comparison = {
            'vehicles': {},
            'summary': {}
        }
        
        for query in queries:
            vehicles = self.search_all(query)
            comparison['vehicles'][query] = vehicles
            
            if vehicles:
                prices = [v['price'] for v in vehicles if v['price'] > 0]
                comparison['summary'][query] = {
                    'count': len(vehicles),
                    'avg_price': sum(prices) / len(prices) if prices else 0,
                    'min_price': min(prices) if prices else 0,
                    'max_price': max(prices) if prices else 0,
                    'sources': list(set(v['source'] for v in vehicles))
                }
        
        return comparison


# LangChain tool wrapper
@tool
def search_vehicle_listings(query: str) -> str:
    """
    Search for vehicle listings across Sri Lankan websites (Riyasewana, Ikman, Patpat).
    
    Args:
        query: Vehicle search query (e.g., "Toyota Aqua 2018", "Honda Fit 2015")
        
    Returns:
        Formatted string with vehicle listings and prices
    """
    scraper_tool = VehicleScraperTool()
    vehicles = scraper_tool.search_all(query)
    
    if not vehicles:
        return f"No vehicles found for query: {query}"
    
    # Format results
    result = f"Found {len(vehicles)} vehicles for '{query}':\n\n"
    
    for i, vehicle in enumerate(vehicles[:10], 1):
        result += f"{i}. {vehicle['title']}\n"
        result += f"   Price: Rs {vehicle['price']:,.0f}\n"
        result += f"   Year: {vehicle['year']}\n"
        result += f"   Location: {vehicle['location']}\n"
        result += f"   Source: {vehicle['source']}\n"
        result += f"   URL: {vehicle['url']}\n\n"
    
    return result


@tool
def compare_vehicle_prices(vehicle_models: str) -> str:
    """
    Compare prices of multiple vehicle models.
    
    Args:
        vehicle_models: Comma-separated list of vehicle models (e.g., "Toyota Aqua 2018, Honda Fit 2015")
        
    Returns:
        Formatted comparison with price statistics
    """
    scraper_tool = VehicleScraperTool()
    queries = [q.strip() for q in vehicle_models.split(',')]
    
    comparison = scraper_tool.compare_vehicles(queries)
    
    result = "Vehicle Price Comparison:\n\n"
    
    for query, summary in comparison['summary'].items():
        result += f"📊 {query}:\n"
        result += f"   Listings found: {summary['count']}\n"
        result += f"   Average price: Rs {summary['avg_price']:,.0f}\n"
        result += f"   Price range: Rs {summary['min_price']:,.0f} - Rs {summary['max_price']:,.0f}\n"
        result += f"   Sources: {', '.join(summary['sources'])}\n\n"
    
    return result


# Export the tool instance
vehicle_scraper = VehicleScraperTool()

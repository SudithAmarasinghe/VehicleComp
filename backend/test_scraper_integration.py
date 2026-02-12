
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tools.scraper_tool import VehicleScraperTool

def test_scraper():
    print("Testing VehicleScraperTool with curl_cffi...")
    scraper = VehicleScraperTool()
    
    # Test Riyasewana search
    query = "Toyota Corolla 1995-2003"
    print(f"\nSearching for: {query}")
    
    try:
        results = scraper.search_all(query, sources=['riyasewana'])
        print(f"Found {len(results)} vehicles.")
        
        if results:
            print("\nTop 3 results:")
            for i, vehicle in enumerate(results[:3], 1):
                print(f"{i}. {vehicle['title']}")
                print(f"   Price: Rs {vehicle['price']:,.0f}")
                print(f"   URL: {vehicle['url']}")
        else:
            print("No results found.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_scraper()

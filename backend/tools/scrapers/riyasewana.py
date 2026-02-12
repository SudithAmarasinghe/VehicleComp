"""
Riyasewana.com vehicle scraper.
"""
from typing import List, Dict
from .base_scraper import BaseScraper
import re


class RiyasewanaScraper(BaseScraper):
    """Scraper for Riyasewana.com vehicle listings."""
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://riyasewana.com"
        self.search_url = f"{self.base_url}/search"
    
    def search(self, query: str, **kwargs) -> List[Dict]:
        """
        Search for vehicles on Riyasewana.
        
        Args:
            query: Search query (e.g., "Toyota Aqua 2018")
            **kwargs: Additional parameters like min_price, max_price, year
            
        Returns:
            List of standardized vehicle dictionaries
        """
        vehicles = []
        
        try:
            # Parse query to extract make, model, year
            query_parts = self._parse_query(query)
            
            # Build search URL
            search_params = self._build_search_params(query_parts, **kwargs)
            search_url = f"{self.search_url}/{search_params}"
            
            # Fetch search results page
            soup = self._fetch_page(search_url)
            if not soup:
                return vehicles
            
            # Extract vehicle listings
            listings = soup.find_all('div', class_='item')
            
            for listing in listings[:self.max_results]:
                vehicle_data = self._extract_vehicle_data(listing)
                if vehicle_data:
                    standardized = self._standardize_vehicle(vehicle_data)
                    vehicles.append(standardized)
        
        except Exception as e:
            print(f"Error searching Riyasewana: {str(e)}")
        
        return vehicles
    
    def _parse_query(self, query: str) -> Dict:
        """Parse search query into components."""
        query_lower = query.lower()
        parts = {
            'make': '',
            'model': '',
            'year': ''
        }
        
        # Common Sri Lankan vehicle makes
        makes = ['toyota', 'honda', 'nissan', 'suzuki', 'mitsubishi', 'mazda', 
                 'bmw', 'benz', 'mercedes', 'audi', 'hyundai', 'kia']
        
        for make in makes:
            if make in query_lower:
                parts['make'] = make.capitalize()
                break
        
        # Extract year (4 digits)
        year_match = re.search(r'\b(19|20)\d{2}\b', query)
        if year_match:
            parts['year'] = year_match.group()
        
        # Model is remaining text
        query_clean = query.lower()
        for make in makes:
            query_clean = query_clean.replace(make, '')
        query_clean = re.sub(r'\b(19|20)\d{2}\b', '', query_clean)
        parts['model'] = query_clean.strip()
        
        return parts
    
    def _build_search_params(self, query_parts: Dict, **kwargs) -> str:
        """Build URL search parameters."""
        # Simplified search path - adjust based on actual Riyasewana URL structure
        params = []
        
        if query_parts.get('make'):
            params.append(query_parts['make'].lower())
        
        if query_parts.get('model'):
            params.append(query_parts['model'].replace(' ', '-').lower())
        
        # In real implementation, this would match Riyasewana's actual URL structure
        return '/'.join(params) if params else 'vehicles'
    
    def _extract_vehicle_data(self, listing) -> Dict:
        """Extract vehicle data from a listing element."""
        try:
            # Note: These selectors are placeholders and need to be adjusted
            # based on actual Riyasewana.com HTML structure
            
            title_elem = listing.find('h2', class_='title') or listing.find('a', class_='title')
            title = title_elem.text.strip() if title_elem else ''
            
            price_elem = listing.find('div', class_='price') or listing.find('span', class_='price')
            price = price_elem.text.strip() if price_elem else '0'
            
            url_elem = listing.find('a', href=True)
            url = self.base_url + url_elem['href'] if url_elem else ''
            
            image_elem = listing.find('img')
            image_url = image_elem.get('src', '') if image_elem else ''
            
            # Extract additional details
            details = listing.find('div', class_='details')
            location = ''
            year = ''
            mileage = ''
            
            if details:
                detail_items = details.find_all('span')
                for item in detail_items:
                    text = item.text.strip()
                    if 'km' in text.lower():
                        mileage = text
                    elif any(char.isdigit() for char in text) and len(text) == 4:
                        year = text
                    else:
                        location = text
            
            return {
                'title': title,
                'price': price,
                'year': year,
                'make': self._extract_make_from_title(title),
                'model': self._extract_model_from_title(title),
                'mileage': mileage,
                'condition': 'Used',  # Default
                'location': location,
                'url': url,
                'source': 'Riyasewana',
                'image_url': image_url
            }
        
        except Exception as e:
            print(f"Error extracting vehicle data: {str(e)}")
            return {}
    
    def _extract_make_from_title(self, title: str) -> str:
        """Extract vehicle make from title."""
        makes = ['Toyota', 'Honda', 'Nissan', 'Suzuki', 'Mitsubishi', 'Mazda', 
                 'BMW', 'Mercedes', 'Benz', 'Audi', 'Hyundai', 'KIA']
        
        for make in makes:
            if make.lower() in title.lower():
                return make
        return ''
    
    def _extract_model_from_title(self, title: str) -> str:
        """Extract vehicle model from title."""
        # Remove make and year, return remaining
        title_clean = title
        for make in ['Toyota', 'Honda', 'Nissan', 'Suzuki', 'Mitsubishi']:
            title_clean = title_clean.replace(make, '')
        title_clean = re.sub(r'\b(19|20)\d{2}\b', '', title_clean)
        return title_clean.strip()


# Test function
if __name__ == "__main__":
    scraper = RiyasewanaScraper()
    results = scraper.search("Toyota Aqua 2018")
    for vehicle in results:
        print(f"{vehicle['title']} - Rs {vehicle['price']:,.0f}")

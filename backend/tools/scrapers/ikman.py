"""
Ikman.lk vehicle scraper.
"""
from typing import List, Dict
from .base_scraper import BaseScraper
import re


class IkmanScraper(BaseScraper):
    """Scraper for Ikman.lk vehicle listings."""
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://ikman.lk"
        self.search_url = f"{self.base_url}/en/ads/sri-lanka/vehicles"
    
    def search(self, query: str, **kwargs) -> List[Dict]:
        """
        Search for vehicles on Ikman.lk.
        
        Args:
            query: Search query (e.g., "Toyota Aqua 2018")
            **kwargs: Additional parameters
            
        Returns:
            List of standardized vehicle dictionaries
        """
        vehicles = []
        
        try:
            # Build search URL with query parameter
            search_url = f"{self.search_url}?query={query.replace(' ', '+')}"
            
            # Fetch search results
            soup = self._fetch_page(search_url)
            if not soup:
                return vehicles
            
            # Extract listings - adjust selectors based on actual Ikman structure
            listings = soup.find_all('li', class_='normal--2QYVk')
            
            if not listings:
                # Try alternative selector
                listings = soup.find_all('div', class_='card')
            
            for listing in listings[:self.max_results]:
                vehicle_data = self._extract_vehicle_data(listing)
                if vehicle_data:
                    standardized = self._standardize_vehicle(vehicle_data)
                    vehicles.append(standardized)
        
        except Exception as e:
            print(f"Error searching Ikman: {str(e)}")
        
        return vehicles
    
    def _extract_vehicle_data(self, listing) -> Dict:
        """Extract vehicle data from listing element."""
        try:
            # Title
            title_elem = listing.find('h2') or listing.find('a', class_='card-title')
            title = title_elem.text.strip() if title_elem else ''
            
            # Price
            price_elem = listing.find('div', class_='price--3SnqI') or listing.find('span', class_='price')
            price = price_elem.text.strip() if price_elem else '0'
            
            # URL
            url_elem = listing.find('a', href=True)
            url = url_elem['href'] if url_elem else ''
            if url and not url.startswith('http'):
                url = self.base_url + url
            
            # Image
            image_elem = listing.find('img')
            image_url = image_elem.get('src', '') or image_elem.get('data-src', '') if image_elem else ''
            
            # Location and details
            location_elem = listing.find('div', class_='description--2-ez3')
            location = location_elem.text.strip() if location_elem else ''
            
            # Extract year from title
            year_match = re.search(r'\b(19|20)\d{2}\b', title)
            year = year_match.group() if year_match else ''
            
            # Extract mileage if present in description
            mileage = ''
            desc_elem = listing.find('div', class_='description')
            if desc_elem:
                desc_text = desc_elem.text
                mileage_match = re.search(r'(\d+[\d,]*)\s*km', desc_text, re.IGNORECASE)
                if mileage_match:
                    mileage = mileage_match.group(1) + ' km'
            
            return {
                'title': title,
                'price': price,
                'year': year,
                'make': self._extract_make_from_title(title),
                'model': self._extract_model_from_title(title),
                'mileage': mileage or 'N/A',
                'condition': 'Used',
                'location': location,
                'url': url,
                'source': 'Ikman',
                'image_url': image_url
            }
        
        except Exception as e:
            print(f"Error extracting Ikman vehicle data: {str(e)}")
            return {}
    
    def _extract_make_from_title(self, title: str) -> str:
        """Extract vehicle make from title."""
        makes = ['Toyota', 'Honda', 'Nissan', 'Suzuki', 'Mitsubishi', 'Mazda', 
                 'BMW', 'Mercedes', 'Benz', 'Audi', 'Hyundai', 'KIA', 'Volkswagen']
        
        for make in makes:
            if make.lower() in title.lower():
                return make
        return ''
    
    def _extract_model_from_title(self, title: str) -> str:
        """Extract vehicle model from title."""
        title_clean = title
        makes = ['Toyota', 'Honda', 'Nissan', 'Suzuki', 'Mitsubishi', 'Mazda']
        
        for make in makes:
            title_clean = title_clean.replace(make, '')
        
        title_clean = re.sub(r'\b(19|20)\d{2}\b', '', title_clean)
        return title_clean.strip()


# Test function
if __name__ == "__main__":
    scraper = IkmanScraper()
    results = scraper.search("Honda Fit 2015")
    for vehicle in results:
        print(f"{vehicle['title']} - Rs {vehicle['price']:,.0f}")

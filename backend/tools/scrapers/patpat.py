"""
Patpat.lk vehicle scraper.
"""
from typing import List, Dict
from .base_scraper import BaseScraper
import re


class PatpatScraper(BaseScraper):
    """Scraper for Patpat.lk vehicle listings."""
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://patpat.lk"
        self.search_url = f"{self.base_url}/vehicles"
    
    def search(self, query: str, **kwargs) -> List[Dict]:
        """
        Search for vehicles on Patpat.lk.
        
        Args:
            query: Search query (e.g., "Suzuki Wagon R 2017")
            **kwargs: Additional parameters
            
        Returns:
            List of standardized vehicle dictionaries
        """
        vehicles = []
        
        try:
            # Build search URL
            search_url = f"{self.search_url}?search={query.replace(' ', '+')}"
            
            # Fetch search results
            soup = self._fetch_page(search_url)
            if not soup:
                return vehicles
            
            # Extract listings
            listings = soup.find_all('div', class_='vehicle-item')
            
            if not listings:
                # Try alternative selectors
                listings = soup.find_all('div', class_='listing-item')
            
            for listing in listings[:self.max_results]:
                vehicle_data = self._extract_vehicle_data(listing)
                if vehicle_data:
                    standardized = self._standardize_vehicle(vehicle_data)
                    vehicles.append(standardized)
        
        except Exception as e:
            print(f"Error searching Patpat: {str(e)}")
        
        return vehicles
    
    def _extract_vehicle_data(self, listing) -> Dict:
        """Extract vehicle data from listing element."""
        try:
            # Title
            title_elem = listing.find('h3') or listing.find('div', class_='title')
            title = title_elem.text.strip() if title_elem else ''
            
            # Price
            price_elem = listing.find('span', class_='price') or listing.find('div', class_='price')
            price = price_elem.text.strip() if price_elem else '0'
            
            # URL
            url_elem = listing.find('a', href=True)
            url = url_elem['href'] if url_elem else ''
            if url and not url.startswith('http'):
                url = self.base_url + url
            
            # Image
            image_elem = listing.find('img')
            image_url = image_elem.get('src', '') or image_elem.get('data-src', '') if image_elem else ''
            
            # Details
            details_elem = listing.find('div', class_='details')
            location = ''
            year = ''
            mileage = ''
            
            if details_elem:
                detail_text = details_elem.text
                
                # Extract year
                year_match = re.search(r'\b(19|20)\d{2}\b', detail_text)
                if year_match:
                    year = year_match.group()
                
                # Extract mileage
                mileage_match = re.search(r'(\d+[\d,]*)\s*km', detail_text, re.IGNORECASE)
                if mileage_match:
                    mileage = mileage_match.group(0)
                
                # Location (usually last item)
                location_elem = details_elem.find('span', class_='location')
                if location_elem:
                    location = location_elem.text.strip()
            
            return {
                'title': title,
                'price': price,
                'year': year,
                'make': self._extract_make_from_title(title),
                'model': self._extract_model_from_title(title),
                'mileage': mileage or 'N/A',
                'condition': 'Used',
                'location': location or 'N/A',
                'url': url,
                'source': 'Patpat',
                'image_url': image_url
            }
        
        except Exception as e:
            print(f"Error extracting Patpat vehicle data: {str(e)}")
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
        title_clean = title
        makes = ['Toyota', 'Honda', 'Nissan', 'Suzuki', 'Mitsubishi']
        
        for make in makes:
            title_clean = title_clean.replace(make, '')
        
        title_clean = re.sub(r'\b(19|20)\d{2}\b', '', title_clean)
        return title_clean.strip()


# Test function
if __name__ == "__main__":
    scraper = PatpatScraper()
    results = scraper.search("Suzuki Alto 2016")
    for vehicle in results:
        print(f"{vehicle['title']} - Rs {vehicle['price']:,.0f}")

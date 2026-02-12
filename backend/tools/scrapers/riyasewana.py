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
            listings = soup.find_all('li', class_='item')
            if not listings:
                # Try alternative selector used in some versions of the site
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
            'year': '',
            'year_start': '',
            'year_end': ''
        }
        
        # Common Sri Lankan vehicle makes
        makes = ['toyota', 'honda', 'nissan', 'suzuki', 'mitsubishi', 'mazda', 
                 'bmw', 'benz', 'mercedes', 'audi', 'hyundai', 'kia']
        
        for make in makes:
            if make in query_lower:
                parts['make'] = make
                break
        
        # Extract year range (e.g., "1995-2003", "2015-2023", "2015 to 2023")
        # Match full 4-digit years with hyphen or 'to' separator
        year_range_match = re.search(r'(19\d{2}|20\d{2})\s*[-to]+\s*(19\d{2}|20\d{2})', query, re.IGNORECASE)
        if year_range_match:
            parts['year_start'] = year_range_match.group(1)
            parts['year_end'] = year_range_match.group(2)
            print(f"Extracted year range: {parts['year_start']}-{parts['year_end']}")
        else:
            # Extract single year (4 digits)
            year_match = re.search(r'\b(19\d{2}|20\d{2})\b', query)
            if year_match:
                parts['year'] = year_match.group(1)
                print(f"Extracted single year: {parts['year']}")
        
        # Model is remaining text
        query_clean = query.lower()
        for make in makes:
            query_clean = query_clean.replace(make, '')
        # Remove year and year ranges
        query_clean = re.sub(r'(19\d{2}|20\d{2})\s*[-to]+\s*(19\d{2}|20\d{2})', '', query_clean, flags=re.IGNORECASE)
        query_clean = re.sub(r'\b(19\d{2}|20\d{2})\b', '', query_clean)
        parts['model'] = query_clean.strip()
        
        print(f"Parsed query parts: {parts}")
        return parts
    
    def _build_search_params(self, query_parts: Dict, **kwargs) -> str:
        """Build URL search parameters matching Riyasewana's structure: /search/{brand}/{model}/{year_range}."""
        params = []
        
        # Add brand (lowercase)
        if query_parts.get('make'):
            params.append(query_parts['make'].lower())
        
        # Add model (lowercase with hyphens)
        if query_parts.get('model'):
            model = self._format_model_name(query_parts['model'])
            params.append(model)
        
        # Add year or year range
        if query_parts.get('year_start') and query_parts.get('year_end'):
            params.append(f"{query_parts['year_start']}-{query_parts['year_end']}")
        elif query_parts.get('year'):
            # Single year - use as range (e.g., 2018 becomes 2018-2018)
            params.append(f"{query_parts['year']}-{query_parts['year']}")
        
        return '/'.join(params) if params else 'vehicles'
    
    def _format_model_name(self, model: str) -> str:
        """Format model name for URL (lowercase with hyphens)."""
        # Replace spaces with hyphens
        formatted = model.strip().replace(' ', '-')
        # Remove special characters except hyphens and alphanumeric
        formatted = re.sub(r'[^a-z0-9-]', '', formatted.lower())
        # Remove multiple consecutive hyphens
        formatted = re.sub(r'-+', '-', formatted)
        # Remove leading/trailing hyphens
        formatted = formatted.strip('-')
        return formatted
    
    def _extract_vehicle_data(self, listing) -> Dict:
        """Extract vehicle data from a listing element."""
        try:
            # Title
            title_elem = listing.find('h2', class_='more')
            if title_elem and title_elem.find('a'):
                title = title_elem.find('a').text.strip()
                url_elem = title_elem.find('a')
                url = url_elem['href'] if url_elem else ''
            else:
                title = ''
                url = ''
            
            # Price and other details are in boxintxt divs
            boxtext = listing.find('div', class_='boxtext')
            price = '0'
            location = ''
            mileage = ''
            year = ''
            
            if boxtext:
                # Price is usually in the bold boxintxt
                price_elem = boxtext.find('div', class_='boxintxt b')
                if price_elem:
                    price = price_elem.text.strip()
                
                # Other details are in other boxintxt divs
                details = boxtext.find_all('div', class_='boxintxt')
                for detail in details:
                    if not detail:
                        continue
                    text = detail.get_text(strip=True)
                    if 'km' in text.lower():
                        mileage = text
                    elif not any(char.isdigit() for char in text) and text != price:
                        location = text
                    # Year might be in title or extracted elsewhere, but let's try to find it
                    # Riyasewana listings don't always have explicit year field in the boxtext
            
            # Extract year from title if not found
            if not year and title:
                import re
                year_match = re.search(r'\b(19|20)\d{2}\b', title)
                if year_match:
                    year = year_match.group()
            
            # Image
            image_elem = listing.find('img')
            image_url = image_elem.get('src', '') if image_elem else ''
            # Fix relative image URLs
            if image_url.startswith('//'):
                image_url = f"https:{image_url}"
            
            data = {
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
            return data
        
        except Exception as e:
            print(f"DEBUG: Error extracting vehicle data: {e}")
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

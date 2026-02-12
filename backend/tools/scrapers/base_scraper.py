"""
Base scraper class with common functionality for all vehicle website scrapers.
"""
import time
from curl_cffi import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from abc import ABC, abstractmethod
from config import config


class BaseScraper(ABC):
    """Abstract base class for vehicle scrapers."""
    
    def __init__(self):
        self.timeout = config.SCRAPER_TIMEOUT
        self.rate_limit = config.SCRAPER_RATE_LIMIT
        self.max_results = config.SCRAPER_MAX_RESULTS
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        self.last_request_time = 0
    
    def _rate_limit_wait(self):
        """Implement rate limiting between requests."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit:
            time.sleep(self.rate_limit - elapsed)
        self.last_request_time = time.time()
    
    def _fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch and parse a webpage."""
        try:
            self._rate_limit_wait()
            # Use curl_cffi to impersonate Chrome for bypassing bot protection (JA3/TLS fingerprinting)
            response = requests.get(
                url, 
                headers=self.headers, 
                timeout=self.timeout,
                impersonate="chrome110"
            )
            response.raise_for_status()
            return BeautifulSoup(response.content, 'lxml')
        except Exception as e:
            print(f"Error fetching {url}: {str(e)}")
            return None
    
    @abstractmethod
    def search(self, query: str, **kwargs) -> List[Dict]:
        """
        Search for vehicles based on query.
        
        Args:
            query: Search query (e.g., "Toyota Aqua 2018")
            **kwargs: Additional search parameters
            
        Returns:
            List of vehicle dictionaries with standardized fields
        """
        pass
    
    def _standardize_vehicle(self, raw_data: Dict) -> Dict:
        """
        Standardize vehicle data format across all scrapers.
        
        Returns:
            {
                'title': str,
                'price': float,
                'year': int,
                'make': str,
                'model': str,
                'mileage': str,
                'condition': str,
                'location': str,
                'url': str,
                'source': str,
                'image_url': str
            }
        """
        return {
            'title': raw_data.get('title', ''),
            'price': self._parse_price(raw_data.get('price', '')),
            'year': self._parse_year(raw_data.get('year', '')),
            'make': raw_data.get('make', ''),
            'model': raw_data.get('model', ''),
            'mileage': raw_data.get('mileage', 'N/A'),
            'condition': raw_data.get('condition', 'N/A'),
            'location': raw_data.get('location', 'N/A'),
            'url': raw_data.get('url', ''),
            'source': raw_data.get('source', ''),
            'image_url': raw_data.get('image_url', '')
        }
    
    def _parse_price(self, price_str: str) -> float:
        """Extract numeric price from string."""
        try:
            # Remove currency symbols and other non-numeric characters (except dot)
            cleaned = price_str.lower().replace('rs.', '').replace('rs', '').replace('lkr', '').replace(',', '').strip()
            return float(cleaned)
        except:
            return 0.0
    
    def _parse_year(self, year_str: str) -> int:
        """Extract year from string."""
        try:
            # Extract 4-digit year
            import re
            match = re.search(r'\b(19|20)\d{2}\b', str(year_str))
            return int(match.group()) if match else 0
        except:
            return 0

"""
Document indexer for populating the vector store with vehicle knowledge.
"""
from typing import List, Dict
from .vector_store import get_vector_store
import uuid
from datetime import datetime


class VehicleIndexer:
    """Indexes vehicle information into the knowledge base."""
    
    def __init__(self):
        self.vector_store = get_vector_store()
    
    def index_vehicle_data(self, vehicles: List[Dict]):
        """
        Index vehicle listings into the knowledge base.
        
        Args:
            vehicles: List of vehicle dictionaries from scrapers
        """
        if not vehicles:
            return
        
        documents = []
        metadatas = []
        ids = []
        
        for vehicle in vehicles:
            # Create document text
            doc_text = self._create_document_text(vehicle)
            documents.append(doc_text)
            
            # Create metadata
            metadata = {
                'title': vehicle.get('title', ''),
                'make': vehicle.get('make', ''),
                'model': vehicle.get('model', ''),
                'year': str(vehicle.get('year', '')),
                'price': str(vehicle.get('price', 0)),
                'source': vehicle.get('source', ''),
                'indexed_date': datetime.now().isoformat()
            }
            metadatas.append(metadata)
            
            # Generate unique ID
            doc_id = str(uuid.uuid4())
            ids.append(doc_id)
        
        # Add to vector store
        self.vector_store.add_documents(documents, metadatas, ids)
    
    def _create_document_text(self, vehicle: Dict) -> str:
        """Create searchable document text from vehicle data."""
        text = f"{vehicle.get('title', '')} "
        text += f"{vehicle.get('make', '')} {vehicle.get('model', '')} "
        text += f"Year: {vehicle.get('year', '')} "
        text += f"Price: Rs {vehicle.get('price', 0):,.0f} "
        text += f"Location: {vehicle.get('location', '')} "
        text += f"Condition: {vehicle.get('condition', '')} "
        text += f"Mileage: {vehicle.get('mileage', '')} "
        text += f"Source: {vehicle.get('source', '')}"
        
        return text.strip()
    
    def index_market_insights(self, insights: List[str], metadata: Dict = None):
        """
        Index general market insights and knowledge.
        
        Args:
            insights: List of insight texts
            metadata: Optional metadata for all insights
        """
        if not insights:
            return
        
        documents = insights
        metadatas = [metadata or {} for _ in insights]
        ids = [str(uuid.uuid4()) for _ in insights]
        
        self.vector_store.add_documents(documents, metadatas, ids)
    
    def seed_knowledge_base(self):
        """Seed the knowledge base with initial vehicle market knowledge."""
        insights = [
            "Toyota Aqua is a popular hybrid vehicle in Sri Lanka, known for fuel efficiency. Typical price range for 2015-2018 models is Rs 4.5M - 6.5M.",
            "Honda Fit (also known as Honda Jazz) is a compact hatchback. 2013-2017 models typically range from Rs 3.5M - 5.5M depending on condition and mileage.",
            "Suzuki Wagon R is an affordable family car. 2015-2019 models usually cost between Rs 2.5M - 4.0M.",
            "Vehicle prices in Sri Lanka are influenced by year, mileage, condition, and import duties. Hybrid vehicles generally have higher resale value.",
            "Popular vehicle websites in Sri Lanka include Riyasewana.com, Ikman.lk, and Patpat.lk for buying and selling vehicles.",
            "When comparing vehicles, consider total cost of ownership including fuel efficiency, maintenance costs, and insurance.",
            "Nissan Leaf is a fully electric vehicle gaining popularity. Used models (2013-2017) range from Rs 2.5M - 4.5M.",
            "Toyota Prius is another popular hybrid. Older models (2010-2015) cost Rs 3.0M - 5.5M, while newer ones (2016-2020) range Rs 6.0M - 9.0M.",
            "Mitsubishi Montero Sport is a popular SUV. 2015-2019 models typically cost Rs 8.0M - 12.0M.",
            "Vehicle depreciation in Sri Lanka averages 10-15% per year for the first 5 years, then slows down."
        ]
        
        metadata = {
            'type': 'market_insight',
            'source': 'knowledge_base',
            'date': datetime.now().isoformat()
        }
        
        self.index_market_insights(insights, metadata)
        print(f"Seeded knowledge base with {len(insights)} insights")


# Export indexer instance
vehicle_indexer = VehicleIndexer()

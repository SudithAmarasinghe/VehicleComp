# Vehicle Market Price AI Agent

A comprehensive multi-step agentic AI system that provides real-time vehicle market price information from Sri Lankan websites using LangGraph for orchestration, RAG pipelines for knowledge retrieval, and a React-based conversational interface.

## Features

- 🤖 **Intelligent AI Agent**: LangGraph-powered workflow with intent classification and tool orchestration
- 🌐 **Real-time Web Scraping**: Fetches current listings from Riyasewana.com, Ikman.lk, and Patpat.lk
- 🔍 **RAG Pipeline**: ChromaDB vector store for historical data and market insights
- 💬 **Real-time Chat**: WebSocket-based conversational interface
- 📊 **Price Comparison**: Compare multiple vehicle models side-by-side
- 🎨 **Modern UI**: Beautiful React interface with glassmorphism and animations

## Architecture

```
┌─────────────────┐
│  React Frontend │
│   (WebSocket)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  FastAPI Server │
│   (WebSocket +  │
│   REST API)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  LangGraph      │
│  Agent Workflow │
└────┬────────┬───┘
     │        │
     ▼        ▼
┌─────────┐ ┌──────────┐
│ Scrapers│ │   RAG    │
│  Tools  │ │ Pipeline │
└─────────┘ └──────────┘
```

## Setup Instructions

### Prerequisites

- Python 3.9+
- Node.js 16+
- OpenAI API Key

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file from the example:
```bash
cp ../.env.example .env
```

5. Edit `.env` and add your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

6. Run the backend server:
```bash
python main.py
```

The backend will start on `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will start on `http://localhost:5173`

## Usage Examples

### Single Vehicle Price Check
```
User: "What's the price of Toyota Aqua 2018?"
```

### Vehicle Comparison
```
User: "Compare Toyota Aqua 2018 vs Honda Fit 2015"
```

### General Market Information
```
User: "Tell me about hybrid vehicle prices in Sri Lanka"
```

## API Documentation

### REST Endpoints

#### POST /api/query
Query the agent with a question.

**Request:**
```json
{
  "query": "Toyota Aqua 2018 price",
  "conversation_history": []
}
```

**Response:**
```json
{
  "response": "I found several Toyota Aqua 2018 listings...",
  "vehicles": [...],
  "comparison": {},
  "intent": "price_check"
}
```

### WebSocket Endpoint

#### WS /ws/{client_id}
Real-time chat connection.

**Send:**
```json
{
  "message": "Toyota Aqua 2018 price"
}
```

**Receive:**
```json
{
  "type": "response",
  "message": "I found several listings...",
  "vehicles": [...],
  "comparison": {},
  "intent": "price_check"
}
```

## Project Structure

```
.
├── backend/
│   ├── agent/              # LangGraph workflow
│   │   ├── state.py        # Agent state definition
│   │   └── graph.py        # Workflow graph
│   ├── tools/              # Agent tools
│   │   ├── scrapers/       # Web scrapers
│   │   └── scraper_tool.py # Unified scraper tool
│   ├── rag/                # RAG pipeline
│   │   ├── vector_store.py # ChromaDB management
│   │   ├── retriever.py    # Document retrieval
│   │   └── indexer.py      # Document indexing
│   ├── config.py           # Configuration
│   ├── main.py             # FastAPI server
│   └── requirements.txt    # Python dependencies
│
├── frontend/
│   ├── src/
│   │   ├── components/     # React components
│   │   │   ├── VehicleCard.jsx
│   │   │   ├── MessageList.jsx
│   │   │   └── ChatInput.jsx
│   │   ├── services/       # Services
│   │   │   └── websocket.js
│   │   ├── App.jsx         # Main app component
│   │   └── index.css       # Global styles
│   ├── package.json        # Node dependencies
│   └── vite.config.js      # Vite configuration
│
└── README.md
```

## Technologies Used

### Backend
- **LangGraph**: Agent workflow orchestration
- **LangChain**: LLM framework and tools
- **FastAPI**: Web server framework
- **ChromaDB**: Vector database
- **BeautifulSoup**: Web scraping
- **Sentence Transformers**: Embeddings

### Frontend
- **React**: UI framework
- **Vite**: Build tool
- **Socket.IO**: WebSocket communication
- **Lucide React**: Icons

## Notes

- Web scraping is subject to website terms of service
- Rate limiting is implemented to be respectful to source websites
- The knowledge base is seeded with initial market insights on first run
- WebSocket automatically reconnects on disconnection

## Future Enhancements

- Add more vehicle websites
- Implement caching for frequently searched vehicles
- Add price trend analysis
- Support for vehicle specifications comparison
- Email alerts for price drops
- Mobile app version

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

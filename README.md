# OttoPilot - OVGU University Chatbot

A bilingual conversational assistant for Otto-von-Guericke University Magdeburg (OVGU) that provides information about admissions, study programs, campus life, and university services in both English and German.

## Overview

OttoPilot is an intelligent chatbot system built to help prospective and current students navigate university information efficiently. The system combines retrieval-augmented generation (RAG) with web search capabilities to provide accurate, contextual answers while maintaining conversation history.

### Key Features

- **Bilingual Support**: Automatic language detection and response generation in English or German
- **Intelligent Routing**: Classifies queries and routes them through appropriate processing pipelines
- **Multi-Source Information**: Retrieves data from university documents and falls back to web search when needed
- **Conversation Memory**: Maintains context across multiple turns for coherent dialogue
- **Similarity Scoring**: Filters retrieved documents by relevance threshold to ensure answer quality
- **Web Interface**: Clean Streamlit-based interface for easy interaction

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                         User Query                          │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    Query Classification                     │
│  (Language Detection + Intent Recognition)                  │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ▼             ▼             ▼
   ┌────────┐   ┌─────────┐   ┌─────────┐
   │  RAG   │   │   Web   │   │ Chitchat│
   └────┬───┘   └────┬────┘   └────┬────┘
        │            │             │
        └────────────┼─────────────┘
                     │
                     ▼
        ┌────────────────────────┐
        │   Answer Generation    │
        │   (with Sources)       │
        └────────────────────────┘
```

### Technology Stack

- **LLM**: Google Gemini (gemini-2.5-flash)
- **Embeddings**: Google text-embedding-004
- **Vector Store**: ChromaDB Cloud
- **Framework**: LangChain + LangGraph
- **Web Search**: Tavily API
- **Web Interface**: Streamlit
- **Language**: Python 3.8+

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Git (for cloning)

### Setup Instructions

1. Clone the repository:
```bash
git clone https://github.com/yourusername/OttoPilot.git
cd OttoPilot
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:

Create a `.env` file in the project root:
```env
# Google AI API Key
GOOGLE_API_KEY=your_google_api_key_here

# ChromaDB Cloud Configuration
CHROMA_API_KEY=your_chroma_api_key
CHROMA_TENANT=your_tenant_id
CHROMA_DATABASE=OttoPilot

# Tavily API Key (for web search)
TAVILY_API_KEY=your_tavily_api_key

# Optional: LangSmith (for debugging)
LANGSMITH_API_KEY=your_langsmith_api_key
LANGSMITH_TRACING=false
```

5. Obtain API Keys:
   - **Google AI**: Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - **ChromaDB Cloud**: Sign up at [ChromaDB](https://www.trychroma.com/)
   - **Tavily**: Get key from [Tavily](https://tavily.com/)

## Usage

### Data Collection

Before running the chatbot, collect university data:

```bash
# Quick start (recommended for testing)
python src/ovgu_scraper.py
# Follow prompts to select collection strategy
```

Available collection options:
- **Quick Start**: Scrapes 6 key pages (2-3 minutes)
- **Optimized**: Targeted collection of 25 important pages (5-7 minutes)
- **Full Collection**: Comprehensive scraping including PDFs (12-15 minutes)

### Document Processing

Process collected data into vector embeddings:

```bash
# 1. Inspect collected data
python src/data_inspector.py

# 2. Process documents into chunks
python src/document_processor.py

# 3. Create vector store
python src/embeddings.py
```

### Running the Chatbot

#### Web Interface (Recommended)

```bash
streamlit run app.py
```

Access at: http://localhost:8501

#### Command Line Interface

```bash
python src/graph.py
```

#### Test Retrieval System

```bash
python src/retriever.py
```

## Project Structure

```
OttoPilot/
├── app.py                      # Streamlit web interface
├── requirements.txt            # Python dependencies
├── .env                        # Environment configuration (not in repo)
├── langgraph.json             # LangGraph configuration
│
├── src/
│   ├── config.py              # Application settings
│   ├── graph.py               # LangGraph workflow definition
│   ├── nodes.py               # Graph node implementations
│   ├── prompts.py             # Prompt templates and language detection
│   ├── retriever.py           # Document retrieval logic
│   ├── embeddings.py          # Vector store management
│   ├── document_processor.py  # Document chunking pipeline
│   ├── scraper.py             # Web scraping utilities
│   ├── document_downloader.py # PDF/document downloader
│   ├── ovgu_scraper.py        # OVGU-specific scraper
│   ├── collect_data.py        # Data collection orchestrator
│   ├── data_inspector.py      # Data quality checker
│   └── web_search.py          # Web search integration
│
├── data/
│   └── raw/                   # Scraped documents and PDFs
│
├── tests/
│   └── test_retrieval.py      # Unit tests
│
└── debug_web_search.py        # Web search diagnostic tool
```

## Configuration

### Vector Store Settings

Modify `src/config.py` for custom settings:

```python
chunk_size = 800           # Document chunk size
chunk_overlap = 150        # Overlap between chunks
top_k_docs = 5            # Number of documents to retrieve
similarity_threshold = 0.5 # Relevance threshold
```

### Model Settings

```python
gemini_model = "gemini-2.5-flash"
embedding_model = "models/text-embedding-004"
temperature = 0.3          # Response randomness (0-1)
```

## Workflow Details

### Query Processing Pipeline

1. **Classification**: Query is analyzed to determine type (RAG/Web/Chitchat) and language
2. **Retrieval**: Based on classification:
   - RAG queries: Search vector store for relevant documents
   - Web queries: Use Tavily to search current information
   - Chitchat: Generate conversational response
3. **Fallback Mechanism**: If RAG retrieval yields no results (similarity score too low), automatically fallback to web search
4. **Answer Generation**: LLM generates response using retrieved context and conversation history
5. **Formatting**: Response is formatted with sources and returned to user

### Language Detection

The system uses multiple signals for accurate language detection:
- German-specific characters (ä, ö, ü, ß)
- Language-specific keywords
- Word patterns and sentence structure
- Single-word dictionary lookup

## Troubleshooting

### Common Issues

**Problem**: No documents retrieved
```bash
# Solution: Check vector store exists
python src/embeddings.py  # Recreate if needed
```

**Problem**: Web search not working
```bash
# Solution: Verify Tavily API key
python debug_web_search.py
```

**Problem**: Wrong language responses
```bash
# Solution: Check prompts.py language detection logic
# Ensure query is clear about language preference
```

**Problem**: ChromaDB connection failed
```bash
# Solution: Verify credentials in .env
# Check ChromaDB Cloud dashboard for tenant/database names
```



## Development

### Adding New Features

1. **Custom Data Sources**: Modify `src/scraper.py` to target specific pages
2. **Additional Languages**: Extend `src/prompts.py` language detection
3. **New Query Types**: Add classifications in `src/nodes.py`
4. **Custom Prompts**: Edit templates in `src/prompts.py`

### Testing

```bash
# Test web search functionality
python test_web_search.py

# Test retrieval system
python tests/test_retrieval.py
```

## Performance Considerations

- **Initial Load Time**: First query takes 3-5 seconds (embedding generation)
- **Subsequent Queries**: ~1-2 seconds average response time
- **Vector Store Size**: Depends on scraped data volume (typically 50-200MB)
- **Memory Usage**: ~500MB-1GB during operation

## Limitations

- **Data Freshness**: Information is current as of last scraping run
- **Language Support**: Currently supports English and German only
- **Web Search**: Subject to Tavily API rate limits
- **Context Window**: Limited to last 5 conversation turns for memory efficiency

## Future Enhancements

Potential improvements for future versions:
- Add support for additional languages (French, Spanish)
- Implement semantic caching for faster repeated queries
- Add user authentication for personalized experiences
- Include feedback mechanism for answer quality
- Expand to cover more universities
- Add voice interface support

## Contributing

Contributions are welcome. Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature-name`)
3. Commit changes (`git commit -m 'Add feature'`)
4. Push to branch (`git push origin feature-name`)
5. Open a Pull Request

## License

This project is provided as-is for educational purposes. 

## Acknowledgments

- Otto-von-Guericke University Magdeburg for providing publicly accessible information
- Google for Gemini AI API
- LangChain community for framework support
- ChromaDB team for vector database infrastructure

## Contact

For questions or issues, contact @ vishnutalwar03@gmail.com

---

**Note**: This is an independent student project and is not officially affiliated with Otto-von-Guericke University Magdeburg. All university information should be verified through official OVGU channels.

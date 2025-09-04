# RAG API with Weaviate + Elysia

## Overview
This project provides an **intelligent document indexing and retrieval API** powered by **Weaviate** (cloud-native vector database) and **Elysia** (agentic AI framework). It offers both traditional semantic search and advanced agentic querying with decision trees.

Files are organized into embeddings by `file_id`, making it perfect for integration with [LibreChat](https://librechat.ai) and other applications requiring document-level retrieval. The API employs modern AI agent capabilities for intelligent document interaction.

**💡 Complete Solution**: Combine this API with the [Elysia Frontend](https://github.com/weaviate/elysia-frontend) for a full-stack document intelligence platform with web interface, chat capabilities, and 3D visualizations.

## ✨ Key Features

- **🤖 Agentic Querying**: AI agents with decision trees for intelligent document retrieval
- **☁️ Cloud-Native**: Weaviate vector database with automatic scaling
- **🔍 Dual Search Modes**: Traditional semantic search + agentic reasoning
- **🐳 Docker Ready**: Complete local development environment included
- **📄 Document Management**: Add, retrieve, and delete documents with metadata
- **🚀 Async Performance**: Built with FastAPI for high-performance operations
- **🔌 Flexible Deployment**: Local development or cloud production ready

## 🚀 Quick Start

### Option 1: Docker (Recommended)
```bash
# 1. Setup environment
cp .env.dev .env
# Edit .env and add your OpenAI API key

# 2. Start services (includes local Weaviate database)
docker compose up --build

# 3. Access the API
# - API: http://localhost:8000
# - Documentation: http://localhost:8000/docs  
# - Weaviate: http://localhost:8080
```

### Option 2: Python Development
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Setup environment for local Weaviate
cp .env.dev .env
# Edit .env with your API credentials

# 3. Start local Weaviate
docker run -p 8080:8080 -e AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true \
  cr.weaviate.io/semitechnologies/weaviate:1.32.5

# 4. Run the API
python main.py
```

## 🎯 API Endpoints

### Document Management
- `POST /upload` - Upload and process documents
- `GET /ids` - Get all document IDs
- `GET /count` - Get total document count  
- `DELETE /documents/{file_id}` - Delete documents by file ID
- `POST /store` - Store pre-uploaded documents

### Querying
- `POST /query` - **Traditional semantic search**
  ```json
  {"query": "What is machine learning?"}
  ```

- `POST /query/agentic` - **🤖 NEW: Agentic query with AI reasoning**
  ```json
  {
    "query": "Analyze the main themes in these documents and provide insights",
    "collection_names": ["Documents"]
  }
  ```

### System
- `GET /health` - Health check
- `GET /stats/{project_id}` - Project statistics

## 📊 Agentic Capabilities

The `/query/agentic` endpoint uses **Elysia's decision tree system** to:

- 🧠 **Intelligently select tools** for document retrieval
- 🔄 **Reason about queries** using AI agent decision trees  
- 📈 **Provide explanations** for search strategies used
- 🎯 **Optimize results** based on document context and user intent

Example response:
```json
{
  "response": "Based on the analysis of your documents, the main themes are...",
  "objects": [...],
  "agent_reasoning": "Query processed through Elysia decision tree"
}
```

## ⚙️ Environment Variables

### Required Configuration
```env
# Weaviate Database
WCD_URL=http://localhost:8080          # Local development
WCD_API_KEY=                           # Empty for local dev
WEAVIATE_COLLECTION_NAME=Documents

# OpenAI for Embeddings (Required)
OPENAI_API_KEY=your-openai-api-key
EMBEDDINGS_PROVIDER=openai
EMBEDDINGS_MODEL=text-embedding-3-small

# API Configuration
RAG_HOST=0.0.0.0
RAG_PORT=8000
RAG_UPLOAD_DIR=./uploads/
```

### Optional Configuration
```env
# Elysia Agentic Framework
OPENROUTER_API_KEY=your-openrouter-api-key

# Document Processing
CHUNK_SIZE=1500
CHUNK_OVERLAP=100
PDF_EXTRACT_IMAGES=False

# Alternative Embedding Providers
EMBEDDINGS_PROVIDER=azure|huggingface|ollama|bedrock|vertexai
# Provider-specific API keys...

# Logging
DEBUG_RAG_API=False
CONSOLE_JSON=False
```

## 🏗️ Architecture

```
┌─────────────────┐    ┌───────────────────┐    ┌─────────────────┐
│   FastAPI       │    │  Elysia Agent     │    │   Weaviate      │
│   Routes        │───▶│  Decision Trees   │───▶│   Vector Store  │
│                 │    │  Tool Selection   │    │   (Local/Cloud) │
└─────────────────┘    └───────────────────┘    └─────────────────┘
```

### Modern Stack Benefits
- **No Database Management**: Weaviate handles vector operations
- **AI-Powered Retrieval**: Elysia agents make intelligent decisions  
- **Simplified Deployment**: Single vector store, no complex setup
- **Cloud-Native Scaling**: Automatic performance optimization
- **Development Friendly**: Local Docker environment included

## 🌐 Deployment Options

### Local Development
Use the included Docker Compose setup with local Weaviate instance.

### Production with Weaviate Cloud
1. Create a Weaviate Cloud cluster at https://console.weaviate.cloud
2. Update `.env` with your cluster URL and API key:
   ```env
   WCD_URL=https://your-cluster.weaviate.network
   WCD_API_KEY=your-weaviate-cloud-api-key
   ```
3. Deploy with `docker compose up`

### Production with Docker
See [DOCKER.md](DOCKER.md) for comprehensive Docker deployment guide.

## 📋 Migration from Legacy Versions

If you're upgrading from the PostgreSQL/MongoDB version, see [README_MIGRATION.md](README_MIGRATION.md) for:
- Complete migration guide
- Breaking changes documentation  
- Architecture comparison
- Migration benefits

## 🖥️ Web Interface (Optional)

For a complete user experience, you can use the **Elysia Frontend** - a modern web interface with chat, data visualization, and 3D graphics:

### Features of Elysia Frontend:
- **💬 Interactive Chat Interface** - Web-based document querying
- **📊 Data Visualization** - Charts and analytics for your documents  
- **🌐 3D Graphics** - Interactive visualizations with Three.js
- **⚙️ Configuration Management** - Easy setup and model configuration
- **🔍 Data Explorer** - Advanced browsing and search capabilities

### Setup Elysia Frontend:
```bash
# Clone the frontend (separate repository)
git clone https://github.com/weaviate/elysia-frontend
cd elysia-frontend

# Install and start
npm install
npm run dev

# Access at http://localhost:3000
```

The frontend integrates with your RAG API to provide a complete document intelligence platform with both programmatic and visual interfaces.

## 🧪 API Testing

```bash
# Test the API
curl http://localhost:8000/health

# Upload a document
curl -X POST "http://localhost:8000/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@document.pdf"

# Query documents (traditional)
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is this document about?"}'

# Query documents (agentic)
curl -X POST "http://localhost:8000/query/agentic" \
  -H "Content-Type: application/json" \
  -d '{"query": "Analyze the key insights from these documents"}'
```

## 🤝 Contributing

This project uses modern Python practices:
- **FastAPI** for async web framework
- **Weaviate** for vector database operations
- **Elysia** for agentic AI capabilities
- **Docker** for containerized development
- **Pydantic** for data validation

## 📄 License

[Add your license information here]

---

**🚀 Ready to build intelligent document retrieval with AI agents?** Get started with the Quick Start guide above!
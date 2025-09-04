# RAG API Migration to Weaviate + Elysia

## Migration Summary

This RAG API has been successfully migrated from a PostgreSQL/MongoDB vector store architecture to a modern **Weaviate + Elysia** stack.

## What Changed

### ✅ Removed Components
- **PostgreSQL/PgVector** - Legacy vector database
- **MongoDB/Atlas** - Legacy document storage
- **Legacy vector store implementations** - Custom PgVector and MongoDB adapters
- **Database connection pooling** - PostgreSQL-specific connection management
- **Complex factory patterns** - Simplified to single Weaviate integration

### ✅ Added Components  
- **Weaviate** - Modern cloud-native vector database
- **Elysia AI** - Agentic framework with decision tree capabilities
- **Unified service layer** - Single `ElysiaWeaviateService` handling all operations
- **Agentic query endpoints** - AI-powered document retrieval

## New Architecture

```
┌─────────────────┐    ┌───────────────────┐    ┌─────────────────┐
│   FastAPI       │    │  Elysia Agent     │    │   Weaviate      │
│   Routes        │───▶│  Decision Trees   │───▶│   Cloud         │
│                 │    │  Tool Selection   │    │   Vector Store  │
└─────────────────┘    └───────────────────┘    └─────────────────┘
```

## Environment Configuration

Create a `.env` file with the following required variables:

```env
# Weaviate Configuration (Required)
WCD_URL=https://your-cluster.weaviate.network
WCD_API_KEY=your-weaviate-api-key
WEAVIATE_COLLECTION_NAME=Documents

# API Configuration
RAG_HOST=0.0.0.0
RAG_PORT=8000
RAG_UPLOAD_DIR=./uploads/

# Embeddings Configuration
EMBEDDINGS_PROVIDER=openai
EMBEDDINGS_MODEL=text-embedding-3-small
OPENAI_API_KEY=your-openai-api-key

# Elysia Configuration (Recommended)
OPENROUTER_API_KEY=your-openrouter-api-key
```

See `.env.example` for all available configuration options.

## API Endpoints

### Core Endpoints
- `GET /health` - Health check
- `GET /ids` - Get all document IDs
- `GET /count` - Get document count
- `POST /upload` - Upload and process documents
- `DELETE /documents/{file_id}` - Delete documents by file ID

### Query Endpoints
- `POST /query` - Simple semantic search
- `POST /query/agentic` - **NEW** Agentic query with Elysia decision trees

### Legacy Compatibility
- `GET /stats/{project_id}` - Project statistics
- `POST /store` - Store pre-uploaded documents

## New Features

### 🤖 Agentic Queries
The `/query/agentic` endpoint uses Elysia's decision tree system to intelligently select tools and provide reasoning:

```json
POST /query/agentic
{
  "query": "What are the main themes in the uploaded documents?",
  "collection_names": ["Documents"]
}
```

Response includes:
- AI-generated response
- Relevant document objects
- Agent reasoning explanation

### 🔍 Enhanced Search
- **Semantic similarity** search powered by Weaviate
- **Hybrid search** capabilities (dense + sparse vectors)
- **Metadata filtering** for precise document retrieval
- **Scalable vector operations** with cloud-native performance

## Installation & Deployment

### Local Development with Docker (Recommended)
```bash
# Copy development environment file
cp .env.dev .env
# Edit .env to add your OpenAI API key

# Start Weaviate database and RAG API
docker-compose up --build

# The API will be available at http://localhost:8000
# Weaviate will be available at http://localhost:8080
```

### Local Development (Python)
```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment for local Weaviate
cp .env.dev .env
# Edit .env with your API credentials

# Start local Weaviate first
docker run -p 8080:8080 -e AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true \
  cr.weaviate.io/semitechnologies/weaviate:1.32.5

# Run the API
python main.py
```

### Production with Weaviate Cloud
```bash
# Use the cloud configuration
cp .env.example .env
# Edit .env with your Weaviate Cloud credentials and API keys

# Build and run (will use cloud Weaviate)
docker-compose up --build
```

## Docker Services

The Docker Compose setup now includes:

- **Weaviate Database** - Local vector database on port 8080
- **RAG API** - FastAPI application on port 8000
- **Persistent Storage** - Named volume for Weaviate data
- **Health Checks** - Ensures Weaviate is ready before starting API

## Migration Benefits

1. **Simplified Architecture** - Single vector store, no complex factory patterns
2. **Cloud-Native Scaling** - Weaviate handles scaling automatically  
3. **Agentic Capabilities** - Intelligent document interaction with Elysia
4. **Modern Stack** - Latest vector database and AI agent technologies
5. **Reduced Complexity** - Eliminated database management overhead
6. **Better Performance** - Purpose-built vector operations

## Breaking Changes

1. **Database Dependencies Removed** - No longer supports PostgreSQL or MongoDB
2. **Factory Pattern Removed** - Direct Weaviate integration only
3. **Legacy Endpoints** - Some internal endpoints may have changed responses
4. **Environment Variables** - Updated configuration schema (see `.env.example`)

## Notes

- All existing document processing capabilities are preserved
- File upload and chunking logic remains unchanged
- Health checks and monitoring endpoints maintained
- Compatible with existing client applications (core endpoints unchanged)

---

**Migration completed successfully!** 🎉

The RAG API now runs on a modern, scalable, and intelligent stack with Weaviate + Elysia.
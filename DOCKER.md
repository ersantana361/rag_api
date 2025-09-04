# Docker Setup Guide

## Quick Start

1. **Setup Environment**
   ```bash
   # Copy the development environment template
   cp .env.dev .env
   
   # Edit and add your OpenAI API key
   nano .env
   ```

2. **Start Services**
   ```bash
   # Build and start both Weaviate and RAG API
   docker compose up --build
   ```

3. **Access Services**
   - **RAG API**: http://localhost:8000
   - **API Docs**: http://localhost:8000/docs
   - **Weaviate**: http://localhost:8080

## Services Overview

### Weaviate Database
- **Image**: `cr.weaviate.io/semitechnologies/weaviate:1.32.5`
- **Ports**: 8080 (HTTP), 50051 (gRPC)
- **Features**:
  - Anonymous access enabled for development
  - Persistent data storage
  - API-based modules enabled
  - Health checks configured
  - OpenAI and HuggingFace vectorizers available

### RAG API
- **Build**: Local Dockerfile
- **Port**: 8000
- **Features**:
  - Depends on healthy Weaviate service
  - Volume mounted uploads directory
  - Environment overrides for local development
  - Automatic connection to local Weaviate

## Environment Configuration

### Development (.env.dev)
Pre-configured for local Docker development:
- Weaviate URL: `http://localhost:8080`
- No API key required (anonymous access)
- Debug mode enabled

### Production (.env.example)
Template for cloud deployment:
- Weaviate Cloud URL and API key required
- Production logging settings

## Data Persistence

- **Weaviate Data**: Stored in named volume `weaviate_data`
- **Uploads**: Mounted from `./uploads` directory
- **Data Survives**: Container restarts and rebuilds

## Common Commands

### Start Services
```bash
# Start in foreground
docker compose up

# Start in background
docker compose up -d

# Rebuild and start
docker compose up --build
```

### Stop Services
```bash
# Stop containers
docker compose down

# Stop and remove volumes
docker compose down -v
```

### View Logs
```bash
# All services
docker compose logs

# Specific service
docker compose logs rag-api
docker compose logs weaviate
```

### Service Management
```bash
# Check status
docker compose ps

# Restart specific service
docker compose restart rag-api

# Access shell
docker compose exec rag-api bash
```

## Health Checks

### Weaviate Health Check
```bash
curl http://localhost:8080/v1/.well-known/ready
```

### RAG API Health Check
```bash
curl http://localhost:8000/health
```

## Development Workflow

1. **Start Development**
   ```bash
   ./test-docker-setup.sh  # Validate setup
   docker compose up --build
   ```

2. **Make Code Changes**
   - Edit Python files
   - Changes require rebuild: `docker compose up --build`

3. **Upload Documents**
   ```bash
   curl -X POST "http://localhost:8000/upload" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@your-document.pdf"
   ```

4. **Query Documents**
   ```bash
   # Simple query
   curl -X POST "http://localhost:8000/query" \
     -H "Content-Type: application/json" \
     -d '{"query": "your question here"}'
   
   # Agentic query
   curl -X POST "http://localhost:8000/query/agentic" \
     -H "Content-Type: application/json" \
     -d '{"query": "your question here"}'
   ```

## Troubleshooting

### Common Issues

**Port Conflicts**
```bash
# Check what's using port 8080 or 8000
lsof -i :8080
lsof -i :8000

# Stop conflicting services or change ports in docker-compose.yaml
```

**Permission Issues**
```bash
# Fix uploads directory permissions
sudo chown -R $USER:$USER ./uploads
```

**Container Won't Start**
```bash
# Check logs for detailed errors
docker compose logs weaviate
docker compose logs rag-api

# Validate configuration
docker compose config
```

**Weaviate Connection Issues**
```bash
# Verify Weaviate is running and healthy
docker compose ps
curl http://localhost:8080/v1/.well-known/ready

# Check environment variables
docker compose exec rag-api env | grep WCD
```

### Reset Everything
```bash
# Stop services and remove all data
docker compose down -v

# Remove images to force rebuild
docker compose down --rmi all

# Start fresh
docker compose up --build
```

## Production Deployment

For production with Weaviate Cloud:

1. **Update Environment**
   ```bash
   cp .env.example .env
   # Edit with your Weaviate Cloud credentials
   ```

2. **Remove Local Overrides**
   Remove the environment overrides from `docker-compose.yaml`:
   ```yaml
   # Remove these lines from rag-api service:
   # - WCD_URL=http://weaviate:8080
   # - WCD_API_KEY=
   ```

3. **Deploy**
   ```bash
   docker compose up -d
   ```

## Monitoring

### View Resource Usage
```bash
docker stats
```

### Check Disk Usage
```bash
# Volume sizes
docker volume ls
docker system df

# Cleanup unused resources
docker system prune
```

---

🐳 **Happy Dockerizing!** Your RAG API with Weaviate is now containerized and ready for development.
# app/routes/document_routes.py
import os
import hashlib
import traceback
import aiofiles
import aiofiles.os
from shutil import copyfileobj
from typing import List, Dict, Any, Optional
from fastapi import (
    APIRouter,
    Request,
    UploadFile,
    HTTPException,
    File,
    Form,
    Body,
    Query,
    status,
)
from langchain_core.documents import Document
from pydantic import BaseModel

from app.config import logger, RAG_UPLOAD_DIR
from app.constants import ERROR_MESSAGES
from app.models import (
    StoreDocument,
    QueryRequestBody,
    DocumentResponse,
    QueryMultipleBody,
)
from app.services.elysia_service import elysia_service
from app.utils.document_loader import get_loader, clean_text, process_documents
from app.utils.health import is_health_ok

router = APIRouter()


class AgenticQueryRequest(BaseModel):
    query: str
    collection_names: Optional[List[str]] = None


@router.get("/health")
async def health_check():
    try:
        if await is_health_ok():
            return {"status": "UP"}
        else:
            logger.error("Health check failed")
            return {"status": "DOWN"}, 503
    except Exception as e:
        logger.error(
            "Error during health check | Error: %s | Traceback: %s",
            str(e),
            traceback.format_exc(),
        )
        return {"status": "DOWN", "error": str(e)}, 503


@router.get("/ids")
async def get_all_ids():
    """Get all document IDs from Weaviate."""
    try:
        ids = await elysia_service.get_all_document_ids()
        return {"ids": ids, "count": len(ids)}
    except Exception as e:
        logger.error(f"Failed to get all IDs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/count")
async def get_document_count():
    """Get total count of documents in Weaviate."""
    try:
        count = await elysia_service.get_document_count()
        return {"count": count}
    except Exception as e:
        logger.error(f"Failed to get document count: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query")
async def query_documents(query_request: QueryRequestBody):
    """Simple semantic search using Weaviate."""
    try:
        results = await elysia_service.simple_query(
            query=query_request.query,
            limit=getattr(query_request, 'limit', 10)
        )
        
        # Convert to expected format
        formatted_results = []
        for result in results:
            formatted_results.append(DocumentResponse(
                page_content=result["content"],
                metadata=result["metadata"]
            ))
        
        return {"results": formatted_results}
        
    except Exception as e:
        logger.error(f"Error in query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query/agentic")
async def agentic_query_documents(query_request: AgenticQueryRequest):
    """Advanced agentic query using Elysia decision trees."""
    try:
        response, objects = await elysia_service.query_with_elysia(
            query=query_request.query,
            collection_names=query_request.collection_names
        )
        
        return {
            "response": response,
            "objects": objects,
            "agent_reasoning": "Query processed through Elysia decision tree"
        }
        
    except Exception as e:
        logger.error(f"Error in agentic query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload")
async def upload_document(
    request: Request,
    file: UploadFile = File(...),
    file_id: Optional[str] = Form(None)
):
    """Upload and process a document into Weaviate via Elysia."""
    try:
        # Generate file_id if not provided
        if not file_id:
            file_content = await file.read()
            await file.seek(0)  # Reset file pointer
            file_id = hashlib.md5(file_content).hexdigest()
        
        # Save file temporarily
        file_path = os.path.join(RAG_UPLOAD_DIR, f"{file_id}_{file.filename}")
        
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        # Process document
        try:
            loader = get_loader(file_path)
            raw_documents = loader.load()
            
            # Clean and process documents
            cleaned_documents = []
            for doc in raw_documents:
                cleaned_content = clean_text(doc.page_content)
                if cleaned_content.strip():
                    doc.page_content = cleaned_content
                    doc.metadata.update({
                        "filename": file.filename,
                        "file_path": file_path,
                        "content_type": file.content_type
                    })
                    cleaned_documents.append(doc)
            
            if not cleaned_documents:
                raise HTTPException(
                    status_code=400, 
                    detail="No valid content found in document"
                )
            
            # Store in Weaviate via Elysia
            success = await elysia_service.store_documents(cleaned_documents, file_id)
            
            if not success:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to store document in Weaviate"
                )
            
            return {
                "message": "Document uploaded and processed successfully",
                "file_id": file_id,
                "filename": file.filename,
                "chunks_created": len(cleaned_documents)
            }
            
        finally:
            # Clean up temporary file
            try:
                await aiofiles.os.remove(file_path)
            except Exception as cleanup_error:
                logger.warning(f"Failed to cleanup temporary file: {cleanup_error}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/documents/{file_id}")
async def delete_document(file_id: str):
    """Delete all documents associated with a file_id."""
    try:
        success = await elysia_service.delete_documents_by_file_id(file_id)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"No documents found for file_id: {file_id}"
            )
        
        return {
            "message": f"Successfully deleted documents for file_id: {file_id}",
            "file_id": file_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/store")
async def store_document(store_request: StoreDocument):
    """Store a document that's already been uploaded."""
    try:
        if not os.path.exists(store_request.filepath):
            raise HTTPException(
                status_code=404,
                detail=f"File not found: {store_request.filepath}"
            )
        
        # Load and process document
        loader = get_loader(store_request.filepath)
        documents = loader.load()
        
        # Add metadata
        for doc in documents:
            doc.metadata.update({
                "filename": store_request.filename,
                "file_path": store_request.filepath,
                "content_type": store_request.file_content_type,
                "file_id": store_request.file_id
            })
        
        # Store in Weaviate
        success = await elysia_service.store_documents(documents, store_request.file_id)
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to store document in Weaviate"
            )
        
        return {
            "message": "Document stored successfully",
            "file_id": store_request.file_id,
            "chunks_created": len(documents)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error storing document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Stats endpoint for compatibility
@router.get("/stats/{project_id}")
async def get_stats(project_id: str):
    """Get statistics for a project (compatibility endpoint)."""
    try:
        count = await elysia_service.get_document_count()
        return {
            "project_id": project_id,
            "document_count": count,
            "vector_store": "weaviate",
            "agent": "elysia"
        }
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
# app/services/elysia_service.py
import weaviate
from elysia import Tree, tool
from typing import List, Dict, Any, Optional
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import (
    WCD_URL, 
    WCD_API_KEY, 
    WEAVIATE_COLLECTION_NAME,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    embeddings,
    logger
)


class ElysiaWeaviateService:
    """Service that combines Elysia agentic capabilities with Weaviate vector storage."""
    
    def __init__(self):
        self.weaviate_client = None
        self.elysia_tree = Tree()
        self._setup_weaviate_connection()
        self._setup_elysia_tools()
        
    def _setup_weaviate_connection(self):
        """Initialize Weaviate client connection."""
        try:
            # Check if we're connecting to local or cloud Weaviate
            if WCD_URL.startswith('http://localhost') or WCD_URL.startswith('http://weaviate'):
                # Local development connection
                self.weaviate_client = weaviate.connect_to_local(
                    host=WCD_URL.replace('http://', '').split(':')[0],
                    port=int(WCD_URL.split(':')[-1]) if ':' in WCD_URL else 8080,
                )
                logger.info("Connected to local Weaviate successfully")
            else:
                # Cloud connection
                self.weaviate_client = weaviate.connect_to_weaviate_cloud(
                    cluster_url=WCD_URL,
                    auth_credentials=weaviate.auth.AuthApiKey(WCD_API_KEY) if WCD_API_KEY else None,
                )
                logger.info("Connected to Weaviate cloud successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Weaviate: {e}")
            raise
            
    def _setup_elysia_tools(self):
        """Setup Elysia tools for document operations."""
        
        @tool(tree=self.elysia_tree)
        async def search_documents(query: str, limit: int = 10) -> List[Dict[str, Any]]:
            """Search for documents in Weaviate using semantic similarity."""
            try:
                collection = self.weaviate_client.collections.get(WEAVIATE_COLLECTION_NAME)
                response = collection.query.near_text(
                    query=query,
                    limit=limit
                )
                
                results = []
                for obj in response.objects:
                    results.append({
                        "content": obj.properties.get("content", ""),
                        "metadata": obj.properties.get("metadata", {}),
                        "distance": obj.metadata.distance if hasattr(obj.metadata, 'distance') else None
                    })
                
                return results
            except Exception as e:
                logger.error(f"Error searching documents: {e}")
                return []
        
        @tool(tree=self.elysia_tree)
        async def get_document_count() -> int:
            """Get the total number of documents in the collection."""
            try:
                collection = self.weaviate_client.collections.get(WEAVIATE_COLLECTION_NAME)
                result = collection.aggregate.over_all(total_count=True)
                return result.total_count or 0
            except Exception as e:
                logger.error(f"Error getting document count: {e}")
                return 0
                
        @tool(tree=self.elysia_tree)
        async def get_all_document_ids() -> List[str]:
            """Retrieve all document IDs from the collection."""
            try:
                collection = self.weaviate_client.collections.get(WEAVIATE_COLLECTION_NAME)
                response = collection.query.fetch_objects(
                    limit=10000,  # Adjust based on your needs
                    return_properties=[]
                )
                
                return [str(obj.uuid) for obj in response.objects]
            except Exception as e:
                logger.error(f"Error getting document IDs: {e}")
                return []
        
        logger.info("Elysia tools setup completed")
    
    async def store_documents(self, documents: List[Document], file_id: str) -> bool:
        """Store documents in Weaviate with chunking."""
        try:
            # Split documents into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=CHUNK_SIZE,
                chunk_overlap=CHUNK_OVERLAP
            )
            
            chunks = text_splitter.split_documents(documents)
            
            # Prepare data for Weaviate
            collection = self.weaviate_client.collections.get(WEAVIATE_COLLECTION_NAME)
            
            data_objects = []
            for i, chunk in enumerate(chunks):
                # Add file_id and chunk info to metadata
                metadata = chunk.metadata.copy()
                metadata.update({
                    "file_id": file_id,
                    "chunk_index": i,
                    "total_chunks": len(chunks)
                })
                
                data_objects.append({
                    "content": chunk.page_content,
                    "metadata": metadata
                })
            
            # Batch insert into Weaviate
            with collection.batch.dynamic() as batch:
                for data_obj in data_objects:
                    batch.add_object(properties=data_obj)
            
            logger.info(f"Stored {len(chunks)} document chunks for file_id: {file_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing documents: {e}")
            return False
    
    async def delete_documents_by_file_id(self, file_id: str) -> bool:
        """Delete all documents associated with a file_id."""
        try:
            collection = self.weaviate_client.collections.get(WEAVIATE_COLLECTION_NAME)
            
            # First, find documents with the file_id
            response = collection.query.fetch_objects(
                where=weaviate.classes.query.Filter.by_property("metadata").contains_any(["file_id", file_id]),
                limit=10000
            )
            
            if not response.objects:
                logger.warning(f"No documents found for file_id: {file_id}")
                return False
            
            # Delete documents by UUID
            uuids_to_delete = [obj.uuid for obj in response.objects]
            collection.data.delete_many(
                where=weaviate.classes.query.Filter.by_id().contains_any(uuids_to_delete)
            )
            
            logger.info(f"Deleted {len(uuids_to_delete)} documents for file_id: {file_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting documents: {e}")
            return False
    
    async def query_with_elysia(self, query: str, collection_names: Optional[List[str]] = None) -> tuple[str, List[Dict[str, Any]]]:
        """Use Elysia's agentic capabilities to query documents."""
        try:
            collection_names = collection_names or [WEAVIATE_COLLECTION_NAME]
            
            # Use Elysia's built-in Weaviate integration
            response, objects = self.elysia_tree(
                query,
                collection_names=collection_names
            )
            
            return response, objects
            
        except Exception as e:
            logger.error(f"Error in Elysia query: {e}")
            return f"Error processing query: {str(e)}", []
    
    async def simple_query(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Simple semantic search without Elysia agent reasoning."""
        try:
            collection = self.weaviate_client.collections.get(WEAVIATE_COLLECTION_NAME)
            response = collection.query.near_text(
                query=query,
                limit=limit
            )
            
            results = []
            for obj in response.objects:
                results.append({
                    "content": obj.properties.get("content", ""),
                    "metadata": obj.properties.get("metadata", {}),
                    "distance": obj.metadata.distance if hasattr(obj.metadata, 'distance') else None
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error in simple query: {e}")
            return []
    
    def close(self):
        """Close Weaviate connection."""
        if self.weaviate_client:
            self.weaviate_client.close()
            logger.info("Weaviate connection closed")


# Global service instance
elysia_service = ElysiaWeaviateService()
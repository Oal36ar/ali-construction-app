import os
import os
import asyncio
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from supabase import create_client, Client
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class SupabaseManager:
    """Manages Supabase interactions for vector embeddings and document storage."""
    
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        self.service_key = os.getenv("SUPABASE_SERVICE_KEY")
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
        
        # Initialize Supabase client (REST API only)
        self.client: Client = create_client(self.supabase_url, self.supabase_key)
        self.vector_dimension = int(os.getenv("VECTOR_DIMENSION", "1536"))
        self.similarity_threshold = float(os.getenv("VECTOR_SIMILARITY_THRESHOLD", "0.7"))
        
        # Test connection and set mode
        self.rest_api_only = self._test_connection()
        
        mode = "REST API only" if self.rest_api_only else "Full PostgreSQL"
        logger.info(f"SupabaseManager initialized with dimension: {self.vector_dimension}, Mode: {mode}")
    
    def _test_connection(self) -> bool:
        """Test Supabase connection and determine if we should use REST API only.
        
        Returns:
            True if should use REST API only, False if full PostgreSQL is available
        """
        try:
            # Try a simple query to test the connection
            result = self.client.table("document_embeddings").select("id").limit(1).execute()
            logger.info("Supabase connection test successful - using full functionality")
            return False  # Full PostgreSQL connection works
        except Exception as e:
            logger.warning(f"PostgreSQL connection failed, using REST API only: {str(e)}")
            return True  # Use REST API only mode
    
    async def store_embedding(
        self,
        content: str,
        embedding: List[float],
        metadata: Dict[str, Any],
        document_id: Optional[str] = None,
        chunk_index: int = 0
    ) -> str:
        """Store document embedding in Supabase.
        
        Args:
            content: The text content
            embedding: The vector embedding
            metadata: Additional metadata (file_name, file_type, etc.)
            document_id: Optional document identifier
            chunk_index: Index of the chunk within the document
            
        Returns:
            The ID of the stored embedding
        """
        try:
            # Validate embedding dimension
            if len(embedding) != self.vector_dimension:
                raise ValueError(f"Embedding dimension {len(embedding)} doesn't match expected {self.vector_dimension}")
            
            # Prepare data for insertion
            data = {
                "content": content,
                "embedding": embedding,
                "metadata": metadata,
                "document_id": document_id,
                "chunk_index": chunk_index,
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Insert into Supabase
            result = self.client.table("document_embeddings").insert(data).execute()
            
            if result.data:
                embedding_id = result.data[0]["id"]
                logger.info(f"Successfully stored embedding with ID: {embedding_id}")
                return embedding_id
            else:
                raise Exception("No data returned from insert operation")
                
        except Exception as e:
            logger.error(f"Error storing embedding: {str(e)}")
            raise
    
    async def similarity_search(
        self,
        query_embedding: List[float],
        limit: int = 5,
        similarity_threshold: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """Perform similarity search using pgvector or fallback method.
        
        Args:
            query_embedding: The query vector
            limit: Maximum number of results to return
            similarity_threshold: Minimum similarity score (uses default if None)
            
        Returns:
            List of similar documents with metadata and similarity scores
        """
        try:
            # Use provided threshold or default
            threshold = similarity_threshold or self.similarity_threshold
            
            # Validate embedding dimension
            if len(query_embedding) != self.vector_dimension:
                raise ValueError(f"Query embedding dimension {len(query_embedding)} doesn't match expected {self.vector_dimension}")
            
            if self.rest_api_only:
                # Fallback: Get all embeddings and compute similarity in Python
                return await self._similarity_search_fallback(query_embedding, limit, threshold)
            else:
                # Use the RPC function for similarity search
                result = self.client.rpc(
                    "match_documents",
                    {
                        "query_embedding": query_embedding,
                        "match_threshold": threshold,
                        "match_count": limit
                    }
                ).execute()
                
                if result.data:
                    logger.info(f"Found {len(result.data)} similar documents")
                    return result.data
                else:
                    logger.info("No similar documents found")
                    return []
                
        except Exception as e:
            logger.error(f"Error performing similarity search: {str(e)}")
            if not self.rest_api_only:
                # If RPC fails, try fallback method
                logger.info("Falling back to Python-based similarity search")
                return await self._similarity_search_fallback(query_embedding, limit, threshold)
            raise
    
    async def _similarity_search_fallback(
        self,
        query_embedding: List[float],
        limit: int,
        threshold: float
    ) -> List[Dict[str, Any]]:
        """Fallback similarity search using Python computation.
        
        Args:
            query_embedding: The query vector
            limit: Maximum number of results to return
            threshold: Minimum similarity score
            
        Returns:
            List of similar documents with metadata and similarity scores
        """
        try:
            # Get all embeddings from the database
            result = self.client.table("document_embeddings").select("*").execute()
            
            if not result.data:
                logger.info("No embeddings found in database")
                return []
            
            # Compute similarities
            similarities = []
            query_vector = np.array(query_embedding)
            
            for item in result.data:
                if item.get("embedding"):
                    doc_vector = np.array(item["embedding"])
                    # Compute cosine similarity
                    similarity = np.dot(query_vector, doc_vector) / (
                        np.linalg.norm(query_vector) * np.linalg.norm(doc_vector)
                    )
                    
                    if similarity >= threshold:
                        similarities.append({
                            **item,
                            "similarity": float(similarity)
                        })
            
            # Sort by similarity and limit results
            similarities.sort(key=lambda x: x["similarity"], reverse=True)
            results = similarities[:limit]
            
            logger.info(f"Found {len(results)} similar documents using fallback method")
            return results
            
        except Exception as e:
            logger.error(f"Error in fallback similarity search: {str(e)}")
            return []
    
    async def get_document_embeddings(
        self,
        document_id: str
    ) -> List[Dict[str, Any]]:
        """Get all embeddings for a specific document.
        
        Args:
            document_id: The document identifier
            
        Returns:
            List of embeddings for the document
        """
        try:
            result = self.client.table("document_embeddings").select("*").eq("document_id", document_id).execute()
            
            if result.data:
                logger.info(f"Found {len(result.data)} embeddings for document {document_id}")
                return result.data
            else:
                logger.info(f"No embeddings found for document {document_id}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting document embeddings: {str(e)}")
            raise
    
    async def delete_document_embeddings(
        self,
        document_id: str
    ) -> bool:
        """Delete all embeddings for a specific document.
        
        Args:
            document_id: The document identifier
            
        Returns:
            True if successful, False otherwise
        """
        try:
            result = self.client.table("document_embeddings").delete().eq("document_id", document_id).execute()
            
            logger.info(f"Deleted embeddings for document {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting document embeddings: {str(e)}")
            return False
    
    async def get_embedding_stats(self) -> Dict[str, Any]:
        """Get statistics about stored embeddings.
        
        Returns:
            Dictionary with embedding statistics
        """
        try:
            # Get total count
            count_result = self.client.table("document_embeddings").select("id", count="exact").execute()
            total_embeddings = count_result.count if count_result.count else 0
            
            # Get unique documents count
            docs_result = self.client.table("document_embeddings").select("document_id").execute()
            unique_documents = len(set(item["document_id"] for item in docs_result.data if item["document_id"]))
            
            # Get file types distribution
            metadata_result = self.client.table("document_embeddings").select("metadata").execute()
            file_types = {}
            for item in metadata_result.data:
                if item["metadata"] and "file_type" in item["metadata"]:
                    file_type = item["metadata"]["file_type"]
                    file_types[file_type] = file_types.get(file_type, 0) + 1
            
            stats = {
                "total_embeddings": total_embeddings,
                "unique_documents": unique_documents,
                "file_types_distribution": file_types,
                "vector_dimension": self.vector_dimension,
                "similarity_threshold": self.similarity_threshold
            }
            
            logger.info(f"Embedding stats: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Error getting embedding stats: {str(e)}")
            return {
                "total_embeddings": 0,
                "unique_documents": 0,
                "file_types_distribution": {},
                "vector_dimension": self.vector_dimension,
                "similarity_threshold": self.similarity_threshold,
                "error": str(e)
            }
    
    def test_connection(self) -> bool:
        """Test the connection to Supabase.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            # Simple query to test connection
            result = self.client.table("document_embeddings").select("id").limit(1).execute()
            logger.info("Supabase connection test successful")
            return True
        except Exception as e:
            logger.error(f"Supabase connection test failed: {str(e)}")
            return False
    
    def test_basic_connection(self) -> bool:
        """Test basic Supabase client creation without database queries.
        
        Returns:
            True if client can be created, False otherwise
        """
        try:
            # Just test that we can create a client with the provided credentials
            test_client = create_client(self.supabase_url, self.supabase_key)
            logger.info("Supabase client creation successful")
            return True
        except Exception as e:
            logger.error(f"Supabase client creation failed: {str(e)}")
            return False

# Global instance
_supabase_manager = None

def get_supabase_manager() -> SupabaseManager:
    """Get or create the global SupabaseManager instance."""
    global _supabase_manager
    if _supabase_manager is None:
        _supabase_manager = SupabaseManager()
    return _supabase_manager
import os
import logging
from typing import List, Dict, Any, Optional
import asyncio
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from utils.supabase_manager import get_supabase_manager
from utils.embedding_manager import EmbeddingManager

logger = logging.getLogger(__name__)

class EnhancedEmbeddingManager:
    """
    Enhanced embedding manager that integrates with Supabase for persistent storage
    and provides advanced search capabilities.
    """
    
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.vector_dimension = 1536  # OpenAI ada-002 dimension
        
        # Initialize components
        self.embeddings = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        
        # Initialize Supabase manager
        try:
            self.supabase = get_supabase_manager()
            logger.info("Enhanced embedding manager initialized with Supabase")
        except Exception as e:
            logger.warning(f"Supabase initialization failed, falling back to local: {e}")
            self.supabase = None
        
        # Fallback to local embedding manager if Supabase fails
        try:
            self.local_embedding_manager = EmbeddingManager()
            logger.info("Local embedding manager initialized as fallback")
        except Exception as e:
            logger.error(f"Failed to initialize local embedding manager: {e}")
            self.local_embedding_manager = None
        
        # Initialize OpenAI embeddings if API key is available
        if self.openai_api_key:
            try:
                self.embeddings = OpenAIEmbeddings(
                    openai_api_key=self.openai_api_key,
                    model="text-embedding-ada-002"
                )
                logger.info("OpenAI embeddings initialized")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI embeddings: {e}")
        else:
            logger.warning("No OpenAI API key found, embedding functionality limited")
    
    def is_available(self) -> bool:
        """Check if embedding functionality is available"""
        return self.embeddings is not None
    
    @property
    def vector_store(self):
        """Get vector store from local embedding manager for compatibility"""
        if self.local_embedding_manager:
            return self.local_embedding_manager.vector_store
        return None
    
    async def embed_file_content(self, content: str, filename: str, file_type: str) -> bool:
        """
        Create embedding and store in Supabase or local storage.
        """
        try:
            if not self.embeddings:
                logger.error("No embedding model available")
                return False
            
            # Split content into chunks
            chunks = self.text_splitter.split_text(content)
            logger.info(f"Split {filename} into {len(chunks)} chunks")
            
            # Try Supabase first, then fallback to local
            if self.supabase:
                success = await self._store_in_supabase(chunks, filename, file_type)
                if success:
                    return True
                logger.warning("Supabase storage failed, falling back to local")
            
            # Fallback to local storage
            if self.local_embedding_manager:
                return await self._store_locally(chunks, filename)
            
            logger.error("No storage backend available")
            return False
            
        except Exception as e:
            logger.error(f"Failed to embed file content: {str(e)}")
            return False
    
    async def _store_in_supabase(self, chunks: List[str], filename: str, file_type: str) -> bool:
        """
        Store chunks in Supabase with embeddings.
        """
        try:
            for i, chunk in enumerate(chunks):
                # Create embedding
                embedding = await asyncio.to_thread(
                    self.embeddings.embed_query, chunk
                )
                
                # Store in Supabase
                embedding_id = await self.supabase.store_embedding(
                    content=chunk,
                    embedding=embedding,
                    metadata={
                        "filename": filename,
                        "file_type": file_type,
                        "chunk_index": i,
                        "total_chunks": len(chunks)
                    }
                )
                
                if not embedding_id:
                    logger.error(f"Failed to store chunk {i} in Supabase")
                    return False
            
            logger.info(f"Successfully stored {len(chunks)} chunks in Supabase")
            return True
            
        except Exception as e:
            logger.error(f"Supabase storage error: {str(e)}")
            return False
    
    async def _store_locally(self, chunks: List[str], filename: str) -> bool:
        """
        Store chunks in local FAISS index.
        """
        try:
            # Use the existing local embedding manager
            full_content = "\n\n".join(chunks)
            success, chunk_metadata = await asyncio.to_thread(
                self.local_embedding_manager.embed_file_content,
                full_content,
                filename
            )
            
            # Save the vector store to persist the data
            if success:
                logger.info(f"Attempting to save vector store for {filename}")
                save_success = await asyncio.to_thread(
                    self.local_embedding_manager.save_vector_store,
                    "vector_store"
                )
                if save_success:
                    logger.info(f"Vector store saved successfully after embedding {filename}")
                else:
                    logger.error(f"Failed to save vector store for {filename}")
            
            return success
        except Exception as e:
            logger.error(f"Local storage error: {str(e)}")
            return False
    
    async def search_memory(
        self, 
        query: str, 
        limit: int = 5, 
        similarity_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Search through stored memories using semantic similarity.
        """
        try:
            if not self.embeddings:
                logger.error("No embedding model available for search")
                return []
            
            # Create query embedding
            query_embedding = await asyncio.to_thread(
                self.embeddings.embed_query, query
            )
            
            # Try Supabase first
            if self.supabase:
                results = await self.supabase.similarity_search(
                    query_embedding=query_embedding,
                    limit=limit,
                    similarity_threshold=similarity_threshold
                )
                if results:
                    return self._format_search_results(results)
                logger.warning("Supabase search failed, falling back to local")
            
            # Fallback to local search
            if self.local_embedding_manager:
                local_results = self.local_embedding_manager.get_retrieval_context(query)
                return self._format_local_results(local_results, query)
            
            logger.error("No search backend available")
            return []
            
        except Exception as e:
            logger.error(f"Memory search failed: {str(e)}")
            return []
    
    def _format_search_results(self, results: List[Dict]) -> List[Dict[str, Any]]:
        """
        Format Supabase search results.
        """
        formatted = []
        for result in results:
            formatted.append({
                "content": result.get("content", ""),
                "filename": result.get("metadata", {}).get("filename", "unknown"),
                "similarity_score": result.get("similarity", 0.0),
                "metadata": result.get("metadata", {})
            })
        return formatted
    
    def _format_local_results(self, local_results: str, query: str) -> List[Dict[str, Any]]:
        """
        Format local search results.
        """
        if not local_results or local_results.strip() == "No relevant context found.":
            return []
        
        # Simple formatting for local results
        return [{
            "content": local_results,
            "filename": "local_storage",
            "similarity_score": 0.8,  # Default score for local results
            "metadata": {"source": "local_faiss", "query": query}
        }]
    
    def get_retrieval_context(self, query: str, max_chunks: int = 3) -> str:
        """
        Get relevant context for a query to enhance chat responses
        
        Args:
            query: User query
            max_chunks: Maximum number of chunks to include
            
        Returns:
            Formatted context string
        """
        if not self.is_available():
            return ""
        
        try:
            # Use local embedding manager for synchronous retrieval
            if self.local_embedding_manager and self.local_embedding_manager.is_available():
                return self.local_embedding_manager.get_retrieval_context(query, max_chunks)
            else:
                return ""
            
        except Exception as e:
            logger.error(f"Error getting retrieval context: {e}")
            return ""
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about stored documents.
        """
        stats = {
            "backend": "enhanced",
            "supabase_available": self.supabase is not None,
            "local_available": self.local_embedding_manager is not None,
            "openai_available": self.embeddings is not None
        }
        
        # Get Supabase stats if available
        if self.supabase:
            try:
                import asyncio
                supabase_stats = asyncio.run(self.supabase.get_embedding_stats())
                stats["supabase_stats"] = supabase_stats
            except Exception as e:
                stats["supabase_error"] = str(e)
        
        # Get local stats if available
        if self.local_embedding_manager:
            try:
                local_stats = self.local_embedding_manager.get_stats()
                stats["local_stats"] = local_stats
            except Exception as e:
                stats["local_error"] = str(e)
        
        return stats

# Global instance
_enhanced_embedding_manager = None

def get_enhanced_embedding_manager() -> EnhancedEmbeddingManager:
    """
    Get or create the global EnhancedEmbeddingManager instance.
    """
    global _enhanced_embedding_manager
    if _enhanced_embedding_manager is None:
        _enhanced_embedding_manager = EnhancedEmbeddingManager()
    return _enhanced_embedding_manager

# Create global instance for direct import
enhanced_embedding_manager = get_enhanced_embedding_manager()
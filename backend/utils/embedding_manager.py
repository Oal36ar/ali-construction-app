"""
Embedding Manager for File-based Chat
Handles text chunking, embedding generation, and retrieval using LangChain and FAISS
"""

import os
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import json

try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain_openai import OpenAIEmbeddings
    from langchain_community.vectorstores import FAISS
    from langchain.schema import Document
    EMBEDDING_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Embedding dependencies not available: {e}")
    EMBEDDING_AVAILABLE = False

class EmbeddingManager:
    """
    Manages file content embedding and retrieval for enhanced chat context
    """
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """
        Initialize embedding manager
        
        Args:
            openai_api_key: OpenAI API key for embeddings (fallback to env var)
        """
        self.embeddings = None
        self.vector_store = None
        self.text_splitter = None
        self.chunks_metadata = []
        
        if not EMBEDDING_AVAILABLE:
            print("⚠️ Embedding functionality disabled - missing dependencies")
            return
        
        try:
            # Initialize OpenAI embeddings
            api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
            if not api_key:
                print("⚠️ No OpenAI API key found - embedding functionality disabled")
                return
                
            self.embeddings = OpenAIEmbeddings(openai_api_key=api_key)
            
            # Initialize text splitter
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len,
                separators=["\n\n", "\n", " ", ""]
            )
            
            print("✅ EmbeddingManager initialized successfully")
            
        except Exception as e:
            print(f"❌ Failed to initialize EmbeddingManager: {e}")
            self.embeddings = None

    def is_available(self) -> bool:
        """Check if embedding functionality is available"""
        return EMBEDDING_AVAILABLE and self.embeddings is not None

    def create_chunks(self, text: str, source: str = "uploaded_file") -> List[Dict[str, Any]]:
        """
        Split text into chunks for embedding
        
        Args:
            text: Raw text content to split
            source: Source identifier (filename)
            
        Returns:
            List of chunk dictionaries with metadata
        """
        if not self.is_available():
            return []
        
        try:
            # Split text into chunks
            chunks = self.text_splitter.split_text(text)
            
            # Create chunk metadata
            chunk_data = []
            for i, chunk in enumerate(chunks):
                chunk_info = {
                    "content": chunk,
                    "source": source,
                    "chunk_index": i,
                    "created_at": datetime.now().isoformat(),
                    "metadata": {
                        "length": len(chunk),
                        "source_file": source,
                        "chunk_id": f"{source}_{i}"
                    }
                }
                chunk_data.append(chunk_info)
            
            print(f"✅ Created {len(chunk_data)} chunks from {source}")
            return chunk_data
            
        except Exception as e:
            print(f"❌ Error creating chunks: {e}")
            return []

    def embed_chunks(self, chunks: List[Dict[str, Any]]) -> bool:
        """
        Create embeddings for text chunks and store in FAISS
        
        Args:
            chunks: List of chunk dictionaries from create_chunks
            
        Returns:
            bool: Success status
        """
        if not self.is_available() or not chunks:
            return False
        
        try:
            # Convert chunks to LangChain Documents
            documents = []
            for chunk in chunks:
                doc = Document(
                    page_content=chunk["content"],
                    metadata=chunk["metadata"]
                )
                documents.append(doc)
            
            # Create or update FAISS vector store
            if self.vector_store is None:
                self.vector_store = FAISS.from_documents(documents, self.embeddings)
                print(f"✅ Created new FAISS vector store with {len(documents)} documents")
            else:
                # Add new documents to existing store
                self.vector_store.add_documents(documents)
                print(f"✅ Added {len(documents)} documents to existing vector store")
            
            # Store metadata
            self.chunks_metadata.extend(chunks)
            
            return True
            
        except Exception as e:
            print(f"❌ Error embedding chunks: {e}")
            return False

    def embed_file_content(self, text: str, filename: str) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Complete pipeline: chunk text, create embeddings, and store
        
        Args:
            text: File content to embed
            filename: Source filename
            
        Returns:
            Tuple of (success, chunk_metadata)
        """
        if not self.is_available():
            return False, []
        
        try:
            # Create chunks
            chunks = self.create_chunks(text, filename)
            if not chunks:
                return False, []
            
            # Embed chunks
            success = self.embed_chunks(chunks)
            
            if success:
                print(f"✅ Successfully embedded file content: {filename}")
                return True, chunks
            else:
                return False, []
                
        except Exception as e:
            print(f"❌ Error in embed_file_content: {e}")
            return False, []

    def search_similar(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """
        Search for similar content using semantic similarity
        
        Args:
            query: Search query
            k: Number of results to return
            
        Returns:
            List of similar chunks with metadata
        """
        if not self.is_available() or self.vector_store is None:
            return []
        
        try:
            # Perform similarity search
            results = self.vector_store.similarity_search_with_score(query, k=k)
            
            # Format results
            similar_chunks = []
            for doc, score in results:
                chunk_info = {
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "similarity_score": float(score),
                    "source": doc.metadata.get("source_file", "unknown")
                }
                similar_chunks.append(chunk_info)
            
            print(f"✅ Found {len(similar_chunks)} similar chunks for query")
            return similar_chunks
            
        except Exception as e:
            print(f"❌ Error searching similar content: {e}")
            return []

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
        
        similar_chunks = self.search_similar(query, k=max_chunks)
        
        if not similar_chunks:
            return ""
        
        # Format context
        context_parts = ["=== RELEVANT FILE CONTEXT ===\n"]
        
        for i, chunk in enumerate(similar_chunks, 1):
            source = chunk["metadata"].get("source_file", "unknown")
            score = chunk["similarity_score"]
            content = chunk["content"]
            
            context_parts.append(f"[Context {i} from {source} (similarity: {score:.3f})]")
            context_parts.append(content)
            context_parts.append("")
        
        context_parts.append("=== END FILE CONTEXT ===\n")
        
        return "\n".join(context_parts)

    def save_vector_store(self, path: str) -> bool:
        """
        Save FAISS vector store to disk
        
        Args:
            path: Directory path to save the store
            
        Returns:
            bool: Success status
        """
        if not self.is_available() or self.vector_store is None:
            return False
        
        try:
            os.makedirs(path, exist_ok=True)
            self.vector_store.save_local(path)
            
            # Save metadata
            metadata_path = os.path.join(path, "chunks_metadata.json")
            with open(metadata_path, 'w') as f:
                json.dump(self.chunks_metadata, f, indent=2)
            
            print(f"✅ Vector store saved to {path}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving vector store: {e}")
            return False

    def load_vector_store(self, path: str) -> bool:
        """
        Load FAISS vector store from disk
        
        Args:
            path: Directory path to load the store from
            
        Returns:
            bool: Success status
        """
        if not self.is_available():
            return False
        
        try:
            if not os.path.exists(path):
                print(f"⚠️ Vector store path does not exist: {path}")
                return False
            
            self.vector_store = FAISS.load_local(path, self.embeddings)
            
            # Load metadata
            metadata_path = os.path.join(path, "chunks_metadata.json")
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r') as f:
                    self.chunks_metadata = json.load(f)
            
            print(f"✅ Vector store loaded from {path}")
            return True
            
        except Exception as e:
            print(f"❌ Error loading vector store: {e}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the current vector store
        
        Returns:
            Dictionary with statistics
        """
        stats = {
            "available": self.is_available(),
            "total_chunks": len(self.chunks_metadata),
            "has_vector_store": self.vector_store is not None,
            "sources": []
        }
        
        if self.chunks_metadata:
            sources = set()
            for chunk in self.chunks_metadata:
                sources.add(chunk.get("source", "unknown"))
            stats["sources"] = list(sources)
            stats["unique_sources"] = len(sources)
        
        return stats

# Global instance
embedding_manager = EmbeddingManager() 
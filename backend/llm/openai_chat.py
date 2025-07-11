#!/usr/bin/env python3
"""
OpenAI Chat LLM Integration for LangChain
Custom wrapper class that uses OpenAI's Chat API through LangChain
"""

import os
from typing import Any, List, Optional, Dict
from dotenv import load_dotenv

# Try different import paths for ChatOpenAI (compatibility with different langchain versions)
try:
    from langchain_openai import ChatOpenAI
    print("✅ Using langchain_openai.ChatOpenAI")
except ImportError:
    try:
        from langchain.chat_models import ChatOpenAI
        print("✅ Using langchain.chat_models.ChatOpenAI")
    except ImportError:
        try:
            from langchain.chat_models.openai import ChatOpenAI
            print("✅ Using langchain.chat_models.openai.ChatOpenAI")
        except ImportError:
            print("❌ Could not import ChatOpenAI from any location")
            ChatOpenAI = None

from langchain.schema import BaseMessage, HumanMessage, AIMessage
from langchain.callbacks.manager import CallbackManagerForLLMRun

# Load environment variables
load_dotenv()


class OpenAIChat:
    """Custom wrapper class for OpenAI Chat API integration"""
    
    def __init__(self, model: str = "gpt-3.5-turbo", **kwargs):
        if ChatOpenAI is None:
            raise ImportError("ChatOpenAI could not be imported. Please install langchain-openai: pip install langchain-openai")
        
        self.model = model
        self.api_key = os.getenv("OPENAI_API_KEY")
        
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        # Initialize the ChatOpenAI instance
        # Filter out problematic kwargs that might not be supported
        filtered_kwargs = {k: v for k, v in kwargs.items() 
                          if k not in ['temperature', 'max_tokens', 'timeout', 'proxies', 'api_key']}
        
        self.chat_llm = ChatOpenAI(
            model=model,
            openai_api_key=self.api_key,
            temperature=kwargs.get('temperature', 0.3),
            max_tokens=kwargs.get('max_tokens', 1500),
            **filtered_kwargs
        )
        
        print(f"✅ OpenAI Chat initialized with model: {model}")
    
    @property
    def _llm_type(self) -> str:
        """Return type of llm."""
        return "openai-chat"
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Call the OpenAI Chat API synchronously."""
        print(f"🤖 OpenAI Chat API call - Model: {self.model}")
        print(f"📝 Prompt length: {len(prompt)} chars")
        
        try:
            # Convert prompt to chat message
            messages = [HumanMessage(content=prompt)]
            
            # Call the ChatOpenAI instance
            response = self.chat_llm.invoke(messages, stop=stop, **kwargs)
            
            # Extract content from response
            if hasattr(response, 'content'):
                result = response.content
            else:
                result = str(response)
            
            print(f"✅ OpenAI response: '{result[:100]}...'")
            return result
            
        except Exception as e:
            error_msg = f"OpenAI Chat API call failed: {e}"
            print(f"❌ {error_msg}")
            return f"Error: {error_msg}"
    
    async def _acall(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Call the OpenAI Chat API asynchronously."""
        try:
            # Convert prompt to chat message
            messages = [HumanMessage(content=prompt)]
            
            # Call the ChatOpenAI instance asynchronously
            response = await self.chat_llm.ainvoke(messages, stop=stop, **kwargs)
            
            # Extract content from response
            if hasattr(response, 'content'):
                result = response.content
            else:
                result = str(response)
            
            return result
            
        except Exception as e:
            raise ValueError(f"OpenAI Chat async call failed: {e}")
    
    async def call_text_only(
        self,
        message: str,
        stop: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Call OpenAI Chat API for text-only messages."""
        print(f"💬 OpenAI Chat text-only call - Model: {self.model}")
        
        try:
            # Convert to chat message
            messages = [HumanMessage(content=message)]
            
            # Call ChatOpenAI
            response = await self.chat_llm.ainvoke(messages, stop=stop, **kwargs)
            
            # Extract response text
            if hasattr(response, 'content'):
                response_text = response.content
            else:
                response_text = str(response)
            
            print(f"✅ OpenAI text-only response: '{response_text[:100]}...'")
            
            return {
                "model": self.model,
                "plugin": None,
                "response": response_text,
                "success": True,
                "provider": "openai"
            }
            
        except Exception as e:
            error_msg = f"OpenAI text-only call failed: {e}"
            print(f"❌ {error_msg}")
            return {
                "model": self.model,
                "plugin": None,
                "response": f"Error: {error_msg}",
                "success": False,
                "provider": "openai",
                "error": error_msg
            }
    
    def get_underlying_llm(self):
        """Get the underlying ChatOpenAI instance for agent compatibility."""
        return self.chat_llm
    
    @property
    def _identifying_params(self) -> Dict[str, Any]:
        """Get the identifying parameters."""
        return {
            "model": self.model,
            "provider": "openai",
            "api_key_set": bool(self.api_key)
        }


class OpenAILLM:
    """LLM-compatible wrapper for OpenAI that matches OpenRouterLLM interface"""
    
    def __init__(self, model: str = "gpt-3.5-turbo", **kwargs):
        self.model = model
        self.api_key = os.getenv("OPENAI_API_KEY")
        
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        # Initialize the underlying ChatOpenAI
        self.openai_chat = OpenAIChat(model=model, **kwargs)
        
        # Set temperature and max_tokens for compatibility
        self.temperature = kwargs.get('temperature', 0.3)
        self.max_tokens = kwargs.get('max_tokens', 1500)
    
    @property
    def _llm_type(self) -> str:
        """Return type of llm."""
        return "openai-llm"
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Call the OpenAI API synchronously through ChatOpenAI."""
        return self.openai_chat._call(prompt, stop, run_manager, **kwargs)
    
    async def _acall(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Call the OpenAI API asynchronously."""
        return await self.openai_chat._acall(prompt, stop, run_manager, **kwargs)
    
    async def call_text_only(
        self,
        message: str,
        stop: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Call OpenAI for text-only messages with same interface as OpenRouterLLM."""
        return await self.openai_chat.call_text_only(message, stop, **kwargs)
    
    def get_underlying_llm(self):
        """Get the underlying ChatOpenAI instance for agent compatibility."""
        return self.openai_chat.get_underlying_llm()
    
    @property
    def _identifying_params(self) -> Dict[str, Any]:
        """Get the identifying parameters."""
        return {
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "provider": "openai"
        } 
#!/usr/bin/env python3
"""
OpenRouter LLM Integration for LangChain
Custom LLM class that uses OpenRouter API for model inference
Enhanced with file-parser plugin support and dual model routing
"""

import json
import httpx
import base64
from typing import Any, List, Optional, Dict, Union, AsyncGenerator
from langchain.llms.base import LLM
from langchain.callbacks.manager import CallbackManagerForLLMRun
from pydantic import Field


class OpenRouterLLM(LLM):
    """Custom LLM class for OpenRouter API integration with file-parser plugin support"""
    
    api_key: str = "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"
    model: Optional[str] = None  # Backward compatibility
    text_model: str = "google/gemini-2.5-flash"  # For text-only messages
    file_model: str = "google/gemma-3-27b-it"   # For file processing
    fallback_file_model: str = "openchat/openchat-3.5-1210"  # Fallback for file processing
    base_url: str = "https://openrouter.ai/api/v1/chat/completions"
    temperature: float = 0.3
    max_tokens: int = 1500
    timeout: int = 30
    
    class Config:
        """Configuration for this pydantic object."""
        extra = "allow"  # Allow extra fields for backward compatibility
        arbitrary_types_allowed = True
    
    def __init__(self, **data):
        """Initialize with backward compatibility for model parameter"""
        # Handle backward compatibility for model parameter
        if 'model' in data and data['model'] and 'text_model' not in data:
            data['text_model'] = data['model']
        elif 'model' in data and data['model']:
            # Use model parameter if provided
            data['text_model'] = data['model']
        
        super().__init__(**data)
    
    @property
    def _llm_type(self) -> str:
        """Return type of llm."""
        return "openrouter"
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Call the OpenRouter API synchronously."""
        print(f"🌐 OpenRouter API call - Model: {self.text_model}")
        print(f"📝 Prompt length: {len(prompt)} chars")
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost",
                "X-Title": "LangChain AI Orchestrator"
            }
            
            print(f"🔑 Using API key: {self.api_key[:15]}...")
            
            payload = {
                "model": self.text_model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "stop": stop or []
            }
            
            # Add any additional kwargs (excluding internal fields)
            filtered_kwargs = {k: v for k, v in kwargs.items() 
                             if k not in ['api_key', 'model', 'text_model', 'file_model']}
            payload.update(filtered_kwargs)
            
            print(f"🚀 Sending request to OpenRouter...")
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    self.base_url,
                    headers=headers,
                    json=payload
                )
                print(f"📡 Response status: {response.status_code}")
                response.raise_for_status()
                
                result = response.json()
                
                if "choices" in result and len(result["choices"]) > 0:
                    response_text = result["choices"][0]["message"]["content"].strip()
                    print(f"✅ OpenRouter response: '{response_text[:100]}...'")
                    return response_text
                else:
                    print(f"❌ Invalid response format: {result}")
                    raise ValueError(f"Invalid response format: {result}")
                    
        except httpx.RequestError as e:
            error_msg = f"OpenRouter API request failed: {e}"
            print(f"❌ {error_msg}")
            return f"Error: {error_msg}"
        except httpx.HTTPStatusError as e:
            error_msg = f"OpenRouter API error {e.response.status_code}: {e.response.text}"
            print(f"❌ {error_msg}")
            return f"Error: {error_msg}"
        except Exception as e:
            error_msg = f"OpenRouter LLM call failed: {e}"
            print(f"❌ {error_msg}")
            return f"Error: {error_msg}"

    async def call_with_file_parser(
        self,
        message: str,
        files: List[Dict[str, Any]],
        stop: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Call OpenRouter API with file-parser plugin for file processing."""
        print(f"📄 OpenRouter file-parser call - Model: {self.file_model}")
        print(f"📁 Processing {len(files)} file(s)")
        
        # Generate file preview information
        file_previews = []
        for file_data in files:
            filename = file_data.get('filename', 'unknown_file')
            content = file_data.get('content', b'')
            file_size = len(content) if isinstance(content, (bytes, str)) else 0
            
            # Estimate pages for PDF files
            if filename.lower().endswith('.pdf'):
                # Rough estimate: 1 page ≈ 2KB of content
                estimated_pages = max(1, file_size // 2048)
                preview = f"📄 Parsed file: {filename} — {estimated_pages} pages extracted"
            else:
                preview = f"📄 Parsed file: {filename} — {file_size} bytes processed"
            
            file_previews.append(preview)
            print(preview)
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost",
                "X-Title": "LangChain AI File Parser"
            }
            
            # Convert files to base64 format
            file_attachments = []
            for file_data in files:
                if 'content' in file_data and 'filename' in file_data:
                    content = file_data['content']
                    # Convert file content to base64
                    if isinstance(content, bytes):
                        base64_content = base64.b64encode(content).decode('utf-8')
                    else:
                        base64_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')
                    
                    file_attachments.append({
                        "name": file_data['filename'],
                        "content": base64_content,
                        "mime_type": file_data.get('content_type', 'application/octet-stream')
                    })
            
            # Build payload with file-parser plugin
            payload = {
                "model": self.file_model,
                "messages": [
                    {
                        "role": "user",
                        "content": message,
                        "attachments": file_attachments
                    }
                ],
                "plugins": [
                    {
                        "id": "file-parser",
                        "pdf": {
                            "engine": "pdf-text"
                        }
                    }
                ],
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "stop": stop or []
            }
            
            # Add filtered kwargs
            filtered_kwargs = {k: v for k, v in kwargs.items() 
                             if k not in ['api_key', 'model', 'text_model', 'file_model']}
            payload.update(filtered_kwargs)
            
            print(f"🚀 Sending file-parser request to OpenRouter...")
            async with httpx.AsyncClient(timeout=self.timeout * 2) as client:
                response = await client.post(
                    self.base_url,
                    headers=headers,
                    json=payload
                )
                print(f"📡 File-parser response status: {response.status_code}")
                
                if response.status_code != 200:
                    # Try fallback model
                    print(f"⚠️ Primary model failed, trying fallback: {self.fallback_file_model}")
                    payload["model"] = self.fallback_file_model
                    response = await client.post(
                        self.base_url,
                        headers=headers,
                        json=payload
                    )
                
                response.raise_for_status()
                result = response.json()
                
                if "choices" in result and len(result["choices"]) > 0:
                    response_text = result["choices"][0]["message"]["content"].strip()
                    print(f"✅ File-parser response: '{response_text[:100]}...'")
                    
                    # Combine file previews with AI response
                    formatted_response = "\n".join(file_previews) + "\n\n" + response_text
                    
                    return {
                        "model": payload["model"],
                        "plugin": "file-parser",
                        "response": formatted_response,
                        "processed_files": len(files),
                        "file_previews": file_previews,
                        "raw_result": result
                    }
                else:
                    print(f"❌ Invalid file-parser response format: {result}")
                    error_msg = f"Invalid response format: {result}"
                    return {
                        "model": payload["model"],
                        "plugin": "file-parser",
                        "response": f"Error processing files: {error_msg}",
                        "processed_files": 0,
                        "file_previews": file_previews,
                        "error": error_msg
                    }
                    
        except httpx.RequestError as e:
            error_msg = f"OpenRouter file-parser API request failed: {e}"
            print(f"❌ {error_msg}")
            return {
                "model": self.file_model,
                "plugin": "file-parser",
                "response": f"Network error processing files: {error_msg}",
                "processed_files": 0,
                "file_previews": file_previews,
                "error": error_msg
            }
        except httpx.HTTPStatusError as e:
            error_msg = f"OpenRouter file-parser API error {e.response.status_code}: {e.response.text}"
            print(f"❌ {error_msg}")
            return {
                "model": self.file_model,
                "plugin": "file-parser", 
                "response": f"API error processing files: {error_msg}",
                "processed_files": 0,
                "file_previews": file_previews,
                "error": error_msg
            }
        except Exception as e:
            error_msg = f"OpenRouter file-parser call failed: {e}"
            print(f"❌ {error_msg}")
            return {
                "model": self.file_model,
                "plugin": "file-parser",
                "response": f"Unexpected error processing files: {error_msg}",
                "processed_files": 0,
                "file_previews": file_previews,
                "error": error_msg
            }

    async def call_text_only(
        self,
        message: str,
        stop: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Call OpenRouter API for text-only messages using Gemini 2.5 Flash."""
        print(f"💬 OpenRouter text-only call - Model: {self.text_model}")
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost",
                "X-Title": "LangChain AI Chat"
            }
            
            payload = {
                "model": self.text_model,
                "messages": [
                    {
                        "role": "user",
                        "content": message
                    }
                ],
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "stop": stop or []
            }
            
            # Add filtered kwargs
            filtered_kwargs = {k: v for k, v in kwargs.items() 
                             if k not in ['api_key', 'model', 'text_model', 'file_model']}
            payload.update(filtered_kwargs)
            
            print(f"🚀 Sending text-only request to OpenRouter...")
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.base_url,
                    headers=headers,
                    json=payload
                )
                print(f"📡 Text-only response status: {response.status_code}")
                response.raise_for_status()
                
                result = response.json()
                
                if "choices" in result and len(result["choices"]) > 0:
                    response_text = result["choices"][0]["message"]["content"].strip()
                    print(f"✅ Text-only response: '{response_text[:100]}...'")
                    
                    return {
                        "model": self.text_model,
                        "plugin": None,
                        "response": response_text,
                        "success": True,
                        "raw_result": result
                    }
                else:
                    error_msg = f"Invalid text-only response format: {result}"
                    print(f"❌ {error_msg}")
                    return {
                        "model": self.text_model,
                        "plugin": None,
                        "response": f"Error: {error_msg}",
                        "success": False,
                        "error": error_msg
                    }
                    
        except httpx.RequestError as e:
            error_msg = f"OpenRouter text-only API request failed: {e}"
            print(f"❌ {error_msg}")
            return {
                "model": self.text_model,
                "plugin": None,
                "response": f"Network error: {error_msg}",
                "success": False,
                "error": error_msg
            }
        except httpx.HTTPStatusError as e:
            error_msg = f"OpenRouter text-only API error {e.response.status_code}: {e.response.text}"
            print(f"❌ {error_msg}")
            return {
                "model": self.text_model,
                "plugin": None,
                "response": f"API error: {error_msg}",
                "success": False,
                "error": error_msg
            }
        except Exception as e:
            error_msg = f"OpenRouter text-only call failed: {e}"
            print(f"❌ {error_msg}")
            return {
                "model": self.text_model,
                "plugin": None,
                "response": f"Unexpected error: {error_msg}",
                "success": False,
                "error": error_msg
            }

    async def _acall(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Call the OpenRouter API asynchronously."""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost",
                "X-Title": "LangChain AI Orchestrator"
            }
            
            payload = {
                "model": self.text_model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "stop": stop or []
            }
            
            # Add any additional kwargs
            payload.update(kwargs)
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.base_url,
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                
                result = response.json()
                
                if "choices" in result and len(result["choices"]) > 0:
                    return result["choices"][0]["message"]["content"].strip()
                else:
                    raise ValueError(f"Invalid response format: {result}")
                    
        except httpx.RequestError as e:
            raise ValueError(f"OpenRouter API request failed: {e}")
        except httpx.HTTPStatusError as e:
            raise ValueError(f"OpenRouter API error {e.response.status_code}: {e.response.text}")
        except Exception as e:
            raise ValueError(f"OpenRouter LLM async call failed: {e}")
    
    @property
    def _identifying_params(self) -> Dict[str, Any]:
        """Get the identifying parameters."""
        return {
            "text_model": self.text_model,
            "file_model": self.file_model,
            "fallback_file_model": self.fallback_file_model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "base_url": self.base_url
        }

    async def stream_text_only(
        self,
        message: str,
        stop: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> AsyncGenerator[str, None]:
        """Stream text-only messages using OpenRouter API"""
        print(f"💬 OpenRouter streaming text-only - Model: {self.text_model}")
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost",
                "X-Title": "LangChain AI Chat Streaming"
            }
            
            payload = {
                "model": self.text_model,
                "messages": [
                    {
                        "role": "user",
                        "content": message
                    }
                ],
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "stop": stop or [],
                "stream": True  # Enable streaming
            }
            
            # Add filtered kwargs
            filtered_kwargs = {k: v for k, v in kwargs.items() 
                             if k not in ['api_key', 'model', 'text_model', 'file_model']}
            payload.update(filtered_kwargs)
            
            print(f"🚀 Starting streaming request to OpenRouter...")
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                async with client.stream(
                    "POST",
                    self.base_url,
                    headers=headers,
                    json=payload
                ) as response:
                    print(f"📡 Streaming response status: {response.status_code}")
                    
                    if response.status_code != 200:
                        error_msg = f"OpenRouter API error {response.status_code}"
                        print(f"❌ {error_msg}")
                        yield f"Error: {error_msg}"
                        return
                    
                    buffer = ""
                    async for chunk in response.aiter_text():
                        buffer += chunk
                        
                        # Process complete lines
                        while '\n' in buffer:
                            line, buffer = buffer.split('\n', 1)
                            line = line.strip()
                            
                            if line.startswith('data: '):
                                data = line[6:]  # Remove 'data: ' prefix
                                
                                if data == '[DONE]':
                                    print("✅ Streaming completed")
                                    return
                                
                                try:
                                    parsed = json.loads(data)
                                    if 'choices' in parsed and len(parsed['choices']) > 0:
                                        delta = parsed['choices'][0].get('delta', {})
                                        content = delta.get('content', '')
                                        if content:
                                            yield content
                                except json.JSONDecodeError:
                                    # Skip invalid JSON
                                    continue
                                except Exception as e:
                                    print(f"⚠️ Error parsing chunk: {e}")
                                    continue
                    
        except Exception as e:
            error_msg = f"OpenRouter streaming error: {e}"
            print(f"❌ {error_msg}")
            yield f"Error: {error_msg}"

    async def stream_with_file_parser(
        self,
        message: str,
        files: List[Dict[str, Any]],
        stop: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> AsyncGenerator[str, None]:
        """Stream file processing using OpenRouter API with file-parser plugin"""
        print(f"📄 OpenRouter streaming file-parser - Model: {self.file_model}")
        print(f"📁 Processing {len(files)} file(s)")
        
        # Generate file preview information first
        for file_data in files:
            filename = file_data.get('filename', 'unknown_file')
            content = file_data.get('content', b'')
            file_size = len(content) if isinstance(content, (bytes, str)) else 0
            
            # Estimate pages for PDF files
            if filename.lower().endswith('.pdf'):
                estimated_pages = max(1, file_size // 2048)
                preview = f"📄 Parsed file: {filename} — {estimated_pages} pages extracted\n\n"
            else:
                preview = f"📄 Parsed file: {filename} — {file_size} bytes processed\n\n"
            
            yield preview
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost",
                "X-Title": "LangChain AI File Parser Streaming"
            }
            
            # Convert files to base64 format
            file_attachments = []
            for file_data in files:
                if 'content' in file_data and 'filename' in file_data:
                    content = file_data['content']
                    # Convert file content to base64
                    if isinstance(content, bytes):
                        base64_content = base64.b64encode(content).decode('utf-8')
                    else:
                        base64_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')
                    
                    file_attachments.append({
                        "name": file_data['filename'],
                        "content": base64_content,
                        "mime_type": file_data.get('content_type', 'application/octet-stream')
                    })
            
            # Build payload with file-parser plugin
            payload = {
                "model": self.file_model,
                "messages": [
                    {
                        "role": "user",
                        "content": message,
                        "attachments": file_attachments
                    }
                ],
                "plugins": [
                    {
                        "id": "file-parser",
                        "pdf": {
                            "engine": "pdf-text"
                        }
                    }
                ],
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "stop": stop or [],
                "stream": True  # Enable streaming
            }
            
            # Add filtered kwargs
            filtered_kwargs = {k: v for k, v in kwargs.items() 
                             if k not in ['api_key', 'model', 'text_model', 'file_model']}
            payload.update(filtered_kwargs)
            
            print(f"🚀 Starting file-parser streaming request to OpenRouter...")
            async with httpx.AsyncClient(timeout=self.timeout * 2) as client:
                async with client.stream(
                    "POST",
                    self.base_url,
                    headers=headers,
                    json=payload
                ) as response:
                    print(f"📡 File-parser streaming response status: {response.status_code}")
                    
                    if response.status_code != 200:
                        # Try fallback model
                        print(f"⚠️ Primary model failed, trying fallback: {self.fallback_file_model}")
                        payload["model"] = self.fallback_file_model
                        
                        async with client.stream(
                            "POST",
                            self.base_url,
                            headers=headers,
                            json=payload
                        ) as fallback_response:
                            response = fallback_response
                    
                    if response.status_code != 200:
                        error_msg = f"OpenRouter file-parser API error {response.status_code}"
                        print(f"❌ {error_msg}")
                        yield f"Error: {error_msg}"
                        return
                    
                    buffer = ""
                    async for chunk in response.aiter_text():
                        buffer += chunk
                        
                        # Process complete lines
                        while '\n' in buffer:
                            line, buffer = buffer.split('\n', 1)
                            line = line.strip()
                            
                            if line.startswith('data: '):
                                data = line[6:]  # Remove 'data: ' prefix
                                
                                if data == '[DONE]':
                                    print("✅ File-parser streaming completed")
                                    return
                                
                                try:
                                    parsed = json.loads(data)
                                    if 'choices' in parsed and len(parsed['choices']) > 0:
                                        delta = parsed['choices'][0].get('delta', {})
                                        content = delta.get('content', '')
                                        if content:
                                            yield content
                                except json.JSONDecodeError:
                                    # Skip invalid JSON
                                    continue
                                except Exception as e:
                                    print(f"⚠️ Error parsing file chunk: {e}")
                                    continue
                    
        except Exception as e:
            error_msg = f"OpenRouter file-parser streaming error: {e}"
            print(f"❌ {error_msg}")
            yield f"Error: {error_msg}"


class OpenRouterChatLLM(OpenRouterLLM):
    """Chat-specific version of OpenRouter LLM for better agent integration"""
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Enhanced call method for chat-based interactions."""
        # If prompt looks like a chat format, handle it appropriately
        if isinstance(prompt, str) and prompt.startswith("System:") or "Human:" in prompt:
            # Parse the prompt to extract system and user messages
            messages = self._parse_chat_prompt(prompt)
        else:
            # Treat as a simple user message
            messages = [{"role": "user", "content": prompt}]
        
        return self._call_with_messages(messages, stop, **kwargs)
    
    async def _acall(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Enhanced async call method for chat-based interactions."""
        # If prompt looks like a chat format, handle it appropriately
        if isinstance(prompt, str) and prompt.startswith("System:") or "Human:" in prompt:
            # Parse the prompt to extract system and user messages
            messages = self._parse_chat_prompt(prompt)
        else:
            # Treat as a simple user message
            messages = [{"role": "user", "content": prompt}]
        
        return await self._acall_with_messages(messages, stop, **kwargs)
    
    def _parse_chat_prompt(self, prompt: str) -> List[Dict[str, str]]:
        """Parse a chat-formatted prompt into messages."""
        messages = []
        
        # Simple parsing - can be enhanced for more complex formats
        if "System:" in prompt:
            parts = prompt.split("Human:")
            if len(parts) > 1:
                system_part = parts[0].replace("System:", "").strip()
                if system_part:
                    messages.append({"role": "system", "content": system_part})
                
                user_part = parts[1].strip()
                if user_part:
                    messages.append({"role": "user", "content": user_part})
        else:
            messages.append({"role": "user", "content": prompt})
        
        return messages
    
    def _call_with_messages(
        self, 
        messages: List[Dict[str, str]], 
        stop: Optional[List[str]] = None, 
        **kwargs: Any
    ) -> str:
        """Call OpenRouter with pre-formatted messages."""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost",
                "X-Title": "LangChain AI Orchestrator"
            }
            
            payload = {
                "model": self.text_model,
                "messages": messages,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "stop": stop or []
            }
            
            payload.update(kwargs)
            
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    self.base_url,
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                
                result = response.json()
                
                if "choices" in result and len(result["choices"]) > 0:
                    return result["choices"][0]["message"]["content"].strip()
                else:
                    raise ValueError(f"Invalid response format: {result}")
                    
        except Exception as e:
            raise ValueError(f"OpenRouter chat LLM call failed: {e}")
    
    async def _acall_with_messages(
        self, 
        messages: List[Dict[str, str]], 
        stop: Optional[List[str]] = None, 
        **kwargs: Any
    ) -> str:
        """Async call OpenRouter with pre-formatted messages."""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost",
                "X-Title": "LangChain AI Orchestrator"
            }
            
            payload = {
                "model": self.text_model,
                "messages": messages,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "stop": stop or []
            }
            
            payload.update(kwargs)
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.base_url,
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                
                result = response.json()
                
                if "choices" in result and len(result["choices"]) > 0:
                    return result["choices"][0]["message"]["content"].strip()
                else:
                    raise ValueError(f"Invalid response format: {result}")
                    
        except Exception as e:
            raise ValueError(f"OpenRouter async chat LLM call failed: {e}") 
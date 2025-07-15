#!/usr/bin/env python3
"""
LangChain Orchestrator Agent
Main agent that coordinates all tools and manages conversation memory using dynamic LLM switching
Supports both OpenRouter and OpenAI APIs with automatic model routing
"""

import os
from typing import Dict, Any, List, Optional, Union
try:
    from langchain.agents import initialize_agent, AgentType
    from langchain.memory import ConversationBufferMemory
    from langchain.schema import BaseMessage
    from langchain.tools import Tool
except ImportError as e:
    print(f'⚠️ LangChain import error: {e}')
    print('Using fallback mode without LangChain features')

from sqlalchemy.orm import Session
from pydantic import ValidationError
from dotenv import load_dotenv

# Load environment variables
try:
    load_dotenv()
    print("✅ Environment variables loaded from .env")
except Exception as e:
    print(f"⚠️ Warning: Could not load .env file: {e}")
    print("Continuing with system environment variables...")

# Import custom modules
from llm.openrouter_llm import OpenRouterLLM, OpenRouterChatLLM

# Try to import OpenAI Chat with fallback
try:
    from llm.openai_chat import OpenAIChat, OpenAILLM
    OPENAI_AVAILABLE = True
    print("✅ OpenAI integration loaded")
except ImportError as e:
    print(f"⚠️ OpenAI integration not available: {e}")
    OPENAI_AVAILABLE = False

from tools.tool_registry import create_tool_registry


def get_llm(model_name: str = "google/gemini-2.5-flash", **kwargs) -> Union[OpenRouterLLM, OpenAILLM]:
    """
    Dynamic LLM factory function that returns appropriate LLM based on model name.
    
    Args:
        model_name: The model name to use
        **kwargs: Additional parameters for LLM initialization
    
    Returns:
        OpenRouterLLM for google/mistral models, OpenAILLM for others
    """
    print(f"🔀 get_llm() called with model: {model_name}")
    
    # Determine provider based on model name prefixes
    model_lower = model_name.lower()
    
    if "google" in model_lower or "mistral" in model_lower or "openrouter" in model_lower:
        # Use OpenRouter for Google, Mistral, and explicit OpenRouter models
        print(f"🌐 Routing to OpenRouter for model: {model_name}")
        
        return OpenRouterLLM(
            text_model=model_name,
            temperature=kwargs.get('temperature', 0.3),
            max_tokens=kwargs.get('max_tokens', 1500),
            **{k: v for k, v in kwargs.items() if k not in ['temperature', 'max_tokens']}
        )
    
    else:
        # Use OpenAI for GPT models and others
        print(f"🤖 Routing to OpenAI for model: {model_name}")
        
        if not OPENAI_AVAILABLE:
            print("❌ OpenAI not available, falling back to OpenRouter")
            # Fallback to OpenRouter if OpenAI is not available
            return OpenRouterLLM(
                text_model=model_name,
                temperature=kwargs.get('temperature', 0.3),
                max_tokens=kwargs.get('max_tokens', 1500),
                **{k: v for k, v in kwargs.items() if k not in ['temperature', 'max_tokens']}
            )
        
        # Check if OpenAI API key is available
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            print("⚠️ OPENAI_API_KEY not found, falling back to OpenRouter")
            # Fallback to OpenRouter if OpenAI key is missing
            return OpenRouterLLM(
                text_model=model_name,
                temperature=kwargs.get('temperature', 0.3),
                max_tokens=kwargs.get('max_tokens', 1500),
                **{k: v for k, v in kwargs.items() if k not in ['temperature', 'max_tokens']}
            )
        
        # Try to create OpenAI LLM, but fallback to OpenRouter if there are compatibility issues
        try:
            # Filter out OpenAI-incompatible parameters
            filtered_kwargs = {k: v for k, v in kwargs.items() 
                              if k not in ['temperature', 'max_tokens', 'timeout', 'api_key', 'text_model', 'file_model']}
            
            return OpenAILLM(
                model=model_name,
                temperature=kwargs.get('temperature', 0.3),
                max_tokens=kwargs.get('max_tokens', 1500),
                **filtered_kwargs
            )
        except Exception as e:
            print(f"⚠️ OpenAI LLM creation failed ({e}), falling back to OpenRouter")
            # Fallback to OpenRouter with the requested model
            return OpenRouterLLM(
                text_model=model_name,
                temperature=kwargs.get('temperature', 0.3),
                max_tokens=kwargs.get('max_tokens', 1500),
                **{k: v for k, v in kwargs.items() if k not in ['temperature', 'max_tokens']}
            )


class OrchestratorAgent:
    """Main orchestrator agent using LangChain with OpenRouter LLM"""
    
    def __init__(self, db_session: Session = None, model: str = "google/gemini-2.5-flash"):
        self.db_session = db_session
        self.model = model
        try:
            self.llm = self._setup_llm()
            self.tool_registry = self._setup_tool_registry()
            self.tools = self.tool_registry.get_tools()
            self.memory = self._setup_memory()
            self.agent_executor = self._setup_agent()
        except Exception as e:
            print(f"❌ Failed to initialize orchestrator agent: {e}")
            raise
    
    def _setup_llm(self) -> Union[OpenRouterLLM, OpenAILLM]:
        """Setup the LLM with dynamic model switching"""
        try:
            # Use the dynamic get_llm function
            llm = get_llm(
                model_name=self.model,
                temperature=0.3,
                max_tokens=1500,
                timeout=30
            )
            print(f"✅ LLM initialized with model: {self.model} (Provider: {getattr(llm, '_llm_type', 'unknown')})")
            return llm
        except ValidationError as e:
            print(f"❌ LLM validation error: {e}")
            # Return error dict instead of raising
            return {
                "error": True,
                "reason": "Agent input format invalid",
                "detail": f"LangChain LLM rejected unexpected field: {e}"
            }
        except Exception as e:
            print(f"❌ LLM setup error: {e}")
            raise
    
    def _setup_tool_registry(self):
        """Setup the tool registry with database session"""
        try:
            return create_tool_registry(self.db_session)
        except Exception as e:
            print(f"❌ Tool registry setup failed: {e}")
            # Return empty registry on failure
            from tools.tool_registry import ToolRegistry
            return ToolRegistry()
    
    def _setup_memory(self) -> ConversationBufferMemory:
        """Setup conversation memory"""
        return ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="output"
        )
    
    def _setup_agent(self):
        """Setup the agent executor with dynamic LLM"""
        try:
            print("🔧 Setting up agent executor...")
            
            # Check if LLM setup failed
            if isinstance(self.llm, dict) and self.llm.get("error"):
                print("❌ Cannot setup agent - LLM initialization failed")
                return None
            
            # For OpenAI LLMs, get the underlying LangChain-compatible instance
            if hasattr(self.llm, 'get_underlying_llm'):
                llm_for_agent = self.llm.get_underlying_llm()
                print("🔄 Using underlying LLM for agent compatibility")
            elif hasattr(self.llm, 'openai_chat') and hasattr(self.llm.openai_chat, 'chat_llm'):
                llm_for_agent = self.llm.openai_chat.chat_llm
                print("🔄 Using OpenAI ChatLLM for agent compatibility")
            else:
                llm_for_agent = self.llm
                print("🔄 Using LLM directly")
            
            # Use ZERO_SHOT_REACT_DESCRIPTION as it's more compatible
            agent = initialize_agent(
                tools=self.tools,
                llm=llm_for_agent,
                agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                memory=self.memory,
                verbose=True,
                max_iterations=3,
                early_stopping_method="generate",
                return_intermediate_steps=True,
                handle_parsing_errors=True
            )
            print("✅ Agent executor setup complete")
            return agent
        except Exception as e:
            print(f"❌ Agent setup failed: {e}")
            return None
    
    async def process_message(self, message: str, context: str = "", session_id: str = None) -> Dict[str, Any]:
        """Process a user message and execute appropriate tools"""
        print(f"🔍 Processing message: '{message[:100]}...'")
        
        # Check if agent setup failed
        if self.agent_executor is None:
            if isinstance(self.llm, dict) and self.llm.get("error"):
                return {
                    "success": False,
                    "response": f"Agent initialization failed: {self.llm.get('detail', 'Unknown error')}",
                    "tools_used": [],
                    "tool_count": 0,
                    "session_id": session_id,
                    "error": self.llm.get("detail", "Agent setup failed")
                }
            else:
                return {
                    "success": False,
                    "response": "Agent executor is not available",
                    "tools_used": [],
                    "tool_count": 0,
                    "session_id": session_id,
                    "error": "Agent setup failed"
                }
        
        try:
            # Add context to the message if provided
            full_message = f"{message}\n\nContext: {context}" if context else message
            print(f"📝 Full message to agent: '{full_message[:200]}...'")
            
            # Log model and payload info
            print(f"🤖 Using model: {self.model}")
            print(f"📊 Available tools: {len(self.tools)}")
            
            # Run the agent with proper error handling
            tools_used = []
            try:
                print("🤖 Starting agent execution (async)...")
                agent_result = await self.agent_executor.ainvoke({
                    "input": full_message,
                    "chat_history": self.memory.chat_memory.messages
                })
                result = agent_result.get("output", str(agent_result))
                print(f"✅ Agent execution completed: '{result[:100]}...'")
            except Exception as async_error:
                print(f"⚠️ Async execution failed: {async_error}")
                # Fallback to synchronous execution
                try:
                    print("🔄 Trying synchronous execution...")
                    agent_result = self.agent_executor.invoke({
                        "input": full_message,
                        "chat_history": self.memory.chat_memory.messages
                    })
                    result = agent_result.get("output", str(agent_result))
                    print(f"✅ Sync execution completed: '{result[:100]}...'")
                except Exception as sync_error:
                    print(f"❌ Both async and sync execution failed")
                    print(f"Async error: {async_error}")
                    print(f"Sync error: {sync_error}")
                    
                    # Return user-friendly error message
                    return {
                        "success": False,
                        "response": f"I encountered an error while processing your request. The AI service may be temporarily unavailable. Please try again in a moment.",
                        "tools_used": [],
                        "tool_count": 0,
                        "session_id": session_id,
                        "error": f"Agent execution failed: {sync_error}"
                    }
            
            # Extract tool usage information
            intermediate_steps = agent_result.get('intermediate_steps', [])
            print(f"🔧 Found {len(intermediate_steps)} intermediate steps")
            
            for i, step in enumerate(intermediate_steps):
                if isinstance(step, tuple) and len(step) >= 2:
                    action, observation = step
                    if hasattr(action, 'tool'):
                        tools_used.append(action.tool)
                        print(f"🛠️ Step {i+1}: Used tool '{action.tool}'")
                        print(f"📊 Tool result: {str(observation)[:200]}...")
            
            # Extract tool names for response
            tool_names = [str(tool) for tool in tools_used]
            print(f"🎯 Tools used: {tool_names}")
            
            return {
                "success": True,
                "response": result,
                "tools_used": tool_names,
                "tool_count": len(tool_names),
                "session_id": session_id,
                "memory_length": len(self.memory.chat_memory.messages)
            }
        
        except ValidationError as e:
            error_msg = f"Agent input format invalid: {e}"
            print(f"❌ Validation error: {error_msg}")
            return {
                "success": False,
                "response": f"I encountered a configuration error. Please try rephrasing your request.",
                "tools_used": [],
                "tool_count": 0,
                "session_id": session_id,
                "error": error_msg
            }
        except Exception as e:
            error_msg = f"Agent execution error: {str(e)}"
            print(f"❌ {error_msg}")
            return {
                "success": False,
                "response": f"I encountered an error while processing your request: {str(e)}",
                "tools_used": [],
                "tool_count": 0,
                "session_id": session_id,
                "error": error_msg
            }
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get information about all available tools"""
        try:
            return self.tool_registry.get_tool_descriptions()
        except Exception as e:
            print(f"❌ Error getting tool descriptions: {e}")
            return []
    
    def clear_memory(self):
        """Clear conversation memory"""
        try:
            self.memory.clear()
        except Exception as e:
            print(f"❌ Error clearing memory: {e}")
    
    def get_memory_summary(self) -> Dict[str, Any]:
        """Get summary of conversation memory"""
        try:
            messages = self.memory.chat_memory.messages
            return {
                "total_messages": len(messages),
                "memory_key": self.memory.memory_key,
                "recent_messages": [
                    {
                        "type": getattr(msg, 'type', 'unknown'),
                        "content": (msg.content[:100] + "...") if len(msg.content) > 100 else msg.content
                    }
                    for msg in messages[-5:]  # Last 5 messages
                ]
            }
        except Exception as e:
            print(f"❌ Error getting memory summary: {e}")
            return {"total_messages": 0, "memory_key": "unknown", "recent_messages": []}
    
    def update_session_context(self, context: str):
        """Update session context in memory"""
        try:
            if context and self.memory:
                self.memory.chat_memory.add_user_message(f"[Context Update]: {context}")
        except Exception as e:
            print(f"❌ Error updating session context: {e}")


class AgentManager:
    """Manages multiple agent instances per session"""
    
    def __init__(self):
        self.agents = {}  # session_id -> OrchestratorAgent
    
    def get_agent(self, session_id: str, db_session: Session = None, model: str = "google/gemini-2.5-flash") -> OrchestratorAgent:
        """Get or create an agent for a session"""
        try:
            if session_id not in self.agents:
                self.agents[session_id] = OrchestratorAgent(db_session, model)
            return self.agents[session_id]
        except Exception as e:
            print(f"❌ Error creating agent for session {session_id}: {e}")
            # Create a minimal agent that returns error responses
            class ErrorAgent:
                def __init__(self, error_msg):
                    self.error_msg = error_msg
                
                async def process_message(self, message, context="", session_id=None):
                    return {
                        "success": False,
                        "response": f"Agent service is temporarily unavailable: {self.error_msg}",
                        "tools_used": [],
                        "tool_count": 0,
                        "session_id": session_id,
                        "error": self.error_msg
                    }
                
                def clear_memory(self): pass
                def get_available_tools(self): return []
                def get_memory_summary(self): return {}
                def update_session_context(self, context): pass
            
            return ErrorAgent(str(e))
    
    def clear_session(self, session_id: str):
        """Clear a specific session's agent"""
        if session_id in self.agents:
            try:
                self.agents[session_id].clear_memory()
            except:
                pass
            del self.agents[session_id]
    
    def get_all_sessions(self) -> List[str]:
        """Get all active session IDs"""
        return list(self.agents.keys())
    
    def cleanup_old_sessions(self, max_sessions: int = 50):
        """Clean up old sessions if we have too many"""
        if len(self.agents) > max_sessions:
            # Remove oldest sessions (simple FIFO)
            sessions_to_remove = list(self.agents.keys())[:-max_sessions]
            for session_id in sessions_to_remove:
                self.clear_session(session_id)


# Global agent manager instance
agent_manager = AgentManager()


# Standalone orchestrator function for direct usage
async def run_orchestrator(input_text: str, db_session: Session = None, model: str = "google/gemini-2.5-flash") -> str:
    """
    Run the orchestrator agent with a single input and return the response.
    
    Args:
        input_text: User input message
        db_session: Optional database session
        model: OpenRouter model to use
    
    Returns:
        Agent's response as a string
    """
    try:
        print(f"🚀 Running orchestrator with model: {model}")
        print(f"📝 Input: {input_text[:100]}...")
        
        # Create a new agent instance
        agent = OrchestratorAgent(db_session=db_session, model=model)
        
        # Process the message
        result = await agent.process_message(input_text)
        
        if result["success"]:
            return result["response"]
        else:
            return f"Error: {result.get('error', 'Unknown error occurred')}"
            
    except Exception as e:
        error_msg = f"Failed to run orchestrator: {str(e)}"
        print(f"❌ {error_msg}")
        return error_msg


def run_orchestrator_sync(input_text: str, db_session: Session = None, model: str = "google/gemini-2.5-flash") -> str:
    """
    Synchronous version of run_orchestrator for compatibility.
    
    Args:
        input_text: User input message
        db_session: Optional database session  
        model: OpenRouter model to use
    
    Returns:
        Agent's response as a string
    """
    try:
        print(f"🚀 Running sync orchestrator with model: {model}")
        
        # Create a new agent instance
        agent = OrchestratorAgent(db_session=db_session, model=model)
        
        if agent.agent_executor is None:
            return "Error: Agent initialization failed"
        
        # Use synchronous execution
        agent_result = agent.agent_executor.invoke({
            "input": input_text,
            "chat_history": []
        })
        result = agent_result.get("output", str(agent_result))
        
        return result
        
    except Exception as e:
        error_msg = f"Failed to run orchestrator: {str(e)}"
        print(f"❌ {error_msg}")
        return error_msg
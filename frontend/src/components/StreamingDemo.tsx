import React, { useState } from 'react'
import { useAppStore } from '../store/useAppStore'
import { apiClient } from '../services/apiClient'
import { Send, Bot, Loader2 } from 'lucide-react'

const StreamingDemo: React.FC = () => {
  const [input, setInput] = useState('')
  const [response, setResponse] = useState('')
  const [isStreaming, setIsStreaming] = useState(false)
  const [isComplete, setIsComplete] = useState(false)

  const handleStreamingTest = async () => {
    if (!input.trim() || isStreaming) return

    setResponse('')
    setIsStreaming(true)
    setIsComplete(false)

    try {
      await apiClient.sendStreamingChatMessage(
        { message: input.trim() },
        // onChunk - append each chunk
        (chunk: string) => {
          setResponse(prev => prev + chunk)
        },
        // onComplete - mark as done
        (finalResponse) => {
          setIsStreaming(false)
          setIsComplete(true)
          console.log('Streaming complete:', finalResponse)
        },
        // onError - handle errors
        (error: string) => {
          setResponse(prev => prev + `\n\nError: ${error}`)
          setIsStreaming(false)
          setIsComplete(true)
        }
      )
    } catch (error) {
      setResponse(prev => prev + `\n\nError: ${error}`)
      setIsStreaming(false)
      setIsComplete(true)
    }
  }

  return (
    <div className="max-w-2xl mx-auto p-6 bg-neutral-900 rounded-lg">
      <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
        <Bot className="text-green-400" size={24} />
        Streaming Chat Demo
      </h2>
      
      <div className="space-y-4">
        {/* Input Section */}
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleStreamingTest()}
            placeholder="Ask me anything... (e.g., 'Tell me a story about AI')"
            className="flex-1 px-4 py-2 bg-neutral-800 border border-neutral-700 rounded-lg text-white placeholder-neutral-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isStreaming}
          />
          <button
            onClick={handleStreamingTest}
            disabled={!input.trim() || isStreaming}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-neutral-700 disabled:cursor-not-allowed text-white rounded-lg flex items-center gap-2 transition-colors"
          >
            {isStreaming ? (
              <>
                <Loader2 className="animate-spin" size={16} />
                Streaming...
              </>
            ) : (
              <>
                <Send size={16} />
                Send
              </>
            )}
          </button>
        </div>

        {/* Response Section */}
        {(response || isStreaming) && (
          <div className="bg-neutral-800 border border-neutral-700 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <Bot className="text-green-400" size={16} />
              <span className="text-neutral-300 text-sm font-medium">
                AI Assistant
                {isStreaming && <span className="text-green-400"> (typing...)</span>}
                {isComplete && <span className="text-blue-400"> (complete)</span>}
              </span>
            </div>
            
            <div className="text-white whitespace-pre-wrap relative">
              {response}
              {isStreaming && (
                <span className="inline-block w-2 h-5 bg-green-400 animate-pulse rounded-sm ml-1"></span>
              )}
            </div>
          </div>
        )}

        {/* Instructions */}
        <div className="bg-blue-900/20 border border-blue-700/30 rounded-lg p-4">
          <h3 className="text-blue-400 font-medium mb-2">How it works:</h3>
          <ul className="text-blue-200 text-sm space-y-1">
            <li>• Type a message and hit Send</li>
            <li>• Watch the response appear word-by-word in real-time</li>
            <li>• The cursor shows active streaming</li>
            <li>• No page refresh or loading delays!</li>
          </ul>
        </div>
      </div>
    </div>
  )
}

export default StreamingDemo 
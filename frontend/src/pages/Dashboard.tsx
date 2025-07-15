import React, { useState, useRef, useCallback, useEffect } from 'react'
import { useAppStore, Message, UploadedFile, IntentOption, ParsedResponse, INTENT_OPTIONS } from '../store/useAppStore'
import { apiClient } from '../services/apiClient'
import TestConnection from '../components/TestConnection'
import { 
  Upload,
  Send,
  Check,
  X,
  FileText,
  Loader2,
  Paperclip,
  Mail,
  MessageSquare,
  Bot,
  User,
  File,
  FileSpreadsheet,
  FileImage,
  Trash2,
  Edit,
  ChevronDown
} from 'lucide-react'

const Dashboard: React.FC = () => {
  const {
    messages,
    addMessage,
    updateMessage,
    appendToMessage,
    isUploading,
    setIsUploading,
    uploadedFiles,
    addUploadedFile,
    updateUploadedFile,
    removeUploadedFile,
    clearUploadedFiles
  } = useAppStore()

  const [inputValue, setInputValue] = useState('')
  const [isDragOver, setIsDragOver] = useState(false)
  const [customCommand, setCustomCommand] = useState('')
  const [selectedChatFiles, setSelectedChatFiles] = useState<File[]>([])
  const [isStreaming, setIsStreaming] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const chatFileInputRef = useRef<HTMLInputElement>(null)
  const chatEndRef = useRef<HTMLDivElement>(null)
  const streamingAbortController = useRef<AbortController | null>(null)

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const getFileTypeIcon = (fileName: string) => {
    const extension = fileName.split('.').pop()?.toLowerCase()
    switch (extension) {
      case 'pdf':
        return <FileText className="text-red-500" size={20} />
      case 'xlsx':
      case 'xls':
      case 'csv':
        return <FileSpreadsheet className="text-green-500" size={20} />
      case 'docx':
      case 'doc':
        return <File className="text-blue-500" size={20} />
      case 'txt':
        return <FileText className="text-neutral-400" size={20} />
      default:
        return <File className="text-neutral-400" size={20} />
    }
  }

  const getAcceptedFileTypes = () => {
    return '.pdf,.csv,.xlsx,.xls,.docx,.doc,.txt'
  }

  const handleFileUpload = async (files: FileList) => {
    const acceptedTypes = ['application/pdf', 'text/csv', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/msword', 'text/plain']
    
    for (const file of Array.from(files)) {
      if (acceptedTypes.includes(file.type) || acceptedTypes.some(type => file.name.toLowerCase().endsWith(type.split('/')[1]))) {
        const fileId = `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
        
        const uploadedFile: UploadedFile = {
          id: fileId,
          file,
          fileMeta: {
            id: fileId,
            name: file.name,
            size: file.size,
            uploadedAt: new Date().toISOString(),
            type: file.type
          },
          isProcessing: false,
          processed: false
        }
        
        addUploadedFile(uploadedFile)
        
        // Add user message showing file upload
        addMessage({
          id: `upload-user-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
          type: 'user',
          role: 'user',
          content: `📁 Uploaded: ${file.name}`,
          fileMeta: uploadedFile.fileMeta,
          timestamp: new Date().toISOString()
        })

        // Add assistant message asking for intent
        addMessage({
          id: `upload-assistant-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
          type: 'assistant',
          role: 'assistant',
          content: `I've received "${file.name}". What would you like me to do with this file? Please select an action from the file card above.`,
          timestamp: new Date().toISOString()
        })
      }
    }
  }

  const handleIntentSelection = async (fileId: string, intent: IntentOption['value']) => {
    const uploadedFile = uploadedFiles.find(f => f.id === fileId)
    if (!uploadedFile) return

    // Update file with selected intent and processing state
    updateUploadedFile(fileId, { 
      intent, 
      isProcessing: true 
    })

    try {
      const formData = new FormData()
      formData.append('file', uploadedFile.file)
      formData.append('intent', intent)

      if (intent === 'custom' && customCommand) {
        formData.append('custom_command', customCommand)
      }

      const result = await apiClient.uploadFile(uploadedFile.file, intent)

      if (result.success && result.data) {
        const data = result.data
        
        const parsedResponse: ParsedResponse = {
          type: intent === 'extract_reminders' ? 'reminders' : 
                intent === 'send_email' ? 'email_draft' :
                intent === 'summarize' ? 'summary' :
                intent === 'parse_contacts' ? 'contacts' : 'custom',
          content: data,
          message: data.summary || 'Processing completed successfully',
          needsConfirmation: data.needs_confirmation || false
        }

        // Update file as processed
        updateUploadedFile(fileId, { 
          isProcessing: false, 
          processed: true,
          response: parsedResponse
        })

        // Add assistant response based on intent
        if (intent === 'extract_reminders' && data.extracted_data?.reminders_found > 0) {
          addMessage({
            id: `process-assistant-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
            type: 'assistant',
            role: 'assistant',
            content: `I found potential reminders in "${uploadedFile.file.name}". ${data.confirmation_prompt || 'Would you like me to extract them?'}`,
            parsedResponse,
            fileMeta: uploadedFile.fileMeta,
            tool_used: 'extract_reminders',
            timestamp: new Date().toISOString()
          })
        } else if (intent === 'send_email') {
          addMessage({
            id: `process-assistant-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
            type: 'assistant',
            role: 'assistant',
            content: `I've analyzed "${uploadedFile.file.name}" for email content. ${data.confirmation_prompt || 'Would you like me to prepare an email summary?'}`,
            parsedResponse,
            fileMeta: uploadedFile.fileMeta,
            tool_used: 'send_email',
            timestamp: new Date().toISOString()
          })
        } else {
          addMessage({
            id: `process-assistant-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
            type: 'assistant',
            role: 'assistant',
            content: parsedResponse.message,
            parsedResponse,
            fileMeta: uploadedFile.fileMeta,
            tool_used: intent,
            timestamp: new Date().toISOString()
          })
        }
      } else {
        throw new Error(result.error || 'Upload failed')
      }
    } catch (error) {
      updateUploadedFile(fileId, { 
        isProcessing: false, 
        processed: false 
      })
      
      console.error('Upload error:', error)
      
      let errorMessage = `File processing failed for ${uploadedFile.file.name}. Please retry.`
      
      if (error instanceof Error) {
        if (error.message.includes('500')) {
          errorMessage = `Backend error processing ${uploadedFile.file.name}. Please retry.`
        } else if (error.message.includes('Network Error')) {
          errorMessage = `Connection failed. Check if backend is running.`
        }
      }
      
      addMessage({
        id: `error-assistant-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        type: 'assistant',
        role: 'assistant',
        content: errorMessage,
        tool_used: 'error',
        timestamp: new Date().toISOString()
      })
    }
  }

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(false)
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(false)
    
    const files = e.dataTransfer.files
    if (files.length > 0) {
      handleFileUpload(files)
    }
  }, [])

  const handleFileSelect = () => {
    fileInputRef.current?.click()
  }

  const handleChatFileUpload = (files: FileList) => {
    const acceptedTypes = ['application/pdf', 'text/csv', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/msword', 'text/plain']
    
    const newFiles = Array.from(files).filter(file => 
      acceptedTypes.includes(file.type) || 
      acceptedTypes.some(type => file.name.toLowerCase().endsWith(type.split('/')[1]))
    )
    
    setSelectedChatFiles(prev => [...prev, ...newFiles])
  }

  const removeChatFile = (index: number) => {
    setSelectedChatFiles(prev => prev.filter((_, i) => i !== index))
  }

  const handleChatFileSelect = () => {
    chatFileInputRef.current?.click()
  }

  const handleSendMessage = async () => {
    if (!inputValue.trim() && selectedChatFiles.length === 0) return
    if (isStreaming) return // Prevent sending while streaming

    const userMessage = inputValue.trim()
    const hasFiles = selectedChatFiles.length > 0
    const hasMessage = userMessage.length > 0

    // Generate unique IDs for proper message tracking
    const userMessageId = `user-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
    const assistantMessageId = `assistant-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`

    // Create user message content
    let userContent = ''
    if (hasMessage && hasFiles) {
      userContent = `${userMessage}\n📎 ${selectedChatFiles.map(f => f.name).join(', ')}`
    } else if (hasMessage) {
      userContent = userMessage
    } else if (hasFiles) {
      userContent = `📎 Uploaded: ${selectedChatFiles.map(f => f.name).join(', ')}`
    }

    // Clear input and files
    setInputValue('')
    const filesToProcess = [...selectedChatFiles]
    setSelectedChatFiles([])

    // Cancel any existing streaming
    if (streamingAbortController.current) {
      streamingAbortController.current.abort()
    }

    // Add user message with explicit ID
    addMessage({
      id: userMessageId,
      type: 'user',
      role: 'user',
      content: userContent,
      timestamp: new Date().toISOString()
    })

    // Add streaming assistant message with explicit ID
    addMessage({
      id: assistantMessageId,
      type: 'assistant',
      role: 'assistant',
      content: '...',
      streaming: true,
      timestamp: new Date().toISOString()
    })

    setIsStreaming(true)
    streamingAbortController.current = new AbortController()

    try {
      // Handle file uploads first if present
      if (hasFiles) {
        for (const file of filesToProcess) {
          const result = await apiClient.uploadFile(file, 'extract_reminders')
          
          if (result.success && result.data) {
            // Add file processing result
            addMessage({
              id: `file-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
              type: 'assistant',
              role: 'assistant',
              content: `📁 Processed ${file.name}: ${result.data.summary || 'File analyzed successfully'}`,
              tool_used: 'file_processing',
              timestamp: new Date().toISOString()
            })
          }
        }
      }

      if (hasMessage) {
        // Use streaming chat API
        await apiClient.sendStreamingChatMessage(
          {
            message: userMessage,
            context: filesToProcess.map(f => f.name).join(', ')
          },
          // onChunk - progressively append content
          (chunk: string) => {
            appendToMessage(assistantMessageId, chunk)
          },
          // onComplete - finalize message
          (response) => {
            updateMessage(assistantMessageId, {
              streaming: false,
              tool_used: response.tool_used || undefined
            })
            setIsStreaming(false)
          },
          // onError - handle errors
          (error: string) => {
            updateMessage(assistantMessageId, {
              content: `I encountered an error: ${error}`,
              streaming: false,
              tool_used: 'error'
            })
            setIsStreaming(false)
          }
        )
      } else {
        // Only files, no message - update with file confirmation
        updateMessage(assistantMessageId, {
          content: `I've processed ${filesToProcess.length} file(s). What would you like me to do with the information?`,
          streaming: false,
          tool_used: 'file_processing'
        })
        setIsStreaming(false)
      }
    } catch (error) {
      console.error('Chat error:', error)
      
      let errorMessage = 'Agent failed to respond. Please retry.'
      
      // Handle specific error types
      if (error instanceof Error) {
        if (error.message.includes('500')) {
          errorMessage = 'Backend server error. Please retry or contact support.'
        } else if (error.message.includes('Network Error') || error.message.includes('fetch')) {
          errorMessage = 'Connection failed. Check if backend is running.'
        } else if (error.message.includes('timeout')) {
          errorMessage = 'Request timeout. Please retry.'
        }
      }
      
      updateMessage(assistantMessageId, {
        content: errorMessage,
        streaming: false,
        tool_used: 'error'
      })
      setIsStreaming(false)
    }
  }

  const handleConfirmReminder = async (messageId: string, reminder: any) => {
    try {
      const result = await apiClient.confirmAction({
        decision: 'yes',
        session_id: messageId
      })

      if (result.success) {
        updateMessage(messageId, {
          reminder: { ...reminder, confirmed: true }
        })
        
        addMessage({
          id: `confirm-assistant-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
          type: 'assistant',
          role: 'assistant',
          content: `✅ Perfect! I've set the reminder "${reminder.text}" for ${reminder.date}. You'll be notified when it's time.`,
          tool_used: 'add_reminder',
          timestamp: new Date().toISOString()
        })
      } else {
        throw new Error(result.error || 'Confirmation failed')
      }
    } catch (error) {
      console.error('Confirmation error:', error)
      
      addMessage({
        id: `error-assistant-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        type: 'assistant',
        role: 'assistant',
        content: `Reminder confirmation failed. ${error instanceof Error ? error.message : 'Please try again.'}`,
        tool_used: 'error',
        timestamp: new Date().toISOString()
      })
    }
  }

  const handleRejectReminder = (messageId: string) => {
    addMessage({
      id: `reject-assistant-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      type: 'assistant',
      role: 'assistant',
      content: 'No problem! The reminder has been discarded. Is there anything else I can help you with?',
      timestamp: new Date().toISOString()
    })
  }

  const handleConfirmEmailSend = async (messageId: string, parsedResponse: ParsedResponse) => {
    // Stub function for email sending
    addMessage({
      id: `email-assistant-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      type: 'assistant',
      role: 'assistant',
      content: '📧 Email sent successfully! The summary has been delivered to the recipients.',
      tool_used: 'send_email',
      timestamp: new Date().toISOString()
    })
  }

  const handleSendEmail = async () => {
    // Stub function for email trigger
    addMessage({
      id: `email-assistant-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      type: 'assistant',
      role: 'assistant',
      content: '📧 Email summary feature coming soon! I\'ll be able to send you a summary of all your reminders and important dates.',
      tool_used: 'send_email',
      timestamp: new Date().toISOString()
    })
  }

  const renderMessage = (message: Message) => {
    const isUser = message.type === 'user' || message.role === 'user'
    
    return (
      <div key={message.id} className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
        <div className={`flex ${isUser ? 'flex-row-reverse' : 'flex-row'} items-start gap-3 max-w-[80%]`}>
          {/* Avatar */}
          <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
            isUser 
              ? 'bg-gradient-to-r from-blue-600 to-purple-600' 
              : 'bg-gradient-to-r from-green-600 to-blue-600'
          }`}>
            {isUser ? <User size={16} className="text-white" /> : <Bot size={16} className="text-white" />}
          </div>

          {/* Message Bubble */}
          <div className={`rounded-lg p-4 ${
            isUser 
              ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white' 
              : 'bg-neutral-800 text-neutral-100 border border-neutral-700'
          }`}>
            {message.isLoading ? (
              <div className="flex items-center gap-2">
                <Loader2 className="animate-spin" size={16} />
                <span>Thinking...</span>
              </div>
            ) : message.streaming ? (
              <div className="flex items-start gap-1">
                <span className="whitespace-pre-wrap">{message.content}</span>
                <span className="inline-block w-2 h-5 bg-green-400 animate-pulse rounded-sm"></span>
              </div>
            ) : (
              <>
                <p className="whitespace-pre-wrap">{message.content}</p>
                
                {/* File attachment indicator */}
                {message.fileMeta && (
                  <div className="flex items-center gap-2 mt-2 pt-2 border-t border-white/20">
                    <Paperclip size={14} />
                    <span className="text-xs opacity-75">{message.fileMeta.name}</span>
                  </div>
                )}

                {/* Reminder confirmation buttons */}
                {message.reminder && !message.reminder.confirmed && (
                  <div className="flex items-center gap-2 mt-3 pt-3 border-t border-neutral-600">
                    <span className="text-sm text-neutral-300">Set this reminder?</span>
                    <button
                      onClick={() => handleConfirmReminder(message.id, message.reminder!)}
                      className="flex items-center gap-1 px-3 py-1 bg-green-600 hover:bg-green-500 text-white text-sm rounded-md transition-colors"
                    >
                      <Check size={14} />
                      Yes
                    </button>
                    <button
                      onClick={() => handleRejectReminder(message.id)}
                      className="flex items-center gap-1 px-3 py-1 bg-neutral-600 hover:bg-neutral-500 text-white text-sm rounded-md transition-colors"
                    >
                      <X size={14} />
                      No
                    </button>
                  </div>
                )}

                {/* Email confirmation buttons */}
                {message.parsedResponse?.type === 'email_draft' && message.parsedResponse.needsConfirmation && (
                  <div className="flex items-center gap-2 mt-3 pt-3 border-t border-neutral-600">
                    <span className="text-sm text-neutral-300">Send this email?</span>
                    <button
                      onClick={() => handleConfirmEmailSend(message.id, message.parsedResponse!)}
                      className="flex items-center gap-1 px-3 py-1 bg-blue-600 hover:bg-blue-500 text-white text-sm rounded-md transition-colors"
                    >
                      <Mail size={14} />
                      Send
                    </button>
                    <button
                      className="flex items-center gap-1 px-3 py-1 bg-yellow-600 hover:bg-yellow-500 text-white text-sm rounded-md transition-colors"
                    >
                      <Edit size={14} />
                      Edit
                    </button>
                    <button
                      onClick={() => handleRejectReminder(message.id)}
                      className="flex items-center gap-1 px-3 py-1 bg-neutral-600 hover:bg-neutral-500 text-white text-sm rounded-md transition-colors"
                    >
                      <X size={14} />
                      Cancel
                    </button>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </div>
    )
  }

  const renderFileCard = (uploadedFile: UploadedFile) => {
    return (
      <div key={uploadedFile.id} className="bg-neutral-800 border border-neutral-700 rounded-lg p-4 mb-3">
        <div className="flex items-start gap-3">
          <div className="flex-shrink-0 mt-1">
            {getFileTypeIcon(uploadedFile.fileMeta.name)}
          </div>
          
          <div className="flex-1 min-w-0">
            <h4 className="text-white font-medium truncate">{uploadedFile.fileMeta.name}</h4>
            <p className="text-neutral-400 text-sm">{(uploadedFile.fileMeta.size / 1024).toFixed(1)} KB</p>
            
            {!uploadedFile.intent && !uploadedFile.isProcessing && (
              <div className="mt-3">
                <label className="block text-sm font-medium text-neutral-300 mb-2">
                  What would you like to do with this file?
                </label>
                <div className="grid grid-cols-1 gap-2">
                  {INTENT_OPTIONS.map((option) => (
                    <button
                      key={option.value}
                      onClick={() => handleIntentSelection(uploadedFile.id, option.value)}
                      className="text-left p-2 bg-neutral-700 hover:bg-neutral-600 rounded text-sm transition-colors border border-neutral-600 hover:border-neutral-500"
                    >
                      <div className="font-medium text-white">{option.label}</div>
                      <div className="text-neutral-400 text-xs">{option.description}</div>
                    </button>
                  ))}
                </div>
                
                {uploadedFile.intent === 'custom' && (
                  <div className="mt-2">
                    <input
                      type="text"
                      value={customCommand}
                      onChange={(e) => setCustomCommand(e.target.value)}
                      placeholder="Enter custom command..."
                      className="w-full px-3 py-2 bg-neutral-700 border border-neutral-600 rounded text-white placeholder-neutral-400 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                )}
              </div>
            )}
            
            {uploadedFile.isProcessing && (
              <div className="mt-3 flex items-center gap-2 text-blue-400">
                <Loader2 className="animate-spin" size={16} />
                <span className="text-sm">Processing with {INTENT_OPTIONS.find(o => o.value === uploadedFile.intent)?.label}...</span>
              </div>
            )}
            
            {uploadedFile.processed && uploadedFile.response && (
              <div className="mt-3 p-2 bg-green-500/10 border border-green-500/20 rounded text-green-400 text-sm">
                ✅ Processed successfully
              </div>
            )}
          </div>
          
          <button
            onClick={() => removeUploadedFile(uploadedFile.id)}
            className="flex-shrink-0 p-1 text-neutral-400 hover:text-red-400 transition-colors"
          >
            <Trash2 size={16} />
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="h-[calc(100vh-64px)] flex flex-col bg-neutral-950">
      {/* Header */}
      <div className="flex-shrink-0 p-6 border-b border-neutral-800">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white flex items-center gap-3">
              <MessageSquare className="text-blue-500" />
              Chat Orchestrator Agent
            </h1>
            <p className="text-neutral-400 mt-1">
              Upload documents, ask questions, and manage your workflow
            </p>
          </div>
          <button
            onClick={handleSendEmail}
            className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg font-medium hover:from-purple-500 hover:to-pink-500 transition-all duration-200"
          >
            <Mail size={16} />
            Email Summary
          </button>
        </div>
      </div>

      {/* Backend Connection Test - Only show when no messages */}
      {messages.length === 0 && (
        <div className="flex-shrink-0 p-6 border-b border-neutral-800">
          <TestConnection />
        </div>
      )}

      {/* Upload Zone */}
      {messages.length === 0 && uploadedFiles.length === 0 && (
        <div className="flex-shrink-0 p-6">
          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={handleFileSelect}
            className={`
              relative border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all duration-200
              ${isDragOver 
                ? 'border-blue-500 bg-blue-500/10' 
                : 'border-neutral-700 hover:border-neutral-600 hover:bg-neutral-900/50'
              }
            `}
          >
            <input
              ref={fileInputRef}
              type="file"
              multiple
              accept={getAcceptedFileTypes()}
              onChange={(e) => e.target.files && handleFileUpload(e.target.files)}
              className="hidden"
            />
            
            <div className="flex flex-col items-center gap-4">
              <Upload className="text-neutral-400" size={48} />
              
              <div>
                <h3 className="text-white font-medium mb-2">Upload Business Documents</h3>
                <p className="text-neutral-400 text-sm mb-2">
                  Drag and drop files here, or click to select
                </p>
                <p className="text-neutral-500 text-xs">
                  Supports: PDF, CSV, XLSX, DOCX, TXT
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Uploaded Files */}
      {uploadedFiles.length > 0 && (
        <div className="flex-shrink-0 p-6 border-b border-neutral-800">
          <div className="space-y-3">
            <h3 className="text-white font-medium mb-3">Uploaded Files</h3>
            {uploadedFiles.map(renderFileCard)}
          </div>
        </div>
      )}

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-6">
        {messages.length === 0 ? (
          <div className="text-center text-neutral-400 mt-8">
            <Bot className="mx-auto mb-4 text-neutral-500" size={48} />
            <p>Start by uploading a document or asking me a question!</p>
          </div>
        ) : (
          <>
            {messages.map(renderMessage)}
            <div ref={chatEndRef} />
          </>
        )}
      </div>

      {/* Input Area */}
      <div className="flex-shrink-0 p-6 border-t border-neutral-800">
        <div className="space-y-3">
          {/* Selected Files Display */}
          {selectedChatFiles.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {selectedChatFiles.map((file, index) => (
                <div key={index} className="flex items-center gap-2 px-3 py-2 bg-neutral-700 rounded-lg border border-neutral-600">
                  <div className="flex items-center gap-2">
                    {getFileTypeIcon(file.name)}
                    <span className="text-sm text-neutral-200 max-w-32 truncate">{file.name}</span>
                    <span className="text-xs text-neutral-400">({(file.size / 1024).toFixed(1)} KB)</span>
                  </div>
                  <button
                    onClick={() => removeChatFile(index)}
                    className="text-neutral-400 hover:text-red-400 transition-colors"
                    title="Remove file"
                  >
                    <X size={14} />
                  </button>
                </div>
              ))}
            </div>
          )}
          
          {/* Input Bar */}
          <div className="flex gap-3">
            <div className="flex-1 relative">
              {/* Hidden file input */}
              <input
                ref={chatFileInputRef}
                type="file"
                multiple
                accept={getAcceptedFileTypes()}
                onChange={(e) => e.target.files && handleChatFileUpload(e.target.files)}
                className="hidden"
              />
              
              {/* Upload icon inside input (left) */}
              <button
                onClick={handleChatFileSelect}
                className="absolute left-3 top-1/2 transform -translate-y-1/2 text-neutral-400 hover:text-neutral-200 transition-colors z-10"
                title="Upload a document to reference"
              >
                <Paperclip size={18} />
              </button>
              
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                placeholder="Ask about your documents, set reminders, or get help..."
                className="w-full pl-12 pr-4 py-3 bg-neutral-800 border border-neutral-700 rounded-lg text-white placeholder-neutral-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                onDragOver={(e) => {
                  e.preventDefault()
                  setIsDragOver(true)
                }}
                onDragLeave={(e) => {
                  e.preventDefault()
                  setIsDragOver(false)
                }}
                onDrop={(e) => {
                  e.preventDefault()
                  setIsDragOver(false)
                  if (e.dataTransfer.files) {
                    handleChatFileUpload(e.dataTransfer.files)
                  }
                }}
              />
              
              {/* Drag over overlay */}
              {isDragOver && (
                <div className="absolute inset-0 bg-blue-500/20 border-2 border-blue-500 border-dashed rounded-lg flex items-center justify-center">
                  <span className="text-blue-400 font-medium">Drop files here</span>
                </div>
              )}
              
              {/* Legacy uploaded files indicator (if any) */}
              {uploadedFiles.length > 0 && (
                <div className="absolute -top-8 left-12 flex gap-2">
                  {uploadedFiles.slice(0, 2).map((file) => (
                    <div key={file.id} className="flex items-center gap-1 px-2 py-1 bg-neutral-700 rounded text-xs text-neutral-300">
                      {getFileTypeIcon(file.fileMeta.name)}
                      <span className="ml-1">{file.fileMeta.name.length > 12 ? file.fileMeta.name.substring(0, 12) + '...' : file.fileMeta.name}</span>
                    </div>
                  ))}
                  {uploadedFiles.length > 2 && (
                    <div className="flex items-center px-2 py-1 bg-neutral-700 rounded text-xs text-neutral-300">
                      +{uploadedFiles.length - 2} more
                    </div>
                  )}
                </div>
              )}
            </div>
            <button
              onClick={handleSendMessage}
              disabled={!inputValue.trim() && selectedChatFiles.length === 0}
              className="px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg font-medium hover:from-blue-500 hover:to-purple-500 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              <Send size={16} />
              Send
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard 
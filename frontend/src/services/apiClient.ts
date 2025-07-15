interface ApiResponse<T = any> {
  data?: T
  error?: string
  success: boolean
  validationErrors?: Array<{
    field: string
    message: string
    type: string
    input?: any
  }>
}

interface ChatRequest {
  message: string
  session_id?: string
  context?: string
}

interface ChatResponse {
  response: string
  session_id: string
  suggestions: string[]
  needs_confirmation: boolean
  confirmation_data?: any
  tool_used?: string
  tool_count: number
  success: boolean
}

interface ConfirmRequest {
  decision: string
  session_id: string
}

interface ReminderCreate {
  title: string
  date: string
  description?: string
  time?: string
  priority?: string
  category?: string
}

interface Reminder {
  id: number
  title: string
  description: string
  date: string
  time: string
  priority: string
  category: string
  completed: boolean
  created_at: string
}

interface HealthCheck {
  status: string
  timestamp: string
  version: string
  services: {
    database: string
    llm: string
    langchain: string
  }
  endpoints: Record<string, string>
}

interface StatusCheck {
  status: string
  backend: string
  model: string
  timestamp: string
  langchain: string
  database: string
}

interface StartupCheck {
  status: string
  routes_loaded: string[]
  expected_routes: string[]
  all_routes_ready: boolean
  missing_routes: string[]
  timestamp: string
}

interface ActivityHistory {
  summary: {
    total_uploads: number
    total_chats: number
    total_reminders: number
    total_activity: number
  }
  recent_uploads: Array<{
    id: number
    filename: string
    type: string
    file_type: string
    file_size: number
    intent: string
    processed: boolean
    uploaded_at: string
    result: any
  }>
  recent_chats: Array<{
    id: number
    session_id: string
    content: string
    message_type: string
    timestamp: string
    metadata: any
  }>
  recent_reminders: Array<{
    id: number
    title: string
    description: string
    type: string
    date: string
    time: string
    priority: string
    category: string
    completed: boolean
    created_at: string
  }>
  last_activity: string | null
  timestamp: string
}

interface Tool {
  name: string
  description: string
  type: string
}

interface ToolsResponse {
  available_tools: Tool[]
  tool_count: number
  status: string
}

interface TestFullResponse {
  timestamp: string
  overall_status: string
  tests: Record<string, {
    status: string
    response_time?: string
    data?: any
    error?: string
    reason?: string
  }>
  summary: {
    passed: number
    failed: number
    skipped: number
    total: number
  }
}

class ApiClient {
  private baseURL: string
  private isConnected: boolean = false
  private healthCheckInterval: number | null = null

  constructor() {
    // Use proxy in development, direct URL in production
    this.baseURL = (import.meta as any).env?.DEV ? '/api' : 'http://127.0.0.1:8000'
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    const fullUrl = `${this.baseURL}${endpoint}`
    
    // ===== COMPREHENSIVE REQUEST LOGGING =====
    console.log(`🚀 === API REQUEST START ===`)
    console.log(`📍 Endpoint: ${endpoint}`)
    console.log(`🔗 Full URL: ${fullUrl}`)
    console.log(`🔧 Method: ${options.method || 'GET'}`)
    console.log(`📋 Headers:`, options.headers)
    if (options.body) {
      try {
        const bodyContent = typeof options.body === 'string' ? JSON.parse(options.body) : options.body
        console.log(`📝 Request body:`, bodyContent)
      } catch {
        console.log(`📝 Request body: [Non-JSON data]`)
      }
    }
    
    try {
      console.log(`⏳ Making fetch request...`)
      const response = await fetch(fullUrl, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
      })

      console.log(`📊 Response received:`)
      console.log(`  Status: ${response.status} ${response.statusText}`)
      console.log(`  Headers:`, Object.fromEntries(response.headers.entries()))

      if (!response.ok) {
        // Handle 422 validation errors specifically
        if (response.status === 422) {
          try {
            const errorData = await response.json()
            const userFriendlyMessage = errorData.detail || "⚠️ Chat input rejected by server — check formatting or file attachment."
            
            // Log validation details for debugging
            console.error('❌ 422 Validation Error Details:', errorData)
            console.log(`🚀 === API REQUEST COMPLETE (422 ERROR) ===\n`)
            
            return {
              error: userFriendlyMessage,
              success: false,
              validationErrors: errorData.validation_errors || []
            }
          } catch {
            console.error('❌ Failed to parse 422 error response')
            console.log(`🚀 === API REQUEST COMPLETE (422 PARSE ERROR) ===\n`)
            return {
              error: "⚠️ Chat input rejected by server — check formatting or file attachment.",
              success: false
            }
          }
        }
        
        // Handle other HTTP errors
        console.error(`❌ HTTP Error: ${response.status} ${response.statusText}`)
        console.log(`🚀 === API REQUEST COMPLETE (HTTP ERROR) ===\n`)
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      console.log(`✅ Parsing response data...`)
      const data = await response.json()
      console.log(`📦 Response data:`, data)
      console.log(`🚀 === API REQUEST COMPLETE (SUCCESS) ===\n`)
      
      return { data, success: true }
    } catch (error) {
      // ===== COMPREHENSIVE ERROR LOGGING =====
      console.error(`❌ === API REQUEST FAILED ===`)
      console.error(`📍 Endpoint: ${endpoint}`)
      console.error(`🔗 Full URL: ${fullUrl}`)
      console.error(`❌ Error type: ${error instanceof Error ? error.constructor.name : typeof error}`)
      console.error(`❌ Error message: ${error instanceof Error ? error.message : String(error)}`)
      
      if (error instanceof TypeError && error.message.includes('fetch')) {
        console.error(`🌐 Network Error: Backend likely not running or unreachable`)
        console.error(`💡 Solution: Start backend with 'cd backend && python main.py'`)
      } else if (error instanceof Error && error.message.includes('ECONNREFUSED')) {
        console.error(`🔌 Connection Refused: Backend server not accepting connections`)
        console.error(`💡 Solution: Check if backend is running on port 8000`)
      } else if (error instanceof Error && error.message.includes('CORS')) {
        console.error(`🚫 CORS Error: Cross-origin request blocked`)
        console.error(`💡 Solution: Check CORS configuration in backend`)
      }
      
      console.error(`🚀 === API REQUEST COMPLETE (FAILED) ===\n`)
      
      return { 
        error: error instanceof Error ? error.message : 'Unknown error',
        success: false 
      }
    }
  }

  private async uploadRequest<T>(
    endpoint: string,
    formData: FormData
  ): Promise<ApiResponse<T>> {
    const fullUrl = `${this.baseURL}${endpoint}`
    
    // ===== COMPREHENSIVE UPLOAD REQUEST LOGGING =====
    console.log(`📤 === UPLOAD REQUEST START ===`)
    console.log(`📍 Endpoint: ${endpoint}`)
    console.log(`🔗 Full URL: ${fullUrl}`)
    console.log(`🔧 Method: POST`)
    console.log(`📦 FormData contents:`)
    for (const [key, value] of formData.entries()) {
      if (value instanceof File) {
        console.log(`  📄 ${key}: File(${value.name}, ${value.size} bytes, ${value.type})`)
      } else {
        console.log(`  📝 ${key}: ${value}`)
      }
    }
    
    try {
      console.log(`⏳ Making upload request...`)
      const response = await fetch(fullUrl, {
        method: 'POST',
        body: formData,
      })

      console.log(`📊 Upload response received:`)
      console.log(`  Status: ${response.status} ${response.statusText}`)
      console.log(`  Headers:`, Object.fromEntries(response.headers.entries()))

      if (!response.ok) {
        // Handle 422 validation errors specifically
        if (response.status === 422) {
          try {
            const errorData = await response.json()
            const userFriendlyMessage = errorData.detail || "⚠️ File upload rejected by server — check file format or size."
            
            // Log validation details for debugging
            console.error('❌ 422 Upload Validation Error Details:', errorData)
            console.log(`📤 === UPLOAD REQUEST COMPLETE (422 ERROR) ===\n`)
            
            return {
              error: userFriendlyMessage,
              success: false,
              validationErrors: errorData.validation_errors || []
            }
          } catch {
            console.error('❌ Failed to parse 422 upload error response')
            console.log(`📤 === UPLOAD REQUEST COMPLETE (422 PARSE ERROR) ===\n`)
            return {
              error: "⚠️ File upload rejected by server — check file format or size.",
              success: false
            }
          }
        }
        
        // Handle other HTTP errors
        console.error(`❌ Upload HTTP Error: ${response.status} ${response.statusText}`)
        console.log(`📤 === UPLOAD REQUEST COMPLETE (HTTP ERROR) ===\n`)
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      console.log(`✅ Parsing upload response data...`)
      const data = await response.json()
      console.log(`📦 Upload response data:`, data)
      console.log(`📤 === UPLOAD REQUEST COMPLETE (SUCCESS) ===\n`)
      
      return { data, success: true }
    } catch (error) {
      // ===== COMPREHENSIVE UPLOAD ERROR LOGGING =====
      console.error(`❌ === UPLOAD REQUEST FAILED ===`)
      console.error(`📍 Endpoint: ${endpoint}`)
      console.error(`🔗 Full URL: ${fullUrl}`)
      console.error(`❌ Error type: ${error instanceof Error ? error.constructor.name : typeof error}`)
      console.error(`❌ Error message: ${error instanceof Error ? error.message : String(error)}`)
      
      if (error instanceof TypeError && error.message.includes('fetch')) {
        console.error(`🌐 Upload Network Error: Backend likely not running or unreachable`)
        console.error(`💡 Solution: Start backend with 'cd backend && python main.py'`)
      } else if (error instanceof Error && error.message.includes('ECONNREFUSED')) {
        console.error(`🔌 Upload Connection Refused: Backend server not accepting connections`)
        console.error(`💡 Solution: Check if backend is running on port 8000`)
      } else if (error instanceof Error && error.message.includes('CORS')) {
        console.error(`🚫 Upload CORS Error: Cross-origin request blocked`)
        console.error(`💡 Solution: Check CORS configuration in backend`)
      }
      
      console.error(`📤 === UPLOAD REQUEST COMPLETE (FAILED) ===\n`)
      
      return { 
        error: error instanceof Error ? error.message : 'Unknown error',
        success: false 
      }
    }
  }

  // Health check endpoint
  async checkHealth(): Promise<ApiResponse<HealthCheck>> {
    const result = await this.request<HealthCheck>('/health')
    this.isConnected = result.success
    return result
  }

  // Status check endpoint
  async checkStatus(): Promise<ApiResponse<StatusCheck>> {
    const result = await this.request<StatusCheck>('/status')
    return result
  }

  // Startup check endpoint
  async checkStartup(): Promise<ApiResponse<StartupCheck>> {
    const result = await this.request<StartupCheck>('/startup-check')
    return result
  }

  // Start monitoring backend health
  startHealthMonitoring(callback?: (connected: boolean) => void): void {
    this.healthCheckInterval = window.setInterval(async () => {
      const health = await this.checkHealth()
      const wasConnected = this.isConnected
      this.isConnected = health.success
      
      if (callback && wasConnected !== this.isConnected) {
        callback(this.isConnected)
      }
    }, 5000) // Check every 5 seconds
  }

  // Stop health monitoring
  stopHealthMonitoring(): void {
    if (this.healthCheckInterval) {
      clearInterval(this.healthCheckInterval)
      this.healthCheckInterval = null
    }
  }

  // Get connection status
  isBackendConnected(): boolean {
    return this.isConnected
  }

  // Chat endpoints
  async sendChatMessage(request: ChatRequest): Promise<ApiResponse<ChatResponse>> {
    const formData = new FormData()
    formData.append('message', request.message)
    if (request.session_id) {
      formData.append('session_id', request.session_id)
    }
    
    return this.uploadRequest<ChatResponse>('/chat', formData)
  }

  // Streaming chat endpoint
  async sendStreamingChatMessage(
    request: ChatRequest,
    onChunk: (chunk: string) => void,
    onComplete: (response: ChatResponse) => void,
    onError: (error: string) => void
  ): Promise<void> {
    try {
      const formData = new FormData()
      formData.append('message', request.message)
      if (request.session_id) {
        formData.append('session_id', request.session_id)
      }

      const response = await fetch(`${this.baseURL}/chat/stream`, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const reader = response.body?.getReader()
      if (!reader) {
        throw new Error('No response body reader available')
      }

      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6)
            if (data === '[DONE]') {
              return
            }
            
            try {
              const parsed = JSON.parse(data)
              if (parsed.content) {
                onChunk(parsed.content)
              }
              if (parsed.complete) {
                onComplete(parsed)
                return
              }
            } catch (e) {
              console.warn('Failed to parse streaming data:', data)
            }
          }
        }
      }
    } catch (error) {
      console.error('Streaming chat error:', error)
      onError(error instanceof Error ? error.message : 'Unknown streaming error')
    }
  }

  // File upload endpoint
  async uploadFile(file: File, intent?: string): Promise<ApiResponse<any>> {
    const formData = new FormData()
    formData.append('file', file)
    if (intent) {
      formData.append('intent', intent)
    }
    
    return this.uploadRequest('/upload', formData)
  }

  // Confirmation endpoint
  async confirmAction(request: ConfirmRequest): Promise<ApiResponse<any>> {
    return this.request('/confirm', {
      method: 'POST',
      body: JSON.stringify(request),
    })
  }

  // Reminders endpoints
  async getReminders(): Promise<ApiResponse<Reminder[]>> {
    return this.request<Reminder[]>('/reminders/all')
  }

  async createReminder(reminder: ReminderCreate): Promise<ApiResponse<Reminder>> {
    return this.request<Reminder>('/reminders', {
      method: 'POST',
      body: JSON.stringify(reminder),
    })
  }

  // Activity history endpoint
  async getActivityHistory(): Promise<ApiResponse<ActivityHistory>> {
    return this.request<ActivityHistory>('/history/activity')
  }

  // Tools endpoint
  async getAvailableTools(): Promise<ApiResponse<ToolsResponse>> {
    return this.request<ToolsResponse>('/tools/available')
  }

  // Agent management endpoints
  async getAgentSessions(): Promise<ApiResponse<any>> {
    return this.request('/chat/sessions')
  }

  async clearAgentSession(sessionId: string): Promise<ApiResponse<any>> {
    return this.request(`/chat/sessions/${sessionId}`, { method: 'DELETE' })
  }

  // Comprehensive backend test endpoint
  async testFullBackend(): Promise<ApiResponse<TestFullResponse>> {
    return this.request<TestFullResponse>('/test/full', { method: 'POST' })
  }

  // Debug endpoint for testing chat payloads
  async debugChatPayload(payload: any): Promise<ApiResponse<any>> {
    return this.request('/chat/test/debug', {
      method: 'POST',
      body: JSON.stringify(payload),
    })
  }
}

export const apiClient = new ApiClient()

// Type exports for components
export type {
  ApiResponse,
  ChatRequest,
  ChatResponse,
  ConfirmRequest,
  ReminderCreate,
  Reminder,
  HealthCheck,
  StatusCheck,
  StartupCheck,
  ActivityHistory,
  Tool,
  ToolsResponse,
  TestFullResponse
}
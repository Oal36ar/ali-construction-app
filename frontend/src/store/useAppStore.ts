import { create } from 'zustand'
import { ToastProps } from '../components/Toast'

interface FileMeta {
  name: string
  size: number
  uploadedAt: string
  type: string
  id: string
}

interface IntentOption {
  value: 'extract_reminders' | 'send_email' | 'summarize' | 'parse_contacts' | 'custom'
  label: string
  description: string
}

interface UploadedFile {
  id: string
  file: File
  fileMeta: FileMeta
  intent?: IntentOption['value']
  isProcessing: boolean
  processed: boolean
  response?: ParsedResponse
}

interface ParsedResponse {
  type: 'reminders' | 'email_draft' | 'summary' | 'contacts' | 'custom'
  content: any
  message: string
  needsConfirmation?: boolean
}

interface Reminder {
  id: string
  text: string
  date: string
  confirmed: boolean
}

interface Message {
  id: string
  type: 'user' | 'assistant'
  role?: 'user' | 'assistant' // Optional - defaults to type
  content: string
  timestamp: string
  fileMeta?: FileMeta
  reminder?: Reminder
  isLoading?: boolean
  streaming?: boolean
  parsedResponse?: ParsedResponse
  tool_used?: string
}

interface AppState {
  activeRoute: string
  setActiveRoute: (route: string) => void
  sidebarCollapsed: boolean
  setSidebarCollapsed: (collapsed: boolean) => void
  reminderCount: number
  setReminderCount: (count: number) => void
  
  // Chat state
  messages: Message[]
  addMessage: (message: Omit<Message, 'timestamp'> & { id?: string; timestamp?: string }) => void
  updateMessage: (id: string, updates: Partial<Message>) => void
  appendToMessage: (id: string, chunk: string) => void
  clearMessages: () => void
  isUploading: boolean
  setIsUploading: (uploading: boolean) => void
  
  // Enhanced file upload state
  uploadedFiles: UploadedFile[]
  addUploadedFile: (uploadedFile: UploadedFile) => void
  updateUploadedFile: (id: string, updates: Partial<UploadedFile>) => void
  removeUploadedFile: (id: string) => void
  clearUploadedFiles: () => void
  
  // Toast management
  toasts: Omit<ToastProps, 'onDismiss'>[]
  addToast: (toast: Omit<ToastProps, 'onDismiss'>) => void
  removeToast: (id: string) => void
  clearToasts: () => void
}

export const useAppStore = create<AppState>((set, get) => ({
  activeRoute: '/',
  setActiveRoute: (route) => set({ activeRoute: route }),
  sidebarCollapsed: false,
  setSidebarCollapsed: (collapsed) => set({ sidebarCollapsed: collapsed }),
  reminderCount: 0,
  setReminderCount: (count) => set({ reminderCount: count }),
  
  // Chat state
  messages: [],
  addMessage: (message) => set((state) => ({
    messages: [...state.messages, {
      ...message,
      id: message.id || `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      timestamp: message.timestamp || new Date().toISOString(),
      role: message.role || message.type
    }]
  })),
  updateMessage: (id, updates) => set((state) => ({
    messages: state.messages.map(msg => 
      msg.id === id ? { ...msg, ...updates } : msg
    )
  })),
  appendToMessage: (id, chunk) => set((state) => ({
    messages: state.messages.map(msg => 
      msg.id === id ? { ...msg, content: msg.content + chunk } : msg
    )
  })),
  clearMessages: () => set({ messages: [] }),
  isUploading: false,
  setIsUploading: (uploading) => set({ isUploading: uploading }),
  
  // Enhanced file upload state
  uploadedFiles: [],
  addUploadedFile: (uploadedFile) => set((state) => ({
    uploadedFiles: [...state.uploadedFiles, uploadedFile]
  })),
  updateUploadedFile: (id, updates) => set((state) => ({
    uploadedFiles: state.uploadedFiles.map(file => 
      file.id === id ? { ...file, ...updates } : file
    )
  })),
  removeUploadedFile: (id) => set((state) => ({
    uploadedFiles: state.uploadedFiles.filter(file => file.id !== id)
  })),
  clearUploadedFiles: () => set({ uploadedFiles: [] }),
  
  // Toast management
  toasts: [],
  
  addToast: (toast) => {
    set((state) => ({
      toasts: [...state.toasts, toast]
    }))
  },
  
  removeToast: (id) => {
    set((state) => ({
      toasts: state.toasts.filter(toast => toast.id !== id)
    }))
  },
  
  clearToasts: () => {
    set({ toasts: [] })
  }
}))

export const INTENT_OPTIONS: IntentOption[] = [
  {
    value: 'extract_reminders',
    label: 'Extract Reminders',
    description: 'Find and extract dates, deadlines, and tasks'
  },
  {
    value: 'send_email',
    label: 'Send Email Summary',
    description: 'Create an email summary of the content'
  },
  {
    value: 'summarize',
    label: 'Summarize Content',
    description: 'Generate a concise summary of the document'
  },
  {
    value: 'parse_contacts',
    label: 'Parse Contacts',
    description: 'Extract names, emails, and contact information'
  },
  {
    value: 'custom',
    label: 'Custom Command',
    description: 'Specify your own instruction for processing'
  }
]

export type { Message, FileMeta, Reminder, UploadedFile, IntentOption, ParsedResponse } 
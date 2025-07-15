import React, { useEffect, useState } from 'react'
import { X, CheckCircle, AlertCircle, Info, Wifi, WifiOff } from 'lucide-react'

export interface ToastProps {
  id: string
  type: 'success' | 'error' | 'info' | 'warning'
  title: string
  message: string
  duration?: number
  onDismiss: (id: string) => void
}

export interface ToastManagerProps {
  toasts: ToastProps[]
  onDismiss: (id: string) => void
}

const Toast: React.FC<ToastProps> = ({ id, type, title, message, duration = 5000, onDismiss }) => {
  const [isVisible, setIsVisible] = useState(false)

  useEffect(() => {
    // Fade in animation
    const timer = setTimeout(() => setIsVisible(true), 10)
    
    // Auto dismiss
    const dismissTimer = setTimeout(() => {
      handleDismiss()
    }, duration)

    return () => {
      clearTimeout(timer)
      clearTimeout(dismissTimer)
    }
  }, [duration])

  const handleDismiss = () => {
    setIsVisible(false)
    setTimeout(() => onDismiss(id), 300) // Wait for fade out animation
  }

  const getIcon = () => {
    switch (type) {
      case 'success':
        return <CheckCircle size={20} className="text-green-400" />
      case 'error':
        return <AlertCircle size={20} className="text-red-400" />
      case 'warning':
        return <AlertCircle size={20} className="text-yellow-400" />
      case 'info':
        return <Info size={20} className="text-blue-400" />
      default:
        return <Info size={20} className="text-neutral-400" />
    }
  }

  const getBorderColor = () => {
    switch (type) {
      case 'success':
        return 'border-green-500'
      case 'error':
        return 'border-red-500'
      case 'warning':
        return 'border-yellow-500'
      case 'info':
        return 'border-blue-500'
      default:
        return 'border-neutral-500'
    }
  }

  return (
    <div
      className={`
        transform transition-all duration-300 ease-in-out
        ${isVisible ? 'translate-x-0 opacity-100' : 'translate-x-full opacity-0'}
        bg-neutral-800 border-l-4 ${getBorderColor()} rounded-lg shadow-lg p-4 mb-3 max-w-sm
      `}
    >
      <div className="flex items-start gap-3">
        {getIcon()}
        <div className="flex-1 min-w-0">
          <h4 className="text-white font-medium text-sm">{title}</h4>
          <p className="text-neutral-300 text-sm mt-1 leading-relaxed">{message}</p>
        </div>
        <button
          onClick={handleDismiss}
          className="text-neutral-400 hover:text-white transition-colors flex-shrink-0"
        >
          <X size={16} />
        </button>
      </div>
    </div>
  )
}

const ToastManager: React.FC<ToastManagerProps> = ({ toasts, onDismiss }) => {
  if (toasts.length === 0) return null

  return (
    <div className="fixed top-4 right-4 z-50 space-y-2">
      {toasts.map((toast) => (
        <Toast key={toast.id} {...toast} onDismiss={onDismiss} />
      ))}
    </div>
  )
}

// Toast utility functions for easy usage
export const createToast = (
  type: ToastProps['type'],
  title: string,
  message: string,
  duration?: number
): Omit<ToastProps, 'onDismiss'> => ({
  id: `toast-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
  type,
  title,
  message,
  duration
})

export const createConnectionToast = (isConnected: boolean): Omit<ToastProps, 'onDismiss'> => {
  if (isConnected) {
    return createToast(
      'success',
      'Backend Connected',
      'Real-time connection established with AI backend',
      3000
    )
  } else {
    return createToast(
      'error',
      'Backend Disconnected',
      'Lost connection to AI backend. Check if server is running.',
      10000
    )
  }
}

export const createAPIErrorToast = (error: string, endpoint?: string): Omit<ToastProps, 'onDismiss'> => {
  const title = endpoint ? `API Error: ${endpoint}` : 'API Error'
  return createToast('error', title, error, 8000)
}

export const createValidationErrorToast = (errors: any[]): Omit<ToastProps, 'onDismiss'> => {
  const message = errors.length > 0 
    ? errors.map(e => e.message || e.field).join(', ')
    : 'Please check your input and try again'
    
  return createToast('warning', 'Validation Error', message, 6000)
}

export default ToastManager 
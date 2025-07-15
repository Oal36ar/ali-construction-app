import React, { useState, useEffect } from 'react'
import { apiClient } from '../services/apiClient'
import { Check, X, Loader2, Upload, MessageSquare, Calendar, Activity } from 'lucide-react'

interface TestResult {
  name: string
  status: 'pending' | 'success' | 'error'
  message?: string
  details?: any
}

const TestConnection: React.FC = () => {
  const [tests, setTests] = useState<TestResult[]>([
    { name: 'Health Check', status: 'pending' },
    { name: 'Startup Check', status: 'pending' },
    { name: 'Chat API', status: 'pending' },
    { name: 'Reminders API', status: 'pending' },
    { name: 'History API', status: 'pending' }
  ])
  const [isRunning, setIsRunning] = useState(false)

  const updateTest = (name: string, status: 'success' | 'error', message?: string, details?: any) => {
    setTests(prev => prev.map(test => 
      test.name === name 
        ? { ...test, status, message, details }
        : test
    ))
  }

  const runTests = async () => {
    setIsRunning(true)
    
    // Reset all tests
    setTests(prev => prev.map(test => ({ ...test, status: 'pending' })))

    try {
      // Test 1: Health Check
      const healthResult = await apiClient.checkHealth()
      if (healthResult.success) {
        updateTest('Health Check', 'success', 'Backend is healthy', healthResult.data)
      } else {
        updateTest('Health Check', 'error', healthResult.error)
      }

      // Test 2: Startup Check
      const startupResult = await apiClient.checkStartup()
      if (startupResult.success && startupResult.data?.all_routes_ready) {
        updateTest('Startup Check', 'success', 'All routes are ready', startupResult.data)
      } else {
        updateTest('Startup Check', 'error', startupResult.error || 'Routes not ready')
      }

      // Test 3: Chat API
      const chatResult = await apiClient.sendChatMessage({ message: 'Hello, test message' })
      if (chatResult.success) {
        updateTest('Chat API', 'success', 'Chat is working', chatResult.data)
      } else {
        updateTest('Chat API', 'error', chatResult.error)
      }

      // Test 4: Reminders API  
      const remindersResult = await apiClient.getReminders()
      if (remindersResult.success) {
        updateTest('Reminders API', 'success', `Found ${remindersResult.data?.length || 0} reminders`, remindersResult.data)
      } else {
        updateTest('Reminders API', 'error', remindersResult.error)
      }

      // Test 5: History API
      const historyResult = await apiClient.getActivityHistory()
      if (historyResult.success) {
        updateTest('History API', 'success', `${historyResult.data?.summary?.total_activity || 0} total activities`, historyResult.data)
      } else {
        updateTest('History API', 'error', historyResult.error)
      }

    } catch (error) {
      console.error('Test suite error:', error)
    } finally {
      setIsRunning(false)
    }
  }

  useEffect(() => {
    runTests()
  }, [])

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
        return <Check className="text-green-500" size={16} />
      case 'error':
        return <X className="text-red-500" size={16} />
      case 'pending':
      default:
        return <Loader2 className="text-yellow-500 animate-spin" size={16} />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success':
        return 'border-green-500/20 bg-green-500/10'
      case 'error':
        return 'border-red-500/20 bg-red-500/10'
      case 'pending':
      default:
        return 'border-yellow-500/20 bg-yellow-500/10'
    }
  }

  const getTestIcon = (name: string) => {
    switch (name) {
      case 'Chat API':
        return <MessageSquare className="text-blue-400" size={16} />
      case 'Reminders API':
        return <Calendar className="text-purple-400" size={16} />
      case 'History API':
        return <Activity className="text-orange-400" size={16} />
      default:
        return <Check className="text-green-400" size={16} />
    }
  }

  const passedTests = tests.filter(t => t.status === 'success').length
  const totalTests = tests.length

  return (
    <div className="bg-neutral-900 rounded-xl border border-neutral-800 p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-white flex items-center gap-2">
            <Upload className="text-blue-500" size={20} />
            Backend Connection Test
          </h3>
          <p className="text-neutral-400 text-sm">
            Verifying all API endpoints are working
          </p>
        </div>
        <button
          onClick={runTests}
          disabled={isRunning}
          className="bg-blue-600 hover:bg-blue-500 disabled:bg-blue-600/50 text-white px-4 py-2 rounded-lg font-medium transition-colors flex items-center gap-2"
        >
          {isRunning ? (
            <>
              <Loader2 className="animate-spin" size={16} />
              Testing...
            </>
          ) : (
            <>
              <Check size={16} />
              Run Tests
            </>
          )}
        </button>
      </div>

      <div className="space-y-3">
        {tests.map((test) => (
          <div
            key={test.name}
            className={`p-4 rounded-lg border transition-all duration-200 ${getStatusColor(test.status)}`}
          >
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-3">
                {getTestIcon(test.name)}
                <span className="text-white font-medium">{test.name}</span>
              </div>
              {getStatusIcon(test.status)}
            </div>
            
            {test.message && (
              <p className="text-neutral-300 text-sm">
                {test.message}
              </p>
            )}
            
            {test.details && test.status === 'success' && (
              <details className="mt-2">
                <summary className="text-neutral-400 text-xs cursor-pointer hover:text-neutral-300">
                  View Details
                </summary>
                <pre className="text-xs text-neutral-400 mt-2 bg-neutral-800 p-2 rounded overflow-auto max-h-32">
                  {JSON.stringify(test.details, null, 2)}
                </pre>
              </details>
            )}
          </div>
        ))}
      </div>

      <div className="mt-6 text-center">
        <div className="text-lg font-semibold text-white">
          {passedTests}/{totalTests} Tests Passed
        </div>
        {passedTests === totalTests && !isRunning && (
          <p className="text-green-400 text-sm mt-1">
            🎉 All systems operational!
          </p>
        )}
      </div>
    </div>
  )
}

export default TestConnection 
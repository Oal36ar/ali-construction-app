import React, { useState, useEffect, useRef } from 'react'
import { Wifi, WifiOff, Loader2, CheckCircle, AlertCircle, Zap, AlertTriangle } from 'lucide-react'
import { apiClient, HealthCheck, StatusCheck, StartupCheck } from '../services/apiClient'
import { useAppStore } from '../store/useAppStore'
import { createConnectionToast } from './Toast'

interface BackendStatusProps {
  className?: string
}

const BackendStatus: React.FC<BackendStatusProps> = ({ className = '' }) => {
  const [isConnected, setIsConnected] = useState(false)
  const [isChecking, setIsChecking] = useState(true)
  const [healthData, setHealthData] = useState<HealthCheck | null>(null)
  const [statusData, setStatusData] = useState<StatusCheck | null>(null)
  const [startupData, setStartupData] = useState<StartupCheck | null>(null)
  const [error, setError] = useState<string | null>(null)
  
  const { addToast } = useAppStore()
  const previousConnectionStatus = useRef<boolean | null>(null)

  useEffect(() => {
    const checkInitialStatus = async () => {
      setIsChecking(true)
      
      // Check health, status, and startup endpoints
      const [healthResult, statusResult, startupResult] = await Promise.all([
        apiClient.checkHealth(),
        apiClient.checkStatus(),
        apiClient.checkStartup()
      ])
      
      if (healthResult.success && healthResult.data) {
        setIsConnected(true)
        setHealthData(healthResult.data)
        setError(null)
        
        // Show connection toast on initial connect
        if (previousConnectionStatus.current === null) {
          addToast(createConnectionToast(true))
        }
      } else {
        setIsConnected(false)
        setHealthData(null)
        setError(healthResult.error || 'Backend unavailable')
      }

      if (statusResult.success && statusResult.data) {
        setStatusData(statusResult.data)
      }

      if (startupResult.success && startupResult.data) {
        setStartupData(startupResult.data)
      }
      
      previousConnectionStatus.current = healthResult.success
      setIsChecking(false)
    }

    checkInitialStatus()

    // Start health monitoring with toast notifications
    apiClient.startHealthMonitoring(async (connected) => {
      const wasConnected = previousConnectionStatus.current
      
      setIsConnected(connected)
      if (!connected) {
        setHealthData(null)
        setStatusData(null)
        setStartupData(null)
        setError('Connection lost')
        
        // Show disconnection toast
        if (wasConnected === true) {
          addToast(createConnectionToast(false))
        }
      } else {
        // Refresh status and startup when reconnected
        const [statusResult, startupResult] = await Promise.all([
          apiClient.checkStatus(),
          apiClient.checkStartup()
        ])
        
        if (statusResult.success && statusResult.data) {
          setStatusData(statusResult.data)
          setError(null)
        }

        if (startupResult.success && startupResult.data) {
          setStartupData(startupResult.data)
        }
        
        // Show reconnection toast
        if (wasConnected === false) {
          addToast(createConnectionToast(true))
        }
      }
      
      previousConnectionStatus.current = connected
    })

    return () => {
      apiClient.stopHealthMonitoring()
    }
  }, [addToast])

  const getStatusColor = () => {
    if (isChecking) return 'text-yellow-500'
    if (isConnected && startupData?.all_routes_ready) return 'text-green-500'
    if (isConnected && !startupData?.all_routes_ready) return 'text-yellow-500'
    return 'text-red-500'
  }

  const getStatusIcon = () => {
    if (isChecking) return <Loader2 className="animate-spin" size={16} />
    if (isConnected && startupData?.all_routes_ready) return <CheckCircle size={16} />
    if (isConnected && !startupData?.all_routes_ready) return <AlertTriangle size={16} />
    return <AlertCircle size={16} />
  }

  const getStatusText = () => {
    if (isChecking) return 'Checking...'
    if (isConnected && startupData?.all_routes_ready) return 'All Routes Ready'
    if (isConnected && !startupData?.all_routes_ready) return 'Partial Routes'
    return 'Disconnected'
  }

  const getBadgeColor = () => {
    if (isConnected && startupData?.all_routes_ready) return 'bg-green-500'
    if (isConnected && !startupData?.all_routes_ready) return 'bg-yellow-500'
    return 'bg-red-500'
  }

  return (
    <div className={`flex items-center gap-3 ${className}`}>
      {/* Connection Badge */}
      <div className={`flex items-center gap-2 px-3 py-1 rounded-full ${getBadgeColor()} text-white text-sm font-medium`}>
        {getStatusIcon()}
        <span>{getStatusText()}</span>
        {isConnected && startupData?.all_routes_ready && (
          <div className="flex items-center gap-1 ml-2 border-l border-white/30 pl-2">
            <Zap size={12} />
            <span className="text-xs">Live</span>
          </div>
        )}
      </div>
      
      {/* Status Details */}
      {isConnected && (statusData || healthData || startupData) && (
        <div className="flex items-center gap-3 text-xs text-neutral-400">
          {statusData && (
            <div className="flex items-center gap-2">
              <span className="text-green-400">Model:</span>
              <span className="font-mono">{statusData.model}</span>
            </div>
          )}

          {startupData && (
            <div className="flex items-center gap-2">
              <span>•</span>
              <span>Routes:</span>
              <span className={startupData.all_routes_ready ? "text-green-400" : "text-yellow-400"}>
                {startupData.routes_loaded.length}/{startupData.expected_routes.length}
              </span>
              {!startupData.all_routes_ready && (
                <span className="text-red-400" title={`Missing: ${startupData.missing_routes.join(', ')}`}>
                  ⚠️
                </span>
              )}
            </div>
          )}
          
          {healthData && (
            <div className="flex items-center gap-2">
              <span>•</span>
              <span>v{healthData.version}</span>
              <span>•</span>
              <span className="flex items-center gap-1">
                <Wifi size={12} />
                Backend
              </span>
            </div>
          )}
        </div>
      )}
      
      {/* Error State */}
      {error && (
        <div className="flex items-center gap-1 text-xs text-red-400">
          <WifiOff size={12} />
          <span>{error}</span>
        </div>
      )}
    </div>
  )
}

export default BackendStatus 
import React, { useEffect, useState } from 'react'
import { apiClient, ActivityHistory } from '../services/apiClient'
import { 
  Calendar, 
  Clock, 
  CheckCircle2,
  AlertCircle,
  XCircle,
  Mail,
  Activity as ActivityIcon,
  FileText,
  Users,
  MapPin,
  TrendingUp,
  Loader2
} from 'lucide-react'

interface Reminder {
  id: string
  title: string
  date: string
  time: string
  priority: 'high' | 'medium' | 'low'
  category: string
  completed: boolean
}

interface EmailSent {
  id: string
  subject: string
  timestamp: string
  status: 'delivered' | 'pending' | 'failed'
  recipient: string
}

interface Event {
  id: string
  title: string
  description: string
  date: string
  type: 'meeting' | 'deadline' | 'inspection'
}

const Activity: React.FC = () => {
  const [activityData, setActivityData] = useState<ActivityHistory | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchActivityData()
  }, [])

  const fetchActivityData = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const result = await apiClient.getActivityHistory()
      
      if (result.success && result.data) {
        setActivityData(result.data)
      } else {
        throw new Error(result.error || 'Failed to fetch activity data')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch activity data')
      console.error('Error fetching activity data:', err)
    } finally {
      setLoading(false)
    }
  }

  // Use actual reminders from backend
  const reminders = activityData?.recent_reminders.map((reminder) => ({
    id: reminder.id.toString(),
    title: reminder.title,
    date: reminder.date,
    time: reminder.time,
    priority: reminder.priority as 'high' | 'medium' | 'low',
    category: reminder.category,
    completed: reminder.completed
  })) || []

  const groupedReminders = reminders.reduce((groups, reminder) => {
    const date = reminder.date
    if (!groups[date]) {
      groups[date] = []
    }
    groups[date].push(reminder)
    return groups
  }, {} as Record<string, Reminder[]>)

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'text-red-400 bg-red-400/10 border-red-400/20'
      case 'medium': return 'text-yellow-400 bg-yellow-400/10 border-yellow-400/20'
      case 'low': return 'text-green-400 bg-green-400/10 border-green-400/20'
      default: return 'text-neutral-400 bg-neutral-400/10 border-neutral-400/20'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'delivered': return <CheckCircle2 className="text-green-500" size={16} />
      case 'pending': return <Clock className="text-yellow-500" size={16} />
      case 'failed': return <XCircle className="text-red-500" size={16} />
      default: return <AlertCircle className="text-neutral-500" size={16} />
    }
  }

  const getStatusBadge = (status: string) => {
    const baseClasses = "px-2 py-1 text-xs font-medium rounded-full border"
    switch (status) {
      case 'delivered': return `${baseClasses} text-green-400 bg-green-400/10 border-green-400/20`
      case 'pending': return `${baseClasses} text-yellow-400 bg-yellow-400/10 border-yellow-400/20`
      case 'failed': return `${baseClasses} text-red-400 bg-red-400/10 border-red-400/20`
      default: return `${baseClasses} text-neutral-400 bg-neutral-400/10 border-neutral-400/20`
    }
  }

  const getEventColor = (type: string) => {
    switch (type) {
      case 'inspection': return 'text-blue-400'
      case 'meeting': return 'text-yellow-400'
      case 'deadline': return 'text-green-400'
      default: return 'text-neutral-400'
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', { 
      weekday: 'long', 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    })
  }

  if (loading) {
    return (
      <div className="p-8 max-w-7xl mx-auto">
        <div className="flex items-center justify-center h-64">
          <div className="flex items-center gap-3">
            <Loader2 className="animate-spin text-blue-500" size={24} />
            <span className="text-neutral-400">Loading activity data...</span>
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-8 max-w-7xl mx-auto">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <AlertCircle className="mx-auto text-red-500 mb-4" size={48} />
            <h3 className="text-xl font-semibold text-red-400 mb-2">Error Loading Activity</h3>
            <p className="text-neutral-400 mb-4">{error}</p>
            <button
              onClick={fetchActivityData}
              className="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg transition-colors"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="p-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2 flex items-center gap-3">
          <ActivityIcon className="text-blue-500" />
          Activity Log
        </h1>
        <p className="text-neutral-400">
          Track reminders, email notifications, and upcoming events
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Reminders Overview */}
        <div className="lg:col-span-2">
          <div className="bg-neutral-900 rounded-xl border border-neutral-800 overflow-hidden">
            <div className="bg-neutral-800 px-6 py-4 border-b border-neutral-700">
              <div className="flex items-center gap-3">
                <FileText className="text-purple-500" size={20} />
                <h2 className="text-xl font-semibold text-white">Recent Activity</h2>
                <span className="text-neutral-400 text-sm">
                  ({activityData?.summary.total_reminders || 0} reminders, {activityData?.summary.total_uploads || 0} uploads, {activityData?.summary.total_chats || 0} chats)
                </span>
              </div>
            </div>

            <div className="p-6 space-y-6 max-h-96 overflow-y-auto">
              {Object.keys(groupedReminders).length === 0 ? (
                <div className="text-center py-8">
                  <FileText className="mx-auto text-neutral-500 mb-4" size={48} />
                  <p className="text-neutral-400">No recent activity</p>
                </div>
              ) : (
                Object.entries(groupedReminders)
                  .sort(([a], [b]) => new Date(a).getTime() - new Date(b).getTime())
                  .map(([date, dateReminders]) => (
                    <div key={date} className="space-y-3">
                      <div className="flex items-center gap-2">
                        <Calendar className="text-blue-400" size={16} />
                        <h3 className="font-medium text-white">{formatDate(date)}</h3>
                      </div>
                      <div className="space-y-2 ml-6">
                        {dateReminders
                          .sort((a, b) => a.time.localeCompare(b.time))
                          .map((reminder) => (
                            <div
                              key={reminder.id}
                              className="flex items-center gap-3 p-3 bg-neutral-800 rounded-lg border border-neutral-700"
                            >
                              <div className="flex-shrink-0">
                                {reminder.completed ? (
                                  <CheckCircle2 className="text-green-500" size={16} />
                                ) : (
                                  <AlertCircle className="text-blue-400" size={16} />
                                )}
                              </div>
                              
                              <div className="flex-1 min-w-0">
                                <div className="flex items-center gap-2 mb-1">
                                  <h4 className={`font-medium ${
                                    reminder.completed ? 'text-neutral-400 line-through' : 'text-white'
                                  }`}>
                                    {reminder.title}
                                  </h4>
                                  <span className={`px-2 py-1 text-xs font-medium rounded-full border ${getPriorityColor(reminder.priority)}`}>
                                    {reminder.priority}
                                  </span>
                                </div>
                                <div className="flex items-center gap-2 text-sm text-neutral-400">
                                  <Clock size={12} />
                                  {reminder.time} • {reminder.category}
                                </div>
                              </div>
                            </div>
                          ))}
                      </div>
                    </div>
                  ))
              )}
            </div>
          </div>
        </div>

        {/* Right Column */}
        <div className="space-y-6">
          {/* Recently Sent Emails */}
          <div className="bg-neutral-900 rounded-xl border border-neutral-800">
            <div className="bg-neutral-800 px-6 py-4 border-b border-neutral-700">
              <div className="flex items-center gap-3">
                <Mail className="text-green-500" size={20} />
                <h2 className="text-lg font-semibold text-white">Recently Sent Emails</h2>
              </div>
            </div>
            
            <div className="p-6 space-y-3 max-h-80 overflow-y-auto">
              {!activityData?.recent_chats.length ? (
                <div className="text-center py-6">
                  <Mail className="mx-auto text-neutral-500 mb-2" size={32} />
                  <p className="text-neutral-400 text-sm">No recent chats</p>
                </div>
              ) : (
                activityData.recent_chats.slice(0, 10).map((chat, index) => (
                  <div key={index} className="p-3 bg-neutral-800 rounded-lg border border-neutral-700">
                    <div className="flex items-start gap-3">
                      <div className="flex-shrink-0 mt-1">
                        {chat.message_type === 'user' ? (
                          <CheckCircle2 className="text-blue-500" size={16} />
                        ) : (
                          <AlertCircle className="text-green-500" size={16} />
                        )}
                      </div>
                      <div className="flex-1 min-w-0">
                        <h4 className="text-white font-medium text-sm mb-1 truncate">
                          {chat.message_type === 'user' ? 'User' : 'Assistant'}: {chat.content}
                        </h4>
                        <div className="flex items-center justify-between">
                          <span className="text-neutral-400 text-xs">
                            {new Date(chat.timestamp).toLocaleString()}
                          </span>
                          <span className={getStatusBadge('delivered')}>
                            {chat.message_type}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Upcoming Events */}
          <div className="bg-neutral-900 rounded-xl border border-neutral-800">
            <div className="bg-neutral-800 px-6 py-4 border-b border-neutral-700">
              <div className="flex items-center gap-3">
                <TrendingUp className="text-orange-500" size={20} />
                <h2 className="text-lg font-semibold text-white">Upcoming Events</h2>
              </div>
            </div>
            
            <div className="p-6 space-y-3">
              {!activityData?.recent_uploads.length ? (
                <div className="text-center py-6">
                  <Calendar className="mx-auto text-neutral-500 mb-2" size={32} />
                  <p className="text-neutral-400 text-sm">No recent uploads</p>
                </div>
              ) : (
                activityData.recent_uploads.map((upload, index) => (
                  <div key={index} className="flex items-center gap-3 p-3 bg-neutral-800 rounded-lg border border-neutral-700">
                    <div className="text-center flex-shrink-0">
                      <div className="text-lg font-bold text-blue-400">
                        {new Date(upload.uploaded_at).getDate()}
                      </div>
                      <div className="text-neutral-500 text-xs">
                        {new Date(upload.uploaded_at).toLocaleDateString('en-US', { month: 'short' })}
                      </div>
                    </div>
                    <div className="flex-1">
                      <div className="text-neutral-300 font-medium text-sm">{upload.filename}</div>
                      <div className="text-neutral-500 text-xs">{upload.file_type}</div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Activity
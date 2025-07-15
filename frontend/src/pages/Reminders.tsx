import React, { useEffect, useState } from 'react'
import { useAppStore } from '../store/useAppStore'
import { apiClient, Reminder as ApiReminder, ReminderCreate } from '../services/apiClient'
import { 
  Calendar, 
  Clock, 
  FileText, 
  Plus, 
  Search,
  Filter,
  AlertCircle,
  CheckCircle2,
  Loader2,
  X
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

const Reminders: React.FC = () => {
  const { setReminderCount } = useAppStore()
  const [searchTerm, setSearchTerm] = useState('')
  const [filterStatus, setFilterStatus] = useState<'all' | 'active' | 'completed'>('all')
  const [reminders, setReminders] = useState<Reminder[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showAddModal, setShowAddModal] = useState(false)
  const [isCreating, setIsCreating] = useState(false)
  const [newReminder, setNewReminder] = useState<ReminderCreate>({
    title: '',
    date: '',
    time: '09:00',
    description: '',
    priority: 'medium',
    category: 'general'
  })

  useEffect(() => {
    fetchReminders()
  }, [])

  const fetchReminders = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const result = await apiClient.getReminders()
      
      if (result.success && result.data) {
        // Transform API response to match our interface
        const transformedReminders: Reminder[] = result.data.map(apiReminder => ({
          id: apiReminder.id.toString(),
          title: apiReminder.title,
          date: apiReminder.date,
          time: apiReminder.time || '09:00',
          priority: (apiReminder.priority || 'medium') as 'high' | 'medium' | 'low',
          category: apiReminder.category || 'General',
          completed: apiReminder.completed
        }))
        
        setReminders(transformedReminders)
      } else {
        throw new Error(result.error || 'Failed to fetch reminders')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch reminders')
      console.error('Error fetching reminders:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    const activeReminders = reminders.filter(r => !r.completed)
    setReminderCount(activeReminders.length)
  }, [reminders, setReminderCount])

  const filteredReminders = reminders.filter(reminder => {
    const matchesSearch = reminder.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         reminder.category.toLowerCase().includes(searchTerm.toLowerCase())
    
    const matchesFilter = filterStatus === 'all' || 
                         (filterStatus === 'active' && !reminder.completed) ||
                         (filterStatus === 'completed' && reminder.completed)
    
    return matchesSearch && matchesFilter
  })

  const groupedReminders = filteredReminders.reduce((groups, reminder) => {
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

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', { 
      weekday: 'long', 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    })
  }

  const handleCreateReminder = async () => {
    if (!newReminder.title || !newReminder.date) {
      setError('Please fill in title and date')
      return
    }

    try {
      setIsCreating(true)
      setError(null)
      
      const result = await apiClient.createReminder(newReminder)
      
      if (result.success) {
        // Reset form
        setNewReminder({
          title: '',
          date: '',
          time: '09:00',
          description: '',
          priority: 'medium',
          category: 'general'
        })
        setShowAddModal(false)
        
        // Refresh reminders list
        await fetchReminders()
      } else {
        throw new Error(result.error || 'Failed to create reminder')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create reminder')
      console.error('Error creating reminder:', err)
    } finally {
      setIsCreating(false)
    }
  }

  if (loading) {
    return (
      <div className="p-8 max-w-6xl mx-auto">
        <div className="flex items-center justify-center h-64">
          <div className="flex items-center gap-3">
            <Loader2 className="animate-spin text-blue-500" size={24} />
            <span className="text-neutral-400">Loading reminders...</span>
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-8 max-w-6xl mx-auto">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <AlertCircle className="mx-auto text-red-500 mb-4" size={48} />
            <h3 className="text-xl font-semibold text-red-400 mb-2">Error Loading Reminders</h3>
            <p className="text-neutral-400 mb-4">{error}</p>
            <button
              onClick={fetchReminders}
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
    <div className="p-8 max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Reminders</h1>
          <p className="text-neutral-400">
            Manage your important dates and deadlines
          </p>
        </div>
        <button 
          onClick={() => setShowAddModal(true)}
          className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-4 py-2 rounded-lg font-medium hover:from-blue-500 hover:to-purple-500 transition-all duration-200 flex items-center gap-2"
        >
          <Plus size={20} />
          Add Reminder
        </button>
      </div>

      {/* Filters and Search */}
      <div className="flex flex-col sm:flex-row gap-4 mb-6">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-neutral-400" size={20} />
          <input
            type="text"
            placeholder="Search reminders..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-neutral-800 border border-neutral-700 rounded-lg text-white placeholder-neutral-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
        <div className="flex gap-2">
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value as any)}
            className="px-4 py-2 bg-neutral-800 border border-neutral-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">All</option>
            <option value="active">Active</option>
            <option value="completed">Completed</option>
          </select>
          <button className="px-4 py-2 bg-neutral-800 border border-neutral-700 rounded-lg text-white hover:bg-neutral-700 transition-colors flex items-center gap-2">
            <Filter size={16} />
            Filter
          </button>
        </div>
      </div>

      {/* Reminders List */}
      <div className="space-y-6">
        {Object.keys(groupedReminders).length === 0 ? (
          <div className="text-center py-12">
            <FileText className="mx-auto text-neutral-500 mb-4" size={48} />
            <h3 className="text-xl font-semibold text-neutral-400 mb-2">No reminders found</h3>
            <p className="text-neutral-500">Try adjusting your search or filter criteria</p>
          </div>
        ) : (
          Object.entries(groupedReminders)
            .sort(([a], [b]) => new Date(a).getTime() - new Date(b).getTime())
            .map(([date, dateReminders]) => (
              <div key={date} className="bg-neutral-900 rounded-xl border border-neutral-800 overflow-hidden">
                <div className="bg-neutral-800 px-6 py-4 border-b border-neutral-700">
                  <div className="flex items-center gap-3">
                    <Calendar className="text-blue-400" size={20} />
                    <h3 className="text-lg font-semibold text-white">{formatDate(date)}</h3>
                    <span className="text-neutral-400 text-sm">
                      ({dateReminders.length} reminder{dateReminders.length !== 1 ? 's' : ''})
                    </span>
                  </div>
                </div>
                <div className="p-6 space-y-4">
                  {dateReminders
                    .sort((a, b) => a.time.localeCompare(b.time))
                    .map((reminder) => (
                      <div
                        key={reminder.id}
                        className={`flex items-center gap-4 p-4 rounded-lg border transition-all duration-200 hover:shadow-md ${
                          reminder.completed 
                            ? 'bg-neutral-800/50 border-neutral-700/50 opacity-75' 
                            : 'bg-neutral-800 border-neutral-700 hover:border-neutral-600'
                        }`}
                      >
                        <div className="flex-shrink-0">
                          {reminder.completed ? (
                            <CheckCircle2 className="text-green-500" size={20} />
                          ) : (
                            <AlertCircle className="text-blue-400" size={20} />
                          )}
                        </div>
                        
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-3 mb-1">
                            <h4 className={`font-medium ${
                              reminder.completed ? 'text-neutral-400 line-through' : 'text-white'
                            }`}>
                              {reminder.title}
                            </h4>
                            <span className={`px-2 py-1 text-xs font-medium rounded-full border ${getPriorityColor(reminder.priority)}`}>
                              {reminder.priority}
                            </span>
                          </div>
                          <div className="flex items-center gap-4 text-sm text-neutral-400">
                            <div className="flex items-center gap-1">
                              <Clock size={14} />
                              {reminder.time}
                            </div>
                            <span>•</span>
                            <span>{reminder.category}</span>
                          </div>
                        </div>
                        
                        <button className="text-neutral-400 hover:text-white transition-colors">
                          <FileText size={16} />
                        </button>
                      </div>
                    ))}
                </div>
              </div>
            ))
        )}
      </div>

      {/* Add Reminder Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-neutral-900 rounded-xl border border-neutral-800 w-full max-w-md">
            <div className="flex items-center justify-between p-6 border-b border-neutral-800">
              <h2 className="text-xl font-semibold text-white">Add New Reminder</h2>
              <button
                onClick={() => setShowAddModal(false)}
                className="text-neutral-400 hover:text-white transition-colors"
              >
                <X size={20} />
              </button>
            </div>
            
            <div className="p-6 space-y-4">
              {error && (
                <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3">
                  <p className="text-red-400 text-sm">{error}</p>
                </div>
              )}
              
              <div>
                <label className="block text-sm font-medium text-neutral-300 mb-2">
                  Title *
                </label>
                <input
                  type="text"
                  value={newReminder.title}
                  onChange={(e) => setNewReminder({ ...newReminder, title: e.target.value })}
                  className="w-full px-3 py-2 bg-neutral-800 border border-neutral-700 rounded-lg text-white placeholder-neutral-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Enter reminder title"
                />
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-neutral-300 mb-2">
                    Date *
                  </label>
                  <input
                    type="date"
                    value={newReminder.date}
                    onChange={(e) => setNewReminder({ ...newReminder, date: e.target.value })}
                    className="w-full px-3 py-2 bg-neutral-800 border border-neutral-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-neutral-300 mb-2">
                    Time
                  </label>
                  <input
                    type="time"
                    value={newReminder.time}
                    onChange={(e) => setNewReminder({ ...newReminder, time: e.target.value })}
                    className="w-full px-3 py-2 bg-neutral-800 border border-neutral-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-neutral-300 mb-2">
                  Description
                </label>
                <textarea
                  value={newReminder.description}
                  onChange={(e) => setNewReminder({ ...newReminder, description: e.target.value })}
                  className="w-full px-3 py-2 bg-neutral-800 border border-neutral-700 rounded-lg text-white placeholder-neutral-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Enter description (optional)"
                  rows={3}
                />
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-neutral-300 mb-2">
                    Priority
                  </label>
                  <select
                    value={newReminder.priority}
                    onChange={(e) => setNewReminder({ ...newReminder, priority: e.target.value })}
                    className="w-full px-3 py-2 bg-neutral-800 border border-neutral-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-neutral-300 mb-2">
                    Category
                  </label>
                  <input
                    type="text"
                    value={newReminder.category}
                    onChange={(e) => setNewReminder({ ...newReminder, category: e.target.value })}
                    className="w-full px-3 py-2 bg-neutral-800 border border-neutral-700 rounded-lg text-white placeholder-neutral-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Category"
                  />
                </div>
              </div>
            </div>
            
            <div className="flex items-center justify-end gap-3 p-6 border-t border-neutral-800">
              <button
                onClick={() => setShowAddModal(false)}
                className="px-4 py-2 text-neutral-400 hover:text-white transition-colors"
                disabled={isCreating}
              >
                Cancel
              </button>
              <button
                onClick={handleCreateReminder}
                disabled={isCreating || !newReminder.title || !newReminder.date}
                className="bg-blue-600 hover:bg-blue-500 disabled:bg-neutral-700 disabled:text-neutral-400 text-white px-4 py-2 rounded-lg transition-colors flex items-center gap-2"
              >
                {isCreating ? (
                  <>
                    <Loader2 className="animate-spin" size={16} />
                    Creating...
                  </>
                ) : (
                  <>
                    <Plus size={16} />
                    Create Reminder
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Reminders
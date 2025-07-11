import React, { useState } from 'react'
import { 
  Bell, 
  Zap, 
  Shield, 
  Database,
  Eye,
  EyeOff,
  Save,
  RefreshCw
} from 'lucide-react'

const Settings: React.FC = () => {
  const [notifications, setNotifications] = useState({
    email: true,
    push: false,
    sms: true
  })
  
  const [apiKey, setApiKey] = useState('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')
  const [showApiKey, setShowApiKey] = useState(false)
  const [autoSync, setAutoSync] = useState(true)
  const [syncInterval, setSyncInterval] = useState(30)

  const handleSave = () => {
    // Handle save logic here
    console.log('Settings saved:', { notifications, apiKey, autoSync, syncInterval })
  }

  const handleTestConnection = () => {
    // Handle test connection logic
    console.log('Testing API connection...')
  }

  return (
    <div className="p-8 max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">Settings</h1>
        <p className="text-neutral-400">
          Configure your integrations and preferences
        </p>
      </div>

      <div className="space-y-6">
        {/* Notifications Section */}
        <div className="bg-neutral-900 rounded-xl p-6 border border-neutral-800">
          <div className="flex items-center gap-3 mb-6">
            <Bell className="text-blue-500" size={24} />
            <h2 className="text-xl font-semibold text-white">Notifications</h2>
          </div>
          
          <div className="space-y-4">
            <div className="flex items-center justify-between py-3">
              <div>
                <h3 className="text-white font-medium">Email Notifications</h3>
                <p className="text-neutral-400 text-sm">Get notified about important reminders via email</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={notifications.email}
                  onChange={(e) => setNotifications(prev => ({ ...prev, email: e.target.checked }))}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-neutral-700 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
              </label>
            </div>

            <div className="flex items-center justify-between py-3">
              <div>
                <h3 className="text-white font-medium">Push Notifications</h3>
                <p className="text-neutral-400 text-sm">Browser notifications for urgent reminders</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={notifications.push}
                  onChange={(e) => setNotifications(prev => ({ ...prev, push: e.target.checked }))}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-neutral-700 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
              </label>
            </div>

            <div className="flex items-center justify-between py-3">
              <div>
                <h3 className="text-white font-medium">SMS Notifications</h3>
                <p className="text-neutral-400 text-sm">Text messages for critical deadlines</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={notifications.sms}
                  onChange={(e) => setNotifications(prev => ({ ...prev, sms: e.target.checked }))}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-neutral-700 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
              </label>
            </div>
          </div>
        </div>

        {/* API Integration Section */}
        <div className="bg-neutral-900 rounded-xl p-6 border border-neutral-800">
          <div className="flex items-center gap-3 mb-6">
            <Zap className="text-yellow-500" size={24} />
            <h2 className="text-xl font-semibold text-white">API Integration</h2>
          </div>
          
          <div className="space-y-4">
            <div>
              <label className="block text-white font-medium mb-2">OpenRouter API Key</label>
              <div className="relative">
                <input
                  type={showApiKey ? 'text' : 'password'}
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  className="w-full px-4 py-2 pr-20 bg-neutral-800 border border-neutral-700 rounded-lg text-white placeholder-neutral-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Enter your OpenRouter API key"
                />
                <button
                  type="button"
                  onClick={() => setShowApiKey(!showApiKey)}
                  className="absolute right-12 top-1/2 transform -translate-y-1/2 text-neutral-400 hover:text-white transition-colors"
                >
                  {showApiKey ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
                <button
                  type="button"
                  onClick={handleTestConnection}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-blue-400 hover:text-blue-300 transition-colors"
                >
                  <RefreshCw size={16} />
                </button>
              </div>
              <p className="text-neutral-400 text-xs mt-1">
                Used for AI-powered PDF processing and reminder extraction
              </p>
            </div>

            <div className="flex items-center justify-between py-3">
              <div>
                <h3 className="text-white font-medium">Auto-Sync</h3>
                <p className="text-neutral-400 text-sm">Automatically sync reminders with external services</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={autoSync}
                  onChange={(e) => setAutoSync(e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-neutral-700 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
              </label>
            </div>

            {autoSync && (
              <div>
                <label className="block text-white font-medium mb-2">Sync Interval (minutes)</label>
                <select
                  value={syncInterval}
                  onChange={(e) => setSyncInterval(Number(e.target.value))}
                  className="w-full px-4 py-2 bg-neutral-800 border border-neutral-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value={15}>15 minutes</option>
                  <option value={30}>30 minutes</option>
                  <option value={60}>1 hour</option>
                  <option value={180}>3 hours</option>
                  <option value={360}>6 hours</option>
                </select>
              </div>
            )}
          </div>
        </div>

        {/* Security Section */}
        <div className="bg-neutral-900 rounded-xl p-6 border border-neutral-800">
          <div className="flex items-center gap-3 mb-6">
            <Shield className="text-green-500" size={24} />
            <h2 className="text-xl font-semibold text-white">Security & Privacy</h2>
          </div>
          
          <div className="space-y-4">
            <div className="flex items-center justify-between py-3">
              <div>
                <h3 className="text-white font-medium">Two-Factor Authentication</h3>
                <p className="text-neutral-400 text-sm">Add an extra layer of security to your account</p>
              </div>
              <button className="bg-blue-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-blue-500 transition-colors">
                Enable 2FA
              </button>
            </div>

            <div className="flex items-center justify-between py-3">
              <div>
                <h3 className="text-white font-medium">Data Encryption</h3>
                <p className="text-neutral-400 text-sm">All data is encrypted at rest and in transit</p>
              </div>
              <span className="text-green-400 font-medium">Enabled</span>
            </div>

            <div className="flex items-center justify-between py-3">
              <div>
                <h3 className="text-white font-medium">Session Timeout</h3>
                <p className="text-neutral-400 text-sm">Automatically log out after inactivity</p>
              </div>
              <select className="px-3 py-1 bg-neutral-800 border border-neutral-700 rounded text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
                <option value={30}>30 minutes</option>
                <option value={60}>1 hour</option>
                <option value={240}>4 hours</option>
                <option value={480}>8 hours</option>
              </select>
            </div>
          </div>
        </div>

        {/* Data Management Section */}
        <div className="bg-neutral-900 rounded-xl p-6 border border-neutral-800">
          <div className="flex items-center gap-3 mb-6">
            <Database className="text-purple-500" size={24} />
            <h2 className="text-xl font-semibold text-white">Data Management</h2>
          </div>
          
          <div className="space-y-4">
            <div className="flex items-center justify-between py-3">
              <div>
                <h3 className="text-white font-medium">Export Data</h3>
                <p className="text-neutral-400 text-sm">Download all your reminders and data</p>
              </div>
              <button className="bg-neutral-700 text-white px-4 py-2 rounded-lg font-medium hover:bg-neutral-600 transition-colors">
                Export
              </button>
            </div>

            <div className="flex items-center justify-between py-3">
              <div>
                <h3 className="text-white font-medium">Clear Cache</h3>
                <p className="text-neutral-400 text-sm">Clear stored data and reset preferences</p>
              </div>
              <button className="bg-neutral-700 text-white px-4 py-2 rounded-lg font-medium hover:bg-neutral-600 transition-colors">
                Clear
              </button>
            </div>

            <div className="flex items-center justify-between py-3">
              <div>
                <h3 className="text-red-400 font-medium">Delete Account</h3>
                <p className="text-neutral-400 text-sm">Permanently delete your account and all data</p>
              </div>
              <button className="bg-red-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-red-500 transition-colors">
                Delete
              </button>
            </div>
          </div>
        </div>

        {/* Save Button */}
        <div className="flex justify-end pt-6">
          <button
            onClick={handleSave}
            className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-3 rounded-lg font-medium hover:from-blue-500 hover:to-purple-500 transition-all duration-200 flex items-center gap-2"
          >
            <Save size={20} />
            Save Changes
          </button>
        </div>
      </div>
    </div>
  )
}

export default Settings 
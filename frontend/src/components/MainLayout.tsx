import React, { useEffect } from 'react'
import { Outlet, useLocation, Link } from 'react-router-dom'
import { Home, FileText, Settings, Activity } from 'lucide-react'
import { useAppStore } from '../store/useAppStore'
import BackendStatus from './BackendStatus'
import ToastManager from './Toast'

const MainLayout: React.FC = () => {
  const location = useLocation()
  const { activeRoute, setActiveRoute, toasts, removeToast } = useAppStore()

  useEffect(() => {
    setActiveRoute(location.pathname)
  }, [location.pathname, setActiveRoute])

  const navigationItems = [
    { path: '/', icon: Home, label: 'Dashboard' },
    { path: '/activity', icon: Activity, label: 'Activity Log' },
    { path: '/reminders', icon: FileText, label: 'Reminders' },
    { path: '/settings', icon: Settings, label: 'Settings' },
  ]

  return (
    <div className="min-h-screen bg-neutral-950 text-white flex">
      {/* Toast Manager */}
      <ToastManager 
        toasts={toasts.map(toast => ({ ...toast, onDismiss: removeToast }))} 
        onDismiss={removeToast} 
      />
      
      {/* Sidebar */}
      <aside className="fixed left-0 top-0 h-screen w-16 bg-neutral-900 border-r border-neutral-800 z-40">
        <nav className="flex flex-col items-center py-8 space-y-4">
          {navigationItems.map(({ path, icon: Icon, label }) => (
            <Link
              key={path}
              to={path}
              className={`
                group relative p-3 rounded-xl transition-all duration-200 ease-out
                ${activeRoute === path 
                  ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg' 
                  : 'text-neutral-400 hover:text-white hover:bg-neutral-800'
                }
                focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-neutral-900
              `}
              aria-label={label}
            >
              <Icon 
                size={20} 
                className={`transition-transform duration-200 ${
                  activeRoute === path ? 'scale-110' : 'group-hover:scale-105'
                }`} 
              />
              
              {/* Tooltip */}
              <div className="absolute left-full ml-3 px-2 py-1 bg-neutral-800 text-white text-sm rounded-md opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 whitespace-nowrap z-50">
                {label}
                <div className="absolute left-0 top-1/2 transform -translate-x-1 -translate-y-1/2 w-2 h-2 bg-neutral-800 rotate-45"></div>
              </div>
            </Link>
          ))}
        </nav>
      </aside>

      {/* Main Content */}
      <main className="ml-16 flex-1">
        {/* Backend Status Bar */}
        <div className="sticky top-0 z-30 bg-neutral-900/95 backdrop-blur-sm border-b border-neutral-800 px-6 py-3">
          <BackendStatus />
        </div>
        
        <Outlet />
      </main>
    </div>
  )
}

export default MainLayout 
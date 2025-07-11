# Construction Dashboard

A modern, responsive React dashboard for construction management with TailwindCSS styling and Lucide icons.

## Features

- **Modern UI**: Clean, dark-themed interface with smooth animations
- **Responsive Design**: Works seamlessly across mobile, tablet, and desktop
- **Accessibility**: Full keyboard navigation and ARIA labels
- **Interactive Components**: Hover effects, focus states, and smooth transitions
- **Real-time Metrics**: Dashboard cards showing project statistics
- **Command Input**: Natural language command interface

## Components

### Sidebar
- Fixed left navigation with icon-only buttons
- Home, Messages, AI Assistant, Settings, History
- Active state highlighting and tooltips
- Smooth hover and focus animations

### Top Navigation
- Company branding and welcome message
- Gradient "Upgrade" button with crown icon
- Responsive design with backdrop blur

### Dashboard Metrics
- 4 metric cards: Active Projects, Pending Approvals, Upcoming Inspections, Overdue Invoices
- Color-coded icons and gradients
- Hover animations and interactive states

### Input Box
- Command input with attachment and send buttons
- Natural language placeholder text
- Form validation and submission handling

## Tech Stack

- **React 18** - Modern function components with hooks
- **Vite** - Fast development build tool
- **TailwindCSS 3** - Utility-first styling
- **Lucide React** - Beautiful, customizable icons
- **Google Fonts** - Inter and Manrope typography

## Getting Started

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

The application will be available at `http://localhost:5173`

## Project Structure

```
src/
├── components/
│   ├── Sidebar.jsx
│   ├── TopNav.jsx
│   ├── DashboardMetrics.jsx
│   └── InputBox.jsx
├── App.jsx
├── main.jsx
└── index.css
```

## Customization

The design system uses consistent spacing (8px base), rounded corners, and fade-in animations. Colors and animations can be customized in `tailwind.config.js`. 
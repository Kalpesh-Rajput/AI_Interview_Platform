import { Outlet, Link, useLocation } from 'react-router-dom';
import { useTheme } from '../context/ThemeContext';

export default function Layout() {
  const { theme, toggleTheme } = useTheme();
  const location = useLocation();

  return (
    <div
      className={`min-h-screen ${
        theme === 'light' ? 'bg-gray-50 text-gray-900' : 'bg-surface text-gray-100'
      }`}
    >
      <header className="sticky top-0 z-50 border-b border-surface-border/60 bg-surface/80 backdrop-blur-md">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <Link to="/" className="flex items-center gap-2">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-accent/20 text-accent-light">
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
              </svg>
            </div>
            <span className="text-lg font-semibold tracking-tight">Interview Intelligence</span>
          </Link>

          <nav className="hidden items-center gap-8 md:flex">
            <Link
              to="/"
              className={`text-sm transition ${location.pathname === '/' ? 'text-white' : 'text-gray-400 hover:text-white'}`}
            >
              Home
            </Link>
            <Link
              to="/upload"
              className={`text-sm transition ${location.pathname === '/upload' ? 'text-white' : 'text-gray-400 hover:text-white'}`}
            >
              Workspace
            </Link>
          </nav>

          <div className="flex items-center gap-3">
            <button
              onClick={toggleTheme}
              className="btn-secondary !px-3 !py-2"
              aria-label="Toggle theme"
            >
              {theme === 'dark' ? '☀️' : '🌙'}
            </button>
            <Link to="/upload" className="btn-primary hidden sm:inline-flex">
              Get Started
            </Link>
          </div>
        </div>
      </header>

      <main>
        <Outlet />
      </main>

      <footer className="border-t border-surface-border py-8 text-center text-sm text-gray-500">
        <p>Interview Intelligence — AI-powered recruiter assistant</p>
      </footer>
    </div>
  );
}

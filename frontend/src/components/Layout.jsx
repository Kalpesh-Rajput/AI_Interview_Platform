import { Outlet, Link, useLocation } from 'react-router-dom';
import { useTheme } from '../context/ThemeContext';

export default function Layout() {
  const { theme, toggleTheme } = useTheme();
  const location = useLocation();

  const navLink = (path, label) => {
    const active = location.pathname === path;
    return (
      <Link
        to={path}
        className={`text-sm font-medium transition-colors duration-300 ease-smooth ${
          active
            ? 'text-ink dark:text-white'
            : 'text-ink-muted hover:text-ink dark:text-gray-400 dark:hover:text-white'
        }`}
      >
        {label}
      </Link>
    );
  };

  return (
    <div
      className={`min-h-screen ${
        theme === 'light' ? 'bg-cream text-ink' : 'bg-surface text-gray-100'
      }`}
    >
      <header className="sticky top-0 z-50 border-b border-cream-dark/80 bg-cream/90 backdrop-blur-md dark:border-surface-border/60 dark:bg-surface/85">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <Link to="/" className="flex items-center gap-2.5 transition-opacity duration-300 hover:opacity-80">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-accent/15 text-accent dark:bg-accent/20 dark:text-accent-light">
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
                />
              </svg>
            </div>
            <span className="text-lg font-semibold tracking-tight text-ink dark:text-white">
              Interview Intelligence
            </span>
          </Link>

          <nav className="hidden items-center gap-8 md:flex">
            {navLink('/', 'Home')}
            {navLink('/upload', 'Workspace')}
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
              Open Workspace
            </Link>
          </div>
        </div>
      </header>

      <main>
        <Outlet />
      </main>

      <footer className="border-t border-cream-dark py-10 text-center dark:border-surface-border">
        <p className="text-sm font-medium text-ink dark:text-gray-200">
          Interview Intelligence by Aptino Technology
        </p>
        <p className="mt-1 text-sm text-ink-muted dark:text-gray-500">
          AI-powered recruiter intelligence platform
        </p>
      </footer>
    </div>
  );
}

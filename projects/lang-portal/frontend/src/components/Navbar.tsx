import React from 'react';
import { Link } from 'react-router-dom';
import { Moon, Sun, Menu, Settings } from 'lucide-react';
import { useThemeStore } from '../store/theme';
import { cn } from '../lib/utils';
import HagXwonLogo from './HagXwonLogo';

export default function Navbar() {
  const { theme, toggleTheme } = useThemeStore();
  const [isMenuOpen, setIsMenuOpen] = React.useState(false);

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 glassmorphism border-b border-white/10">
      <div className="container mx-auto px-4">
        <div className="flex h-16 items-center justify-between">
          <Link to="/" className="flex items-center space-x-3">
            <HagXwonLogo variant="gradient" size="md" />
            <span className="text-2xl font-bold neon-text">
              HagXwon
            </span>
          </Link>

          <div className="hidden md:flex items-center space-x-1">
            <Link
              to="/word-practice"
              className="btn-futuristic text-foreground/80 hover:text-foreground"
            >
              Word Practice
            </Link>
            <Link
              to="/listening-practice"
              className="btn-futuristic text-foreground/80 hover:text-foreground"
            >
              Listening Practice
            </Link>
            <Link
              to="/sentence-practice"
              className="btn-futuristic text-foreground/80 hover:text-foreground"
            >
              Sentence Practice
            </Link>
            <Link
              to="/study-history"
              className="btn-futuristic text-foreground/80 hover:text-foreground"
            >
              Study History
            </Link>
            <Link
              to="/admin"
              className="btn-futuristic text-foreground/80 hover:text-foreground"
            >
              Admin
            </Link>
          </div>

          <div className="flex items-center space-x-4">
            <button
              onClick={toggleTheme}
              className="hud-element p-2 rounded-full"
              aria-label="Toggle theme"
            >
              {theme === 'dark' ? (
                <Sun className="h-5 w-5 text-[#4A90E2]" />
              ) : (
                <Moon className="h-5 w-5 text-[#6B2FB3]" />
              )}
            </button>
            <button
              className="md:hidden hud-element p-2 rounded-full"
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              aria-label="Toggle menu"
            >
              <Menu className="h-5 w-5" />
            </button>
          </div>
        </div>
      </div>

      {/* Mobile menu */}
      <div
        className={cn(
          "md:hidden",
          isMenuOpen ? "block" : "hidden"
        )}
      >
        <div className="space-y-1 px-4 pb-3 pt-2">
          <Link
            to="/word-practice"
            className="block px-3 py-2 btn-futuristic rounded-md"
            onClick={() => setIsMenuOpen(false)}
          >
            Word Practice
          </Link>
          <Link
            to="/listening-practice"
            className="block px-3 py-2 btn-futuristic rounded-md"
            onClick={() => setIsMenuOpen(false)}
          >
            Listening Practice
          </Link>
          <Link
            to="/sentence-practice"
            className="block px-3 py-2 btn-futuristic rounded-md"
            onClick={() => setIsMenuOpen(false)}
          >
            Sentence Practice
          </Link>
          <Link
            to="/study-history"
            className="block px-3 py-2 btn-futuristic rounded-md"
            onClick={() => setIsMenuOpen(false)}
          >
            Study History
          </Link>
          <Link
            to="/admin"
            className="block px-3 py-2 btn-futuristic rounded-md"
            onClick={() => setIsMenuOpen(false)}
          >
            Admin
          </Link>
        </div>
      </div>
    </nav>
  );
}
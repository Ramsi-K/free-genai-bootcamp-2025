import React from 'react';
import { Link, useLocation } from 'react-router-dom';

const navItems = [
  { path: '/', label: 'Dashboard' },
  { path: '/word-practice', label: 'Words' },
  { path: '/listening-practice', label: 'Listening' },
  { path: '/sentence-practice', label: 'Sentences' },
  { path: '/games/muncher', label: 'Word Muncher' },
  { path: '/study-history', label: 'History' },
  { path: '/admin', label: 'Admin' },
];

const Navbar = () => {
  const location = useLocation();

  return (
    <nav className="glassmorphism sticky top-0 z-50 mb-8">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <Link to="/" className="flex items-center">
            <span className="text-2xl font-bold neon-text">HagXwon</span>
          </Link>
          
          <div className="hidden md:flex space-x-4">
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`btn-futuristic ${
                  location.pathname === item.path ? 'neon-glow' : ''
                }`}
              >
                {item.label}
              </Link>
            ))}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;

import React from 'react';
import { Link } from 'react-router-dom';
import { Button } from '../ui/Button';
import { Menu, X } from 'lucide-react';
import { useState } from 'react';

export const Navbar: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-zinc-950/80 backdrop-blur-md border-b border-zinc-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-20">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2 group">
            <span className="text-3xl">✈</span>
            <span className="text-2xl font-black bg-gradient-to-r from-violet-400 to-indigo-400 bg-clip-text text-transparent group-hover:scale-105 transition-transform duration-300">
              Musafir
            </span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-8">
            <Link to="/" className="text-zinc-300 hover:text-violet-400 transition-colors duration-300">
              Home
            </Link>
            <Link to="/plan" className="text-zinc-300 hover:text-violet-400 transition-colors duration-300">
              Plan a Trip
            </Link>
            <a href="#features" className="text-zinc-300 hover:text-violet-400 transition-colors duration-300">
              About
            </a>
            <Link to="/plan">
              <Button size="md">Start Planning →</Button>
            </Link>
          </div>

          {/* Mobile menu button */}
          <button
            className="md:hidden text-zinc-400 hover:text-zinc-300"
            onClick={() => setIsOpen(!isOpen)}
          >
            {isOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>

        {/* Mobile Navigation */}
        {isOpen && (
          <div className="md:hidden pb-4 space-y-4">
            <Link
              to="/"
              className="block text-zinc-300 hover:text-violet-400 transition-colors duration-300"
              onClick={() => setIsOpen(false)}
            >
              Home
            </Link>
            <Link
              to="/plan"
              className="block text-zinc-300 hover:text-violet-400 transition-colors duration-300"
              onClick={() => setIsOpen(false)}
            >
              Plan a Trip
            </Link>
            <a
              href="#features"
              className="block text-zinc-300 hover:text-violet-400 transition-colors duration-300"
              onClick={() => setIsOpen(false)}
            >
              About
            </a>
            <Link to="/plan" onClick={() => setIsOpen(false)}>
              <Button size="md" className="w-full">
                Start Planning →
              </Button>
            </Link>
          </div>
        )}
      </div>
    </nav>
  );
};


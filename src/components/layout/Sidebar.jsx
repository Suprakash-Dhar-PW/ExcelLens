import React, { useState } from 'react';
import { LayoutDashboard, PieChart, BarChart3, Settings, Upload, Menu, X, BrainCircuit } from 'lucide-react';
import { Link, useLocation } from 'react-router-dom';

export default function Sidebar({ isOpen, setIsOpen }) {
  const location = useLocation();
  const currentPath = location.pathname;

  const menuItems = [
    { icon: LayoutDashboard, label: 'Command Center', path: '/dashboard' },
    { icon: BrainCircuit, label: 'AI Copilot', path: '/copilot' },
    { icon: Upload, label: 'Upload Data', path: '/upload' },
    { icon: Settings, label: 'Settings', path: '/settings' },
  ];

  return (
    <aside 
      className={`fixed top-0 left-0 h-screen bg-background border-r border-border transition-all duration-300 z-50 flex flex-col shadow-sm
        ${isOpen ? 'w-64' : 'w-20'}
      `}
    >
      {/* Logo Area */}
      <div className="flex items-center justify-between h-16 px-4 border-b border-border bg-background/50 backdrop-blur-sm sticky top-0">
        <div className={`flex items-center gap-3 overflow-hidden whitespace-nowrap transition-all duration-300 ${isOpen ? 'w-auto opacity-100' : 'w-0 opacity-0'}`}>
          <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0 border border-primary/20">
            <LayoutDashboard className="text-primary w-5 h-5" />
          </div>
          <span className="font-bold text-lg tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-foreground to-foreground/70">
            Nexus
          </span>
        </div>
        <button 
          onClick={() => setIsOpen(!isOpen)}
          className="p-2 rounded-lg hover:bg-accent/50 text-muted-foreground transition-colors mx-auto"
        >
          {isOpen ? <X size={20} /> : <Menu size={20} />}
        </button>
      </div>

      <nav className="flex-1 py-6 flex flex-col gap-2 px-3">
        {menuItems.map((item, index) => {
          const Icon = item.icon;
          return (
            <Link
              key={index}
              to={item.path || '#'}
              className={`flex items-center gap-4 px-3 py-3 rounded-xl transition-all
                ${item.path === currentPath 
                  ? 'bg-primary/10 text-primary font-medium shadow-sm border border-primary/20' 
                  : 'text-muted-foreground hover:bg-accent hover:text-foreground border border-transparent'
                }
                ${!isOpen && 'justify-center'}
              `}
              title={!isOpen ? item.label : ''}
            >
              <Icon size={20} className={item.path === currentPath ? 'text-primary' : 'opacity-80'} />
              {isOpen && <span>{item.label}</span>}
            </Link>
          );
        })}
      </nav>

      <div className="p-4 border-t border-border">
        {isOpen ? (
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-primary to-purple-500 flex items-center justify-center text-white font-bold text-sm shadow-md">
              LL
            </div>
            <div className="flex flex-col">
              <span className="text-sm font-medium">Logged in</span>
              <span className="text-xs text-muted-foreground">Admin</span>
            </div>
          </div>
        ) : (
          <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-primary to-purple-500 flex items-center justify-center text-white font-bold text-sm shadow-md mx-auto">
            LL
          </div>
        )}
      </div>
    </aside>
  );
}

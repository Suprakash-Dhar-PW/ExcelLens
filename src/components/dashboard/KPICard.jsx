import React from 'react';

export default function KPICard({ title, value, subValue, trend, isPositive }) {
  return (
    <div className="glass-panel hover-glass-panel p-6 rounded-xl flex flex-col justify-between h-full">
      <h3 className="text-sm font-medium text-muted-foreground">{title}</h3>
      <div className="mt-4">
        <p className="text-3xl font-bold tracking-tight text-foreground">{value}</p>
        {subValue && (
          <p className={`text-xs mt-2 flex items-center font-medium ${isPositive ? 'text-emerald-400' : 'text-rose-400'}`}>
            {isPositive ? '↑' : '↓'} {subValue}
          </p>
        )}
      </div>
    </div>
  );
}

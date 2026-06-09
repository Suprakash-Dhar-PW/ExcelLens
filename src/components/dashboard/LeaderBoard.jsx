import React from 'react';

export default function LeaderBoard({ data, loading }) {
  if (loading) {
    return <div className="h-[400px] rounded-xl bg-accent/20 animate-pulse border border-border flex items-center justify-center">Loading leaders...</div>;
  }

  if (!data || data.length === 0) {
    return <div className="h-[400px] rounded-xl border border-border flex items-center justify-center text-muted-foreground">No leader data available</div>;
  }

  const formatCurrency = (val) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(val);

  return (
    <div className="h-[400px] p-6 glass-panel rounded-xl flex flex-col shadow-lg overflow-hidden">
      <h3 className="text-lg font-semibold mb-4 flex-none text-foreground/90">Leader Performance</h3>
      <div className="flex-1 overflow-y-auto pr-2 space-y-4 custom-scrollbar">
        {data.map((leader, i) => {
          const progress = leader.target > 0 ? Math.min(100, (leader.revenue / leader.target) * 100) : 0;
          return (
            <div key={i} className="flex flex-col space-y-1">
              <div className="flex justify-between items-end">
                <span className="font-medium text-sm">{leader.name}</span>
                <span className="text-xs text-muted-foreground">{formatCurrency(leader.revenue)} / {formatCurrency(leader.target)}</span>
              </div>
              <div className="h-2 w-full bg-secondary rounded-full overflow-hidden">
                <div 
                  className={`h-full rounded-full ${progress >= 100 ? 'bg-emerald-500' : progress >= 80 ? 'bg-blue-500' : 'bg-amber-500'}`}
                  style={{ width: `${Math.max(5, progress)}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

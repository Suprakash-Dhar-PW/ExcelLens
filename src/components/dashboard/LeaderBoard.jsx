import React from 'react';

export default function LeaderBoard({ data, loading }) {
  if (loading) {
    return <div className="h-[400px] rounded-xl bg-accent/20 animate-pulse border border-border flex items-center justify-center">Loading leaders...</div>;
  }

  if (!data || !data.data || data.data.length === 0) {
    return (
      <div className="h-[400px] rounded-xl border border-border p-6 flex flex-col shadow-lg glass-panel">
         <h3 className="text-lg font-semibold mb-4 text-foreground/90">Leader Performance</h3>
         <div className="flex-1 flex flex-col items-center justify-center text-muted-foreground text-center">
            <span className="text-3xl mb-3">🏆</span>
            <p className="font-medium">No leader data available</p>
            <p className="text-sm mt-2 opacity-80">Raw rows loaded: {data?.raw_count || 0}</p>
            <p className="text-sm opacity-80">Rows after filter: {data?.filtered_count || 0}</p>
         </div>
      </div>
    );
  }

  const formatCurrency = (val) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(val);

  return (
    <div className="h-[400px] p-6 glass-panel rounded-xl flex flex-col shadow-lg overflow-hidden">
      <div className="flex justify-between items-center mb-4 flex-none">
        <h3 className="text-lg font-semibold text-foreground/90">Leader Performance</h3>
        <div className="text-xs text-muted-foreground">Raw: {data.raw_count} | Rendered: {data.filtered_count}</div>
      </div>
      <div className="flex-1 overflow-y-auto pr-2 space-y-4 custom-scrollbar">
        {data.data.map((leader, i) => {
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

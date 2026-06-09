import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export default function BatchesChart({ data, loading }) {
  if (loading) {
    return <div className="h-[400px] rounded-xl bg-accent/20 animate-pulse border border-border flex items-center justify-center">Loading batches...</div>;
  }

  if (!data || !data.data || data.data.length === 0) {
    return (
      <div className="h-[400px] rounded-xl border border-border p-6 flex flex-col shadow-lg glass-panel">
         <h3 className="text-lg font-semibold mb-4 text-foreground/90">Batch Performance</h3>
         <div className="flex-1 flex flex-col items-center justify-center text-muted-foreground text-center">
            <span className="text-3xl mb-3">👥</span>
            <p className="font-medium">No batch data available</p>
            <p className="text-sm mt-2 opacity-80">Raw rows loaded: {data?.raw_count || 0}</p>
            <p className="text-sm opacity-80">Rows after filter: {data?.filtered_count || 0}</p>
         </div>
      </div>
    );
  }

  const chartData = data.data;

  return (
    <div className="h-[400px] min-h-[300px] min-w-0 p-6 glass-panel rounded-xl flex flex-col shadow-lg">
      <div className="flex justify-between items-center mb-6 flex-none">
        <h3 className="text-lg font-semibold text-foreground/90">Batch Performance</h3>
        <div className="text-xs text-muted-foreground">Raw: {data.raw_count} | Rendered: {data.filtered_count}</div>
      </div>
      <div className="flex-1 w-full min-h-[300px]">
        <ResponsiveContainer width="100%" height="100%" minHeight={300}>
          <BarChart data={chartData} margin={{ top: 5, right: 5, left: -20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="hsl(var(--border))" />
            <XAxis dataKey="name" stroke="hsl(var(--muted-foreground))" fontSize={12} tickLine={false} axisLine={false} />
            <YAxis stroke="hsl(var(--muted-foreground))" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(value) => `$${(value/1000).toFixed(0)}k`} />
            <Tooltip 
              contentStyle={{ backgroundColor: 'rgba(17, 24, 39, 0.9)', backdropFilter: 'blur(10px)', borderColor: 'rgba(255,255,255,0.1)', borderRadius: '12px', color: '#fff' }}
              itemStyle={{ color: '#e2e8f0' }}
              cursor={{fill: 'rgba(255,255,255,0.05)'}}
            />
            <Bar dataKey="revenue" name="Revenue" fill="#3b82f6" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

export default function CategoryChart({ data, loading, title = "Top Categories" }) {
  if (loading) {
    return <div className="h-[400px] rounded-xl bg-accent/20 animate-pulse border border-border flex items-center justify-center">Loading categories...</div>;
  }

  if (!data || data.length === 0) {
    return <div className="h-[400px] rounded-xl border border-border flex items-center justify-center text-muted-foreground">No category data available</div>;
  }

  const colors = ['#8b5cf6', '#3b82f6', '#06b6d4', '#10b981', '#f59e0b'];

  return (
    <div className="h-[400px] min-h-[300px] min-w-0 p-6 glass-panel rounded-xl flex flex-col">
      <h3 className="text-lg font-semibold mb-6 flex-none">{title}</h3>
      <div className="flex-1 w-full min-h-0">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} layout="vertical" margin={{ top: 0, right: 20, left: 20, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} stroke="hsl(var(--border))" />
            <XAxis type="number" stroke="hsl(var(--muted-foreground))" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(value) => `$${(value/1000).toFixed(0)}k`} />
            <YAxis dataKey="name" type="category" stroke="hsl(var(--muted-foreground))" fontSize={12} tickLine={false} axisLine={false} width={100} />
            <Tooltip 
              cursor={{fill: 'rgba(255,255,255,0.05)'}}
              contentStyle={{ backgroundColor: 'rgba(17, 24, 39, 0.8)', backdropFilter: 'blur(10px)', borderColor: 'rgba(255,255,255,0.1)', borderRadius: '12px', color: '#fff' }}
            />
            <Bar dataKey="value" radius={[0, 4, 4, 0]}>
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

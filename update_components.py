import os

components_dir = r's:\AI-Dashboard-Gen\src\components\dashboard'

daily_trend = """import React from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export default function DailyTrendChart({ data, loading }) {
  if (loading) {
    return <div className="h-[400px] rounded-xl bg-accent/20 animate-pulse border border-border flex items-center justify-center">Loading trend data...</div>;
  }

  if (!data || !data.data || data.data.length === 0) {
    return (
      <div className="h-[400px] rounded-xl border border-border p-6 flex flex-col shadow-lg glass-panel">
         <h3 className="text-lg font-semibold mb-4 text-foreground/90">Daily Collection Trend</h3>
         <div className="flex-1 flex flex-col items-center justify-center text-muted-foreground text-center">
            <span className="text-3xl mb-3">📈</span>
            <p className="font-medium">No daily trend data available</p>
            <p className="text-sm mt-2 opacity-80">Raw rows loaded: {data?.raw_count || 0}</p>
            <p className="text-sm opacity-80">Rows after filter: {data?.filtered_count || 0}</p>
            {data?.raw_count > 0 && <p className="text-xs text-amber-500 mt-2">Hint: Check if date columns were parsed correctly.</p>}
         </div>
      </div>
    );
  }

  const chartData = data.data;

  return (
    <div className="h-[400px] min-h-[300px] min-w-0 p-6 glass-panel rounded-xl flex flex-col shadow-lg">
      <div className="flex justify-between items-center mb-6 flex-none">
        <h3 className="text-lg font-semibold text-foreground/90">Daily Collection Trend</h3>
        <div className="text-xs text-muted-foreground">Raw: {data.raw_count} | Rendered: {data.filtered_count}</div>
      </div>
      <div className="flex-1 w-full min-h-[300px]">
        <ResponsiveContainer width="100%" height="100%" minHeight={300}>
          <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#10b981" stopOpacity={0.6}/>
                <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
              </linearGradient>
              <linearGradient id="colorTarget" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#6366f1" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="hsl(var(--border))" />
            <XAxis dataKey="name" stroke="hsl(var(--muted-foreground))" fontSize={12} tickLine={false} axisLine={false} />
            <YAxis stroke="hsl(var(--muted-foreground))" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(value) => `$${(value/1000).toFixed(0)}k`} />
            <Tooltip 
              contentStyle={{ backgroundColor: 'rgba(17, 24, 39, 0.9)', backdropFilter: 'blur(10px)', borderColor: 'rgba(255,255,255,0.1)', borderRadius: '12px', color: '#fff' }}
              itemStyle={{ color: '#e2e8f0' }}
            />
            <Area type="monotone" dataKey="revenue" name="Collection" stroke="#10b981" strokeWidth={3} fillOpacity={1} fill="url(#colorRevenue)" />
            <Area type="monotone" dataKey="target" name="Target" stroke="#6366f1" strokeWidth={2} strokeDasharray="5 5" fillOpacity={1} fill="url(#colorTarget)" />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
"""

category_chart = """import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export default function CategoryChart({ data, loading, title }) {
  if (loading) {
    return <div className="h-[400px] rounded-xl bg-accent/20 animate-pulse border border-border flex items-center justify-center">Loading categories...</div>;
  }

  if (!data || !data.data || data.data.length === 0) {
    return (
      <div className="h-[400px] rounded-xl border border-border p-6 flex flex-col shadow-lg glass-panel">
         <h3 className="text-lg font-semibold mb-4 text-foreground/90">{title}</h3>
         <div className="flex-1 flex flex-col items-center justify-center text-muted-foreground text-center">
            <span className="text-3xl mb-3">📊</span>
            <p className="font-medium">No category data available</p>
            <p className="text-sm mt-2 opacity-80">Raw rows loaded: {data?.raw_count || 0}</p>
            <p className="text-sm opacity-80">Rows after filter: {data?.filtered_count || 0}</p>
            {data?.raw_count > 0 && <p className="text-xs text-amber-500 mt-2">Hint: Check if rank_type matches '{title.toLowerCase().includes('top') ? 'top' : 'bottom'}'.</p>}
         </div>
      </div>
    );
  }

  const chartData = data.data;
  const isTop = title.toLowerCase().includes('top');

  return (
    <div className="h-[400px] min-h-[300px] min-w-0 p-6 glass-panel rounded-xl flex flex-col shadow-lg">
      <div className="flex justify-between items-center mb-6 flex-none">
        <h3 className="text-lg font-semibold text-foreground/90">{title}</h3>
        <div className="text-xs text-muted-foreground">Raw: {data.raw_count} | Rendered: {data.filtered_count}</div>
      </div>
      <div className="flex-1 w-full min-h-[300px]">
        <ResponsiveContainer width="100%" height="100%" minHeight={300}>
          <BarChart data={chartData} layout="vertical" margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="hsl(var(--border))" />
            <XAxis type="number" stroke="hsl(var(--muted-foreground))" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(value) => `$${(value/1000).toFixed(0)}k`} />
            <YAxis dataKey="name" type="category" stroke="hsl(var(--muted-foreground))" fontSize={12} tickLine={false} axisLine={false} width={80} />
            <Tooltip 
              contentStyle={{ backgroundColor: 'rgba(17, 24, 39, 0.9)', backdropFilter: 'blur(10px)', borderColor: 'rgba(255,255,255,0.1)', borderRadius: '12px', color: '#fff' }}
              itemStyle={{ color: '#e2e8f0' }}
              cursor={{fill: 'rgba(255,255,255,0.05)'}}
            />
            <Bar dataKey="value" name="Revenue" fill={isTop ? '#10b981' : '#ef4444'} radius={[0, 4, 4, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
"""

leader_board = """import React from 'react';

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
"""

offering_chart = """import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export default function OfferingChart({ data, loading }) {
  if (loading) {
    return <div className="h-[400px] rounded-xl bg-accent/20 animate-pulse border border-border flex items-center justify-center">Loading offerings...</div>;
  }

  if (!data || !data.data || data.data.length === 0) {
    return (
      <div className="h-[400px] rounded-xl border border-border p-6 flex flex-col shadow-lg glass-panel">
         <h3 className="text-lg font-semibold mb-4 text-foreground/90">Offering Performance</h3>
         <div className="flex-1 flex flex-col items-center justify-center text-muted-foreground text-center">
            <span className="text-3xl mb-3">📦</span>
            <p className="font-medium">No offering data available</p>
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
        <h3 className="text-lg font-semibold text-foreground/90">Offering Performance</h3>
        <div className="text-xs text-muted-foreground">Raw: {data.raw_count} | Rendered: {data.filtered_count}</div>
      </div>
      <div className="flex-1 w-full min-h-[300px]">
        <ResponsiveContainer width="100%" height="100%" minHeight={300}>
          <BarChart data={chartData} layout="vertical" margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="hsl(var(--border))" />
            <XAxis type="number" stroke="hsl(var(--muted-foreground))" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(value) => `$${(value/1000).toFixed(0)}k`} />
            <YAxis dataKey="name" type="category" stroke="hsl(var(--muted-foreground))" fontSize={12} tickLine={false} axisLine={false} width={100} />
            <Tooltip 
              contentStyle={{ backgroundColor: 'rgba(17, 24, 39, 0.9)', backdropFilter: 'blur(10px)', borderColor: 'rgba(255,255,255,0.1)', borderRadius: '12px', color: '#fff' }}
              itemStyle={{ color: '#e2e8f0' }}
              cursor={{fill: 'rgba(255,255,255,0.05)'}}
            />
            <Bar dataKey="value" name="Revenue" fill="#8b5cf6" radius={[0, 4, 4, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
"""

batches_chart = """import React from 'react';
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
"""

kpi_grid = """import React from 'react';
import KPICard from './KPICard';

export default function KPIGrid({ kpis, loading }) {
  if (loading) {
    return (
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-5">
        {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map(i => (
          <div key={i} className="h-28 rounded-xl bg-accent/20 animate-pulse border border-border" />
        ))}
      </div>
    );
  }

  if (!kpis) return null;

  const formatCurrency = (val) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(val);
  const formatNumber = (val) => new Intl.NumberFormat('en-US').format(val);

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-5">
      <KPICard 
        title="Orders MTD" 
        value={formatNumber(kpis.ordersMTD || 0)} 
        subValue={`YTD: ${formatNumber(kpis.ordersYTD || 0)}`}
        isPositive={true}
      />
      <KPICard 
        title="Collection MTD" 
        value={formatCurrency(kpis.collectionMTD || 0)} 
        subValue={`YTD: ${formatCurrency(kpis.collectionYTD || 0)}`}
        isPositive={true}
      />
      <KPICard 
        title="AOV MTD" 
        value={formatCurrency(kpis.aovMTD || 0)} 
        isPositive={true}
      />
      <KPICard 
        title="Target Achievement" 
        value={`${kpis.achievement || 0}%`} 
        subValue={`Target: ${formatCurrency(kpis.targetCollectionMTD || 0)}`}
        isPositive={kpis.achievement >= 100}
      />
      <KPICard 
        title="Projected End of Month" 
        value={formatCurrency(kpis.forecast?.projectedCollection || 0)} 
        subValue={`Orders: ${formatNumber(kpis.forecast?.projectedOrders || 0)}`}
        isPositive={true}
      />
    </div>
  );
}
"""

import io
with io.open(os.path.join(components_dir, 'DailyTrendChart.jsx'), 'w', encoding='utf-8') as f:
    f.write(daily_trend)
with io.open(os.path.join(components_dir, 'CategoryChart.jsx'), 'w', encoding='utf-8') as f:
    f.write(category_chart)
with io.open(os.path.join(components_dir, 'LeaderBoard.jsx'), 'w', encoding='utf-8') as f:
    f.write(leader_board)
with io.open(os.path.join(components_dir, 'OfferingChart.jsx'), 'w', encoding='utf-8') as f:
    f.write(offering_chart)
with io.open(os.path.join(components_dir, 'BatchesChart.jsx'), 'w', encoding='utf-8') as f:
    f.write(batches_chart)
with io.open(os.path.join(components_dir, 'KPIGrid.jsx'), 'w', encoding='utf-8') as f:
    f.write(kpi_grid)

print('Updated components')

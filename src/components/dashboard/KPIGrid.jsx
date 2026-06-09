import React from 'react';
import KPICard from './KPICard';

export default function KPIGrid({ kpis, loading }) {
  if (loading) {
    return (
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-7">
        {[1, 2, 3, 4, 5, 6, 7].map(i => (
          <div key={i} className="h-28 rounded-xl bg-accent/20 animate-pulse border border-border" />
        ))}
      </div>
    );
  }

  if (!kpis) return null;

  const formatCurrency = (val) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(val);
  const formatNumber = (val) => new Intl.NumberFormat('en-US').format(val);

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-7">
      <KPICard 
        title="Target Collection" 
        value={formatCurrency(kpis.targetRevenue || 0)} 
        isPositive={true}
      />
      <KPICard 
        title="Achieved Collection" 
        value={formatCurrency(kpis.totalRevenue || 0)} 
        isPositive={kpis.totalRevenue >= kpis.targetRevenue}
      />
      <KPICard 
        title="Projected Collection" 
        value={formatCurrency((kpis.totalRevenue || 0) * 1.1)} // Dummy projection since not in API
        isPositive={true}
      />
      <KPICard 
        title="Delta" 
        value={formatCurrency(Math.abs(kpis.revenueGap || 0))} 
        subValue={kpis.revenueGap >= 0 ? 'Over Target' : 'Below Target'}
        isPositive={kpis.revenueGap >= 0}
      />
      <KPICard 
        title="Target Orders" 
        value={formatNumber(kpis.targetOrders || 0)} 
        isPositive={true}
      />
      <KPICard 
        title="Achieved Orders" 
        value={formatNumber(kpis.totalOrders || 0)} 
        isPositive={kpis.totalOrders >= kpis.targetOrders}
      />
      <KPICard 
        title="Achievement %" 
        value={`${kpis.achievement || 0}%`} 
        isPositive={kpis.achievement >= 100}
      />
    </div>
  );
}

import React from 'react';
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

import React from 'react';
import { AlertTriangle, CheckCircle } from 'lucide-react';

export default function AlertsPanel({ alerts, loading }) {
  if (loading) {
    return (
      <div className="glass-panel p-6 rounded-xl flex flex-col space-y-4">
        <h3 className="text-lg font-semibold">Active Alerts</h3>
        <div className="space-y-3 mt-4">
          <div className="h-12 rounded-lg bg-accent/20 animate-pulse" />
        </div>
      </div>
    );
  }

  const hasAlerts = alerts && alerts.length > 0 && !alerts[0].includes("healthy");

  return (
    <div className="glass-panel p-6 rounded-xl">
      <h3 className="text-lg font-semibold mb-6 flex items-center gap-2">
        {hasAlerts ? <AlertTriangle className="w-5 h-5 text-rose-500" /> : <CheckCircle className="w-5 h-5 text-emerald-500" />}
        Status Alerts
      </h3>
      <div className="space-y-4">
        {alerts && alerts.map((alert, idx) => {
          const isGood = alert.includes("healthy");
          return (
            <div key={idx} className={`p-4 rounded-lg border text-sm leading-relaxed ${isGood ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400' : 'bg-rose-500/10 border-rose-500/20 text-rose-400'}`}>
              {alert}
            </div>
          );
        })}
      </div>
    </div>
  );
}

import React from 'react';
import { Sparkles } from 'lucide-react';

export default function InsightsPanel({ insights, loading }) {
  if (loading) {
    return (
      <div className="glass-panel p-6 rounded-xl flex flex-col space-y-4">
        <h3 className="text-lg font-semibold flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-accent" /> AI Insights
        </h3>
        <div className="space-y-3 mt-4">
          {[1, 2, 3].map(i => (
            <div key={i} className="h-12 rounded-lg bg-accent/20 animate-pulse" />
          ))}
        </div>
      </div>
    );
  }

  if (!insights || insights.length === 0) {
    return null;
  }

  return (
    <div className="glass-panel p-6 rounded-xl">
      <h3 className="text-lg font-semibold flex items-center gap-2 mb-6">
        <Sparkles className="w-5 h-5 text-primary" /> Executive AI Insights
      </h3>
      <div className="space-y-4">
        {insights.map((insight, idx) => (
          <div key={idx} className="p-4 rounded-lg bg-accent/10 border border-accent/20 text-sm leading-relaxed text-foreground/90">
            {insight}
          </div>
        ))}
      </div>
    </div>
  );
}

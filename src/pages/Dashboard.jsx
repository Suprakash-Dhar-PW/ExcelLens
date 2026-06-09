import React, { useEffect, useState } from 'react';
import KPIGrid from '../components/dashboard/KPIGrid';
import DailyTrendChart from '../components/dashboard/DailyTrendChart';
import CategoryChart from '../components/dashboard/CategoryChart';
import LeaderBoard from '../components/dashboard/LeaderBoard';
import OfferingChart from '../components/dashboard/OfferingChart';
import BatchesChart from '../components/dashboard/BatchesChart';
import InsightsPanel from '../components/dashboard/InsightsPanel';
import AlertsPanel from '../components/dashboard/AlertsPanel';
import UploadHistory from '../components/dashboard/UploadHistory';
import { api } from '../services/api';
import { RefreshCcw } from 'lucide-react';
import { useDashboardSocket } from '../hooks/useDashboardSocket';

export default function Dashboard() {
  const [data, setData] = useState({
    kpis: null,
    dailyTrend: null,
    topCategories: null,
    bottomCategories: null,
    offerings: null,
    batches: null,
    leaders: null,
    insights: null,
    alerts: null,
    history: null,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = React.useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [kpis, dailyTrend, topCategories, bottomCategories, offerings, batches, leaders, insights, alerts, history] = await Promise.all([
        api.getKPIs().catch(error => { console.error("KPIs error:", error); throw error; }),
        api.getDailyTrend().catch(error => { console.error("DailyTrend error:", error); throw error; }),
        api.getTopCategories().catch(error => { console.error("TopCategories error:", error); throw error; }),
        api.getBottomCategories().catch(error => { console.error("BottomCategories error:", error); throw error; }),
        api.getOfferings().catch(error => { console.error("Offerings error:", error); throw error; }),
        api.getBatches().catch(error => { console.error("Batches error:", error); throw error; }),
        api.getLeaders().catch(error => { console.error("Leaders error:", error); throw error; }),
        api.getInsights().catch(error => { console.error("Insights error:", error); throw error; }),
        api.getAlerts().catch(error => { console.error("Alerts error:", error); throw error; }),
        api.getUploadHistory().catch(error => { console.error("History error:", error); throw error; })
      ]);

      console.log("Fetched Data:", { kpis, dailyTrend, topCategories, bottomCategories, offerings, batches, leaders });


      setData({ kpis, dailyTrend, topCategories, bottomCategories, offerings, batches, leaders, insights, alerts, history });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  useDashboardSocket(() => {
    console.log("WebSocket triggered data refresh");
    fetchData();
  });

  return (
    <div className="max-w-[1600px] mx-auto space-y-8 animate-in fade-in duration-500 pb-10">
      <div className="flex justify-between items-end">
        <div>
          <h2 className="text-4xl font-bold tracking-tight">Command Center</h2>
          <p className="text-muted-foreground mt-2 text-lg">Executive revenue intelligence and insights.</p>
        </div>
        <div className="flex gap-4">
          <button 
            onClick={fetchData}
            className="flex items-center gap-2 px-4 py-2 bg-primary/10 text-primary hover:bg-primary/20 rounded-lg transition-colors font-medium text-sm border border-primary/20"
          >
            <RefreshCcw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} /> Refresh
          </button>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-destructive/10 text-destructive border border-destructive/20 rounded-xl">
          Failed to load dashboard data: {error}
        </div>
      )}

      {/* Row 1: KPI Grid */}
      <KPIGrid kpis={data.kpis} loading={loading} />

      {/* Row 2: Daily Collection Trend */}
      <div className="grid gap-6 lg:grid-cols-1">
        <DailyTrendChart data={data.dailyTrend} loading={loading} />
      </div>

      {/* Row 3: Leader Performance & Offering Performance */}
      <div className="grid gap-6 lg:grid-cols-2">
        <LeaderBoard data={data.leaders} loading={loading} />
        <OfferingChart data={data.offerings} loading={loading} />
      </div>

      {/* Row 4: Top Categories, Bottom Categories, Top Batches */}
      <div className="grid gap-6 lg:grid-cols-3">
        <CategoryChart data={data.topCategories} loading={loading} title="Top Categories" />
        <CategoryChart data={data.bottomCategories} loading={loading} title="Bottom Categories" />
        <BatchesChart data={data.batches} loading={loading} />
      </div>

      {/* Row 5: Insights, Alerts, History */}
      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-1">
          <InsightsPanel insights={data.insights} loading={loading} />
        </div>
        <div className="lg:col-span-1">
          <AlertsPanel alerts={data.alerts} loading={loading} />
        </div>
        <div className="lg:col-span-1">
          <UploadHistory uploads={data.history} loading={loading} />
        </div>
      </div>
    </div>
  );
}

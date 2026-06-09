const API_BASE_URL = 'http://localhost:8000/api/v1';
const WS_BASE_URL = 'ws://localhost:8000/api/v1/ws/dashboard';

export const api = {
  async getKPIs() {
    const res = await fetch(`${API_BASE_URL}/dashboard/kpis`);
    if (!res.ok) throw new Error('Failed to fetch KPIs');
    return res.json();
  },
  
  async getDailyTrend() {
    const res = await fetch(`${API_BASE_URL}/dashboard/daily-trend`);
    if (!res.ok) throw new Error('Failed to fetch daily trend');
    return res.json();
  },
  
  async getTopCategories() {
    const res = await fetch(`${API_BASE_URL}/dashboard/categories/top`);
    if (!res.ok) throw new Error('Failed to fetch top categories');
    return res.json();
  },
  
  async getBottomCategories() {
    const res = await fetch(`${API_BASE_URL}/dashboard/categories/bottom`);
    if (!res.ok) throw new Error('Failed to fetch bottom categories');
    return res.json();
  },

  async getOfferings() {
    const res = await fetch(`${API_BASE_URL}/dashboard/offerings`);
    if (!res.ok) throw new Error('Failed to fetch offerings');
    return res.json();
  },

  async getBatches() {
    const res = await fetch(`${API_BASE_URL}/dashboard/batches`);
    if (!res.ok) throw new Error('Failed to fetch batches');
    return res.json();
  },

  async getLeaders() {
    const res = await fetch(`${API_BASE_URL}/dashboard/leaders`);
    if (!res.ok) throw new Error('Failed to fetch leaders');
    return res.json();
  },
  
  async getInsights() {
    const res = await fetch(`${API_BASE_URL}/dashboard/insights`);
    if (!res.ok) throw new Error('Failed to fetch insights');
    return res.json();
  },
  
  async getAlerts() {
    const res = await fetch(`${API_BASE_URL}/dashboard/alerts`);
    if (!res.ok) throw new Error('Failed to fetch alerts');
    return res.json();
  },

  async getUploadHistory() {
    const res = await fetch(`${API_BASE_URL}/upload/history`);
    if (!res.ok) throw new Error('Failed to fetch upload history');
    return res.json();
  },

  async chat(message, sessionId = null) {
    const res = await fetch(`${API_BASE_URL}/copilot/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, session_id: sessionId })
    });
    if (!res.ok) throw new Error('Failed to chat with Copilot');
    return res.json();
  }
};

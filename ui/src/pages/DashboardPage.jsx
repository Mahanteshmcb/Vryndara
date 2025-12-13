import React, { useState, useEffect } from 'react';
import { Activity, Server, Database, Terminal, Clock, Zap, ExternalLink, Box, Monitor } from 'lucide-react';
import { LineChart, Line, ResponsiveContainer, XAxis, YAxis, Tooltip } from 'recharts';

const GATEWAY_WS = "ws://localhost:8081/ws";
const APP_STORE_KEY = "vryndara_installed_apps";

const StatCard = ({ title, value, subtext, icon: Icon, color }) => (
  <div className={`bg-[#111113] border border-gray-800 p-5 rounded-xl hover:border-${color}-500/50 transition-colors`}>
    <div className="flex justify-between items-start mb-4">
      <div className={`p-2 rounded-lg bg-${color}-500/10 text-${color}-500`}>
        <Icon size={20} />
      </div>
      <div className={`text-xs font-mono px-2 py-1 rounded bg-${color}-500/10 text-${color}-500`}>
        ACTIVE
      </div>
    </div>
    <div className="text-2xl font-bold text-white mb-1">{value}</div>
    <div className="text-xs text-gray-500">{subtext}</div>
  </div>
);

export default function DashboardPage() {
  const [isConnected, setIsConnected] = useState(false);
  // Initialize with some dummy data so the chart isn't empty
  const [loadData, setLoadData] = useState(Array(20).fill(0).map((_, i) => ({ time: i, value: 20 + Math.random() * 10 })));
  const [installedApps, setInstalledApps] = useState({});

  useEffect(() => {
    // 1. Load Installed Apps
    const saved = localStorage.getItem(APP_STORE_KEY);
    if (saved) setInstalledApps(JSON.parse(saved));

    // 2. Connect to Gateway
    const ws = new WebSocket(GATEWAY_WS);
    ws.onopen = () => setIsConnected(true);
    ws.onclose = () => setIsConnected(false);

    // 3. Chart Animation Loop (Fixed)
    const interval = setInterval(() => {
      setLoadData(prev => {
        // FIX: We must define 'lastVal' by reading the previous state
        const lastVal = prev[prev.length - 1].value; 
        const nextValue = Math.max(5, Math.min(100, lastVal + (Math.random() - 0.5) * 20));
        return [...prev.slice(1), { time: Date.now(), value: nextValue }];
      });
    }, 1000);

    return () => { ws.close(); clearInterval(interval); };
  }, []);

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto animate-fade-in text-white">
      {/* HEADER */}
      <div className="flex justify-between items-end mb-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">System Overview</h1>
          <p className="text-gray-500 mt-1">Vryndara Orchestration Layer v1.0</p>
        </div>
        <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-bold border ${isConnected ? 'bg-green-900/20 border-green-900 text-green-400' : 'bg-red-900/20 border-red-900 text-red-400'}`}>
          <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`} />
          {isConnected ? "GATEWAY ONLINE" : "GATEWAY OFFLINE"}
        </div>
      </div>

      {/* TOP STATS */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatCard title="Uptime" value="12h 45m" subtext="Since last reboot" icon={Clock} color="blue" />
        <StatCard title="Memory" value="14.2 GB" subtext="64% Utilized" icon={Database} color="purple" />
        <StatCard title="Agents" value="3 Online" subtext="All systems nominal" icon={Terminal} color="green" />
        <StatCard title="Workflows" value="128" subtext="Executed today" icon={Zap} color="yellow" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* CHART SECTION */}
        <div className="lg:col-span-2 bg-[#0a0a0a] border border-gray-800 rounded-xl p-5 shadow-sm">
          <div className="flex justify-between items-center mb-6">
            <h3 className="font-bold flex items-center gap-2">
              <Activity size={18} className="text-blue-500" />
              Neural Load
            </h3>
            <span className="text-xs text-gray-500 font-mono">LIVE TELEMETRY</span>
          </div>
          <div className="h-[250px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={loadData}>
                <defs><linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/><stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/></linearGradient></defs>
                <XAxis dataKey="time" hide />
                <YAxis hide domain={[0, 100]} />
                <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: 'none', borderRadius: '8px', color: '#fff' }} itemStyle={{ color: '#fff' }} />
                <Line type="monotone" dataKey="value" stroke="#3b82f6" strokeWidth={2} dot={false} activeDot={{ r: 4, fill: '#60a5fa' }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* APP LAUNCHPAD */}
        <div className="bg-[#0a0a0a] border border-gray-800 rounded-xl p-5 flex flex-col">
          <h3 className="font-bold flex items-center gap-2 mb-4">
            <Box size={18} className="text-orange-500" />
            My Apps
          </h3>
          
          <div className="flex-1 space-y-3">
            {!installedApps.historabook && !installedApps.vrindadev && (
              <div className="text-center text-gray-600 py-8 text-sm">
                No apps installed.<br/>Visit the <span className="text-blue-400 cursor-pointer">Agent Store</span>.
              </div>
            )}

            {/* HISTORABOOK */}
            {installedApps.historabook && (
              <div className="bg-[#111113] border border-gray-800 p-3 rounded-lg flex justify-between items-center group hover:border-green-500/50 transition-colors">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded bg-green-900/30 flex items-center justify-center text-green-500 font-bold">H</div>
                  <div>
                    <div className="font-bold text-sm">Historabook</div>
                    <div className="text-[10px] text-gray-500">Running on Port 8001</div>
                  </div>
                </div>
                <a href="http://localhost:8001" target="_blank" rel="noopener noreferrer" className="p-2 text-gray-400 hover:text-white hover:bg-white/10 rounded">
                  <ExternalLink size={16} />
                </a>
              </div>
            )}

            {/* VRINDADEV */}
            {installedApps.vrindadev && (
              <div className="bg-[#111113] border border-gray-800 p-3 rounded-lg flex justify-between items-center group hover:border-purple-500/50 transition-colors">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded bg-purple-900/30 flex items-center justify-center text-purple-500 font-bold">V</div>
                  <div>
                    <div className="font-bold text-sm">VrindaDev</div>
                    <div className="text-[10px] text-gray-500">Desktop Window</div>
                  </div>
                </div>
                <div className="p-2 text-gray-500 cursor-default">
                  <Monitor size={16} />
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
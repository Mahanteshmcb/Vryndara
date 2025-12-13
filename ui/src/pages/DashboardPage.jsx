import React, { useState, useEffect } from 'react';
import { Activity, Server, Database, Terminal, Clock, Zap } from 'lucide-react';
import { LineChart, Line, ResponsiveContainer, XAxis, YAxis, Tooltip } from 'recharts';

const GATEWAY_WS = "ws://localhost:8081/ws";

// --- WIDGET COMPONENTS ---

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

const AgentCard = ({ name, role, status, model }) => (
  <div className="flex items-center justify-between p-3 bg-[#111113] border border-gray-800 rounded-lg group hover:border-gray-600 transition-colors">
    <div className="flex items-center gap-3">
      <div className={`w-2 h-2 rounded-full ${status === 'idle' ? 'bg-green-500' : 'bg-yellow-500 animate-pulse'}`} />
      <div>
        <div className="text-sm font-medium text-gray-200">{name}</div>
        <div className="text-xs text-gray-500 font-mono">{role}</div>
      </div>
    </div>
    <div className="text-xs text-gray-600 bg-gray-900 px-2 py-1 rounded border border-gray-800 group-hover:border-gray-700">
      {model}
    </div>
  </div>
);

// --- PAGE COMPONENT ---

export default function DashboardPage() {
  const [isConnected, setIsConnected] = useState(false);
  // Initial dummy data for the chart
  const [loadData, setLoadData] = useState(Array(20).fill(0).map((_, i) => ({ time: i, value: 20 + Math.random() * 10 })));
  
  useEffect(() => {
    // 1. Check Gateway Connection
    const ws = new WebSocket(GATEWAY_WS);
    ws.onopen = () => setIsConnected(true);
    ws.onclose = () => setIsConnected(false);

    // 2. Simulate Neural Load (Live Chart Animation)
    const interval = setInterval(() => {
      setLoadData(prev => {
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
          {isConnected ? "GATEWAY CONNECTED" : "GATEWAY OFFLINE"}
        </div>
      </div>

      {/* TOP STATS GRID */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatCard title="Uptime" value="12h 45m" subtext="Since last reboot" icon={Clock} color="blue" />
        <StatCard title="Memory" value="14.2 GB" subtext="64% Utilized" icon={Database} color="purple" />
        <StatCard title="Agents" value="3 Online" subtext="All systems nominal" icon={Terminal} color="green" />
        <StatCard title="Workflows" value="128" subtext="Executed today" icon={Zap} color="yellow" />
      </div>

      {/* MAIN CONTENT SPLIT */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* LEFT: CHART SECTION (2 Cols) */}
        <div className="lg:col-span-2 bg-[#0a0a0a] border border-gray-800 rounded-xl p-5 shadow-sm">
          <div className="flex justify-between items-center mb-6">
            <h3 className="font-bold flex items-center gap-2">
              <Activity size={18} className="text-blue-500" />
              Neural Load
            </h3>
            <span className="text-xs text-gray-500 font-mono">LIVE TELEMETRY</span>
          </div>
          <div className="h-[300px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={loadData}>
                <defs>
                  <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <XAxis dataKey="time" hide />
                <YAxis hide domain={[0, 100]} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1f2937', border: 'none', borderRadius: '8px', color: '#fff' }}
                  itemStyle={{ color: '#fff' }}
                />
                <Line 
                  type="monotone" 
                  dataKey="value" 
                  stroke="#3b82f6" 
                  strokeWidth={2}
                  dot={false}
                  activeDot={{ r: 4, fill: '#60a5fa' }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* RIGHT: AGENTS LIST (1 Col) */}
        <div className="bg-[#0a0a0a] border border-gray-800 rounded-xl p-5">
          <h3 className="font-bold flex items-center gap-2 mb-6">
            <Server size={18} className="text-purple-500" />
            Agent Registry
          </h3>
          <div className="space-y-3">
            <AgentCard name="Researcher-1" role="Information Retrieval" status="idle" model="Llama-3-8b" />
            <AgentCard name="Media-Director" role="Video Synthesis" status="idle" model="Llama-3-8b" />
            <AgentCard name="Coder-Alpha" role="Software Engineer" status="idle" model="Codellama-7b" />
            
            <div className="mt-6 pt-4 border-t border-gray-800">
              <div className="text-xs text-center text-gray-600 mb-2">INTEGRATIONS</div>
              <div className="flex justify-center gap-4 text-gray-400">
                <span className="flex items-center gap-1 text-xs"><div className="w-1.5 h-1.5 bg-green-500 rounded-full"/> Historabook</span>
                <span className="flex items-center gap-1 text-xs"><div className="w-1.5 h-1.5 bg-green-500 rounded-full"/> VrindaDev</span>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
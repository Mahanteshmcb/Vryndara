import React, { useState, useEffect, useRef } from 'react';
import { Terminal, Activity, Play, Pause, Trash2 } from 'lucide-react';

const GATEWAY_WS = "ws://localhost:8081/ws";

const LogEntry = ({ log }) => {
  let color = "text-gray-400";
  let bg = "bg-transparent";
  
  if (log.type === "TASK_REQUEST") { color = "text-blue-400"; bg = "bg-blue-900/10"; }
  if (log.type === "TASK_RESULT") { color = "text-green-400"; bg = "bg-green-900/10"; }
  if (log.type === "ERROR") { color = "text-red-400"; bg = "bg-red-900/10"; }

  return (
    <div className={`mb-1 font-mono text-xs border-b border-gray-800 pb-2 pt-2 px-2 ${bg} rounded hover:bg-white/5 transition-colors`}>
      <div className="flex justify-between text-gray-500 text-[10px] mb-1">
        <span>{new Date(log.timestamp * 1000).toLocaleTimeString()}</span>
        <span className="uppercase tracking-widest">{log.type}</span>
      </div>
      <div className="flex items-start gap-2">
        <span className={`font-bold ${color} whitespace-nowrap`}>{log.source_agent_id}</span>
        <span className="text-gray-600">➔</span>
        <span className="text-purple-400 whitespace-nowrap">{log.target_agent_id}</span>
      </div>
      <div className="mt-1 ml-4 text-gray-300 break-words leading-relaxed">
        {log.payload}
      </div>
    </div>
  );
};

export default function LiveConsolePage() {
  const [isConnected, setIsConnected] = useState(false);
  const [logs, setLogs] = useState([]);
  const [autoScroll, setAutoScroll] = useState(true);
  const scrollRef = useRef(null);

  useEffect(() => {
    const ws = new WebSocket(GATEWAY_WS);

    ws.onopen = () => {
      console.log("✅ Live Console Connected");
      setIsConnected(true);
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (!data.timestamp) data.timestamp = Date.now() / 1000;
        setLogs(prev => [...prev.slice(-199), data]); 
      } catch (e) { console.error(e); }
    };

    ws.onclose = () => setIsConnected(false);
    return () => ws.close();
  }, []);

  useEffect(() => {
    if (autoScroll && scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs, autoScroll]);

  return (
    <div className="h-[calc(100vh-100px)] m-4 flex flex-col bg-[#0a0a0a] rounded-lg border border-gray-800 overflow-hidden">
      {/* TOOLBAR */}
      <div className="bg-gray-900/50 p-3 border-b border-gray-800 flex justify-between items-center backdrop-blur-sm">
        <div className="flex items-center gap-3">
          <Terminal size={18} className="text-green-500" />
          <h2 className="font-bold text-sm tracking-wide text-gray-200">NEURAL FEED</h2>
          <div className={`px-2 py-0.5 rounded text-[10px] font-bold border ${isConnected ? 'border-green-800 bg-green-900/20 text-green-400' : 'border-red-800 bg-red-900/20 text-red-400'} flex items-center gap-1`}>
            <div className={`w-1.5 h-1.5 rounded-full ${isConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`} />
            {isConnected ? "ONLINE" : "OFFLINE"}
          </div>
        </div>
        
        <div className="flex gap-2">
          <button onClick={() => setLogs([])} className="p-1.5 hover:bg-white/10 rounded text-gray-400 hover:text-white" title="Clear">
            <Trash2 size={16} />
          </button>
          <button onClick={() => setAutoScroll(!autoScroll)} className={`p-1.5 rounded ${autoScroll ? 'text-green-400 bg-green-900/20' : 'text-gray-400 hover:bg-white/10'}`} title="Auto-Scroll">
            {autoScroll ? <Pause size={16} /> : <Play size={16} />}
          </button>
        </div>
      </div>

      {/* LOG AREA */}
      <div className="flex-1 overflow-y-auto p-4 space-y-2 font-mono" ref={scrollRef}>
        {logs.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-gray-700 space-y-2 opacity-50">
            <Activity size={48} />
            <p>Waiting for neural signals...</p>
            <p className="text-xs">System ready. Trigger an agent to view activity.</p>
          </div>
        ) : (
          logs.map((log, i) => <LogEntry key={i} log={log} />)
        )}
      </div>
    </div>
  );
}
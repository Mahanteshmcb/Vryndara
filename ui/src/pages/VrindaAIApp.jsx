import React, { useState } from 'react';
import { FaCube, FaMagic, FaImage, FaTerminal, FaCheckCircle, FaSpinner } from 'react-icons/fa';

export default function VrindaAIApp() {
  const [prompt, setPrompt] = useState('');
  const [status, setStatus] = useState('IDLE'); // IDLE, GENERATING, RENDERING, COMPLETE
  const [logs, setLogs] = useState([]);
  const [geometryData, setGeometryData] = useState(null);
  const [renderUrl, setRenderUrl] = useState(null);

  const addLog = (msg) => setLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] ${msg}`]);

  const handleGenerate = async () => {
    if (!prompt) return;
    setStatus('GENERATING');
    setLogs([]);
    addLog("🚀 Sending task to Mistral Engineering Brain...");

    try {
      const res = await fetch('http://localhost:8081/api/engineer/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt })
      });
      
      const data = await res.json();
      
      if (data.status === 'success') {
        setGeometryData(data.data); // Contains stl paths and blueprint
        addLog("✅ Geometry compiled successfully.");
        addLog(`📦 Volume: ${data.data.blueprint_data.volume_cm3} cm³`);
        setStatus('READY_TO_RENDER');
      } else {
        addLog(`❌ Error: ${data.detail || "Unknown error"}`);
        setStatus('IDLE');
      }
    } catch (e) {
      addLog(`🔥 Network Error: ${e.message}`);
      setStatus('IDLE');
    }
  };

  const handleRender = async () => {
    if (!geometryData) return;
    setStatus('RENDERING');
    addLog("🎨 Sending geometry to Blender Engine...");

    try {
      // Note: We send the LOCAL file path because Blender runs on the same server
      const res = await fetch('http://localhost:8081/api/engineer/render', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ stl_path: geometryData.high_res })
      });

      const data = await res.json();
      
      if (data.status === 'success') {
        // Convert local path to a file URL (or serve it statically in real prod)
        // For local dev, we might need to rely on the backend serving this folder
        // For now, let's assume we can load it if the browser allows local file access 
        // OR simpler: Display the path for now
        setRenderUrl(data.image_path);
        addLog("✨ Render Complete!");
        setStatus('COMPLETE');
      }
    } catch (e) {
      addLog(`🔥 Render Error: ${e.message}`);
      setStatus('READY_TO_RENDER');
    }
  };

  return (
    <div className="flex h-full bg-[#0a0a0a] text-white">
      {/* LEFT: CONTROLS */}
      <div className="w-1/3 border-r border-gray-800 p-6 flex flex-col">
        <div className="mb-8 flex items-center gap-3 text-cyan-400">
          <FaCube size={28} />
          <h1 className="text-2xl font-bold tracking-wider">VRINDA<span className="text-white">AI</span></h1>
        </div>

        <div className="space-y-4 mb-6">
          <label className="text-xs font-bold text-gray-500 uppercase">Engineering Prompt</label>
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            className="w-full bg-[#111113] border border-gray-700 rounded-lg p-4 text-sm focus:border-cyan-500 outline-none h-32 resize-none"
            placeholder="E.g., Design a coffee mug with a thick handle..."
          />
          <button
            onClick={handleGenerate}
            disabled={status !== 'IDLE' && status !== 'COMPLETE'}
            className={`w-full py-3 rounded-lg font-bold flex items-center justify-center gap-2 transition-all ${
              status === 'GENERATING' 
                ? 'bg-gray-800 text-gray-400 cursor-not-allowed'
                : 'bg-cyan-600 hover:bg-cyan-500 text-white'
            }`}
          >
            {status === 'GENERATING' ? <FaSpinner className="animate-spin" /> : <FaMagic />}
            Generate Geometry
          </button>
        </div>

        {/* Console Output */}
        <div className="flex-1 bg-black rounded-lg border border-gray-800 p-4 font-mono text-xs overflow-y-auto text-green-400 space-y-1">
          <div className="flex items-center gap-2 text-gray-500 border-b border-gray-900 pb-2 mb-2">
            <FaTerminal /> SYSTEM LOG
          </div>
          {logs.map((log, i) => <div key={i}>{log}</div>)}
        </div>
      </div>

      {/* RIGHT: PREVIEW */}
      <div className="flex-1 p-8 flex flex-col items-center justify-center bg-[#050505] relative">
        {!geometryData ? (
          <div className="text-gray-700 flex flex-col items-center gap-4">
            <FaCube size={64} />
            <p>Waiting for Input...</p>
          </div>
        ) : (
          <div className="w-full max-w-3xl space-y-6 animate-fade-in">
            
            {/* Blueprint View */}
            {geometryData.blueprint_data && (
               <div className="bg-[#001a33] border border-cyan-900/50 rounded-lg p-1 overflow-hidden relative group">
                 <div className="absolute top-2 left-2 text-[10px] text-cyan-400 font-mono bg-black/50 px-2 py-1 rounded">BLUEPRINT</div>
                 {/* In a real web app, we'd serve this image via HTTP. For now, we show a placeholder unless you set up static serving. */}
                 <div className="h-64 w-full flex items-center justify-center text-cyan-600/50">
                    [Blueprint Loaded: {geometryData.blueprint_data.mass_grams}g]
                 </div>
               </div>
            )}

            {/* Render Button */}
            {status === 'READY_TO_RENDER' && (
              <button
                onClick={handleRender}
                className="w-full py-4 border-2 border-dashed border-gray-700 hover:border-purple-500 hover:bg-purple-900/10 rounded-xl text-gray-400 hover:text-white transition-all flex flex-col items-center gap-2"
              >
                <FaImage size={24} />
                <span>Process High-Fidelity Render (Blender)</span>
              </button>
            )}

            {/* Final Render */}
            {status === 'RENDERING' && (
               <div className="w-full h-64 flex items-center justify-center text-purple-400 animate-pulse">
                 Processing Raytracing...
               </div>
            )}

            {renderUrl && (
              <div className="bg-black border border-purple-900/50 rounded-lg p-1 overflow-hidden relative animate-fade-in">
                 <div className="absolute top-2 left-2 text-[10px] text-purple-400 font-mono bg-black/50 px-2 py-1 rounded">FINAL RENDER</div>
                 {/* Again, needs static file serving for the image to actually show in browser */}
                 <div className="h-96 w-full flex items-center justify-center text-purple-200">
                    Render Saved at: {renderUrl}
                 </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
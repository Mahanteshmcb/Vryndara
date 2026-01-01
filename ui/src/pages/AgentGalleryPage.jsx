import React, { useState, useEffect } from 'react';
import { Bot, Code, Video, BookOpen, Settings, Download, Check, Terminal } from 'lucide-react';

const APP_STORE_KEY = "vryndara_installed_apps";

const initialApps = [
  { 
    id: "historabook",
    name: "Historabook", 
    role: "APP SUITE", 
    icon: BookOpen, 
    color: "green",
    description: "AI-powered history timeline generator. Converts text into interactive visual lessons.",
    capabilities: ["Timeline Gen", "Visual Learning", "Quiz Auto-Gen"],
    installed: false,
    url: "http://localhost:8001" 
  },
  { 
    id: "vrindadev",
    name: "VrindaDev", 
    role: "DEV TOOLS", 
    icon: Terminal, 
    color: "purple",
    description: "Automated coding assistant and project bootstrapper. Generates boilerplate code instantly.",
    capabilities: ["Scaffolding", "Refactoring", "Doc Gen"],
    installed: false,
    url: "app://vrindadev" // Placeholder for Desktop App
  },
  { 
    id: "vrinda_ai", 
    name: "VrindaAI", 
    role: "ENGINEERING", 
    icon: Code, 
    color: "cyan",
    description: "Text-to-CAD Engineering Engine. Generates 3D STL files and blueprints from natural language prompts.",
    capabilities: ["CAD Generation", "Physics Calc", "Blender Render"],
    installed: false,
    url: "/vrinda-ai" 
  },
  { 
    id: "media_director",
    name: "Media Director", 
    role: "CORE AGENT", 
    icon: Video, 
    color: "pink",
    description: "Specializes in visual storytelling, scriptwriting, and scene composition.",
    capabilities: ["Scriptwriting", "Video Rendering", "TTS Audio"],
    installed: true,
    core: true
  },
  { 
    id: "researcher",
    name: "Researcher", 
    role: "CORE AGENT", 
    icon: BookOpen, 
    color: "blue",
    description: "Deep web retrieval specialist. Gathers facts and summarizes documents.",
    capabilities: ["Web Scrape", "Fact Check"],
    installed: true,
    core: true
  }
];

export default function AgentGalleryPage() {
  const [apps, setApps] = useState(initialApps);

  useEffect(() => {
    const saved = localStorage.getItem(APP_STORE_KEY);
    if (saved) {
      const savedState = JSON.parse(saved);
      setApps(prev => prev.map(app => ({
        ...app,
        installed: savedState[app.id] ?? app.installed
      })));
    }
  }, []);

  const toggleInstall = (id) => {
    setApps(prev => {
      const newApps = prev.map(app => 
        app.id === id ? { ...app, installed: !app.installed } : app
      );
      const saveState = newApps.reduce((acc, app) => ({...acc, [app.id]: app.installed}), {});
      localStorage.setItem(APP_STORE_KEY, JSON.stringify(saveState));
      return newApps;
    });
  };

  return (
    <div className="p-8 max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white">App & Agent Store</h1>
        <p className="text-gray-500 mt-2">Install capabilities and connect external applications to the Vryndara OS.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {apps.map((app) => (
          <div key={app.id} className={`bg-[#111113] border ${app.installed ? 'border-green-900/50' : 'border-gray-800'} rounded-xl overflow-hidden hover:border-gray-600 transition-all duration-300 group`}>
            
            <div className={`h-24 bg-gradient-to-r from-${app.color}-900/50 to-transparent p-6 relative`}>
              <div className={`w-12 h-12 rounded-lg bg-[#0a0a0a] border border-gray-700 flex items-center justify-center text-${app.color}-500 shadow-xl group-hover:scale-110 transition-transform`}>
                <app.icon size={24} />
              </div>
              {app.installed && (
                <div className="absolute top-4 right-4 bg-green-500/20 text-green-400 px-2 py-1 rounded text-xs font-bold flex items-center gap-1">
                  <Check size={12} /> INSTALLED
                </div>
              )}
            </div>

            <div className="p-6 pt-2 text-white">
              <h3 className="text-xl font-bold">{app.name}</h3>
              <p className={`text-sm text-${app.color}-400 font-mono mb-4`}>{app.role}</p>
              <p className="text-gray-400 text-sm mb-6 leading-relaxed min-h-[60px]">
                {app.description}
              </p>
              
              <div className="space-y-2 mb-6">
                <div className="text-xs font-bold text-gray-600 uppercase">Capabilities</div>
                <div className="flex flex-wrap gap-2">
                  {app.capabilities.map((cap, i) => (
                    <span key={i} className="px-2 py-1 bg-gray-900 border border-gray-800 rounded text-xs text-gray-300">
                      {cap}
                    </span>
                  ))}
                </div>
              </div>
              
              {app.core ? (
                <div className="w-full py-2 bg-gray-900/50 border border-gray-800 rounded-lg text-sm text-gray-500 text-center cursor-not-allowed">
                  System Core (Built-in)
                </div>
              ) : (
                <button 
                  onClick={() => toggleInstall(app.id)}
                  className={`w-full py-2 border rounded-lg text-sm font-bold transition-colors flex items-center justify-center gap-2 ${
                    app.installed 
                    ? 'border-gray-700 text-gray-400 hover:bg-red-900/20 hover:text-red-400 hover:border-red-900' 
                    : 'bg-green-600 border-green-600 text-white hover:bg-green-500'
                  }`}
                >
                  {app.installed ? 'Uninstall' : <><Download size={16} /> Install App</>}
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
import React from 'react';
import { Bot, Code, Video, BookOpen, Settings } from 'lucide-react';

const AgentProfile = ({ name, role, description, icon: Icon, color, capabilities }) => (
  <div className="bg-[#111113] border border-gray-800 rounded-xl overflow-hidden hover:border-gray-600 transition-all duration-300 group">
    <div className={`h-24 bg-gradient-to-r from-${color}-900/50 to-transparent p-6`}>
      <div className={`w-12 h-12 rounded-lg bg-[#0a0a0a] border border-gray-700 flex items-center justify-center text-${color}-500 shadow-xl group-hover:scale-110 transition-transform`}>
        <Icon size={24} />
      </div>
    </div>
    <div className="p-6 pt-2 text-white">
      <h3 className="text-xl font-bold">{name}</h3>
      <p className={`text-sm text-${color}-400 font-mono mb-4`}>{role}</p>
      <p className="text-gray-400 text-sm mb-6 leading-relaxed">
        {description}
      </p>
      
      <div className="space-y-2">
        <div className="text-xs font-bold text-gray-600 uppercase">Capabilities</div>
        <div className="flex flex-wrap gap-2">
          {capabilities.map((cap, i) => (
            <span key={i} className="px-2 py-1 bg-gray-900 border border-gray-800 rounded text-xs text-gray-300">
              {cap}
            </span>
          ))}
        </div>
      </div>
      
      <button className="w-full mt-6 py-2 border border-gray-700 rounded-lg text-sm text-gray-300 hover:bg-gray-800 transition-colors flex items-center justify-center gap-2">
        <Settings size={14} /> Configure Agent
      </button>
    </div>
  </div>
);

export default function AgentGalleryPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white">Neural Agents</h1>
        <p className="text-gray-500 mt-2">Manage and configure the specialized intelligences powering Vryndara.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <AgentProfile 
          name="Media Director" 
          role="CREATIVE ENGINE" 
          icon={Video} 
          color="pink"
          description="Specializes in visual storytelling, scriptwriting, and scene composition using computer vision models."
          capabilities={["Scriptwriting", "Image Gen", "Video Rendering", "TTS Audio"]}
        />
        
        <AgentProfile 
          name="Coder Alpha" 
          role="ENGINEERING CORE" 
          icon={Code} 
          color="yellow"
          description="Advanced coding assistant capable of generating boilerplate, refactoring legacy code, and debugging errors."
          capabilities={["Python", "React/JS", "Refactoring", "Documentation"]}
        />

        <AgentProfile 
          name="Researcher-1" 
          role="KNOWLEDGE BASE" 
          icon={BookOpen} 
          color="cyan"
          description="Deep web retrieval specialist. Gathers facts, summarizes documents, and provides context for other agents."
          capabilities={["Web Scrape", "Summarization", "Fact Check", "Report Gen"]}
        />
      </div>
    </div>
  );
}
import { useState } from 'react';
import { FaRobot, FaSearch, FaDownload, FaCheck, FaMicrochip, FaBook, FaCode, FaNetworkWired } from 'react-icons/fa';

// Mock Marketplace Data
const initialAgents = [
  { id: 1, name: 'Coder Alpha', category: 'Productivity', description: 'General purpose Python coding assistant powered by Llama 3.', icon: FaCode, installed: true },
  { id: 2, name: 'HistorA Tutor', category: 'Education', description: 'Interactive history tutor that generates visual timelines.', icon: FaBook, installed: false },
  { id: 3, name: 'Robot Controller', category: 'Robotics', description: 'ROS2 bridge for controlling manipulators and mobile bases.', icon: FaMicrochip, installed: false },
  { id: 4, name: 'Web Researcher', category: 'Productivity', description: 'Searches the web and summarizes findings automatically.', icon: FaNetworkWired, installed: false },
  { id: 5, name: 'IoT Monitor', category: 'Robotics', description: 'Real-time telemetry monitor for MQTT/HTTP sensors.', icon: FaCheck, installed: true },
  { id: 6, name: 'Data Analyst', category: 'Productivity', description: 'Process CSV/Excel files and generate charts.', icon: FaChartPie => <FaRobot />, installed: false }, // Quick fix icon
];

const AgentGalleryPage = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [agents, setAgents] = useState(initialAgents);
  const [activeTab, setActiveTab] = useState('All');

  const categories = ['All', 'Productivity', 'Robotics', 'Education'];

  const toggleInstall = (id) => {
    setAgents(prev => prev.map(agent => 
      agent.id === id ? { ...agent, installed: !agent.installed } : agent
    ));
  };

  const filteredAgents = agents.filter(agent => {
    const matchesSearch = agent.name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = activeTab === 'All' || agent.category === activeTab;
    return matchesSearch && matchesCategory;
  });

  return (
    <div className="p-8 space-y-8 animate-fade-in">
      
      {/* Header & Search */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-white">Agent Gallery</h1>
          <p className="text-gray-400 mt-1">Browse and install AI capabilities</p>
        </div>
        
        <div className="relative w-full md:w-96">
          <FaSearch className="absolute left-4 top-3.5 text-gray-500" />
          <input 
            type="text"
            placeholder="Search agents..." 
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-gray-800 border border-gray-700 text-white pl-10 pr-4 py-3 rounded-xl focus:outline-none focus:border-green-500 transition-colors"
          />
        </div>
      </div>

      {/* Category Tabs */}
      <div className="flex gap-2 overflow-x-auto pb-2">
        {categories.map(cat => (
          <button
            key={cat}
            onClick={() => setActiveTab(cat)}
            className={`px-6 py-2 rounded-full font-medium transition-colors whitespace-nowrap ${
              activeTab === cat 
                ? 'bg-green-600 text-white' 
                : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Grid of Agents */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredAgents.map((agent) => {
          const Icon = agent.icon;
          return (
            <div key={agent.id} className="bg-gray-800 border border-gray-700 rounded-xl p-6 shadow-lg hover:border-green-500/50 transition-colors group relative overflow-hidden">
              
              {/* Subtle Glow Effect */}
              <div className="absolute top-0 right-0 p-32 bg-green-500/5 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2 group-hover:bg-green-500/10 transition-colors"></div>

              <div className="relative z-10 flex flex-col h-full">
                <div className="flex justify-between items-start mb-4">
                  <div className={`p-4 rounded-xl ${agent.installed ? 'bg-green-500/20 text-green-400' : 'bg-gray-700/50 text-gray-400'}`}>
                    <Icon className="text-3xl" />
                  </div>
                  <span className="text-xs font-mono text-gray-500 border border-gray-700 px-2 py-1 rounded">
                    {agent.category}
                  </span>
                </div>

                <h3 className="text-xl font-bold text-white mb-2">{agent.name}</h3>
                <p className="text-gray-400 text-sm mb-6 flex-1">
                  {agent.description}
                </p>

                <div className="flex gap-3 mt-auto">
                  <button 
                    onClick={() => toggleInstall(agent.id)}
                    className={`flex-1 flex items-center justify-center gap-2 py-2.5 rounded-lg font-bold transition-colors ${
                      agent.installed
                        ? 'bg-gray-700 text-gray-300 hover:bg-red-900/50 hover:text-red-400'
                        : 'bg-green-600 text-white hover:bg-green-500'
                    }`}
                  >
                    {agent.installed ? (
                      <>
                        <FaCheck /> Installed
                      </>
                    ) : (
                      <>
                        <FaDownload /> Install
                      </>
                    )}
                  </button>
                  <button className="px-4 py-2 border border-gray-600 text-gray-300 rounded-lg hover:bg-gray-700">
                    Details
                  </button>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default AgentGalleryPage;
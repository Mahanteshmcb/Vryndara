import { useEffect, useState } from 'react';
import { FaTimes, FaRobot, FaMicrochip } from 'react-icons/fa';

const PropertiesPanel = ({ selectedNode, onClose, onUpdate }) => {
  const [label, setLabel] = useState('');
  const [task, setTask] = useState('');
  const [agentId, setAgentId] = useState('');

  // When user clicks a different node, update the form
  useEffect(() => {
    if (selectedNode) {
      setLabel(selectedNode.data.label || '');
      setTask(selectedNode.data.task || '');
      setAgentId(selectedNode.data.agentId || '');
    }
  }, [selectedNode]);

  const handleSave = () => {
    onUpdate(selectedNode.id, { 
      label, 
      task, 
      agentId 
    });
  };

  if (!selectedNode) return null;

  return (
    <div className="absolute right-0 top-16 bottom-0 w-80 bg-gray-800 border-l border-gray-700 shadow-2xl p-6 overflow-y-auto transform transition-transform animate-slide-in z-10">
      
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-bold text-white flex items-center gap-2">
          <FaMicrochip className="text-green-400" />
          Properties
        </h2>
        <button onClick={onClose} className="text-gray-400 hover:text-white transition-colors">
          <FaTimes />
        </button>
      </div>

      <div className="space-y-6">
        
        {/* Node Name Input */}
        <div>
          <label className="block text-xs font-bold text-gray-400 uppercase mb-2">Node Name</label>
          <input 
            type="text" 
            value={label}
            onChange={(e) => setLabel(e.target.value)}
            className="w-full bg-gray-900 border border-gray-700 rounded-lg p-3 text-white focus:border-green-500 focus:outline-none"
          />
        </div>

        {/* Agent ID Selector (Simplified for now) */}
        <div>
          <label className="block text-xs font-bold text-gray-400 uppercase mb-2">Assigned Agent</label>
          <select 
            value={agentId}
            onChange={(e) => setAgentId(e.target.value)}
            className="w-full bg-gray-900 border border-gray-700 rounded-lg p-3 text-white focus:border-green-500 focus:outline-none appearance-none"
          >
            <option value="">Select an Agent...</option>
            <option value="researcher-1">Researcher Agent</option>
            <option value="coder-alpha">Coder Agent (Llama 3)</option>
            <option value="robot-1">Robot Controller</option>
          </select>
        </div>

        {/* Task Prompt Area */}
        <div>
          <label className="block text-xs font-bold text-gray-400 uppercase mb-2">Task Instruction</label>
          <textarea 
            value={task}
            onChange={(e) => setTask(e.target.value)}
            rows={6}
            className="w-full bg-gray-900 border border-gray-700 rounded-lg p-3 text-white focus:border-green-500 focus:outline-none resize-none font-mono text-sm"
            placeholder="What should this agent do?"
          />
          <p className="text-xs text-gray-500 mt-2">
            This prompt will be sent to the Local LLM.
          </p>
        </div>

        {/* Save Button */}
        <button 
          onClick={handleSave}
          className="w-full bg-green-600 hover:bg-green-500 text-white font-bold py-3 rounded-lg transition-all"
        >
          Update Node
        </button>

        {/* Debug Info */}
        <div className="pt-6 border-t border-gray-700">
            <p className="text-xs text-gray-600 font-mono">ID: {selectedNode.id}</p>
        </div>

      </div>
    </div>
  );
};

export default PropertiesPanel;
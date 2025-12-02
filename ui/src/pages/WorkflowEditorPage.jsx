import { useState, useCallback } from 'react';
import ReactFlow, { 
  Controls, 
  Background, 
  applyEdgeChanges, 
  applyNodeChanges, 
  addEdge,
  MarkerType
} from 'reactflow';
import 'reactflow/dist/style.css';
import { FaPlay, FaSave, FaPlus, FaSpinner } from 'react-icons/fa';
import axios from 'axios';

// API Configuration
const API_URL = "http://localhost:8081";

// --- Initial Nodes ---
const initialNodes = [
  { 
    id: '1', 
    type: 'input', 
    data: { label: 'HistorA Tutor (Trigger)' }, 
    position: { x: 250, y: 50 },
    style: { background: '#1F2937', color: '#fff', border: '1px solid #10B981', borderRadius: '10px', width: 180 }
  },
  { 
    id: '2', 
    data: { label: 'Researcher Agent', agentId: 'researcher-1', task: 'Search for History of Rome' }, 
    position: { x: 100, y: 200 },
    style: { background: '#1F2937', color: '#fff', border: '1px solid #3B82F6', borderRadius: '10px', width: 180 }
  },
  { 
    id: '3', 
    data: { label: 'Coder Agent', agentId: 'coder-alpha', task: 'Write a summary script' }, 
    position: { x: 400, y: 200 },
    style: { background: '#1F2937', color: '#fff', border: '1px solid #8B5CF6', borderRadius: '10px', width: 180 }
  },
  { 
    id: '4', 
    type: 'output', 
    data: { label: 'Robot Output' }, 
    position: { x: 250, y: 350 },
    style: { background: '#1F2937', color: '#fff', border: '1px solid #EC4899', borderRadius: '10px', width: 180 }
  },
];

const initialEdges = [
  { id: 'e1-2', source: '1', target: '2', animated: true, style: { stroke: '#10B981' } },
  { id: 'e1-3', source: '1', target: '3', animated: true, style: { stroke: '#10B981' } },
  { id: 'e2-4', source: '2', target: '4', markerEnd: { type: MarkerType.ArrowClosed }, style: { stroke: '#3B82F6' } },
  { id: 'e3-4', source: '3', target: '4', markerEnd: { type: MarkerType.ArrowClosed }, style: { stroke: '#8B5CF6' } },
];

const WorkflowEditorPage = () => {
  const [nodes, setNodes] = useState(initialNodes);
  const [edges, setEdges] = useState(initialEdges);
  const [isRunning, setIsRunning] = useState(false);

  const onNodesChange = useCallback((changes) => setNodes((nds) => applyNodeChanges(changes, nds)), []);
  const onEdgesChange = useCallback((changes) => setEdges((eds) => applyEdgeChanges(changes, eds)), []);
  const onConnect = useCallback((params) => setEdges((eds) => addEdge(params, eds)), []);

  // --- THE NEW LOGIC: Run the Graph ---
  const handleRunSimulation = async () => {
    setIsRunning(true);
    
    // 1. Convert Nodes to Workflow Steps
    // In a real app, we would traverse the graph. For Phase 1, we filter for known agents.
    const steps = [];
    let orderCounter = 1;

    nodes.forEach(node => {
        // If the node has an 'agentId' (defined in initialNodes above), we add it to execution
        if (node.data.agentId) {
            steps.push({
                agent_id: node.data.agentId,
                task: node.data.task || "Default Task",
                order: orderCounter++ 
            });
        }
    });

    try {
        console.log("Sending Workflow:", steps);
        
        // 2. Call the API
        const res = await axios.post(`${API_URL}/api/v1/workflow`, { steps });
        
        alert(`Workflow Started! ID: ${res.data.id}`);
        
    } catch (err) {
        console.error(err);
        alert("Failed to start workflow. Check console.");
    }

    setTimeout(() => setIsRunning(false), 2000); // Reset button after 2s
  };

  return (
    <div className="h-full flex flex-col bg-gray-900 text-white animate-fade-in">
      
      {/* Toolbar */}
      <div className="h-16 border-b border-gray-700 flex items-center justify-between px-6 bg-gray-800">
        <div className="flex items-center gap-4">
          <h1 className="text-xl font-bold">Project Canvas: <span className="text-green-400">Demo Workflow</span></h1>
          {isRunning && <span className="text-xs bg-green-900 text-green-200 px-2 py-1 rounded animate-pulse">Running...</span>}
        </div>
        <div className="flex gap-3">
          <button className="flex items-center gap-2 px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg text-sm transition-colors">
            <FaPlus /> Add Node
          </button>
          <button className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg text-sm transition-colors">
            <FaSave /> Save
          </button>
          
          <button 
            onClick={handleRunSimulation}
            disabled={isRunning}
            className={`flex items-center gap-2 px-6 py-2 rounded-lg text-sm font-bold shadow-lg transition-all 
                ${isRunning ? 'bg-gray-600 cursor-not-allowed' : 'bg-green-600 hover:bg-green-500 hover:scale-105 shadow-green-900/50'}`}
          >
            {isRunning ? <FaSpinner className="animate-spin" /> : <FaPlay />}
            {isRunning ? 'Executing...' : 'Run Simulation'}
          </button>
        </div>
      </div>

      <div className="flex-1 w-full h-[calc(100vh-64px)]">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          fitView
          className="bg-gray-900"
        >
          <Background color="#374151" gap={20} />
          <Controls className="bg-gray-800 border-gray-700 text-white fill-white" />
        </ReactFlow>
      </div>

    </div>
  );
};

export default WorkflowEditorPage;
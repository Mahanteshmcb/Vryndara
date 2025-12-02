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
import { FaPlay, FaSave, FaPlus } from 'react-icons/fa';

// --- Initial Nodes (The Workflow) ---
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
    data: { label: 'Researcher Agent (Python)' }, 
    position: { x: 100, y: 200 },
    style: { background: '#1F2937', color: '#fff', border: '1px solid #3B82F6', borderRadius: '10px', width: 180 }
  },
  { 
    id: '3', 
    data: { label: 'Coder Agent (Llama 3)' }, 
    position: { x: 400, y: 200 },
    style: { background: '#1F2937', color: '#fff', border: '1px solid #8B5CF6', borderRadius: '10px', width: 180 }
  },
  { 
    id: '4', 
    type: 'output', 
    data: { label: 'Robot Controller (ROS2)' }, 
    position: { x: 250, y: 350 },
    style: { background: '#1F2937', color: '#fff', border: '1px solid #EC4899', borderRadius: '10px', width: 180 }
  },
];

// --- Connections (The Lines) ---
const initialEdges = [
  { id: 'e1-2', source: '1', target: '2', animated: true, style: { stroke: '#10B981' } },
  { id: 'e1-3', source: '1', target: '3', animated: true, style: { stroke: '#10B981' } },
  { id: 'e2-4', source: '2', target: '4', markerEnd: { type: MarkerType.ArrowClosed }, style: { stroke: '#3B82F6' } },
  { id: 'e3-4', source: '3', target: '4', markerEnd: { type: MarkerType.ArrowClosed }, style: { stroke: '#8B5CF6' } },
];

const WorkflowEditorPage = () => {
  const [nodes, setNodes] = useState(initialNodes);
  const [edges, setEdges] = useState(initialEdges);

  // Handlers for dragging nodes and connecting lines
  const onNodesChange = useCallback((changes) => setNodes((nds) => applyNodeChanges(changes, nds)), []);
  const onEdgesChange = useCallback((changes) => setEdges((eds) => applyEdgeChanges(changes, eds)), []);
  const onConnect = useCallback((params) => setEdges((eds) => addEdge(params, eds)), []);

  return (
    <div className="h-full flex flex-col bg-gray-900 text-white animate-fade-in">
      
      {/* Toolbar */}
      <div className="h-16 border-b border-gray-700 flex items-center justify-between px-6 bg-gray-800">
        <div className="flex items-center gap-4">
          <h1 className="text-xl font-bold">Project Canvas: <span className="text-green-400">Demo Workflow</span></h1>
          <span className="text-xs bg-gray-700 px-2 py-1 rounded text-gray-300">Read Only Mode</span>
        </div>
        <div className="flex gap-3">
          <button className="flex items-center gap-2 px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg text-sm transition-colors">
            <FaPlus /> Add Node
          </button>
          <button className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg text-sm transition-colors">
            <FaSave /> Save
          </button>
          <button className="flex items-center gap-2 px-6 py-2 bg-green-600 hover:bg-green-500 rounded-lg text-sm font-bold shadow-lg shadow-green-900/50 transition-all hover:scale-105">
            <FaPlay /> Run Simulation
          </button>
        </div>
      </div>

      {/* The Graph Editor */}
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
          {/* Background Grid */}
          <Background color="#374151" gap={20} />
          
          {/* Zoom Controls */}
          <Controls className="bg-gray-800 border-gray-700 text-white fill-white" />
        </ReactFlow>
      </div>

    </div>
  );
};

export default WorkflowEditorPage;
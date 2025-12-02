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
import PropertiesPanel from '../components/PropertiesPanel'; // Import the new panel

const API_URL = "http://localhost:8081";

// Initial nodes (Notice the 'task' field is editable now!)
const initialNodes = [
  { 
    id: '1', 
    type: 'input', 
    data: { label: 'Start Trigger' }, 
    position: { x: 250, y: 50 },
    style: { background: '#1F2937', color: '#fff', border: '1px solid #10B981', borderRadius: '10px', width: 180 }
  },
  { 
    id: '2', 
    data: { label: 'Coder Agent', agentId: 'coder-alpha', task: 'Write a Python script to print the first 10 Fibonacci numbers.' }, 
    position: { x: 250, y: 200 },
    style: { background: '#1F2937', color: '#fff', border: '1px solid #8B5CF6', borderRadius: '10px', width: 180 }
  },
  { 
    id: '3', 
    type: 'output', 
    data: { label: 'Output Log' }, 
    position: { x: 250, y: 350 },
    style: { background: '#1F2937', color: '#fff', border: '1px solid #EC4899', borderRadius: '10px', width: 180 }
  },
];

const initialEdges = [
  { id: 'e1-2', source: '1', target: '2', animated: true, style: { stroke: '#10B981' } },
  { id: 'e2-3', source: '2', target: '3', markerEnd: { type: MarkerType.ArrowClosed }, style: { stroke: '#8B5CF6' } },
];

const WorkflowEditorPage = () => {
  const [nodes, setNodes] = useState(initialNodes);
  const [edges, setEdges] = useState(initialEdges);
  const [isRunning, setIsRunning] = useState(false);
  const [selectedNode, setSelectedNode] = useState(null); // Track which node is clicked

  const onNodesChange = useCallback((changes) => setNodes((nds) => applyNodeChanges(changes, nds)), []);
  const onEdgesChange = useCallback((changes) => setEdges((eds) => applyEdgeChanges(changes, eds)), []);
  const onConnect = useCallback((params) => setEdges((eds) => addEdge(params, eds)), []);

  // --- NEW: Handle Click ---
  const onNodeClick = useCallback((event, node) => {
    setSelectedNode(node);
  }, []);

  const onPaneClick = useCallback(() => {
    setSelectedNode(null); // Close panel when clicking background
  }, []);

  // --- NEW: Update Node Data ---
  const handleUpdateNode = (nodeId, newData) => {
    setNodes((nds) => 
      nds.map((node) => {
        if (node.id === nodeId) {
          return { 
            ...node, 
            data: { ...node.data, ...newData } // Merge new data
          };
        }
        return node;
      })
    );
    // Keep panel open but refresh data logic is handled by useEffect in panel
  };

  const handleRunSimulation = async () => {
    setIsRunning(true);
    
    // Convert Nodes to Steps (Dynamic!)
    const steps = [];
    let orderCounter = 1;

    // Sort nodes by Y position to guess order (simple logic)
    const sortedNodes = [...nodes].sort((a, b) => a.position.y - b.position.y);

    sortedNodes.forEach(node => {
        if (node.data.agentId && node.data.task) {
            steps.push({
                agent_id: node.data.agentId,
                task: node.data.task, // Uses the CURRENT text in the node
                order: orderCounter++ 
            });
        }
    });

    try {
        console.log("Sending Workflow:", steps);
        const res = await axios.post(`${API_URL}/api/v1/workflow`, { steps });
        alert(`Workflow Started! ID: ${res.data.id}`);
    } catch (err) {
        console.error(err);
        alert("Failed to start workflow.");
    }

    setTimeout(() => setIsRunning(false), 2000);
  };

  return (
    <div className="h-full flex flex-col bg-gray-900 text-white animate-fade-in relative">
      
      {/* Toolbar */}
      <div className="h-16 border-b border-gray-700 flex items-center justify-between px-6 bg-gray-800">
        <h1 className="text-xl font-bold">Project Canvas</h1>
        <div className="flex gap-3">
          <button 
            onClick={handleRunSimulation}
            disabled={isRunning}
            className={`flex items-center gap-2 px-6 py-2 rounded-lg text-sm font-bold shadow-lg transition-all 
                ${isRunning ? 'bg-gray-600' : 'bg-green-600 hover:bg-green-500 hover:scale-105'}`}
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
          onNodeClick={onNodeClick} // Capture Clicks
          onPaneClick={onPaneClick} // Capture Background Clicks
          fitView
          className="bg-gray-900"
        >
          <Background color="#374151" gap={20} />
          <Controls className="bg-gray-800 border-gray-700 text-white fill-white" />
        </ReactFlow>
      </div>

      {/* The Property Panel Slide-out */}
      <PropertiesPanel 
        selectedNode={selectedNode} 
        onClose={() => setSelectedNode(null)} 
        onUpdate={handleUpdateNode}
      />

    </div>
  );
};

export default WorkflowEditorPage;
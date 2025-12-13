import React, { useState, useRef, useCallback } from 'react';
import ReactFlow, { 
  ReactFlowProvider, 
  addEdge, 
  useNodesState, 
  useEdgesState, 
  Controls, 
  Background 
} from 'reactflow';
import 'reactflow/dist/style.css';
import { Play, Brain } from 'lucide-react';
import AgentNode from '../components/AgentNode';

const nodeTypes = { agent: AgentNode };

const initialNodes = [
  { 
    id: '1', 
    type: 'agent', 
    position: { x: 100, y: 100 }, 
    data: { label: 'Researcher', type: 'researcher', task: 'Research the history of the Internet.', onTaskChange: () => {} } 
  },
  { 
    id: '2', 
    type: 'agent', 
    position: { x: 500, y: 100 }, 
    data: { label: 'Media Director', type: 'media', task: 'Create a movie script based on the research.', onTaskChange: () => {} } 
  }
];

const initialEdges = [{ id: 'e1-2', source: '1', target: '2', animated: true, style: { stroke: '#3b82f6' } }];

let id = 3;
const getId = () => `${id++}`;

const WorkflowEditor = () => {
  const reactFlowWrapper = useRef(null);
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const [isRunning, setIsRunning] = useState(false);

  // --- Handlers ---

  const onConnect = useCallback((params) => setEdges((eds) => addEdge({ ...params, animated: true, style: { stroke: '#3b82f6' } }, eds)), [setEdges]);

  const onDragOver = useCallback((event) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

  const onDrop = useCallback(
    (event) => {
      event.preventDefault();
      const type = event.dataTransfer.getData('application/reactflow');
      if (!type) return;

      const position = reactFlowWrapper.current.getBoundingClientRect();
      const newNode = {
        id: getId(),
        type: 'agent',
        position: {
          x: event.clientX - position.left - 100,
          y: event.clientY - position.top,
        },
        data: { 
          label: type === 'media' ? 'Media Director' : type === 'coder' ? 'Coder Alpha' : 'Researcher', 
          type: type,
          task: '',
          // Simplified binding for demo
          onTaskChange: (val) => { newNode.data.task = val; }
        },
      };

      setNodes((nds) => nds.concat(newNode));
    },
    [setNodes]
  );

  // --- EXECUTION ENGINE ---
  const handleExecute = async () => {
    setIsRunning(true);
    console.log("🚀 Compiling Workflow...");

    // 1. Sort nodes by X position (Linear execution assumption for V1)
    const sortedNodes = [...nodes].sort((a, b) => a.position.x - b.position.x);
    
    // 2. Map to Vryndara Protocol
    const payload = {
      steps: sortedNodes.map((node, index) => {
        let agentId = "researcher-1"; // Default
        if (node.data.type === "media") agentId = "media-director";
        if (node.data.type === "coder") agentId = "coder-alpha";
        
        return {
          agent_id: agentId,
          task: node.data.task || "Do your job.",
          order: index + 1
        };
      })
    };

    console.log("📤 Sending Payload:", payload);

    try {
      const res = await fetch("http://localhost:8081/api/v1/workflow", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      
      const data = await res.json();
      alert(`✅ Workflow Started! ID: ${data.id}`);
    } catch (e) {
      alert("❌ Execution Failed: " + e.message);
    }
    setIsRunning(false);
  };

  return (
    <div className="h-full flex flex-col bg-[#0a0a0a]">
      {/* TOOLBAR */}
      <div className="h-14 border-b border-gray-800 bg-[#111113] flex justify-between items-center px-4">
        <div className="flex items-center gap-2">
          <Brain className="text-purple-500" size={20} />
          <h1 className="font-bold text-white">Workflow Architect</h1>
        </div>
        <div className="flex gap-2">
          <button 
            onClick={handleExecute}
            disabled={isRunning}
            className="flex items-center gap-2 px-4 py-1.5 bg-green-600 hover:bg-green-500 text-white rounded font-bold text-sm transition-colors disabled:opacity-50"
          >
            {isRunning ? "Running..." : <><Play size={16} /> Run Pipeline</>}
          </button>
        </div>
      </div>

      <div className="flex-1 flex overflow-hidden">
        {/* SIDEBAR */}
        <div className="w-64 border-r border-gray-800 bg-[#0f0f10] p-4 space-y-4">
          <div className="text-xs font-bold text-gray-500 uppercase">Library</div>
          
          <div className="space-y-2">
            {['researcher', 'media', 'coder'].map((type) => (
              <div 
                key={type}
                className="bg-[#1a1a1c] border border-gray-800 p-3 rounded cursor-move hover:border-gray-600 transition-colors flex items-center gap-3"
                onDragStart={(event) => event.dataTransfer.setData('application/reactflow', type)}
                draggable
              >
                <div className={`w-2 h-2 rounded-full bg-${type === 'media' ? 'pink' : type === 'coder' ? 'yellow' : 'cyan'}-500`} />
                <span className="capitalize text-sm font-medium text-gray-300">{type} Agent</span>
              </div>
            ))}
          </div>
          
          <div className="text-xs text-gray-600 mt-10">
            Drag nodes onto the canvas.<br/>Connect them left-to-right.<br/>Click Run.
          </div>
        </div>

        {/* CANVAS */}
        <div className="flex-1 h-full" ref={reactFlowWrapper}>
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onDrop={onDrop}
            onDragOver={onDragOver}
            nodeTypes={nodeTypes}
            fitView
          >
            <Background color="#222" gap={16} />
            <Controls className="bg-gray-800 border-gray-700 text-white" />
          </ReactFlow>
        </div>
      </div>
    </div>
  );
};

export default function WorkflowEditorPage() {
  return (
    <ReactFlowProvider>
      <WorkflowEditor />
    </ReactFlowProvider>
  );
}
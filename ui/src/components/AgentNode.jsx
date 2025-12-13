import React, { memo } from 'react';
import { Handle, Position } from 'reactflow';
import { Bot, Video, Code, Search } from 'lucide-react';

const icons = {
  "researcher": Search,
  "media": Video,
  "coder": Code,
  "default": Bot
};

const colors = {
  "researcher": "cyan",
  "media": "pink",
  "coder": "yellow",
  "default": "gray"
};

export default memo(({ data }) => {
  const type = data.type || "default";
  const Icon = icons[type] || icons.default;
  const color = colors[type] || colors.default;

  return (
    <div className={`w-64 bg-[#111113] border-2 border-gray-800 rounded-xl overflow-hidden shadow-lg transition-all hover:border-${color}-500/50 hover:shadow-${color}-500/20`}>
      {/* Input Handle */}
      <Handle type="target" position={Position.Left} className="!bg-gray-500 !w-3 !h-3 !border-none" />
      
      {/* Header */}
      <div className={`bg-${color}-900/20 p-3 border-b border-gray-800 flex items-center gap-3`}>
        <div className={`p-1.5 rounded bg-${color}-500/20 text-${color}-400`}>
          <Icon size={16} />
        </div>
        <div>
          <div className="text-sm font-bold text-gray-200 uppercase tracking-wider">{data.label}</div>
          <div className="text-[10px] text-gray-500 font-mono">{data.model || "Llama-3-8b"}</div>
        </div>
      </div>

      {/* Body */}
      <div className="p-3">
        <div className="text-xs text-gray-400 mb-2 font-mono">TASK INSTRUCTION:</div>
        <textarea 
          className="w-full bg-[#0a0a0a] border border-gray-800 rounded p-2 text-xs text-gray-300 focus:border-blue-500 focus:outline-none resize-none"
          rows={3}
          placeholder="What should this agent do?"
          defaultValue={data.task}
          onChange={(evt) => data.onTaskChange(evt.target.value)}
        />
      </div>

      {/* Output Handle */}
      <Handle type="source" position={Position.Right} className={`!bg-${color}-500 !w-3 !h-3 !border-none`} />
    </div>
  );
});
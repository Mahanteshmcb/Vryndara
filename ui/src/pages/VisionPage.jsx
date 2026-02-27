import React from 'react';
import VryndaraScene from '../components/VryndaraScene';
import { useVryndara } from '../hooks/useVryndara';

export default function VisionPage() {
  // We only pull the status now to avoid re-rendering the whole page
  const { status } = useVryndara();

  return (
    <div className="flex flex-col w-full h-full bg-[#050505] overflow-hidden">
      
      {/* Top Header Section */}
      <div className="p-6 border-b border-gray-800 flex justify-between items-center z-10">
        <div>
          <h2 className="text-cyan-400 text-xl font-bold tracking-widest uppercase">
            Vision Neural Link
          </h2>
          <p className="text-gray-500 text-xs font-mono mt-1">
            Gateway Status: <span className={status === 'CONNECTED' ? 'text-green-500' : 'text-yellow-500'}>{status}</span>
          </p>
        </div>
        <div className="px-3 py-1 rounded-full bg-green-900/20 border border-green-500/50 text-green-500 text-[10px] animate-pulse">
          LIVE_FEED_ACTIVE
        </div>
      </div>

      {/* 3D Scene Container */}
      <div className="flex-1 relative w-full h-full">
        <VryndaraScene />
      </div>

    </div>
  );
}
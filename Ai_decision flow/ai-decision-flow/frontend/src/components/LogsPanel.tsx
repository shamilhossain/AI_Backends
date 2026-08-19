"use client";

import React, { useEffect, useRef } from 'react';
import { useFlowStore } from '@/store/useFlowStore';

export function LogsPanel() {
  const logs = useFlowStore((state) => state.logs);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs]);

  return (
    <div className="w-80 h-full bg-slate-900 text-green-400 p-4 font-mono text-sm overflow-hidden flex flex-col border-l border-slate-700">
      <h3 className="text-white font-semibold mb-4 border-b border-slate-700 pb-2">Execution Logs</h3>
      <div className="flex-1 overflow-y-auto space-y-2 pr-2 pb-10">
        {logs.length === 0 ? (
          <p className="text-slate-500 italic text-xs">No logs yet. Run the flow to see output.</p>
        ) : (
          logs.map((log, i) => (
            <div key={i} className="break-words leading-tight">{log}</div>
          ))
        )}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}

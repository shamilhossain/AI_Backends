import React from 'react';
import { Handle, Position } from '@xyflow/react';
import { Input } from '@/components/ui/input';
import { useFlowStore } from '@/store/useFlowStore';

export function DecisionNode({ id, data }: { id: string; data: any }) {
  const updateNodeData = useFlowStore((state) => state.updateNodeData);

  return (
    <div className="bg-white border-2 border-slate-200 rounded-md p-4 w-[250px] shadow-sm relative">
      {/* Target Handle (Incoming) */}
      <Handle 
        type="target" 
        position={Position.Top} 
        className="w-3 h-3 bg-blue-500" 
      />
      
      <div className="flex flex-col gap-2 mb-4">
        <label className="text-xs font-semibold text-slate-500 uppercase">Decision Node</label>
        <Input 
          placeholder="Enter prompt (e.g. Is it support?)"
          value={data.prompt || ''}
          onChange={(e) => updateNodeData(id, { prompt: e.target.value })}
          className="nodrag text-sm"
        />
      </div>

      {/* Source Handle (YES) */}
      <Handle 
        type="source" 
        position={Position.Bottom} 
        id="yes"
        className="w-3 h-3 bg-green-500"
        style={{ left: '25%' }}
      />
      <div className="absolute -bottom-6 left-[25%] -translate-x-1/2 text-[10px] font-bold text-green-600">
        YES
      </div>
      
      {/* Source Handle (NO) */}
      <Handle 
        type="source" 
        position={Position.Bottom} 
        id="no"
        className="w-3 h-3 bg-red-500"
        style={{ left: '75%' }}
      />
      <div className="absolute -bottom-6 left-[75%] -translate-x-1/2 text-[10px] font-bold text-red-600">
        NO
      </div>
    </div>
  );
}

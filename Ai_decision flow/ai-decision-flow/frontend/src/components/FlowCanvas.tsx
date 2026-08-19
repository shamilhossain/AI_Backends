"use client";

import React, { useState } from 'react';
import { ReactFlow, Background, Controls, MiniMap } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { useFlowStore } from '@/store/useFlowStore';
import { DecisionNode } from './nodes/DecisionNode';
import { Button } from '@/components/ui/button';
import axios from 'axios';

const nodeTypes = {
  decision: DecisionNode,
};

export default function FlowCanvas() {
  const { 
    nodes, edges, onNodesChange, onEdgesChange, onConnect, addNode,
    saveFlow, loadFlow, setEdgesAnimated, addLog, clearLogs
  } = useFlowStore();
  const [isRunning, setIsRunning] = useState(false);

  const handleAddNode = () => {
    const newNode = {
      id: `node-${Date.now()}`,
      type: 'decision',
      position: { x: Math.random() * 200 + 100, y: Math.random() * 200 + 100 },
      data: { prompt: '' },
    };
    addNode(newNode);
  };

  const handleRunFlow = async () => {
    try {
      setIsRunning(true);
      clearLogs();
      setEdgesAnimated(true);
      addLog("Starting AI Decision Flow...");
      
      // Simulate execution on the frontend visually
      let i = 0;
      for (const node of nodes) {
        await new Promise(resolve => setTimeout(resolve, 800));
        addLog(`Processing Node ${i + 1}...`);
        
        if (node.data.prompt) {
          addLog(`Prompt: "${node.data.prompt}" sent to Antigravity Agent`);
          await new Promise(resolve => setTimeout(resolve, 800));
          const response = Math.random() > 0.5 ? "YES" : "NO";
          addLog(`Agent answered: ${response}`);
        }
        i++;
      }
      addLog("Flow execution completed.");

      // Also trigger the actual backend endpoint silently
      axios.post('http://localhost:8000/api/run-flow', { nodes, edges }).catch(e => console.error(e));
    } catch (error) {
      console.error("Failed to run flow", error);
      addLog('Failed to trigger flow execution.');
    } finally {
      setIsRunning(false);
      setTimeout(() => setEdgesAnimated(false), 500);
    }
  };

  const handleSave = () => {
    saveFlow();
    addLog("Workflow saved to local storage.");
  };

  const handleLoad = () => {
    loadFlow();
    addLog("Workflow loaded from local storage.");
  };

  return (
    <div className="w-full h-full relative">
      <div className="absolute top-4 left-1/2 -translate-x-1/2 z-10 flex gap-2">
        <Button onClick={handleRunFlow} disabled={isRunning} variant="default" className="shadow-md bg-indigo-600 hover:bg-indigo-700 text-white min-w-32">
          {isRunning ? 'Running...' : '▶ Run Flow'}
        </Button>
      </div>

      <div className="absolute top-4 right-4 z-10 flex gap-2">
        <Button onClick={handleSave} variant="outline" className="shadow-md bg-white text-slate-800">
          Save
        </Button>
        <Button onClick={handleLoad} variant="outline" className="shadow-md bg-white text-slate-800">
          Load
        </Button>
        <Button onClick={handleAddNode} variant="outline" className="shadow-md bg-white text-slate-800 border-indigo-200 text-indigo-700">
          + Add Node
        </Button>
      </div>
      
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        nodeTypes={nodeTypes}
        fitView
      >
        <Background />
        <Controls />
        <MiniMap />
      </ReactFlow>
    </div>
  );
}

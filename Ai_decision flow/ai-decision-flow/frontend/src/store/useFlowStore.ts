import { create } from 'zustand';
import {
  Connection,
  Edge,
  EdgeChange,
  Node,
  NodeChange,
  addEdge,
  OnNodesChange,
  OnEdgesChange,
  OnConnect,
  applyNodeChanges,
  applyEdgeChanges,
} from '@xyflow/react';

export type FlowState = {
  nodes: Node[];
  edges: Edge[];
  logs: string[];
  onNodesChange: OnNodesChange;
  onEdgesChange: OnEdgesChange;
  onConnect: OnConnect;
  addNode: (node: Node) => void;
  updateNodeData: (nodeId: string, data: any) => void;
  setEdgesAnimated: (animated: boolean) => void;
  addLog: (log: string) => void;
  clearLogs: () => void;
  saveFlow: () => void;
  loadFlow: () => void;
};

export const useFlowStore = create<FlowState>((set, get) => ({
  nodes: [],
  edges: [],
  logs: [],
  onNodesChange: (changes: NodeChange[]) => {
    set({
      nodes: applyNodeChanges(changes, get().nodes),
    });
  },
  onEdgesChange: (changes: EdgeChange[]) => {
    set({
      edges: applyEdgeChanges(changes, get().edges),
    });
  },
  onConnect: (connection: Connection) => {
    set({
      edges: addEdge(connection, get().edges),
    });
  },
  addNode: (node: Node) => {
    set({
      nodes: [...get().nodes, node],
    });
  },
  updateNodeData: (nodeId: string, data: any) => {
    set({
      nodes: get().nodes.map((node) => {
        if (node.id === nodeId) {
          return { ...node, data: { ...node.data, ...data } };
        }
        return node;
      }),
    });
  },
  setEdgesAnimated: (animated: boolean) => {
    set({
      edges: get().edges.map((edge) => ({ ...edge, animated })),
    });
  },
  addLog: (log: string) => {
    set({
      logs: [...get().logs, `[${new Date().toLocaleTimeString()}] ${log}`],
    });
  },
  clearLogs: () => {
    set({ logs: [] });
  },
  saveFlow: () => {
    const { nodes, edges } = get();
    localStorage.setItem('flow-storage', JSON.stringify({ nodes, edges }));
  },
  loadFlow: () => {
    const data = localStorage.getItem('flow-storage');
    if (data) {
      const parsed = JSON.parse(data);
      set({ nodes: parsed.nodes || [], edges: parsed.edges || [] });
    }
  },
}));

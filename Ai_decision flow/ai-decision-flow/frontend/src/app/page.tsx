import FlowCanvas from '@/components/FlowCanvas';
import { LogsPanel } from '@/components/LogsPanel';

export default function Home() {
  return (
    <main className="w-full h-screen overflow-hidden bg-slate-50 flex">
      <div className="flex-1 h-full">
        <FlowCanvas />
      </div>
      <LogsPanel />
    </main>
  );
}

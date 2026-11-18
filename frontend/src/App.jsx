import { Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Navbar from './components/Navbar';
import { useWebSocket } from './hooks/useWebSocket';
import Dashboard from './pages/Dashboard';
import AttackSim from './pages/AttackSim';
import Logs from './pages/Logs';
import Settings from './pages/Settings';
import StreamArchitecture from './pages/StreamArchitecture';
import LiveThreatMonitor from './pages/LiveThreatMonitor';
import ModelHealth from './pages/ModelHealth';

export default function App() {
  useWebSocket();

  return (
    <div style={{ display: 'flex', minHeight: '100vh', background: '#0B0F19' }}>
      <Sidebar />
      <main style={{ flex: 1, marginLeft: 260, minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
        <Navbar />
        <div style={{ flex: 1, padding: '28px 32px' }}>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/attack-sim" element={<AttackSim />} />
            <Route path="/logs" element={<Logs />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="/stream" element={<StreamArchitecture />} />
            <Route path="/live-threat" element={<LiveThreatMonitor />} />
            <Route path="/model-health" element={<ModelHealth />} />
          </Routes>
        </div>
      </main>
    </div>
  );
}

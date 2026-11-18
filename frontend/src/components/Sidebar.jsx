import { NavLink } from 'react-router-dom';
import { useGraphStore } from '../store/graphStore';
import { LayoutDashboard, Terminal, Settings, Shield, Zap, Crosshair, Activity, Radar, Cpu } from 'lucide-react';

const mainLinks = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/attack-sim', icon: Crosshair, label: 'Attack Sim' },
  { to: '/logs', icon: Terminal, label: 'Logs' },
  { to: '/settings', icon: Settings, label: 'Settings' },
];

const phase3Links = [
  { to: '/stream', icon: Activity, label: 'Stream Monitor', dot: '#00F0FF' },
  { to: '/live-threat', icon: Radar, label: 'Live Threat', dot: '#FF1744' },
];

const modelLinks = [
  { to: '/model-health', icon: Cpu, label: 'Model Health', dot: '#7C3AED' },
];

export default function Sidebar() {
  const { wsConnected } = useGraphStore();

  const renderLink = (l, showDot = false) => {
    const Icon = l.icon;
    return (
      <NavLink key={l.to} to={l.to} end={l.to === '/'} className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
        {showDot && l.dot && (
          <div style={{ width: 6, height: 6, borderRadius: '50%', background: l.dot, boxShadow: `0 0 6px ${l.dot}`, flexShrink: 0 }} />
        )}
        <Icon size={18} strokeWidth={1.8} />
        <span>{l.label}</span>
      </NavLink>
    );
  };

  return (
    <aside className="sidebar">
      {/* Logo */}
      <div style={{ padding: '28px 24px 32px', display: 'flex', alignItems: 'center', gap: '14px' }}>
        <div style={{
          width: 42, height: 42, borderRadius: 12,
          background: 'linear-gradient(135deg, #06B6D4, #3B82F6)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          boxShadow: '0 4px 15px rgba(6, 182, 212, 0.3)',
        }}>
          <Shield size={22} color="#fff" strokeWidth={2.5} />
        </div>
        <div>
          <div style={{ fontSize: '1.15rem', fontWeight: 800, color: '#F1F5F9', letterSpacing: '0.05em' }}>GRASP</div>
          <div style={{ fontSize: '0.6rem', color: '#64748B', letterSpacing: '0.12em', marginTop: 1 }}>SECURITY PLATFORM</div>
        </div>
      </div>

      {/* Navigation */}
      <nav style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 2, padding: '0 0' }}>
        <div style={{ padding: '0 24px', marginBottom: 8 }}>
          <span style={{ fontSize: '0.65rem', fontWeight: 600, color: '#475569', textTransform: 'uppercase', letterSpacing: '0.1em' }}>Menu</span>
        </div>
        {mainLinks.map(l => renderLink(l, false))}

        {/* Divider — Phase 3 Sections */}
        <div style={{ margin: '12px 24px 8px', borderTop: '1px solid rgba(100,116,139,0.2)' }} />
        <div style={{ padding: '0 24px', marginBottom: 8 }}>
          <span style={{ fontSize: '0.65rem', fontWeight: 600, color: '#475569', textTransform: 'uppercase', letterSpacing: '0.1em' }}>Live Systems</span>
        </div>
        {phase3Links.map(l => renderLink(l, true))}

        {/* Divider — Model */}
        <div style={{ margin: '12px 24px 8px', borderTop: '1px solid rgba(100,116,139,0.2)' }} />
        <div style={{ padding: '0 24px', marginBottom: 8 }}>
          <span style={{ fontSize: '0.65rem', fontWeight: 600, color: '#475569', textTransform: 'uppercase', letterSpacing: '0.1em' }}>Intelligence</span>
        </div>
        {modelLinks.map(l => renderLink(l, true))}
      </nav>

      {/* Status footer */}
      <div style={{ padding: '20px 24px', borderTop: '1px solid var(--border)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
          <div style={{
            width: 8, height: 8, borderRadius: '50%',
            background: wsConnected ? '#10B981' : '#EF4444',
            boxShadow: wsConnected ? '0 0 8px rgba(16,185,129,0.5)' : '0 0 8px rgba(239,68,68,0.5)',
          }} />
          <span style={{ fontSize: '0.78rem', color: '#94A3B8' }}>{wsConnected ? 'System Online' : 'Disconnected'}</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <Zap size={13} color="#06B6D4" />
          <span style={{ fontSize: '0.68rem', color: '#64748B' }}>17 AI Agents Active</span>
        </div>
      </div>
    </aside>
  );
}

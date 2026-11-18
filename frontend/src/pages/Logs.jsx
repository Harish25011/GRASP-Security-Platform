import { useEffect, useRef } from 'react';
import { useGraphStore } from '../store/graphStore';
import { Terminal as TerminalIcon, Circle } from 'lucide-react';

const levelStyle = {
  INFO: { color: '#3B82F6', bg: 'rgba(59,130,246,0.08)' },
  WARNING: { color: '#F59E0B', bg: 'rgba(245,158,11,0.08)' },
  ALERT: { color: '#EF4444', bg: 'rgba(239,68,68,0.08)' },
};

function getLevel(event) {
  if (event.label && event.label !== 'benign') return 'ALERT';
  if (event.risk_score > 0.3) return 'WARNING';
  return 'INFO';
}

function formatLogLine(event, i) {
  const level = getLevel(event);
  const style = levelStyle[level];
  const time = event.timestamp ? new Date(event.timestamp).toLocaleTimeString() : '--:--:--';

  return (
    <div key={event.id || i} style={{
      padding: '6px 0',
      borderBottom: '1px solid rgba(148,163,184,0.04)',
      display: 'flex',
      alignItems: 'flex-start',
      gap: 12,
      animation: i === 0 ? 'fadeUp 0.3s ease-out' : undefined,
    }}>
      <span style={{ color: '#475569', minWidth: 78, flexShrink: 0 }}>{time}</span>
      <span style={{
        padding: '1px 8px', borderRadius: 4, fontSize: '0.68rem', fontWeight: 700,
        color: style.color, background: style.bg, minWidth: 62, textAlign: 'center', flexShrink: 0,
      }}>{level}</span>
      <span style={{ color: '#94A3B8', minWidth: 110, flexShrink: 0 }}>{event.source_ip || '—'}</span>
      <span style={{ color: '#475569' }}>→</span>
      <span style={{ color: '#94A3B8', minWidth: 110, flexShrink: 0 }}>{event.dest_ip || '—'}</span>
      <span style={{ color: '#475569', minWidth: 44, flexShrink: 0 }}>{event.protocol || '—'}</span>
      <span style={{ color: level === 'ALERT' ? '#EF4444' : '#64748B', flex: 1 }}>
        {event.event_type || 'network_flow'}
        {event.label && event.label !== 'benign' && (
          <span style={{
            marginLeft: 8, padding: '1px 7px', borderRadius: 4, fontSize: '0.62rem', fontWeight: 700,
            background: 'rgba(239,68,68,0.1)', color: '#EF4444', border: '1px solid rgba(239,68,68,0.2)',
          }}>{event.label}</span>
        )}
      </span>
    </div>
  );
}

export default function Logs() {
  const { eventLog } = useGraphStore();
  const bodyRef = useRef(null);

  useEffect(() => {
    if (bodyRef.current) {
      bodyRef.current.scrollTop = 0;
    }
  }, [eventLog.length]);

  const events = eventLog.slice(0, 100);

  return (
    <div className="fade-up">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 28 }}>
        <div>
          <h1 style={{ fontSize: '1.7rem', fontWeight: 800, color: '#F1F5F9', letterSpacing: '-0.02em' }}>Logs</h1>
          <p style={{ fontSize: '0.85rem', color: '#64748B', marginTop: 4 }}>Live security event stream</p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <Circle size={8} fill="#10B981" color="#10B981" />
          <span className="font-mono" style={{ fontSize: '0.78rem', color: '#94A3B8' }}>{events.length} events captured</span>
        </div>
      </div>

      <div className="terminal">
        <div className="terminal-header">
          <div className="terminal-dot" style={{ background: '#EF4444' }} />
          <div className="terminal-dot" style={{ background: '#F59E0B' }} />
          <div className="terminal-dot" style={{ background: '#10B981' }} />
          <span style={{ marginLeft: 12, fontSize: '0.78rem', color: '#64748B', fontWeight: 500 }}>
            <TerminalIcon size={13} style={{ display: 'inline', marginRight: 6, verticalAlign: 'middle' }} />
            grasp-security-feed
          </span>
          <div style={{ marginLeft: 'auto', display: 'flex', gap: 16, fontSize: '0.68rem', color: '#475569' }}>
            <span>INFO <span style={{ color: '#3B82F6', fontWeight: 700 }}>{events.filter(e => getLevel(e) === 'INFO').length}</span></span>
            <span>WARN <span style={{ color: '#F59E0B', fontWeight: 700 }}>{events.filter(e => getLevel(e) === 'WARNING').length}</span></span>
            <span>ALERT <span style={{ color: '#EF4444', fontWeight: 700 }}>{events.filter(e => getLevel(e) === 'ALERT').length}</span></span>
          </div>
        </div>
        <div className="terminal-body" ref={bodyRef}>
          {events.length === 0 ? (
            <div style={{ textAlign: 'center', color: '#475569', padding: '60px 0' }}>
              <TerminalIcon size={32} style={{ margin: '0 auto 12px', display: 'block', opacity: 0.3 }} />
              <p>Waiting for events...</p>
              <p style={{ fontSize: '0.7rem', marginTop: 4 }}>Events will appear here in real-time</p>
            </div>
          ) : events.map((e, i) => formatLogLine(e, i))}
        </div>
      </div>
    </div>
  );
}

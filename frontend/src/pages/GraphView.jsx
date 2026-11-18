import { useEffect, useRef, useState } from 'react';
import cytoscape from 'cytoscape';
import { useGraphStore } from '../store/graphStore';
import NodeCard from '../components/NodeCard';

function getNodeColor(risk) {
  if (risk > 0.7) return '#FF1744';
  if (risk > 0.6) return '#FF9100';
  if (risk > 0.3) return '#FFD600';
  return '#00E676';
}

export default function GraphView() {
  const containerRef = useRef(null);
  const cyRef = useRef(null);
  const { graph, agentScores } = useGraphStore();
  const [selectedNode, setSelectedNode] = useState(null);

  useEffect(() => {
    if (!containerRef.current) return;
    const cy = cytoscape({
      container: containerRef.current,
      elements: graph.elements || [],
      style: [
        { selector: 'node', style: {
          'background-color': (ele) => getNodeColor(ele.data('risk_score') || 0),
          'label': 'data(label)',
          'color': '#E2E8F0',
          'font-size': '8px',
          'font-family': '"JetBrains Mono", monospace',
          'text-valign': 'bottom',
          'text-margin-y': 5,
          'width': 24,
          'height': 24,
          'border-width': (ele) => (ele.data('risk_score') || 0) > 0.7 ? 3 : 1,
          'border-color': (ele) => getNodeColor(ele.data('risk_score') || 0),
          'overlay-opacity': 0,
        }},
        { selector: 'edge', style: {
          'width': 1,
          'line-color': 'rgba(0,240,255,0.15)',
          'target-arrow-shape': 'triangle',
          'target-arrow-color': 'rgba(0,240,255,0.15)',
          'curve-style': 'bezier',
          'arrow-scale': 0.6,
        }},
        { selector: 'node:selected', style: {
          'border-width': 3,
          'border-color': '#00F0FF',
          'overlay-opacity': 0.1,
          'overlay-color': '#00F0FF',
        }},
      ],
      layout: { name: 'cose', animate: false, nodeRepulsion: 8000, idealEdgeLength: 80 },
    });

    cy.on('tap', 'node', (e) => {
      const data = e.target.data();
      setSelectedNode({ ...data, agent_scores: agentScores });
    });

    cy.on('tap', (e) => { if (e.target === cy) setSelectedNode(null); });
    cyRef.current = cy;

    return () => cy.destroy();
  }, [graph]);

  return (
    <div>
      <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',marginBottom:'1rem'}}>
        <h1 style={{fontSize:'1.4rem',fontWeight:800,color:'#E2E8F0'}}>
          <span style={{color:'#00F0FF'}}>Graph View</span> — Supply Chain Network
        </h1>
        <div style={{display:'flex',gap:'0.75rem',fontSize:'0.7rem'}}>
          {[{c:'#00E676',l:'Safe'},{c:'#FFD600',l:'Watch'},{c:'#FF9100',l:'Suspicious'},{c:'#FF1744',l:'Anomaly'}].map(i=>(
            <div key={i.l} style={{display:'flex',alignItems:'center',gap:'0.3rem'}}>
              <div style={{width:10,height:10,borderRadius:'50%',background:i.c,boxShadow:`0 0 6px ${i.c}44`}}/>
              <span style={{color:'#94A3B8'}}>{i.l}</span>
            </div>
          ))}
        </div>
      </div>
      <div className="glass-card" style={{padding:0,overflow:'hidden'}}>
        <div ref={containerRef} style={{width:'100%',height:'calc(100vh - 180px)',background:'#0A0E17'}} />
      </div>
      {selectedNode && <NodeCard node={selectedNode} onClose={() => setSelectedNode(null)} />}
    </div>
  );
}

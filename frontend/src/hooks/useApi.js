import axios from 'axios';

const API_BASE = '/api';
const api = axios.create({ baseURL: API_BASE, timeout: 10000 });

export function useApi() {
  return {
    loadDataset: () => api.post('/load'),
    getGraph: () => api.get('/graph'),
    analyze: () => api.get('/analyze'),
    simulate: (data) => api.post('/simulate', data),
    attack: (data) => api.post('/attack', data),
    getSafeBox: () => api.get('/safe_box'),
    releaseNode: (nodeId) => api.post(`/safe_box/release/${nodeId}`),
    getAgentStatus: () => api.get('/agents/status'),
    explainNode: (nodeId) => api.get(`/explain/${nodeId}`),
    runPoisoning: () => api.post('/adversarial/poison'),
    runEvasion: () => api.post('/adversarial/evade'),
    getRobustness: () => api.get('/adversarial/report'),
    trainClassifier: () => api.post('/classifier/train'),
    getMetrics: () => api.get('/metrics'),
  };
}

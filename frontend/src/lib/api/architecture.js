/**
 * Architecture API methods
 */
import { apiRequest } from './auth';

export const getCurrentArchitecture = () => apiRequest('/api/v1/architecture/current');
export const getArchitectureIssues = () => apiRequest('/api/v1/architecture/issues');

// Ingestion endpoints (used by architecture discovery page)
export const ingestSpan = (span) =>
    apiRequest('/api/v1/ingest', { method: 'POST', body: JSON.stringify(span) });
export const ingestBatch = (spans) =>
    apiRequest('/api/v1/ingest/batch', { method: 'POST', body: JSON.stringify(spans) });
export const getIngestStats = () => apiRequest('/api/v1/ingest/stats');
export const submitArchitectureDiscovery = (data) =>
    apiRequest('/api/v1/ingest/architecture-discovery', {
        method: 'POST',
        body: JSON.stringify(data),
    });
export const getArchitectureDiscoveries = () =>
    apiRequest('/api/v1/ingest/architecture-discoveries');

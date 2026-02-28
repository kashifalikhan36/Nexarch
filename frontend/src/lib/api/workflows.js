/**
 * Workflow & AI Design API methods
 */
import { apiRequest } from './auth';

// Workflows
export const getGeneratedWorkflows = () => apiRequest('/api/v1/workflows/generated');
export const getWorkflowComparison = () => apiRequest('/api/v1/workflows/comparison');
export const getWorkflowGraph = () => apiRequest('/api/v1/workflows/architecture/graph');
export const getWorkflowSuggestions = (goal) =>
    apiRequest(`/api/v1/dashboard/workflows?goal=${encodeURIComponent(goal)}`);

// AI Architecture Design
export const designNewArchitecture = (requirements) =>
    apiRequest('/api/v1/ai-design/design-new', {
        method: 'POST',
        body: JSON.stringify(requirements),
    });
export const decomposeMonolith = (data) =>
    apiRequest('/api/v1/ai-design/decompose-monolith', {
        method: 'POST',
        body: JSON.stringify(data),
    });
export const designEventDriven = (data) =>
    apiRequest('/api/v1/ai-design/event-driven-design', {
        method: 'POST',
        body: JSON.stringify(data),
    });
export const optimizeArchitecture = (data) =>
    apiRequest('/api/v1/ai-design/optimize-architecture', {
        method: 'POST',
        body: JSON.stringify(data),
    });
export const getDesignTemplates = () => apiRequest('/api/v1/ai-design/design-templates');

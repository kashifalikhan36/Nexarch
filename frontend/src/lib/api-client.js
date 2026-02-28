/**
 * Nexarch API Client — backward-compatible facade
 *
 * All domain logic is now in focused modules under src/lib/api/.
 * This file imports from those modules and re-exports as the `apiClient`
 * singleton so all existing pages continue to work unchanged.
 *
 * New code should import directly from the domain modules, e.g.:
 *   import { getDashboardOverview } from '@/lib/api/dashboard';
 */

import { tokenStorage, apiRequest } from './api/auth';
import * as authApi from './api/auth';
import * as dashboardApi from './api/dashboard';
import * as architectureApi from './api/architecture';
import * as workflowsApi from './api/workflows';
import * as adminApi from './api/admin';

class NexarchClient {
    // ── Token / session helpers ─────────────────────────────────────────
    getToken()            { return tokenStorage.get(); }
    setToken(token)       { tokenStorage.set(token); }
    removeToken()         { tokenStorage.remove(); }
    getUser()             { return tokenStorage.getUser(); }
    setUser(user)         { tokenStorage.setUser(user); }

    /** Low-level fetch wrapper (kept for any internal callers). */
    async request(endpoint, options = {}) { return apiRequest(endpoint, options); }

    // ── Auth ────────────────────────────────────────────────────────────
    signup(email, password, fullName = null) { return authApi.signup(email, password, fullName); }
    login(email, password)                  { return authApi.login(email, password); }
    getGoogleAuthUrl()                       { return authApi.getGoogleAuthUrl(); }
    googleSignIn(code, state = null)         { return authApi.googleSignIn(code, state); }
    getCurrentUser()                         { return authApi.getCurrentUser(); }
    getGoogleStatus()                        { return authApi.getGoogleStatus(); }
    logout()                                 { return authApi.logout(); }

    // ── Health & System ─────────────────────────────────────────────────
    getHealth()           { return adminApi.getHealth(); }
    getHealthDetailed()   { return adminApi.getHealthDetailed(); }
    getSystemInfo()       { return adminApi.getSystemInfo(); }
    getSystemStats()      { return adminApi.getSystemStats(); }

    // ── Dashboard ───────────────────────────────────────────────────────
    getDashboardOverview()              { return dashboardApi.getDashboardOverview(); }
    getArchitectureMap()                { return dashboardApi.getArchitectureMap(); }
    getServices()                       { return dashboardApi.getServices(); }
    getServiceMetrics(name)             { return dashboardApi.getServiceMetrics(name); }
    getTrends(hours = 24)               { return dashboardApi.getTrends(hours); }
    getInsights()                       { return dashboardApi.getInsights(); }
    getDashboardHealth()                { return dashboardApi.getDashboardHealth(); }
    getBottlenecks()                    { return dashboardApi.getBottlenecks(); }
    getWorkflows(goal)                  { return dashboardApi.getWorkflows(goal); }
    getRecommendations()                { return dashboardApi.getRecommendations(); }
    getStreamStatus()                   { return dashboardApi.getStreamStatus(); }

    // ── Architecture ────────────────────────────────────────────────────
    getCurrentArchitecture()            { return architectureApi.getCurrentArchitecture(); }
    getArchitectureIssues()             { return architectureApi.getArchitectureIssues(); }
    ingestSpan(span)                    { return architectureApi.ingestSpan(span); }
    ingestBatch(spans)                  { return architectureApi.ingestBatch(spans); }
    getIngestStats()                    { return architectureApi.getIngestStats(); }
    submitArchitectureDiscovery(data)   { return architectureApi.submitArchitectureDiscovery(data); }
    getArchitectureDiscoveries()        { return architectureApi.getArchitectureDiscoveries(); }

    // ── Workflows & AI Design ───────────────────────────────────────────
    getGeneratedWorkflows()             { return workflowsApi.getGeneratedWorkflows(); }
    getWorkflowComparison()             { return workflowsApi.getWorkflowComparison(); }
    getWorkflowGraph()                  { return workflowsApi.getWorkflowGraph(); }
    getArchitectureGraph()              { return workflowsApi.getWorkflowGraph(); }
    getWorkflowSuggestions(goal)        { return workflowsApi.getWorkflowSuggestions(goal); }
    designNewArchitecture(req)          { return workflowsApi.designNewArchitecture(req); }
    decomposeMonolith(data)             { return workflowsApi.decomposeMonolith(data); }
    designEventDriven(data)             { return workflowsApi.designEventDriven(data); }
    optimizeArchitecture(data)          { return workflowsApi.optimizeArchitecture(data); }
    getDesignTemplates()                { return workflowsApi.getDesignTemplates(); }

    // ── Admin, Cache, API Keys ───────────────────────────────────────────
    createTenant(data)                  { return adminApi.createTenant(data); }
    getTenants()                        { return adminApi.getTenants(); }
    getTenant(id)                       { return adminApi.getTenant(id); }
    updateTenant(id, data)              { return adminApi.updateTenant(id, data); }
    deleteTenant(id)                    { return adminApi.deleteTenant(id); }
    getCacheStats()                     { return adminApi.getCacheStats(); }
    invalidateCache()                   { return adminApi.invalidateCache(); }
    invalidateCacheOperation(op)        { return adminApi.invalidateCacheOperation(op); }
    warmCache(op)                       { return adminApi.warmCache(op); }
    generateApiKey(name)                { return adminApi.generateApiKey(name); }
    listApiKeys()                       { return adminApi.listApiKeys(); }
    revokeApiKey(key)                   { return adminApi.revokeApiKey(key); }
    generateSampleData(count = 100)     { return adminApi.generateSampleData(count); }
    clearData()                         { return adminApi.clearData(); }
    clearDemoData()                     { return adminApi.clearData(); }
}

// Export singleton instance (backward compatible)
export const apiClient = new NexarchClient();
export default apiClient;

// Re-export domain modules for new code that imports directly
export { tokenStorage, apiRequest } from './api/auth';
export * as authApi from './api/auth';
export * as dashboardApi from './api/dashboard';
export * as architectureApi from './api/architecture';
export * as workflowsApi from './api/workflows';
export * as adminApi from './api/admin';

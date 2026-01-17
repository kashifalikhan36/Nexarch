// Nexarch API Client
// Handles all API communication with authentication support

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://api.modelx.world';

class NexarchClient {
    constructor() {
        this.baseUrl = API_URL;
    }

    // Get stored access token
    getToken() {
        if (typeof window !== 'undefined') {
            return localStorage.getItem('access_token');
        }
        return null;
    }

    // Store access token
    setToken(token) {
        if (typeof window !== 'undefined') {
            localStorage.setItem('access_token', token);
        }
    }

    // Remove access token
    removeToken() {
        if (typeof window !== 'undefined') {
            localStorage.removeItem('access_token');
            localStorage.removeItem('user');
        }
    }

    // Store user data
    setUser(user) {
        if (typeof window !== 'undefined') {
            localStorage.setItem('user', JSON.stringify(user));
        }
    }

    // Get stored user
    getUser() {
        if (typeof window !== 'undefined') {
            const user = localStorage.getItem('user');
            return user ? JSON.parse(user) : null;
        }
        return null;
    }

    // Generic request method
    async request(endpoint, options = {}) {
        const token = this.getToken();

        const response = await fetch(`${this.baseUrl}${endpoint}`, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
                ...options.headers,
            },
        });

        if (response.status === 401) {
            this.removeToken();
            if (typeof window !== 'undefined') {
                window.location.href = '/login';
            }
            throw new Error('Unauthorized');
        }

        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            throw new Error(error.detail || response.statusText);
        }

        return response.json();
    }

    // ============================================
    // AUTH ENDPOINTS
    // ============================================

    // Get Google OAuth authorization URL
    async getGoogleAuthUrl() {
        return this.request('/auth/google');
    }

    // Exchange Google auth code for token
    async googleSignIn(code, state = null) {
        const result = await this.request('/auth/google/signin', {
            method: 'POST',
            body: JSON.stringify({ code, state }),
        });

        if (result.access_token) {
            this.setToken(result.access_token);
            if (result.user) {
                this.setUser(result.user);
            }
        }

        return result;
    }

    // Get current authenticated user
    async getCurrentUser() {
        return this.request('/auth/me');
    }

    // Check Google OAuth configuration status
    async getGoogleStatus() {
        return this.request('/auth/google/status');
    }

    // Logout
    async logout() {
        try {
            await this.request('/auth/logout', { method: 'POST' });
        } finally {
            this.removeToken();
        }
    }

    // ============================================
    // HEALTH & SYSTEM ENDPOINTS
    // ============================================

    async getHealth() {
        return this.request('/api/v1/health');
    }

    async getHealthDetailed() {
        return this.request('/api/v1/health/detailed');
    }

    async getSystemInfo() {
        return this.request('/api/v1/system/info');
    }

    async getSystemStats() {
        return this.request('/api/v1/system/stats');
    }

    // ============================================
    // DASHBOARD ENDPOINTS
    // ============================================

    async getDashboardOverview() {
        return this.request('/api/v1/dashboard/overview');
    }

    async getArchitectureMap() {
        return this.request('/api/v1/dashboard/architecture-map');
    }

    async getServices() {
        return this.request('/api/v1/dashboard/services');
    }

    async getServiceMetrics(serviceName) {
        return this.request(`/api/v1/dashboard/services/${serviceName}/metrics`);
    }

    async getTrends(hours = 24) {
        return this.request(`/api/v1/dashboard/trends?hours=${hours}`);
    }

    async getInsights() {
        return this.request('/api/v1/dashboard/insights');
    }

    async getDashboardHealth() {
        return this.request('/api/v1/dashboard/health');
    }

    async getBottlenecks() {
        return this.request('/api/v1/dashboard/bottlenecks');
    }

    async getWorkflows(goal = 'optimize_performance') {
        return this.request(`/api/v1/dashboard/workflows?goal=${goal}`);
    }

    async getRecommendations() {
        return this.request('/api/v1/dashboard/recommendations');
    }

    // ============================================
    // AI DESIGN ENDPOINTS
    // ============================================

    async designNewArchitecture(requirements) {
        return this.request('/api/v1/ai-design/design-new', {
            method: 'POST',
            body: JSON.stringify(requirements),
        });
    }

    async decomposeMonolith(data) {
        return this.request('/api/v1/ai-design/decompose-monolith', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    async designEventDriven(data) {
        return this.request('/api/v1/ai-design/event-driven-design', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    async optimizeArchitecture(data) {
        return this.request('/api/v1/ai-design/optimize-architecture', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    async getDesignTemplates() {
        return this.request('/api/v1/ai-design/design-templates');
    }

    // ============================================
    // WORKFLOW ENDPOINTS
    // ============================================

    async getGeneratedWorkflows() {
        return this.request('/api/v1/workflows/generated');
    }

    async getWorkflowComparison() {
        return this.request('/api/v1/workflows/comparison');
    }

    async getWorkflowGraph() {
        return this.request('/api/v1/workflows/architecture/graph');
    }

    // ============================================
    // ARCHITECTURE ENDPOINTS
    // ============================================

    async getCurrentArchitecture() {
        return this.request('/api/v1/architecture/current');
    }

    async getArchitectureIssues() {
        return this.request('/api/v1/architecture/issues');
    }

    // ============================================
    // INGESTION ENDPOINTS
    // ============================================

    async ingestSpan(span) {
        return this.request('/api/v1/ingest', {
            method: 'POST',
            body: JSON.stringify(span),
        });
    }

    async ingestBatch(spans) {
        return this.request('/api/v1/ingest/batch', {
            method: 'POST',
            body: JSON.stringify(spans),
        });
    }

    async getIngestStats() {
        return this.request('/api/v1/ingest/stats');
    }

    async submitArchitectureDiscovery(data) {
        return this.request('/api/v1/ingest/architecture-discovery', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    async getArchitectureDiscoveries() {
        return this.request('/api/v1/ingest/architecture-discoveries');
    }

    // ============================================
    // ADMIN ENDPOINTS
    // ============================================

    async createTenant(data) {
        return this.request('/api/v1/admin/tenants', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    async getTenants() {
        return this.request('/api/v1/admin/tenants');
    }

    async getTenant(tenantId) {
        return this.request(`/api/v1/admin/tenants/${tenantId}`);
    }

    async updateTenant(tenantId, data) {
        return this.request(`/api/v1/admin/tenants/${tenantId}`, {
            method: 'PUT',
            body: JSON.stringify(data),
        });
    }

    async deleteTenant(tenantId) {
        return this.request(`/api/v1/admin/tenants/${tenantId}`, {
            method: 'DELETE',
        });
    }

    // ============================================
    // CACHE ENDPOINTS
    // ============================================

    async getCacheStats() {
        return this.request('/api/v1/cache/stats');
    }

    async invalidateCache() {
        return this.request('/api/v1/cache/invalidate', { method: 'DELETE' });
    }

    async invalidateCacheOperation(operation) {
        return this.request(`/api/v1/cache/invalidate/${operation}`, { method: 'DELETE' });
    }

    async warmCache(operation) {
        return this.request(`/api/v1/cache/warm/${operation}`, { method: 'POST' });
    }

    // ============================================
    // DEMO ENDPOINTS
    // ============================================

    async generateSampleData(count = 100) {
        return this.request(`/api/v1/demo/generate-sample-data?count=${count}`, {
            method: 'POST',
        });
    }

    async clearData() {
        return this.request('/api/v1/demo/clear-data', { method: 'DELETE' });
    }

    // Alias for clearData
    async clearDemoData() {
        return this.clearData();
    }

    // Alias for getWorkflowGraph
    async getArchitectureGraph() {
        return this.getWorkflowGraph();
    }

    // Get workflow suggestions based on goal
    async getWorkflowSuggestions(goal) {
        return this.request(`/api/v1/dashboard/workflows?goal=${encodeURIComponent(goal)}`);
    }
}

// Export singleton instance
export const apiClient = new NexarchClient();
export default apiClient;

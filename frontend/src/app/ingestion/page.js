'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useAuth } from '@/lib/auth-context';
import { apiClient } from '@/lib/api-client';
import {
    Database,
    Activity,
    Server,
    ArrowUpCircle,
    RefreshCw,
    Plus,
    Layers,
    Globe,
    Code,
    ChevronDown,
    ChevronUp
} from 'lucide-react';

export default function IngestionPage() {
    const { isAuthenticated, loading: authLoading } = useAuth();
    const [stats, setStats] = useState(null);
    const [discoveries, setDiscoveries] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [showForm, setShowForm] = useState(false);
    const [submitting, setSubmitting] = useState(false);
    const [expandedDiscovery, setExpandedDiscovery] = useState(null);

    // Form state
    const [formData, setFormData] = useState({
        service_name: '',
        service_type: 'fastapi',
        version: '1.0.0',
        endpoints: '',
        databases: '',
        external_services: '',
        middleware: '',
        architecture_pattern: 'microservices'
    });

    useEffect(() => {
        if (!authLoading && isAuthenticated) {
            fetchData();
        }
    }, [authLoading, isAuthenticated]);

    const fetchData = async () => {
        setLoading(true);
        setError(null);
        try {
            const [statsData, discoveriesData] = await Promise.all([
                apiClient.getIngestStats(),
                apiClient.getArchitectureDiscoveries()
            ]);
            setStats(statsData);
            setDiscoveries(discoveriesData);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleSubmitDiscovery = async (e) => {
        e.preventDefault();
        setSubmitting(true);
        try {
            const discovery = {
                service_name: formData.service_name,
                service_type: formData.service_type,
                version: formData.version,
                endpoints: formData.endpoints.split('\n').filter(e => e.trim()).map(e => {
                    const parts = e.trim().split(' ');
                    return { method: parts[0] || 'GET', path: parts[1] || e, handler: parts[2] || '' };
                }),
                databases: formData.databases.split('\n').filter(d => d.trim()).map(d => {
                    const parts = d.trim().split(':');
                    return { type: parts[0] || 'postgresql', host: parts[1] || 'localhost', database: parts[2] || '' };
                }),
                external_services: formData.external_services.split(',').map(s => s.trim()).filter(Boolean),
                middleware: formData.middleware.split(',').map(m => m.trim()).filter(Boolean),
                architecture_patterns: { pattern: formData.architecture_pattern },
                discovered_at: new Date().toISOString()
            };

            await apiClient.submitArchitectureDiscovery(discovery);
            setShowForm(false);
            setFormData({
                service_name: '',
                service_type: 'fastapi',
                version: '1.0.0',
                endpoints: '',
                databases: '',
                external_services: '',
                middleware: '',
                architecture_pattern: 'microservices'
            });
            fetchData();
        } catch (err) {
            setError(err.message);
        } finally {
            setSubmitting(false);
        }
    };

    if (authLoading) {
        return (
            <div className="page-loading">
                <div className="spinner"></div>
                <p>Loading...</p>
            </div>
        );
    }

    if (!isAuthenticated) {
        return (
            <div className="auth-required">
                <h2 className="display-title display-md">ACCESS REQUIRED</h2>
                <p>Please sign in to view ingestion data.</p>
                <Link href="/login" className="btn btn-primary">Sign In</Link>
            </div>
        );
    }

    return (
        <div className="dashboard-page">
            {/* Header */}
            <nav className="dashboard-nav">
                <Link href="/" className="navbar__logo">NEXRCH</Link>
                <div className="dashboard-nav__links">
                    <Link href="/dashboard">Dashboard</Link>
                    <Link href="/ingestion" className="active">Ingestion</Link>
                    <Link href="/architecture">Architecture</Link>
                    <Link href="/ai-design">AI Design</Link>
                </div>
            </nav>

            {/* Page Content */}
            <div className="dashboard-content">
                <div className="dashboard-header">
                    <div>
                        <span className="tape-label">Data Pipeline</span>
                        <h1 className="display-title display-md" style={{ marginTop: '0.5rem' }}>
                            DATA INGESTION
                        </h1>
                    </div>
                    <div className="dashboard-header__actions">
                        <button onClick={fetchData} className="btn btn-secondary" disabled={loading}>
                            <RefreshCw size={16} className={loading ? 'spinning' : ''} />
                            Refresh
                        </button>
                        <button onClick={() => setShowForm(!showForm)} className="btn btn-primary">
                            <Plus size={16} />
                            Add Discovery
                        </button>
                    </div>
                </div>

                {error && (
                    <div className="dashboard-error">
                        {error}
                    </div>
                )}

                {/* Stats Cards */}
                <div className="stats-grid">
                    <div className="stat-card">
                        <div className="stat-card__icon">
                            <Activity size={24} />
                        </div>
                        <div className="stat-card__content">
                            <span className="stat-card__label">Total Spans</span>
                            <span className="stat-card__value">{stats?.total_spans?.toLocaleString() || '0'}</span>
                        </div>
                    </div>

                    <div className="stat-card">
                        <div className="stat-card__icon">
                            <Server size={24} />
                        </div>
                        <div className="stat-card__content">
                            <span className="stat-card__label">Unique Services</span>
                            <span className="stat-card__value">{stats?.unique_services || '0'}</span>
                        </div>
                    </div>

                    <div className="stat-card">
                        <div className="stat-card__icon">
                            <Layers size={24} />
                        </div>
                        <div className="stat-card__content">
                            <span className="stat-card__label">Unique Traces</span>
                            <span className="stat-card__value">{stats?.unique_traces?.toLocaleString() || '0'}</span>
                        </div>
                    </div>

                    <div className="stat-card">
                        <div className="stat-card__icon">
                            <Database size={24} />
                        </div>
                        <div className="stat-card__content">
                            <span className="stat-card__label">Discoveries</span>
                            <span className="stat-card__value">{discoveries?.total || '0'}</span>
                        </div>
                    </div>
                </div>

                {/* Discovery Form */}
                {showForm && (
                    <div className="discovery-form-container">
                        <h2 className="section-title">Submit Architecture Discovery</h2>
                        <form onSubmit={handleSubmitDiscovery} className="discovery-form">
                            <div className="form-row">
                                <div className="form-group">
                                    <label>Service Name *</label>
                                    <input
                                        type="text"
                                        value={formData.service_name}
                                        onChange={(e) => setFormData({ ...formData, service_name: e.target.value })}
                                        placeholder="api-gateway"
                                        required
                                    />
                                </div>
                                <div className="form-group">
                                    <label>Service Type</label>
                                    <select
                                        value={formData.service_type}
                                        onChange={(e) => setFormData({ ...formData, service_type: e.target.value })}
                                    >
                                        <option value="fastapi">FastAPI</option>
                                        <option value="express">Express</option>
                                        <option value="nextjs">Next.js</option>
                                        <option value="django">Django</option>
                                        <option value="spring">Spring Boot</option>
                                        <option value="other">Other</option>
                                    </select>
                                </div>
                                <div className="form-group">
                                    <label>Version</label>
                                    <input
                                        type="text"
                                        value={formData.version}
                                        onChange={(e) => setFormData({ ...formData, version: e.target.value })}
                                        placeholder="1.0.0"
                                    />
                                </div>
                            </div>

                            <div className="form-group">
                                <label>Endpoints (one per line: METHOD /path handler)</label>
                                <textarea
                                    value={formData.endpoints}
                                    onChange={(e) => setFormData({ ...formData, endpoints: e.target.value })}
                                    placeholder="GET /api/users get_users&#10;POST /api/users create_user&#10;GET /api/health health_check"
                                    rows={4}
                                />
                            </div>

                            <div className="form-group">
                                <label>Databases (one per line: type:host:database)</label>
                                <textarea
                                    value={formData.databases}
                                    onChange={(e) => setFormData({ ...formData, databases: e.target.value })}
                                    placeholder="postgresql:localhost:myapp&#10;redis:localhost:cache"
                                    rows={3}
                                />
                            </div>

                            <div className="form-row">
                                <div className="form-group">
                                    <label>External Services (comma-separated)</label>
                                    <input
                                        type="text"
                                        value={formData.external_services}
                                        onChange={(e) => setFormData({ ...formData, external_services: e.target.value })}
                                        placeholder="stripe.com, sendgrid.com, aws.amazon.com"
                                    />
                                </div>
                                <div className="form-group">
                                    <label>Middleware (comma-separated)</label>
                                    <input
                                        type="text"
                                        value={formData.middleware}
                                        onChange={(e) => setFormData({ ...formData, middleware: e.target.value })}
                                        placeholder="cors, auth, logging"
                                    />
                                </div>
                            </div>

                            <div className="form-group">
                                <label>Architecture Pattern</label>
                                <select
                                    value={formData.architecture_pattern}
                                    onChange={(e) => setFormData({ ...formData, architecture_pattern: e.target.value })}
                                >
                                    <option value="microservices">Microservices</option>
                                    <option value="monolith">Monolith</option>
                                    <option value="event-driven">Event-Driven</option>
                                    <option value="serverless">Serverless</option>
                                    <option value="hybrid">Hybrid</option>
                                </select>
                            </div>

                            <div className="form-actions">
                                <button type="button" onClick={() => setShowForm(false)} className="btn btn-secondary">
                                    Cancel
                                </button>
                                <button type="submit" className="btn btn-primary" disabled={submitting}>
                                    <ArrowUpCircle size={16} />
                                    {submitting ? 'Submitting...' : 'Submit Discovery'}
                                </button>
                            </div>
                        </form>
                    </div>
                )}

                {/* Discoveries List */}
                <div className="discoveries-section">
                    <h2 className="section-title">Architecture Discoveries</h2>

                    {loading ? (
                        <div className="loading-state">
                            <div className="spinner"></div>
                            <p>Loading discoveries...</p>
                        </div>
                    ) : discoveries?.discoveries?.length > 0 ? (
                        <div className="discoveries-list">
                            {discoveries.discoveries.map((discovery) => (
                                <div key={discovery.id} className="discovery-card">
                                    <div
                                        className="discovery-card__header"
                                        onClick={() => setExpandedDiscovery(
                                            expandedDiscovery === discovery.id ? null : discovery.id
                                        )}
                                    >
                                        <div className="discovery-card__info">
                                            <Server size={20} />
                                            <div>
                                                <h3>{discovery.service_name}</h3>
                                                <span className="discovery-card__meta">
                                                    {discovery.service_type} • v{discovery.version}
                                                </span>
                                            </div>
                                        </div>
                                        <div className="discovery-card__stats">
                                            <span className="stat-badge">
                                                <Code size={14} />
                                                {discovery.endpoints?.length || 0} endpoints
                                            </span>
                                            <span className="stat-badge">
                                                <Database size={14} />
                                                {discovery.databases?.length || 0} databases
                                            </span>
                                            <span className="stat-badge">
                                                <Globe size={14} />
                                                {discovery.external_services?.length || 0} external
                                            </span>
                                            {expandedDiscovery === discovery.id ? (
                                                <ChevronUp size={20} />
                                            ) : (
                                                <ChevronDown size={20} />
                                            )}
                                        </div>
                                    </div>

                                    {expandedDiscovery === discovery.id && (
                                        <div className="discovery-card__details">
                                            {discovery.endpoints?.length > 0 && (
                                                <div className="detail-section">
                                                    <h4>Endpoints</h4>
                                                    <ul className="endpoint-list">
                                                        {discovery.endpoints.map((ep, i) => (
                                                            <li key={i}>
                                                                <span className={`method method--${ep.method?.toLowerCase()}`}>
                                                                    {ep.method}
                                                                </span>
                                                                <code>{ep.path}</code>
                                                            </li>
                                                        ))}
                                                    </ul>
                                                </div>
                                            )}

                                            {discovery.databases?.length > 0 && (
                                                <div className="detail-section">
                                                    <h4>Databases</h4>
                                                    <ul className="database-list">
                                                        {discovery.databases.map((db, i) => (
                                                            <li key={i}>
                                                                <span className="db-type">{db.type}</span>
                                                                {db.host}:{db.database}
                                                            </li>
                                                        ))}
                                                    </ul>
                                                </div>
                                            )}

                                            {discovery.external_services?.length > 0 && (
                                                <div className="detail-section">
                                                    <h4>External Services</h4>
                                                    <div className="tag-list">
                                                        {discovery.external_services.map((svc, i) => (
                                                            <span key={i} className="tag">{svc}</span>
                                                        ))}
                                                    </div>
                                                </div>
                                            )}

                                            {discovery.middleware?.length > 0 && (
                                                <div className="detail-section">
                                                    <h4>Middleware</h4>
                                                    <div className="tag-list">
                                                        {discovery.middleware.map((mw, i) => (
                                                            <span key={i} className="tag tag--secondary">{mw}</span>
                                                        ))}
                                                    </div>
                                                </div>
                                            )}

                                            <div className="discovery-card__footer">
                                                <span>Discovered: {new Date(discovery.discovered_at).toLocaleString()}</span>
                                                {discovery.updated_at && (
                                                    <span>Updated: {new Date(discovery.updated_at).toLocaleString()}</span>
                                                )}
                                            </div>
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div className="empty-state">
                            <Database size={48} />
                            <h3>No Discoveries Yet</h3>
                            <p>Submit your first architecture discovery to get started.</p>
                            <button onClick={() => setShowForm(true)} className="btn btn-primary">
                                <Plus size={16} />
                                Add Discovery
                            </button>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

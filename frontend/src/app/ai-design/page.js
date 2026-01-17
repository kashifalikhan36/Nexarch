'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useAuth } from '@/lib/auth-context';
import { apiClient } from '@/lib/api-client';
import {
    Cpu,
    Sparkles,
    Layers,
    Workflow,
    Zap,
    FileText,
    ChevronRight,
    Plus,
    RefreshCw,
    CheckCircle,
    AlertCircle,
    Server,
    Database,
    Cloud,
    Clock,
    DollarSign,
    Users,
    Shield,
    ArrowRight
} from 'lucide-react';

export default function AIDesignPage() {
    const { isAuthenticated, loading: authLoading } = useAuth();
    const [activeTab, setActiveTab] = useState('design-new');
    const [templates, setTemplates] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [results, setResults] = useState(null);

    // Design New Form
    const [designForm, setDesignForm] = useState({
        business_domain: '',
        expected_scale: '',
        key_features: '',
        max_latency_ms: 100,
        availability: '99.9%',
        budget: 'medium',
        timeline: '6 months',
        team_size: 10,
        existing_tech_stack: '',
        compliance_requirements: '',
        num_alternatives: 3
    });

    // Decompose Monolith Form
    const [decomposeForm, setDecomposeForm] = useState({
        monolith_description: '',
        business_capabilities: ''
    });

    // Event-Driven Form
    const [eventForm, setEventForm] = useState({
        use_cases: '',
        data_flows: ''
    });

    // Optimize Form
    const [optimizeForm, setOptimizeForm] = useState({
        pain_points: '',
        optimization_goals: ''
    });

    useEffect(() => {
        if (!authLoading && isAuthenticated) {
            fetchTemplates();
        }
    }, [authLoading, isAuthenticated]);

    const fetchTemplates = async () => {
        try {
            const data = await apiClient.getDesignTemplates();
            setTemplates(data);
        } catch (err) {
            console.error('Failed to fetch templates:', err);
        }
    };

    const handleDesignNew = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        setResults(null);
        try {
            const payload = {
                business_domain: designForm.business_domain,
                expected_scale: designForm.expected_scale,
                key_features: designForm.key_features.split(',').map(f => f.trim()).filter(Boolean),
                performance_requirements: {
                    max_latency_ms: parseInt(designForm.max_latency_ms),
                    availability: designForm.availability
                },
                constraints: {
                    budget: designForm.budget,
                    timeline: designForm.timeline,
                    team_size: parseInt(designForm.team_size)
                },
                existing_tech_stack: designForm.existing_tech_stack.split(',').map(t => t.trim()).filter(Boolean),
                compliance_requirements: designForm.compliance_requirements.split(',').map(c => c.trim()).filter(Boolean),
                num_alternatives: parseInt(designForm.num_alternatives)
            };
            const data = await apiClient.designNewArchitecture(payload);
            setResults({ type: 'design-new', data });
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleDecompose = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        setResults(null);
        try {
            const payload = {
                monolith_description: decomposeForm.monolith_description,
                business_capabilities: decomposeForm.business_capabilities.split(',').map(c => c.trim()).filter(Boolean)
            };
            const data = await apiClient.decomposeMonolith(payload);
            setResults({ type: 'decompose', data });
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleEventDriven = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        setResults(null);
        try {
            const payload = {
                use_cases: eventForm.use_cases.split('\n').map(u => u.trim()).filter(Boolean),
                data_flows: eventForm.data_flows.split('\n').map(f => {
                    const parts = f.split('->').map(p => p.trim());
                    return { from: parts[0], to: parts[1], description: parts[2] || '' };
                }).filter(f => f.from && f.to)
            };
            const data = await apiClient.designEventDriven(payload);
            setResults({ type: 'event-driven', data });
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleOptimize = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        setResults(null);
        try {
            const payload = {
                pain_points: optimizeForm.pain_points.split('\n').map(p => p.trim()).filter(Boolean),
                optimization_goals: optimizeForm.optimization_goals.split('\n').map(g => g.trim()).filter(Boolean)
            };
            const data = await apiClient.optimizeArchitecture(payload);
            setResults({ type: 'optimize', data });
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
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
                <p>Please sign in to use AI Design tools.</p>
                <Link href="/login" className="btn btn-primary">Sign In</Link>
            </div>
        );
    }

    const tabs = [
        { id: 'design-new', label: 'Design New', icon: Plus },
        { id: 'decompose', label: 'Decompose Monolith', icon: Layers },
        { id: 'event-driven', label: 'Event-Driven', icon: Workflow },
        { id: 'optimize', label: 'Optimize', icon: Zap },
        { id: 'templates', label: 'Templates', icon: FileText }
    ];

    return (
        <div className="dashboard-page">
            {/* Header */}
            <nav className="dashboard-nav">
                <Link href="/" className="navbar__logo">NEXARCH</Link>
                <div className="dashboard-nav__links">
                    <Link href="/dashboard">Dashboard</Link>
                    <Link href="/ingestion">Ingestion</Link>
                    <Link href="/architecture">Architecture</Link>
                    <Link href="/ai-design" className="active">AI Design</Link>
                </div>
            </nav>

            {/* Page Content */}
            <div className="dashboard-content">
                <div className="dashboard-header">
                    <div>
                        <span className="tape-label">
                            <Sparkles size={12} /> AI-Powered
                        </span>
                        <h1 className="display-title display-md" style={{ marginTop: '0.5rem' }}>
                            ARCHITECTURE DESIGNER
                        </h1>
                        <p className="dashboard-welcome">Design, decompose, and optimize system architectures with AI</p>
                    </div>
                </div>

                {error && (
                    <div className="dashboard-error">
                        {error}
                    </div>
                )}

                {/* Tabs */}
                <div className="ai-tabs">
                    {tabs.map(tab => {
                        const Icon = tab.icon;
                        return (
                            <button
                                key={tab.id}
                                className={`ai-tab ${activeTab === tab.id ? 'ai-tab--active' : ''}`}
                                onClick={() => { setActiveTab(tab.id); setResults(null); }}
                            >
                                <Icon size={16} />
                                {tab.label}
                            </button>
                        );
                    })}
                </div>

                <div className="ai-content">
                    {/* Design New Tab */}
                    {activeTab === 'design-new' && (
                        <div className="ai-panel">
                            <div className="ai-panel__header">
                                <Cpu size={24} />
                                <div>
                                    <h2>Design New Architecture</h2>
                                    <p>Generate complete architecture designs based on your business requirements</p>
                                </div>
                            </div>

                            <form onSubmit={handleDesignNew} className="ai-form">
                                <div className="form-section">
                                    <h3>Business Requirements</h3>
                                    <div className="form-row">
                                        <div className="form-group">
                                            <label>Business Domain *</label>
                                            <input
                                                type="text"
                                                value={designForm.business_domain}
                                                onChange={(e) => setDesignForm({ ...designForm, business_domain: e.target.value })}
                                                placeholder="e.g., food delivery, e-commerce, fintech"
                                                required
                                            />
                                        </div>
                                        <div className="form-group">
                                            <label>Expected Scale</label>
                                            <input
                                                type="text"
                                                value={designForm.expected_scale}
                                                onChange={(e) => setDesignForm({ ...designForm, expected_scale: e.target.value })}
                                                placeholder="e.g., 1M orders/day, 100K users"
                                            />
                                        </div>
                                    </div>

                                    <div className="form-group">
                                        <label>Key Features (comma-separated)</label>
                                        <input
                                            type="text"
                                            value={designForm.key_features}
                                            onChange={(e) => setDesignForm({ ...designForm, key_features: e.target.value })}
                                            placeholder="real-time tracking, payment processing, notifications"
                                        />
                                    </div>
                                </div>

                                <div className="form-section">
                                    <h3>Performance Requirements</h3>
                                    <div className="form-row">
                                        <div className="form-group">
                                            <label>Max Latency (ms)</label>
                                            <input
                                                type="number"
                                                value={designForm.max_latency_ms}
                                                onChange={(e) => setDesignForm({ ...designForm, max_latency_ms: e.target.value })}
                                            />
                                        </div>
                                        <div className="form-group">
                                            <label>Availability</label>
                                            <select
                                                value={designForm.availability}
                                                onChange={(e) => setDesignForm({ ...designForm, availability: e.target.value })}
                                            >
                                                <option value="99%">99% (3.65 days/year downtime)</option>
                                                <option value="99.9%">99.9% (8.76 hours/year)</option>
                                                <option value="99.99%">99.99% (52.6 min/year)</option>
                                                <option value="99.999%">99.999% (5.26 min/year)</option>
                                            </select>
                                        </div>
                                    </div>
                                </div>

                                <div className="form-section">
                                    <h3>Constraints</h3>
                                    <div className="form-row">
                                        <div className="form-group">
                                            <label>Budget</label>
                                            <select
                                                value={designForm.budget}
                                                onChange={(e) => setDesignForm({ ...designForm, budget: e.target.value })}
                                            >
                                                <option value="low">Low (&lt;$1K/month)</option>
                                                <option value="medium">Medium ($1K-$10K/month)</option>
                                                <option value="high">High ($10K+/month)</option>
                                            </select>
                                        </div>
                                        <div className="form-group">
                                            <label>Timeline</label>
                                            <input
                                                type="text"
                                                value={designForm.timeline}
                                                onChange={(e) => setDesignForm({ ...designForm, timeline: e.target.value })}
                                                placeholder="e.g., 6 months"
                                            />
                                        </div>
                                        <div className="form-group">
                                            <label>Team Size</label>
                                            <input
                                                type="number"
                                                value={designForm.team_size}
                                                onChange={(e) => setDesignForm({ ...designForm, team_size: e.target.value })}
                                            />
                                        </div>
                                    </div>
                                </div>

                                <div className="form-section">
                                    <h3>Technical Context</h3>
                                    <div className="form-row">
                                        <div className="form-group">
                                            <label>Existing Tech Stack (comma-separated)</label>
                                            <input
                                                type="text"
                                                value={designForm.existing_tech_stack}
                                                onChange={(e) => setDesignForm({ ...designForm, existing_tech_stack: e.target.value })}
                                                placeholder="python, react, postgresql"
                                            />
                                        </div>
                                        <div className="form-group">
                                            <label>Compliance (comma-separated)</label>
                                            <input
                                                type="text"
                                                value={designForm.compliance_requirements}
                                                onChange={(e) => setDesignForm({ ...designForm, compliance_requirements: e.target.value })}
                                                placeholder="PCI-DSS, GDPR, HIPAA"
                                            />
                                        </div>
                                    </div>
                                </div>

                                <div className="form-group">
                                    <label>Number of Alternatives to Generate</label>
                                    <select
                                        value={designForm.num_alternatives}
                                        onChange={(e) => setDesignForm({ ...designForm, num_alternatives: e.target.value })}
                                    >
                                        <option value="1">1</option>
                                        <option value="2">2</option>
                                        <option value="3">3</option>
                                        <option value="5">5</option>
                                    </select>
                                </div>

                                <button type="submit" className="btn btn-primary btn-large" disabled={loading}>
                                    <Sparkles size={18} />
                                    {loading ? 'Generating...' : 'Generate Architecture Designs'}
                                </button>
                            </form>
                        </div>
                    )}

                    {/* Decompose Monolith Tab */}
                    {activeTab === 'decompose' && (
                        <div className="ai-panel">
                            <div className="ai-panel__header">
                                <Layers size={24} />
                                <div>
                                    <h2>Decompose Monolith</h2>
                                    <p>Break down your monolithic application into microservices</p>
                                </div>
                            </div>

                            <form onSubmit={handleDecompose} className="ai-form">
                                <div className="form-group">
                                    <label>Monolith Description *</label>
                                    <textarea
                                        value={decomposeForm.monolith_description}
                                        onChange={(e) => setDecomposeForm({ ...decomposeForm, monolith_description: e.target.value })}
                                        placeholder="Describe your monolith: tech stack, size (LOC), main modules, current challenges..."
                                        rows={4}
                                        required
                                    />
                                </div>

                                <div className="form-group">
                                    <label>Business Capabilities (comma-separated)</label>
                                    <input
                                        type="text"
                                        value={decomposeForm.business_capabilities}
                                        onChange={(e) => setDecomposeForm({ ...decomposeForm, business_capabilities: e.target.value })}
                                        placeholder="user management, catalog, ordering, payment, shipping"
                                    />
                                </div>

                                <button type="submit" className="btn btn-primary btn-large" disabled={loading}>
                                    <Layers size={18} />
                                    {loading ? 'Analyzing...' : 'Decompose Monolith'}
                                </button>
                            </form>
                        </div>
                    )}

                    {/* Event-Driven Tab */}
                    {activeTab === 'event-driven' && (
                        <div className="ai-panel">
                            <div className="ai-panel__header">
                                <Workflow size={24} />
                                <div>
                                    <h2>Event-Driven Design</h2>
                                    <p>Design event-driven architecture with domain events, streams, and sagas</p>
                                </div>
                            </div>

                            <form onSubmit={handleEventDriven} className="ai-form">
                                <div className="form-group">
                                    <label>Use Cases (one per line)</label>
                                    <textarea
                                        value={eventForm.use_cases}
                                        onChange={(e) => setEventForm({ ...eventForm, use_cases: e.target.value })}
                                        placeholder="User places order&#10;Payment is processed&#10;Inventory is updated&#10;Notifications are sent"
                                        rows={4}
                                    />
                                </div>

                                <div className="form-group">
                                    <label>Data Flows (format: source -&gt; target -&gt; description)</label>
                                    <textarea
                                        value={eventForm.data_flows}
                                        onChange={(e) => setEventForm({ ...eventForm, data_flows: e.target.value })}
                                        placeholder="order-service -> payment-service -> order details&#10;payment-service -> notification-service -> payment confirmation"
                                        rows={4}
                                    />
                                </div>

                                <button type="submit" className="btn btn-primary btn-large" disabled={loading}>
                                    <Workflow size={18} />
                                    {loading ? 'Designing...' : 'Design Event-Driven Architecture'}
                                </button>
                            </form>
                        </div>
                    )}

                    {/* Optimize Tab */}
                    {activeTab === 'optimize' && (
                        <div className="ai-panel">
                            <div className="ai-panel__header">
                                <Zap size={24} />
                                <div>
                                    <h2>Optimize Architecture</h2>
                                    <p>Get AI-powered recommendations to optimize your existing architecture</p>
                                </div>
                            </div>

                            <form onSubmit={handleOptimize} className="ai-form">
                                <div className="form-group">
                                    <label>Current Pain Points (one per line)</label>
                                    <textarea
                                        value={optimizeForm.pain_points}
                                        onChange={(e) => setOptimizeForm({ ...optimizeForm, pain_points: e.target.value })}
                                        placeholder="Database bottleneck at 1000 QPS&#10;API response time > 500ms&#10;Frequent 503 errors during peak"
                                        rows={4}
                                    />
                                </div>

                                <div className="form-group">
                                    <label>Optimization Goals (one per line)</label>
                                    <textarea
                                        value={optimizeForm.optimization_goals}
                                        onChange={(e) => setOptimizeForm({ ...optimizeForm, optimization_goals: e.target.value })}
                                        placeholder="Reduce latency to <100ms&#10;Scale to 10000 QPS&#10;99.99% availability"
                                        rows={4}
                                    />
                                </div>

                                <button type="submit" className="btn btn-primary btn-large" disabled={loading}>
                                    <Zap size={18} />
                                    {loading ? 'Analyzing...' : 'Get Optimization Recommendations'}
                                </button>
                            </form>
                        </div>
                    )}

                    {/* Templates Tab */}
                    {activeTab === 'templates' && (
                        <div className="ai-panel">
                            <div className="ai-panel__header">
                                <FileText size={24} />
                                <div>
                                    <h2>Design Templates</h2>
                                    <p>Start from proven architecture templates for common use cases</p>
                                </div>
                            </div>

                            {templates?.templates?.length > 0 ? (
                                <div className="templates-grid">
                                    {templates.templates.map((template, idx) => (
                                        <div key={idx} className="template-card">
                                            <div className="template-card__header">
                                                <h3>{template.name}</h3>
                                                <span className="template-card__type">{template.architecture_type}</span>
                                            </div>
                                            <div className="template-card__body">
                                                <div className="template-info">
                                                    <Server size={14} />
                                                    <span>{template.domain}</span>
                                                </div>
                                                <div className="template-info">
                                                    <Users size={14} />
                                                    <span>{template.scale}</span>
                                                </div>
                                                <div className="template-info">
                                                    <DollarSign size={14} />
                                                    <span>{template.estimated_cost}</span>
                                                </div>
                                            </div>
                                            {template.features?.length > 0 && (
                                                <div className="template-card__features">
                                                    {template.features.slice(0, 4).map((feature, fIdx) => (
                                                        <span key={fIdx} className="tag tag--secondary">{feature}</span>
                                                    ))}
                                                </div>
                                            )}
                                            <button
                                                className="btn btn-secondary btn-small"
                                                onClick={() => {
                                                    setDesignForm({
                                                        ...designForm,
                                                        business_domain: template.domain,
                                                        key_features: template.features?.join(', ') || ''
                                                    });
                                                    setActiveTab('design-new');
                                                }}
                                            >
                                                Use Template <ArrowRight size={14} />
                                            </button>
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <div className="empty-state">
                                    <FileText size={48} />
                                    <h3>No Templates Available</h3>
                                    <p>Templates will appear here when available.</p>
                                </div>
                            )}
                        </div>
                    )}

                    {/* Results Section */}
                    {results && (
                        <div className="ai-results">
                            <h2 className="section-title">
                                <Sparkles size={18} />
                                AI Generated Results
                            </h2>

                            {/* Design New Results */}
                            {results.type === 'design-new' && Array.isArray(results.data) && (
                                <div className="designs-grid">
                                    {results.data.map((design, idx) => (
                                        <div key={idx} className="design-card">
                                            <div className="design-card__header">
                                                <h3>{design.name}</h3>
                                                <span className={`risk-badge risk-badge--${design.risk_level}`}>
                                                    {design.risk_level} risk
                                                </span>
                                            </div>
                                            <p className="design-card__description">{design.description}</p>

                                            {design.services?.length > 0 && (
                                                <div className="design-section">
                                                    <h4>Services ({design.services.length})</h4>
                                                    <div className="services-mini-list">
                                                        {design.services.slice(0, 4).map((svc, sIdx) => (
                                                            <div key={sIdx} className="service-mini">
                                                                <Server size={14} />
                                                                <span>{svc.name}</span>
                                                            </div>
                                                        ))}
                                                    </div>
                                                </div>
                                            )}

                                            {design.databases?.length > 0 && (
                                                <div className="design-section">
                                                    <h4>Databases</h4>
                                                    <div className="tag-list">
                                                        {design.databases.map((db, dIdx) => (
                                                            <span key={dIdx} className="tag">{db.type}</span>
                                                        ))}
                                                    </div>
                                                </div>
                                            )}

                                            <div className="design-card__meta">
                                                <span><DollarSign size={14} /> {design.estimated_cost}</span>
                                                <span><Cloud size={14} /> {design.deployment?.strategy}</span>
                                            </div>

                                            <div className="design-card__pros-cons">
                                                {design.pros?.length > 0 && (
                                                    <div className="pros">
                                                        <h5><CheckCircle size={14} /> Pros</h5>
                                                        <ul>
                                                            {design.pros.slice(0, 3).map((pro, pIdx) => (
                                                                <li key={pIdx}>{pro}</li>
                                                            ))}
                                                        </ul>
                                                    </div>
                                                )}
                                                {design.cons?.length > 0 && (
                                                    <div className="cons">
                                                        <h5><AlertCircle size={14} /> Cons</h5>
                                                        <ul>
                                                            {design.cons.slice(0, 3).map((con, cIdx) => (
                                                                <li key={cIdx}>{con}</li>
                                                            ))}
                                                        </ul>
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}

                            {/* Decompose Results */}
                            {results.type === 'decompose' && results.data && (
                                <div className="decompose-results">
                                    {results.data.microservices?.length > 0 && (
                                        <div className="result-section">
                                            <h3>Recommended Microservices</h3>
                                            <div className="microservices-list">
                                                {results.data.microservices.map((ms, idx) => (
                                                    <div key={idx} className="microservice-card">
                                                        <h4>{ms.name}</h4>
                                                        <p className="bounded-context">{ms.bounded_context}</p>
                                                        <div className="responsibilities">
                                                            <strong>Responsibilities:</strong>
                                                            <ul>
                                                                {ms.responsibilities?.map((r, rIdx) => (
                                                                    <li key={rIdx}>{r}</li>
                                                                ))}
                                                            </ul>
                                                        </div>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    )}

                                    {results.data.migration_order?.length > 0 && (
                                        <div className="result-section">
                                            <h3>Migration Order</h3>
                                            <div className="migration-timeline">
                                                {results.data.migration_order.map((step, idx) => (
                                                    <div key={idx} className="migration-step">
                                                        <span className="step-number">{step.priority}</span>
                                                        <div className="step-content">
                                                            <strong>{step.service}</strong>
                                                            <p>{step.reason}</p>
                                                            <span className="effort">{step.estimated_effort}</span>
                                                        </div>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    )}
                                </div>
                            )}

                            {/* Event-Driven Results */}
                            {results.type === 'event-driven' && results.data && (
                                <div className="event-driven-results">
                                    {results.data.domain_events?.length > 0 && (
                                        <div className="result-section">
                                            <h3>Domain Events</h3>
                                            <div className="events-list">
                                                {results.data.domain_events.map((event, idx) => (
                                                    <div key={idx} className="event-card">
                                                        <h4>{event.name}</h4>
                                                        <div className="event-flow">
                                                            <span>Producers: {event.producers?.join(', ')}</span>
                                                            <ArrowRight size={14} />
                                                            <span>Consumers: {event.consumers?.join(', ')}</span>
                                                        </div>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    )}

                                    {results.data.sagas?.length > 0 && (
                                        <div className="result-section">
                                            <h3>Sagas</h3>
                                            {results.data.sagas.map((saga, idx) => (
                                                <div key={idx} className="saga-card">
                                                    <h4>{saga.name}</h4>
                                                    <div className="saga-steps">
                                                        {saga.steps?.map((step, sIdx) => (
                                                            <span key={sIdx} className="saga-step">
                                                                {step.service}: {step.action}
                                                                {sIdx < saga.steps.length - 1 && <ChevronRight size={14} />}
                                                            </span>
                                                        ))}
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            )}

                            {/* Optimize Results */}
                            {results.type === 'optimize' && results.data && (
                                <div className="optimize-results">
                                    {results.data.optimizations?.length > 0 && (
                                        <div className="result-section">
                                            <h3>Recommended Optimizations</h3>
                                            <div className="optimizations-list">
                                                {results.data.optimizations.map((opt, idx) => (
                                                    <div key={idx} className={`optimization-card optimization-card--${opt.priority}`}>
                                                        <div className="opt-header">
                                                            <span className={`priority-badge priority-badge--${opt.priority}`}>
                                                                {opt.priority}
                                                            </span>
                                                            <span className="opt-effort">{opt.effort}</span>
                                                        </div>
                                                        <h4>{opt.action}</h4>
                                                        <p className="opt-impact">{opt.impact}</p>
                                                        {opt.implementation_steps?.length > 0 && (
                                                            <ol className="opt-steps">
                                                                {opt.implementation_steps.map((step, sIdx) => (
                                                                    <li key={sIdx}>{step}</li>
                                                                ))}
                                                            </ol>
                                                        )}
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    )}

                                    {results.data.expected_outcomes && (
                                        <div className="result-section">
                                            <h3>Expected Outcomes</h3>
                                            <div className="outcomes-grid">
                                                <div className="outcome">
                                                    <span className="outcome-label">Latency Reduction</span>
                                                    <span className="outcome-value">{results.data.expected_outcomes.latency_reduction}</span>
                                                </div>
                                                <div className="outcome">
                                                    <span className="outcome-label">Throughput Increase</span>
                                                    <span className="outcome-value">{results.data.expected_outcomes.throughput_increase}</span>
                                                </div>
                                                <div className="outcome">
                                                    <span className="outcome-label">Availability</span>
                                                    <span className="outcome-value">{results.data.expected_outcomes.availability_improvement}</span>
                                                </div>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

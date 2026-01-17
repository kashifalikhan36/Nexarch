'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useAuth } from '@/lib/auth-context';
import { apiClient } from '@/lib/api-client';
import {
    Workflow,
    GitBranch,
    RefreshCw,
    Play,
    Pause,
    CheckCircle,
    XCircle,
    Clock,
    ArrowRight,
    BarChart2,
    Activity,
    Zap,
    Server,
    Database,
    Scale,
    ChevronDown,
    ChevronUp,
    Network
} from 'lucide-react';

export default function WorkflowsPage() {
    const { isAuthenticated, loading: authLoading } = useAuth();
    const [activeTab, setActiveTab] = useState('generated');
    const [workflows, setWorkflows] = useState(null);
    const [comparison, setComparison] = useState(null);
    const [architectureGraph, setArchitectureGraph] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [expandedWorkflow, setExpandedWorkflow] = useState(null);
    const [workflowGoal, setWorkflowGoal] = useState('');

    useEffect(() => {
        if (!authLoading && isAuthenticated) {
            fetchData();
        }
    }, [authLoading, isAuthenticated]);

    const fetchData = async () => {
        setLoading(true);
        setError(null);
        try {
            const [workflowsData, comparisonData, graphData] = await Promise.all([
                apiClient.getGeneratedWorkflows(),
                apiClient.getWorkflowComparison(),
                apiClient.getArchitectureGraph()
            ]);
            setWorkflows(workflowsData);
            setComparison(comparisonData);
            setArchitectureGraph(graphData);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const fetchWorkflowsWithGoal = async () => {
        if (!workflowGoal.trim()) return;
        setLoading(true);
        try {
            const data = await apiClient.getWorkflowSuggestions(workflowGoal);
            setWorkflows(prev => ({
                ...prev,
                suggestions: data.suggestions || data.workflows
            }));
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const getStatusIcon = (status) => {
        switch (status) {
            case 'completed':
            case 'success':
                return <CheckCircle size={16} className="status-icon status-icon--success" />;
            case 'running':
            case 'in_progress':
                return <Play size={16} className="status-icon status-icon--running" />;
            case 'failed':
            case 'error':
                return <XCircle size={16} className="status-icon status-icon--error" />;
            case 'paused':
                return <Pause size={16} className="status-icon status-icon--paused" />;
            default:
                return <Clock size={16} className="status-icon status-icon--pending" />;
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
                <p>Please sign in to view workflows.</p>
                <Link href="/login" className="btn btn-primary">Sign In</Link>
            </div>
        );
    }

    const tabs = [
        { id: 'generated', label: 'Generated Workflows', icon: Workflow },
        { id: 'comparison', label: 'Comparison', icon: Scale },
        { id: 'graph', label: 'Architecture Graph', icon: Network }
    ];

    return (
        <div className="dashboard-page">
            {/* Header */}
            <nav className="dashboard-nav">
                <Link href="/" className="navbar__logo">NEXRCH</Link>
                <div className="dashboard-nav__links">
                    <Link href="/dashboard">Dashboard</Link>
                    <Link href="/ingestion">Ingestion</Link>
                    <Link href="/architecture">Architecture</Link>
                    <Link href="/ai-design">AI Design</Link>
                    <Link href="/workflows" className="active">Workflows</Link>
                </div>
            </nav>

            {/* Page Content */}
            <div className="dashboard-content">
                <div className="dashboard-header">
                    <div>
                        <span className="tape-label">Process Automation</span>
                        <h1 className="display-title display-md" style={{ marginTop: '0.5rem' }}>
                            WORKFLOWS
                        </h1>
                    </div>
                    <div className="dashboard-header__actions">
                        <button onClick={fetchData} className="btn btn-secondary" disabled={loading}>
                            <RefreshCw size={16} className={loading ? 'spinning' : ''} />
                            Refresh
                        </button>
                    </div>
                </div>

                {error && (
                    <div className="dashboard-error">
                        {error}
                    </div>
                )}

                {/* Tabs */}
                <div className="workflow-tabs">
                    {tabs.map(tab => {
                        const Icon = tab.icon;
                        return (
                            <button
                                key={tab.id}
                                className={`workflow-tab ${activeTab === tab.id ? 'workflow-tab--active' : ''}`}
                                onClick={() => setActiveTab(tab.id)}
                            >
                                <Icon size={16} />
                                {tab.label}
                            </button>
                        );
                    })}
                </div>

                {loading ? (
                    <div className="loading-state">
                        <div className="spinner"></div>
                        <p>Loading workflows...</p>
                    </div>
                ) : (
                    <div className="workflow-content">
                        {/* Generated Workflows Tab */}
                        {activeTab === 'generated' && (
                            <div className="workflows-panel">
                                {/* Goal-based workflow search */}
                                <div className="workflow-search">
                                    <input
                                        type="text"
                                        value={workflowGoal}
                                        onChange={(e) => setWorkflowGoal(e.target.value)}
                                        placeholder="Enter a goal (e.g., 'process payment', 'onboard user')..."
                                        className="workflow-search__input"
                                        onKeyDown={(e) => e.key === 'Enter' && fetchWorkflowsWithGoal()}
                                    />
                                    <button
                                        onClick={fetchWorkflowsWithGoal}
                                        className="btn btn-primary"
                                        disabled={!workflowGoal.trim()}
                                    >
                                        <Zap size={16} />
                                        Generate
                                    </button>
                                </div>

                                {/* Suggestions */}
                                {workflows?.suggestions?.length > 0 && (
                                    <div className="workflow-section">
                                        <h3 className="section-title">Suggested Workflows for "{workflowGoal}"</h3>
                                        <div className="workflow-suggestions">
                                            {workflows.suggestions.map((suggestion, idx) => (
                                                <div key={idx} className="suggestion-card">
                                                    <h4>{suggestion.name}</h4>
                                                    <p>{suggestion.description}</p>
                                                    {suggestion.steps?.length > 0 && (
                                                        <div className="suggestion-steps">
                                                            {suggestion.steps.map((step, sIdx) => (
                                                                <span key={sIdx} className="suggestion-step">
                                                                    {step.service}{sIdx < suggestion.steps.length - 1 && <ArrowRight size={12} />}
                                                                </span>
                                                            ))}
                                                        </div>
                                                    )}
                                                    <div className="suggestion-meta">
                                                        <span><Clock size={12} /> {suggestion.estimated_duration}</span>
                                                        <span><Activity size={12} /> {suggestion.complexity || 'medium'}</span>
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                )}

                                {/* Generated Workflows List */}
                                <div className="workflow-section">
                                    <h3 className="section-title">Generated Workflows</h3>

                                    {workflows?.workflows?.length > 0 ? (
                                        <div className="workflows-list">
                                            {workflows.workflows.map((workflow, idx) => (
                                                <div key={idx} className="workflow-card">
                                                    <div
                                                        className="workflow-card__header"
                                                        onClick={() => setExpandedWorkflow(
                                                            expandedWorkflow === workflow.id ? null : workflow.id
                                                        )}
                                                    >
                                                        <div className="workflow-card__info">
                                                            {getStatusIcon(workflow.status)}
                                                            <div>
                                                                <h4>{workflow.name}</h4>
                                                                <span className="workflow-card__type">{workflow.type}</span>
                                                            </div>
                                                        </div>
                                                        <div className="workflow-card__stats">
                                                            <span className="workflow-stat">
                                                                <GitBranch size={14} />
                                                                {workflow.steps?.length || 0} steps
                                                            </span>
                                                            <span className="workflow-stat">
                                                                <Clock size={14} />
                                                                {workflow.avg_duration_ms?.toFixed(0) || 0}ms
                                                            </span>
                                                            <span className={`status-badge status-badge--${workflow.status}`}>
                                                                {workflow.status}
                                                            </span>
                                                            {expandedWorkflow === workflow.id ? (
                                                                <ChevronUp size={18} />
                                                            ) : (
                                                                <ChevronDown size={18} />
                                                            )}
                                                        </div>
                                                    </div>

                                                    {expandedWorkflow === workflow.id && (
                                                        <div className="workflow-card__details">
                                                            {workflow.description && (
                                                                <p className="workflow-description">{workflow.description}</p>
                                                            )}

                                                            {workflow.steps?.length > 0 && (
                                                                <div className="workflow-steps">
                                                                    <h5>Workflow Steps</h5>
                                                                    <div className="steps-timeline">
                                                                        {workflow.steps.map((step, sIdx) => (
                                                                            <div key={sIdx} className="step-item">
                                                                                <div className="step-number">{sIdx + 1}</div>
                                                                                <div className="step-content">
                                                                                    <div className="step-header">
                                                                                        <Server size={14} />
                                                                                        <strong>{step.service}</strong>
                                                                                        <span className="step-operation">{step.operation}</span>
                                                                                    </div>
                                                                                    {step.input && (
                                                                                        <div className="step-io">
                                                                                            <span>Input: {step.input}</span>
                                                                                        </div>
                                                                                    )}
                                                                                    {step.output && (
                                                                                        <div className="step-io">
                                                                                            <span>Output: {step.output}</span>
                                                                                        </div>
                                                                                    )}
                                                                                    <div className="step-metrics">
                                                                                        <span>{step.avg_latency_ms?.toFixed(0) || 0}ms latency</span>
                                                                                        <span>{((step.success_rate || 0) * 100).toFixed(1)}% success</span>
                                                                                    </div>
                                                                                </div>
                                                                                {sIdx < workflow.steps.length - 1 && (
                                                                                    <div className="step-connector">
                                                                                        <ArrowRight size={16} />
                                                                                    </div>
                                                                                )}
                                                                            </div>
                                                                        ))}
                                                                    </div>
                                                                </div>
                                                            )}

                                                            {workflow.metrics && (
                                                                <div className="workflow-metrics">
                                                                    <h5>Performance Metrics</h5>
                                                                    <div className="metrics-grid">
                                                                        <div className="metric-item">
                                                                            <span className="metric-label">Executions</span>
                                                                            <span className="metric-value">{workflow.metrics.total_executions?.toLocaleString()}</span>
                                                                        </div>
                                                                        <div className="metric-item">
                                                                            <span className="metric-label">Success Rate</span>
                                                                            <span className="metric-value">{((workflow.metrics.success_rate || 0) * 100).toFixed(1)}%</span>
                                                                        </div>
                                                                        <div className="metric-item">
                                                                            <span className="metric-label">Avg Duration</span>
                                                                            <span className="metric-value">{workflow.metrics.avg_duration_ms?.toFixed(0)}ms</span>
                                                                        </div>
                                                                        <div className="metric-item">
                                                                            <span className="metric-label">P95 Duration</span>
                                                                            <span className="metric-value">{workflow.metrics.p95_duration_ms?.toFixed(0)}ms</span>
                                                                        </div>
                                                                    </div>
                                                                </div>
                                                            )}

                                                            <div className="workflow-card__footer">
                                                                <span>Created: {new Date(workflow.created_at).toLocaleString()}</span>
                                                                {workflow.last_run && (
                                                                    <span>Last Run: {new Date(workflow.last_run).toLocaleString()}</span>
                                                                )}
                                                            </div>
                                                        </div>
                                                    )}
                                                </div>
                                            ))}
                                        </div>
                                    ) : (
                                        <div className="empty-state">
                                            <Workflow size={48} />
                                            <h3>No Workflows Yet</h3>
                                            <p>Workflows will appear here once your services start processing requests.</p>
                                        </div>
                                    )}
                                </div>
                            </div>
                        )}

                        {/* Comparison Tab */}
                        {activeTab === 'comparison' && (
                            <div className="comparison-panel">
                                <h3 className="section-title">Workflow Comparison</h3>

                                {comparison?.comparisons?.length > 0 ? (
                                    <div className="comparison-table-wrapper">
                                        <table className="comparison-table">
                                            <thead>
                                                <tr>
                                                    <th>Workflow</th>
                                                    <th>Executions</th>
                                                    <th>Avg Duration</th>
                                                    <th>Success Rate</th>
                                                    <th>Error Rate</th>
                                                    <th>Trend</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {comparison.comparisons.map((item, idx) => (
                                                    <tr key={idx}>
                                                        <td className="comparison-name">
                                                            <Workflow size={14} />
                                                            {item.name}
                                                        </td>
                                                        <td>{item.total_executions?.toLocaleString()}</td>
                                                        <td>{item.avg_duration_ms?.toFixed(0)}ms</td>
                                                        <td className={item.success_rate > 0.95 ? 'success' : item.success_rate > 0.9 ? 'warning' : 'error'}>
                                                            {((item.success_rate || 0) * 100).toFixed(1)}%
                                                        </td>
                                                        <td className={item.error_rate > 0.05 ? 'error' : 'success'}>
                                                            {((item.error_rate || 0) * 100).toFixed(2)}%
                                                        </td>
                                                        <td>
                                                            <span className={`trend-indicator trend-indicator--${item.trend || 'stable'}`}>
                                                                {item.trend || 'stable'}
                                                            </span>
                                                        </td>
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    </div>
                                ) : comparison?.workflows ? (
                                    // Alternative comparison format
                                    <div className="comparison-cards">
                                        {Object.entries(comparison.workflows).map(([name, data], idx) => (
                                            <div key={idx} className="comparison-card">
                                                <h4>{name}</h4>
                                                <div className="comparison-card__metrics">
                                                    <div className="metric">
                                                        <span className="label">Executions</span>
                                                        <span className="value">{data.executions?.toLocaleString()}</span>
                                                    </div>
                                                    <div className="metric">
                                                        <span className="label">Avg Duration</span>
                                                        <span className="value">{data.avg_duration_ms?.toFixed(0)}ms</span>
                                                    </div>
                                                    <div className="metric">
                                                        <span className="label">Success Rate</span>
                                                        <span className="value">{((data.success_rate || 0) * 100).toFixed(1)}%</span>
                                                    </div>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                ) : (
                                    <div className="empty-state">
                                        <Scale size={48} />
                                        <h3>No Comparison Data</h3>
                                        <p>Comparison data will appear once multiple workflows have been executed.</p>
                                    </div>
                                )}

                                {comparison?.summary && (
                                    <div className="comparison-summary">
                                        <h4>Summary</h4>
                                        <div className="summary-grid">
                                            <div className="summary-item">
                                                <span className="summary-label">Best Performer</span>
                                                <span className="summary-value">{comparison.summary.best_performer}</span>
                                            </div>
                                            <div className="summary-item">
                                                <span className="summary-label">Needs Attention</span>
                                                <span className="summary-value warning">{comparison.summary.needs_attention}</span>
                                            </div>
                                            <div className="summary-item">
                                                <span className="summary-label">Total Workflows</span>
                                                <span className="summary-value">{comparison.summary.total_workflows}</span>
                                            </div>
                                        </div>
                                    </div>
                                )}
                            </div>
                        )}

                        {/* Architecture Graph Tab */}
                        {activeTab === 'graph' && (
                            <div className="graph-panel">
                                <h3 className="section-title">Architecture Graph</h3>

                                {architectureGraph?.nodes?.length > 0 ? (
                                    <div className="graph-visualization">
                                        {/* Graph Stats */}
                                        <div className="graph-stats">
                                            <div className="graph-stat">
                                                <Server size={18} />
                                                <span className="graph-stat__value">{architectureGraph.nodes.length}</span>
                                                <span className="graph-stat__label">Services</span>
                                            </div>
                                            <div className="graph-stat">
                                                <GitBranch size={18} />
                                                <span className="graph-stat__value">{architectureGraph.edges?.length || 0}</span>
                                                <span className="graph-stat__label">Connections</span>
                                            </div>
                                            <div className="graph-stat">
                                                <Database size={18} />
                                                <span className="graph-stat__value">
                                                    {architectureGraph.nodes.filter(n => n.type === 'database').length}
                                                </span>
                                                <span className="graph-stat__label">Databases</span>
                                            </div>
                                            <div className="graph-stat">
                                                <BarChart2 size={18} />
                                                <span className="graph-stat__value">
                                                    {architectureGraph.metrics?.total_requests?.toLocaleString() || 0}
                                                </span>
                                                <span className="graph-stat__label">Requests</span>
                                            </div>
                                        </div>

                                        {/* Nodes List */}
                                        <div className="graph-nodes-section">
                                            <h4>Service Nodes</h4>
                                            <div className="graph-nodes-grid">
                                                {architectureGraph.nodes.map((node, idx) => (
                                                    <div key={idx} className={`graph-node-card graph-node-card--${node.type || 'service'}`}>
                                                        <div className="graph-node-card__header">
                                                            {node.type === 'database' ? <Database size={16} /> : <Server size={16} />}
                                                            <span className="node-name">{node.id}</span>
                                                        </div>
                                                        <span className="node-type">{node.type || 'service'}</span>
                                                        <div className="node-metrics">
                                                            <span>{node.metrics?.call_count?.toLocaleString() || 0} calls</span>
                                                            <span>{node.metrics?.avg_latency_ms?.toFixed(0) || 0}ms</span>
                                                        </div>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>

                                        {/* Edges / Connections */}
                                        {architectureGraph.edges?.length > 0 && (
                                            <div className="graph-edges-section">
                                                <h4>Connections</h4>
                                                <div className="graph-edges-list">
                                                    {architectureGraph.edges.map((edge, idx) => (
                                                        <div key={idx} className="graph-edge">
                                                            <span className="edge-source">{edge.source}</span>
                                                            <div className="edge-arrow">
                                                                <ArrowRight size={14} />
                                                                <span className="edge-label">{edge.call_count} calls</span>
                                                            </div>
                                                            <span className="edge-target">{edge.target}</span>
                                                        </div>
                                                    ))}
                                                </div>
                                            </div>
                                        )}

                                        {/* Workflows in Graph */}
                                        {architectureGraph.workflows?.length > 0 && (
                                            <div className="graph-workflows-section">
                                                <h4>Identified Workflows</h4>
                                                <div className="graph-workflows">
                                                    {architectureGraph.workflows.map((wf, idx) => (
                                                        <div key={idx} className="graph-workflow">
                                                            <span className="workflow-name">{wf.name}</span>
                                                            <div className="workflow-path">
                                                                {wf.path?.map((service, sIdx) => (
                                                                    <span key={sIdx} className="path-service">
                                                                        {service}
                                                                        {sIdx < wf.path.length - 1 && <ArrowRight size={12} />}
                                                                    </span>
                                                                ))}
                                                            </div>
                                                            <span className="workflow-count">{wf.request_count} requests</span>
                                                        </div>
                                                    ))}
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                ) : (
                                    <div className="empty-state">
                                        <Network size={48} />
                                        <h3>No Graph Data</h3>
                                        <p>Architecture graph will appear once services and connections are discovered.</p>
                                    </div>
                                )}
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}

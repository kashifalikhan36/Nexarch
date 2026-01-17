'use client';

import { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import { useAuth } from '@/lib/auth-context';
import { apiClient } from '@/lib/api-client';
import {
    Network,
    AlertTriangle,
    CheckCircle,
    RefreshCw,
    Server,
    Database,
    ArrowRight,
    Activity,
    Zap,
    AlertCircle,
    Box,
    GitBranch
} from 'lucide-react';

export default function ArchitecturePage() {
    const { isAuthenticated, loading: authLoading } = useAuth();
    const [architectureMap, setArchitectureMap] = useState(null);
    const [currentArch, setCurrentArch] = useState(null);
    const [issues, setIssues] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [selectedNode, setSelectedNode] = useState(null);

    useEffect(() => {
        if (!authLoading && isAuthenticated) {
            fetchData();
        }
    }, [authLoading, isAuthenticated]);

    const fetchData = async () => {
        setLoading(true);
        setError(null);
        try {
            const [mapData, archData, issuesData] = await Promise.all([
                apiClient.getArchitectureMap(),
                apiClient.getCurrentArchitecture(),
                apiClient.getArchitectureIssues()
            ]);
            setArchitectureMap(mapData);
            setCurrentArch(archData);
            setIssues(issuesData);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const getNodeColor = (errorRate) => {
        if (errorRate > 0.05) return 'var(--color-error)';
        if (errorRate > 0.02) return 'var(--color-warning)';
        return 'var(--color-success)';
    };

    const getSeverityIcon = (severity) => {
        switch (severity) {
            case 'high':
            case 'critical':
                return <AlertTriangle size={16} className="severity-icon severity-icon--critical" />;
            case 'medium':
                return <AlertCircle size={16} className="severity-icon severity-icon--warning" />;
            default:
                return <AlertCircle size={16} className="severity-icon severity-icon--info" />;
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
                <p>Please sign in to view architecture data.</p>
                <Link href="/login" className="btn btn-primary">Sign In</Link>
            </div>
        );
    }

    return (
        <div className="dashboard-page">
            {/* Header */}
            <nav className="dashboard-nav">
                <Link href="/" className="navbar__logo">NEXARCH</Link>
                <div className="dashboard-nav__links">
                    <Link href="/dashboard">Dashboard</Link>
                    <Link href="/ingestion">Ingestion</Link>
                    <Link href="/architecture" className="active">Architecture</Link>
                    <Link href="/ai-design">AI Design</Link>
                </div>
            </nav>

            {/* Page Content */}
            <div className="dashboard-content">
                <div className="dashboard-header">
                    <div>
                        <span className="tape-label">System Overview</span>
                        <h1 className="display-title display-md" style={{ marginTop: '0.5rem' }}>
                            ARCHITECTURE MAP
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

                {/* Summary Stats */}
                <div className="stats-grid">
                    <div className="stat-card">
                        <div className="stat-card__icon">
                            <Server size={24} />
                        </div>
                        <div className="stat-card__content">
                            <span className="stat-card__label">Total Services</span>
                            <span className="stat-card__value">
                                {architectureMap?.graph_stats?.total_nodes || currentArch?.metrics_summary?.total_services || '0'}
                            </span>
                        </div>
                    </div>

                    <div className="stat-card">
                        <div className="stat-card__icon">
                            <GitBranch size={24} />
                        </div>
                        <div className="stat-card__content">
                            <span className="stat-card__label">Dependencies</span>
                            <span className="stat-card__value">
                                {architectureMap?.graph_stats?.total_edges || '0'}
                            </span>
                        </div>
                    </div>

                    <div className="stat-card">
                        <div className="stat-card__icon">
                            <Activity size={24} />
                        </div>
                        <div className="stat-card__content">
                            <span className="stat-card__label">Avg Latency</span>
                            <span className="stat-card__value">
                                {currentArch?.metrics_summary?.avg_latency_ms?.toFixed(1) || '0'}ms
                            </span>
                        </div>
                    </div>

                    <div className="stat-card">
                        <div className="stat-card__icon">
                            <AlertTriangle size={24} />
                        </div>
                        <div className="stat-card__content">
                            <span className="stat-card__label">Issues</span>
                            <span className="stat-card__value">
                                {issues?.total_count || '0'}
                            </span>
                        </div>
                    </div>
                </div>

                {loading ? (
                    <div className="loading-state">
                        <div className="spinner"></div>
                        <p>Loading architecture...</p>
                    </div>
                ) : (
                    <div className="architecture-layout">
                        {/* Architecture Graph */}
                        <div className="architecture-graph-section">
                            <h2 className="section-title">Service Dependencies</h2>

                            {architectureMap?.nodes?.length > 0 ? (
                                <div className="architecture-graph">
                                    {/* Nodes */}
                                    <div className="graph-nodes">
                                        {architectureMap.nodes.map((node) => (
                                            <div
                                                key={node.id}
                                                className={`graph-node ${selectedNode === node.id ? 'graph-node--selected' : ''}`}
                                                onClick={() => setSelectedNode(selectedNode === node.id ? null : node.id)}
                                                style={{
                                                    '--node-color': getNodeColor(node.metrics?.error_rate || 0)
                                                }}
                                            >
                                                <div className="graph-node__header">
                                                    <Box size={18} />
                                                    <span className="graph-node__name">{node.id}</span>
                                                </div>
                                                <div className="graph-node__type">{node.type || 'service'}</div>
                                                <div className="graph-node__metrics">
                                                    <span>
                                                        <Zap size={12} />
                                                        {node.metrics?.avg_latency_ms?.toFixed(0) || 0}ms
                                                    </span>
                                                    <span>
                                                        <Activity size={12} />
                                                        {node.metrics?.call_count?.toLocaleString() || 0} calls
                                                    </span>
                                                </div>
                                                {node.metrics?.error_rate > 0 && (
                                                    <div className="graph-node__error">
                                                        {(node.metrics.error_rate * 100).toFixed(2)}% errors
                                                    </div>
                                                )}
                                            </div>
                                        ))}
                                    </div>

                                    {/* Edges / Connections */}
                                    {architectureMap.edges?.length > 0 && (
                                        <div className="graph-edges">
                                            <h3>Connections</h3>
                                            <div className="edges-list">
                                                {architectureMap.edges.map((edge, idx) => (
                                                    <div key={idx} className="edge-item">
                                                        <span className="edge-source">{edge.source}</span>
                                                        <ArrowRight size={16} />
                                                        <span className="edge-target">{edge.target}</span>
                                                        <span className="edge-stats">
                                                            {edge.call_count?.toLocaleString()} calls • {edge.avg_latency_ms?.toFixed(0)}ms
                                                        </span>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    )}

                                    {/* Bottlenecks */}
                                    {architectureMap.bottlenecks?.length > 0 && (
                                        <div className="bottlenecks-alert">
                                            <AlertTriangle size={20} />
                                            <div>
                                                <strong>Bottlenecks Detected:</strong>
                                                <span>{architectureMap.bottlenecks.join(', ')}</span>
                                            </div>
                                        </div>
                                    )}

                                    {/* Critical Paths */}
                                    {architectureMap.critical_paths?.length > 0 && (
                                        <div className="critical-paths">
                                            <h4>Critical Paths</h4>
                                            {architectureMap.critical_paths.map((path, idx) => (
                                                <div key={idx} className="critical-path">
                                                    {path.map((node, nodeIdx) => (
                                                        <span key={nodeIdx}>
                                                            {node}
                                                            {nodeIdx < path.length - 1 && <ArrowRight size={14} />}
                                                        </span>
                                                    ))}
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            ) : (
                                <div className="empty-state">
                                    <Network size={48} />
                                    <h3>No Architecture Data</h3>
                                    <p>Start by ingesting telemetry data or submitting architecture discoveries.</p>
                                    <Link href="/ingestion" className="btn btn-primary">
                                        Go to Ingestion
                                    </Link>
                                </div>
                            )}
                        </div>

                        {/* Issues Panel */}
                        <div className="issues-section">
                            <h2 className="section-title">Detected Issues</h2>

                            {issues?.issues?.length > 0 ? (
                                <div className="issues-list">
                                    {issues.issues.map((issue, idx) => (
                                        <div key={idx} className={`issue-card issue-card--${issue.severity}`}>
                                            <div className="issue-card__header">
                                                {getSeverityIcon(issue.severity)}
                                                <span className="issue-card__type">{issue.type}</span>
                                                <span className={`severity-badge severity-badge--${issue.severity}`}>
                                                    {issue.severity}
                                                </span>
                                            </div>
                                            <div className="issue-card__service">
                                                <Server size={14} />
                                                {issue.service}
                                            </div>
                                            <p className="issue-card__description">{issue.description}</p>
                                            {issue.recommendation && (
                                                <div className="issue-card__recommendation">
                                                    <strong>Recommendation:</strong> {issue.recommendation}
                                                </div>
                                            )}
                                            {issue.affected_operations?.length > 0 && (
                                                <div className="issue-card__operations">
                                                    <strong>Affected:</strong>
                                                    <div className="tag-list">
                                                        {issue.affected_operations.map((op, opIdx) => (
                                                            <span key={opIdx} className="tag tag--secondary">{op}</span>
                                                        ))}
                                                    </div>
                                                </div>
                                            )}
                                            <div className="issue-card__footer">
                                                Detected: {new Date(issue.detected_at).toLocaleString()}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <div className="no-issues">
                                    <CheckCircle size={32} />
                                    <p>No issues detected</p>
                                </div>
                            )}
                        </div>
                    </div>
                )}

                {/* Selected Node Details */}
                {selectedNode && architectureMap?.nodes && (
                    <div className="node-details-panel">
                        <h3>Service Details: {selectedNode}</h3>
                        {(() => {
                            const node = architectureMap.nodes.find(n => n.id === selectedNode);
                            if (!node) return null;
                            return (
                                <div className="node-details">
                                    <div className="node-detail">
                                        <span className="node-detail__label">Type</span>
                                        <span className="node-detail__value">{node.type || 'Unknown'}</span>
                                    </div>
                                    <div className="node-detail">
                                        <span className="node-detail__label">Call Count</span>
                                        <span className="node-detail__value">{node.metrics?.call_count?.toLocaleString() || 0}</span>
                                    </div>
                                    <div className="node-detail">
                                        <span className="node-detail__label">Avg Latency</span>
                                        <span className="node-detail__value">{node.metrics?.avg_latency_ms?.toFixed(2) || 0}ms</span>
                                    </div>
                                    <div className="node-detail">
                                        <span className="node-detail__label">Error Rate</span>
                                        <span className="node-detail__value">{((node.metrics?.error_rate || 0) * 100).toFixed(2)}%</span>
                                    </div>

                                    {/* Outgoing connections */}
                                    <div className="node-connections">
                                        <h4>Outgoing Connections</h4>
                                        {architectureMap.edges
                                            .filter(e => e.source === selectedNode)
                                            .map((edge, idx) => (
                                                <div key={idx} className="connection-item">
                                                    <ArrowRight size={14} />
                                                    <span>{edge.target}</span>
                                                    <span className="connection-stats">{edge.call_count} calls</span>
                                                </div>
                                            ))
                                        }
                                        {architectureMap.edges.filter(e => e.source === selectedNode).length === 0 && (
                                            <p className="no-connections">No outgoing connections</p>
                                        )}
                                    </div>

                                    {/* Incoming connections */}
                                    <div className="node-connections">
                                        <h4>Incoming Connections</h4>
                                        {architectureMap.edges
                                            .filter(e => e.target === selectedNode)
                                            .map((edge, idx) => (
                                                <div key={idx} className="connection-item">
                                                    <span>{edge.source}</span>
                                                    <ArrowRight size={14} />
                                                    <span className="connection-stats">{edge.call_count} calls</span>
                                                </div>
                                            ))
                                        }
                                        {architectureMap.edges.filter(e => e.target === selectedNode).length === 0 && (
                                            <p className="no-connections">No incoming connections</p>
                                        )}
                                    </div>
                                </div>
                            );
                        })()}
                        <button onClick={() => setSelectedNode(null)} className="btn btn-secondary">
                            Close
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
}

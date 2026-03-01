'use client';

import { useState, useEffect, useCallback, useMemo } from 'react';
import Link from 'next/link';
import {
    ReactFlow,
    Background,
    Controls,
    MiniMap,
    Handle,
    Position,
    useNodesState,
    useEdgesState,
    MarkerType,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { useAuth } from '@/lib/auth-context';
import { apiClient } from '@/lib/api-client';
import { useRealtimeStream } from '@/lib/stream-client';
import { LiveStreamBadge } from '@/components/LiveStreamBadge';
import { ErrorBoundary } from '@/components/ErrorBoundary';
import {
    Network,
    AlertTriangle,
    CheckCircle,
    RefreshCw,
    Server,
    Activity,
    Zap,
    AlertCircle,
    Box,
    GitBranch,
    Key,
    ArrowRight,
} from 'lucide-react';

// ─── colour helpers ──────────────────────────────────────────────────────────

function errorColor(rate) {
    if (rate > 0.05) return '#ef4444';
    if (rate > 0.02) return '#f59e0b';
    return '#22c55e';
}

function errorBg(rate) {
    if (rate > 0.05) return '#fef2f2';
    if (rate > 0.02) return '#fffbeb';
    return '#f0fdf4';
}

// ─── Custom ReactFlow service node ───────────────────────────────────────────

function ServiceNode({ data }) {
    const color = errorColor(data.errorRate || 0);
    const bg    = errorBg(data.errorRate || 0);
    return (
        <div style={{
            background: bg,
            border: `2px solid ${color}`,
            borderRadius: 8,
            padding: '10px 14px',
            minWidth: 160,
            boxShadow: '0 2px 8px rgba(0,0,0,.08)',
            cursor: 'pointer',
        }}>
            <Handle type="target" position={Position.Left} />
            <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 4 }}>
                <Box size={14} color={color} />
                <span style={{ fontWeight: 700, fontSize: 13, color: '#111' }}>{data.label}</span>
            </div>
            <div style={{ fontSize: 11, color: '#555', marginBottom: 4 }}>{data.nodeType || 'service'}</div>
            <div style={{ display: 'flex', gap: 8, fontSize: 11, color: '#444' }}>
                <span><Zap size={10} style={{ display: 'inline', marginRight: 2 }} />{data.latency ?? 0}ms</span>
                <span><Activity size={10} style={{ display: 'inline', marginRight: 2 }} />{(data.calls ?? 0).toLocaleString()}</span>
            </div>
            {(data.errorRate || 0) > 0 && (
                <div style={{ fontSize: 10, color, marginTop: 4 }}>{(data.errorRate * 100).toFixed(2)}% errors</div>
            )}
            <Handle type="source" position={Position.Right} />
        </div>
    );
}

const nodeTypes = { service: ServiceNode };

// ─── Layout helpers ──────────────────────────────────────────────────────────

function computeLayout(apiNodes) {
    const cols = Math.max(1, Math.ceil(Math.sqrt(apiNodes.length)));
    return apiNodes.map((n, i) => ({
        x: (i % cols) * 220 + 40,
        y: Math.floor(i / cols) * 140 + 40,
    }));
}

function toFlowGraph(architectureMap, liveMetrics) {
    const nodes     = architectureMap?.nodes || [];
    const positions = computeLayout(nodes);

    const rfNodes = nodes.map((n, i) => {
        const live      = liveMetrics[n.id]?.[0];  // newest snapshot in history array
        const errorRate = live?.error_rate   ?? n.metrics?.error_rate   ?? 0;
        const latency   = live?.avg_latency_ms != null
            ? Math.round(live.avg_latency_ms)
            : Math.round(n.metrics?.avg_latency_ms ?? 0);
        const calls     = live?.call_count   ?? n.metrics?.call_count   ?? 0;
        return {
            id: n.id,
            type: 'service',
            position: positions[i],
            data: { label: n.id, nodeType: n.type, errorRate, latency, calls, raw: n },
        };
    });

    const rfEdges = (architectureMap?.edges || []).map((e, i) => ({
        id: `e${i}`,
        source: e.source,
        target: e.target,
        label: e.call_count ? `${e.call_count} calls` : undefined,
        animated: true,
        markerEnd: { type: MarkerType.ArrowClosed },
        style: { stroke: '#94a3b8', strokeWidth: 1.5 },
        labelStyle: { fontSize: 10, fill: '#64748b' },
        labelBgStyle: { fill: '#fff', fillOpacity: 0.85 },
    }));

    return { rfNodes, rfEdges };
}

// ─── Severity icon ───────────────────────────────────────────────────────────

function SeverityIcon({ severity }) {
    if (severity === 'high' || severity === 'critical')
        return <AlertTriangle size={16} style={{ color: '#ef4444' }} />;
    if (severity === 'medium')
        return <AlertCircle size={16} style={{ color: '#f59e0b' }} />;
    return <AlertCircle size={16} style={{ color: '#3b82f6' }} />;
}

// ─── Main page ───────────────────────────────────────────────────────────────

export default function ArchitecturePage() {
    const { isAuthenticated, loading: authLoading, user } = useAuth();

    const [architectureMap, setArchitectureMap] = useState(null);
    const [currentArch,     setCurrentArch]     = useState(null);
    const [issues,          setIssues]           = useState(null);
    const [loading,         setLoading]          = useState(true);
    const [error,           setError]            = useState(null);
    const [selectedNodeId,  setSelectedNodeId]   = useState(null);

    const [rfNodes, setRfNodes, onNodesChange] = useNodesState([]);
    const [rfEdges, setRfEdges, onEdgesChange] = useEdgesState([]);

    const tenantId = user?.tenant_id || user?.id || null;
    const { connected, metrics: liveMetrics, issues: liveIssues } = useRealtimeStream(tenantId);

    const fetchData = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            const [mapData, archData, issuesData] = await Promise.all([
                apiClient.getArchitectureMap(),
                apiClient.getCurrentArchitecture(),
                apiClient.getArchitectureIssues(),
            ]);
            setArchitectureMap(mapData);
            setCurrentArch(archData);
            setIssues(issuesData);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        if (!authLoading && isAuthenticated) fetchData();
    }, [authLoading, isAuthenticated, fetchData]);

    // Rebuild ReactFlow graph whenever API data or live metrics change
    useEffect(() => {
        if (!architectureMap) return;
        const { rfNodes: n, rfEdges: e } = toFlowGraph(architectureMap, liveMetrics);
        setRfNodes(n);
        setRfEdges(e);
    }, [architectureMap, liveMetrics, setRfNodes, setRfEdges]);

    const displayIssues = useMemo(() => {
        if (liveIssues.length > 0) return { total_count: liveIssues.length, issues: liveIssues };
        return issues;
    }, [issues, liveIssues]);

    const onNodeClick = useCallback((_evt, node) => {
        setSelectedNodeId(prev => (prev === node.id ? null : node.id));
    }, []);

    const selectedNodeData = useMemo(() => {
        if (!selectedNodeId || !architectureMap) return null;
        return architectureMap.nodes?.find(n => n.id === selectedNodeId) ?? null;
    }, [selectedNodeId, architectureMap]);

    if (authLoading) {
        return (
            <div className="page-loading">
                <div className="spinner" />
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

    const stats = [
        { icon: <Server size={24} />,       label: 'Services',     value: architectureMap?.graph_stats?.total_nodes ?? currentArch?.metrics_summary?.total_services ?? 0 },
        { icon: <GitBranch size={24} />,    label: 'Dependencies', value: architectureMap?.graph_stats?.total_edges ?? 0 },
        { icon: <Activity size={24} />,     label: 'Avg Latency',  value: `${(currentArch?.metrics_summary?.avg_latency_ms ?? 0).toFixed(1)}ms` },
        { icon: <AlertTriangle size={24} />,label: 'Issues',       value: displayIssues?.total_count ?? 0 },
    ];

    return (
        <div className="dashboard-page">
            <nav className="dashboard-nav">
                <Link href="/" className="navbar__logo">NEXARCH</Link>
                <div className="dashboard-nav__links">
                    <Link href="/dashboard">Dashboard</Link>
                    <Link href="/ingestion">Ingestion</Link>
                    <Link href="/architecture" className="active">Architecture</Link>
                    <Link href="/workflows">Workflows</Link>
                    <Link href="/ai-design">AI Design</Link>
                    <Link href="/api-keys" className="api-link">
                        <Key size={14} /><span>API Keys</span>
                    </Link>
                </div>
            </nav>

            <div className="dashboard-content">
                <div className="dashboard-header">
                    <div>
                        <span className="tape-label">System Overview</span>
                        <h1 className="display-title display-md" style={{ marginTop: '0.5rem' }}>ARCHITECTURE MAP</h1>
                    </div>
                    <div className="dashboard-header__actions" style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
                        <LiveStreamBadge connected={connected} />
                        <button onClick={fetchData} className="btn btn-secondary" disabled={loading}>
                            <RefreshCw size={16} className={loading ? 'spinning' : ''} />
                            Refresh
                        </button>
                    </div>
                </div>

                {error && <div className="dashboard-error">{error}</div>}

                <div className="stats-grid">
                    {stats.map(s => (
                        <div key={s.label} className="stat-card">
                            <div className="stat-card__icon">{s.icon}</div>
                            <div className="stat-card__content">
                                <span className="stat-card__label">{s.label}</span>
                                <span className="stat-card__value">{s.value}</span>
                            </div>
                        </div>
                    ))}
                </div>

                {loading ? (
                    <div className="loading-state">
                        <div className="spinner" />
                        <p>Loading architecture...</p>
                    </div>
                ) : (
                    <div className="architecture-layout">
                        {/* React Flow canvas */}
                        <div className="architecture-graph-section">
                            <h2 className="section-title">Service Dependencies</h2>

                            {rfNodes.length > 0 ? (
                                <ErrorBoundary fallback={<p style={{ color: '#ef4444' }}>Graph failed to render.</p>}>
                                    <div style={{ width: '100%', height: 520, borderRadius: 8, border: '1px solid #e2e8f0', overflow: 'hidden' }}>
                                        <ReactFlow
                                            nodes={rfNodes}
                                            edges={rfEdges}
                                            onNodesChange={onNodesChange}
                                            onEdgesChange={onEdgesChange}
                                            onNodeClick={onNodeClick}
                                            nodeTypes={nodeTypes}
                                            fitView
                                            fitViewOptions={{ padding: 0.2 }}
                                            minZoom={0.3}
                                            maxZoom={2}
                                            attributionPosition="bottom-right"
                                        >
                                            <Background gap={20} color="#f1f5f9" />
                                            <Controls />
                                            <MiniMap
                                                nodeColor={node => errorColor(node.data?.errorRate ?? 0)}
                                                nodeBorderRadius={4}
                                                style={{ background: '#f8fafc' }}
                                            />
                                        </ReactFlow>
                                    </div>
                                </ErrorBoundary>
                            ) : (
                                <div className="empty-state">
                                    <Network size={48} />
                                    <h3>No Architecture Data</h3>
                                    <p>Start by ingesting telemetry data or submitting architecture discoveries.</p>
                                    <Link href="/ingestion" className="btn btn-primary">Go to Ingestion</Link>
                                </div>
                            )}

                            {architectureMap?.bottlenecks?.length > 0 && (
                                <div className="bottlenecks-alert" style={{ marginTop: 12 }}>
                                    <AlertTriangle size={20} />
                                    <div>
                                        <strong>Bottlenecks:</strong>
                                        <span> {architectureMap.bottlenecks.join(', ')}</span>
                                    </div>
                                </div>
                            )}

                            {architectureMap?.critical_paths?.length > 0 && (
                                <div className="critical-paths" style={{ marginTop: 12 }}>
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

                        {/* Issues panel */}
                        <div className="issues-section">
                            <h2 className="section-title">
                                Detected Issues
                                {liveIssues.length > 0 && (
                                    <span style={{ fontSize: 11, marginLeft: 8, color: '#22c55e' }}>(live)</span>
                                )}
                            </h2>

                            {displayIssues?.issues?.length > 0 ? (
                                <div className="issues-list">
                                    {displayIssues.issues.map((issue, idx) => (
                                        <div key={idx} className={`issue-card issue-card--${issue.severity}`}>
                                            <div className="issue-card__header">
                                                <SeverityIcon severity={issue.severity} />
                                                <span className="issue-card__type">{issue.type}</span>
                                                <span className={`severity-badge severity-badge--${issue.severity}`}>{issue.severity}</span>
                                            </div>
                                            <div className="issue-card__service"><Server size={14} />{issue.affected_nodes?.[0] || issue.affected_services?.[0] || 'Multiple Services'}</div>
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

                {/* Selected node side panel */}
                {selectedNodeId && selectedNodeData && (
                    <div className="node-details-panel">
                        <h3>Service Details: {selectedNodeId}</h3>
                        <div className="node-details">
                            <div className="node-detail">
                                <span className="node-detail__label">Type</span>
                                <span className="node-detail__value">{selectedNodeData.type || 'Unknown'}</span>
                            </div>
                            <div className="node-detail">
                                <span className="node-detail__label">Call Count</span>
                                <span className="node-detail__value">
                                    {(liveMetrics[selectedNodeId]?.call_count ?? selectedNodeData.metrics?.call_count ?? 0).toLocaleString()}
                                </span>
                            </div>
                            <div className="node-detail">
                                <span className="node-detail__label">Avg Latency</span>
                                <span className="node-detail__value">
                                    {(liveMetrics[selectedNodeId]?.avg_latency_ms ?? selectedNodeData.metrics?.avg_latency_ms ?? 0).toFixed(2)}ms
                                </span>
                            </div>
                            <div className="node-detail">
                                <span className="node-detail__label">Error Rate</span>
                                <span className="node-detail__value">
                                    {((liveMetrics[selectedNodeId]?.error_rate ?? selectedNodeData.metrics?.error_rate ?? 0) * 100).toFixed(2)}%
                                </span>
                            </div>

                            <div className="node-connections">
                                <h4>Outgoing</h4>
                                {architectureMap.edges.filter(e => e.source === selectedNodeId).map((edge, idx) => (
                                    <div key={idx} className="connection-item">
                                        <ArrowRight size={14} /><span>{edge.target}</span>
                                        <span className="connection-stats">{edge.call_count} calls</span>
                                    </div>
                                ))}
                                {architectureMap.edges.filter(e => e.source === selectedNodeId).length === 0 && (
                                    <p className="no-connections">None</p>
                                )}
                            </div>

                            <div className="node-connections">
                                <h4>Incoming</h4>
                                {architectureMap.edges.filter(e => e.target === selectedNodeId).map((edge, idx) => (
                                    <div key={idx} className="connection-item">
                                        <span>{edge.source}</span><ArrowRight size={14} />
                                        <span className="connection-stats">{edge.call_count} calls</span>
                                    </div>
                                ))}
                                {architectureMap.edges.filter(e => e.target === selectedNodeId).length === 0 && (
                                    <p className="no-connections">None</p>
                                )}
                            </div>
                        </div>
                        <button onClick={() => setSelectedNodeId(null)} className="btn btn-secondary">Close</button>
                    </div>
                )}
            </div>
        </div>
    );
}

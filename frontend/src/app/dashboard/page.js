'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useAuth } from '@/lib/auth-context';
import { apiClient } from '@/lib/api-client';
import {
    BarChart3,
    Activity,
    Server,
    AlertTriangle,
    RefreshCw,
    Heart,
    Clock,
    TrendingUp,
    TrendingDown,
    Zap,
    Lightbulb,
    Target,
    CheckCircle,
    XCircle,
    AlertCircle,
    ArrowUpRight,
    Percent,
    Timer,
    Layers
} from 'lucide-react';

export default function DashboardPage() {
    const { isAuthenticated, loading: authLoading, user } = useAuth();
    const [overview, setOverview] = useState(null);
    const [health, setHealth] = useState(null);
    const [trends, setTrends] = useState(null);
    const [insights, setInsights] = useState(null);
    const [recommendations, setRecommendations] = useState(null);
    const [bottlenecks, setBottlenecks] = useState(null);
    const [services, setServices] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [trendHours, setTrendHours] = useState(24);

    useEffect(() => {
        if (!authLoading && isAuthenticated) {
            fetchData();
        }
    }, [authLoading, isAuthenticated]);

    useEffect(() => {
        if (isAuthenticated) {
            fetchTrends();
        }
    }, [trendHours, isAuthenticated]);

    const fetchData = async () => {
        setLoading(true);
        setError(null);
        try {
            const [overviewData, healthData, trendsData, insightsData, recsData, bottlenecksData, servicesData] = await Promise.all([
                apiClient.getDashboardOverview(),
                apiClient.getDashboardHealth(),
                apiClient.getTrends(trendHours),
                apiClient.getInsights(),
                apiClient.getRecommendations(),
                apiClient.getBottlenecks(),
                apiClient.getServices()
            ]);
            setOverview(overviewData);
            setHealth(healthData);
            setTrends(trendsData);
            setInsights(insightsData);
            setRecommendations(recsData);
            setBottlenecks(bottlenecksData);
            setServices(servicesData);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const fetchTrends = async () => {
        try {
            const trendsData = await apiClient.getTrends(trendHours);
            setTrends(trendsData);
        } catch (err) {
            console.error('Failed to fetch trends:', err);
        }
    };

    const getHealthIcon = (status) => {
        switch (status) {
            case 'healthy':
                return <CheckCircle size={16} className="health-icon health-icon--healthy" />;
            case 'degraded':
                return <AlertCircle size={16} className="health-icon health-icon--degraded" />;
            case 'unhealthy':
                return <XCircle size={16} className="health-icon health-icon--unhealthy" />;
            default:
                return <AlertCircle size={16} className="health-icon" />;
        }
    };

    const getScoreColor = (score) => {
        if (score >= 80) return 'var(--color-success)';
        if (score >= 60) return 'var(--color-warning)';
        return 'var(--color-error)';
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
                <p>Please sign in to view the dashboard.</p>
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
                    <Link href="/dashboard" className="active">Dashboard</Link>
                    <Link href="/ingestion">Ingestion</Link>
                    <Link href="/architecture">Architecture</Link>
                    <Link href="/ai-design">AI Design</Link>
                </div>
            </nav>

            {/* Page Content */}
            <div className="dashboard-content">
                <div className="dashboard-header">
                    <div>
                        <span className="tape-label">System Monitor</span>
                        <h1 className="display-title display-md" style={{ marginTop: '0.5rem' }}>
                            DASHBOARD
                        </h1>
                        {user && <p className="dashboard-welcome">Welcome back, {user.name || user.email}</p>}
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

                {loading ? (
                    <div className="loading-state">
                        <div className="spinner"></div>
                        <p>Loading dashboard...</p>
                    </div>
                ) : (
                    <>
                        {/* Overview Stats */}
                        <div className="stats-grid stats-grid--large">
                            <div className="stat-card stat-card--featured">
                                <div className="stat-card__icon" style={{ backgroundColor: getScoreColor(overview?.health_score || 0) }}>
                                    <Heart size={24} />
                                </div>
                                <div className="stat-card__content">
                                    <span className="stat-card__label">Health Score</span>
                                    <span className="stat-card__value">{overview?.health_score || 0}</span>
                                </div>
                                <div className="stat-card__indicator" style={{ '--score-color': getScoreColor(overview?.health_score || 0) }}>
                                    <div className="score-bar" style={{ width: `${overview?.health_score || 0}%` }}></div>
                                </div>
                            </div>

                            <div className="stat-card">
                                <div className="stat-card__icon">
                                    <Server size={24} />
                                </div>
                                <div className="stat-card__content">
                                    <span className="stat-card__label">Services</span>
                                    <span className="stat-card__value">{overview?.total_services || 0}</span>
                                </div>
                            </div>

                            <div className="stat-card">
                                <div className="stat-card__icon">
                                    <BarChart3 size={24} />
                                </div>
                                <div className="stat-card__content">
                                    <span className="stat-card__label">Total Requests</span>
                                    <span className="stat-card__value">{overview?.total_requests?.toLocaleString() || 0}</span>
                                </div>
                            </div>

                            <div className="stat-card">
                                <div className="stat-card__icon">
                                    <Timer size={24} />
                                </div>
                                <div className="stat-card__content">
                                    <span className="stat-card__label">Avg Latency</span>
                                    <span className="stat-card__value">{overview?.avg_latency_ms?.toFixed(1) || 0}ms</span>
                                </div>
                            </div>

                            <div className="stat-card">
                                <div className="stat-card__icon" style={{ backgroundColor: overview?.error_rate > 0.05 ? 'var(--color-error)' : 'var(--color-yellow)' }}>
                                    <Percent size={24} />
                                </div>
                                <div className="stat-card__content">
                                    <span className="stat-card__label">Error Rate</span>
                                    <span className="stat-card__value">{((overview?.error_rate || 0) * 100).toFixed(2)}%</span>
                                </div>
                            </div>

                            <div className="stat-card">
                                <div className="stat-card__icon">
                                    <ArrowUpRight size={24} />
                                </div>
                                <div className="stat-card__content">
                                    <span className="stat-card__label">Uptime</span>
                                    <span className="stat-card__value">{overview?.uptime_percentage || 0}%</span>
                                </div>
                            </div>
                        </div>

                        {/* Alerts Row */}
                        {(overview?.critical_issues > 0 || overview?.warnings > 0 || overview?.active_incidents > 0) && (
                            <div className="alerts-row">
                                {overview?.critical_issues > 0 && (
                                    <div className="alert-badge alert-badge--critical">
                                        <AlertTriangle size={16} />
                                        <span>{overview.critical_issues} Critical Issue{overview.critical_issues > 1 ? 's' : ''}</span>
                                    </div>
                                )}
                                {overview?.warnings > 0 && (
                                    <div className="alert-badge alert-badge--warning">
                                        <AlertCircle size={16} />
                                        <span>{overview.warnings} Warning{overview.warnings > 1 ? 's' : ''}</span>
                                    </div>
                                )}
                                {overview?.active_incidents > 0 && (
                                    <div className="alert-badge alert-badge--incident">
                                        <Activity size={16} />
                                        <span>{overview.active_incidents} Active Incident{overview.active_incidents > 1 ? 's' : ''}</span>
                                    </div>
                                )}
                            </div>
                        )}

                        {/* Main Dashboard Grid */}
                        <div className="dashboard-grid">
                            {/* Trends Section */}
                            <div className="dashboard-panel trends-panel">
                                <div className="panel-header">
                                    <h2 className="section-title">Trends</h2>
                                    <div className="trend-selector">
                                        {[6, 12, 24, 48].map(hours => (
                                            <button
                                                key={hours}
                                                className={`trend-btn ${trendHours === hours ? 'trend-btn--active' : ''}`}
                                                onClick={() => setTrendHours(hours)}
                                            >
                                                {hours}h
                                            </button>
                                        ))}
                                    </div>
                                </div>

                                {trends?.data_points?.length > 0 ? (
                                    <div className="trends-content">
                                        <div className="trend-summary">
                                            <div className="trend-item">
                                                <div className="trend-item__header">
                                                    <Zap size={18} />
                                                    <span>Latency Trend</span>
                                                </div>
                                                <div className="trend-item__value">
                                                    {trends.summary?.latency_change > 0 ? (
                                                        <TrendingUp size={16} className="trend-up" />
                                                    ) : (
                                                        <TrendingDown size={16} className="trend-down" />
                                                    )}
                                                    {Math.abs(trends.summary?.latency_change || 0).toFixed(1)}%
                                                </div>
                                            </div>

                                            <div className="trend-item">
                                                <div className="trend-item__header">
                                                    <AlertTriangle size={18} />
                                                    <span>Error Trend</span>
                                                </div>
                                                <div className="trend-item__value">
                                                    {trends.summary?.error_change > 0 ? (
                                                        <TrendingUp size={16} className="trend-up" />
                                                    ) : (
                                                        <TrendingDown size={16} className="trend-down" />
                                                    )}
                                                    {Math.abs(trends.summary?.error_change || 0).toFixed(1)}%
                                                </div>
                                            </div>

                                            <div className="trend-item">
                                                <div className="trend-item__header">
                                                    <BarChart3 size={18} />
                                                    <span>Request Volume</span>
                                                </div>
                                                <div className="trend-item__value">
                                                    {trends.summary?.volume_change > 0 ? (
                                                        <TrendingUp size={16} className="trend-down" />
                                                    ) : (
                                                        <TrendingDown size={16} className="trend-up" />
                                                    )}
                                                    {Math.abs(trends.summary?.volume_change || 0).toFixed(1)}%
                                                </div>
                                            </div>
                                        </div>

                                        {/* Simple trend visualization */}
                                        <div className="trend-chart">
                                            <div className="trend-chart__bars">
                                                {trends.data_points.slice(-12).map((point, idx) => (
                                                    <div
                                                        key={idx}
                                                        className="trend-bar"
                                                        style={{
                                                            height: `${Math.min(100, (point.request_count / (trends.summary?.max_requests || 1)) * 100)}%`,
                                                            backgroundColor: point.error_rate > 0.05 ? 'var(--color-error)' : 'var(--color-yellow)'
                                                        }}
                                                        title={`${point.request_count} requests, ${(point.error_rate * 100).toFixed(1)}% errors`}
                                                    />
                                                ))}
                                            </div>
                                            <div className="trend-chart__labels">
                                                <span>Requests over last {trendHours}h</span>
                                            </div>
                                        </div>
                                    </div>
                                ) : (
                                    <div className="empty-state empty-state--small">
                                        <BarChart3 size={32} />
                                        <p>No trend data available</p>
                                    </div>
                                )}
                            </div>

                            {/* Services Panel */}
                            <div className="dashboard-panel services-panel">
                                <div className="panel-header">
                                    <h2 className="section-title">Services</h2>
                                    <Link href="/architecture" className="panel-link">View All →</Link>
                                </div>

                                {services?.length > 0 ? (
                                    <div className="services-list">
                                        {services.slice(0, 6).map((service, idx) => (
                                            <div key={idx} className="service-item">
                                                <div className="service-item__info">
                                                    {getHealthIcon(service.health_status)}
                                                    <span className="service-item__name">{service.name}</span>
                                                </div>
                                                <div className="service-item__stats">
                                                    <span>{service.call_count?.toLocaleString() || 0} calls</span>
                                                    <span>{service.avg_latency_ms?.toFixed(0) || 0}ms</span>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                ) : (
                                    <div className="empty-state empty-state--small">
                                        <Server size={32} />
                                        <p>No services discovered</p>
                                    </div>
                                )}
                            </div>

                            {/* Insights Panel */}
                            <div className="dashboard-panel insights-panel">
                                <div className="panel-header">
                                    <h2 className="section-title">
                                        <Lightbulb size={18} />
                                        AI Insights
                                    </h2>
                                </div>

                                {insights?.insights?.length > 0 ? (
                                    <div className="insights-list">
                                        {insights.insights.slice(0, 4).map((insight, idx) => (
                                            <div key={idx} className={`insight-item insight-item--${insight.priority || 'medium'}`}>
                                                <div className="insight-item__type">{insight.type}</div>
                                                <p className="insight-item__message">{insight.message}</p>
                                                {insight.action && (
                                                    <span className="insight-item__action">{insight.action}</span>
                                                )}
                                            </div>
                                        ))}
                                    </div>
                                ) : (
                                    <div className="empty-state empty-state--small">
                                        <Lightbulb size={32} />
                                        <p>No insights available</p>
                                    </div>
                                )}
                            </div>

                            {/* Recommendations Panel */}
                            <div className="dashboard-panel recommendations-panel">
                                <div className="panel-header">
                                    <h2 className="section-title">
                                        <Target size={18} />
                                        Recommendations
                                    </h2>
                                </div>

                                {recommendations?.recommendations ? (
                                    <div className="recommendations-content">
                                        <div className="rec-header">
                                            <span className="rec-type">{recommendations.recommendations.architecture_type}</span>
                                            <span className={`rec-risk rec-risk--${recommendations.recommendations.risk_assessment}`}>
                                                {recommendations.recommendations.risk_assessment} risk
                                            </span>
                                        </div>

                                        {recommendations.recommendations.patterns?.length > 0 && (
                                            <div className="rec-section">
                                                <h4>Recommended Patterns</h4>
                                                <div className="tag-list">
                                                    {recommendations.recommendations.patterns.map((pattern, idx) => (
                                                        <span key={idx} className="tag">{pattern}</span>
                                                    ))}
                                                </div>
                                            </div>
                                        )}

                                        {recommendations.recommendations.optimizations?.length > 0 && (
                                            <div className="rec-section">
                                                <h4>Optimizations</h4>
                                                <ul className="rec-list">
                                                    {recommendations.recommendations.optimizations.slice(0, 3).map((opt, idx) => (
                                                        <li key={idx}>{opt}</li>
                                                    ))}
                                                </ul>
                                            </div>
                                        )}

                                        <div className="rec-footer">
                                            <span>Priority: {recommendations.recommendations.priority}</span>
                                            <span>Effort: {recommendations.recommendations.estimated_effort}</span>
                                        </div>
                                    </div>
                                ) : (
                                    <div className="empty-state empty-state--small">
                                        <Target size={32} />
                                        <p>No recommendations available</p>
                                    </div>
                                )}
                            </div>

                            {/* Bottlenecks Panel */}
                            <div className="dashboard-panel bottlenecks-panel">
                                <div className="panel-header">
                                    <h2 className="section-title">
                                        <AlertTriangle size={18} />
                                        Bottlenecks
                                    </h2>
                                </div>

                                {bottlenecks?.bottlenecks?.length > 0 ? (
                                    <div className="bottlenecks-list">
                                        {bottlenecks.bottlenecks.map((bottleneck, idx) => (
                                            <div key={idx} className="bottleneck-item">
                                                <Server size={16} />
                                                <span>{bottleneck}</span>
                                            </div>
                                        ))}
                                        {bottlenecks.recommendations?.length > 0 && (
                                            <div className="bottleneck-recs">
                                                <h4>Recommendations:</h4>
                                                {bottlenecks.recommendations.map((rec, idx) => (
                                                    <p key={idx}>{rec}</p>
                                                ))}
                                            </div>
                                        )}
                                    </div>
                                ) : (
                                    <div className="no-issues">
                                        <CheckCircle size={32} />
                                        <p>No bottlenecks detected</p>
                                    </div>
                                )}
                            </div>

                            {/* Health Status Panel */}
                            <div className="dashboard-panel health-panel">
                                <div className="panel-header">
                                    <h2 className="section-title">
                                        <Activity size={18} />
                                        System Health
                                    </h2>
                                </div>

                                {health?.components ? (
                                    <div className="health-grid">
                                        {Object.entries(health.components).map(([name, status]) => (
                                            <div key={name} className="health-item">
                                                {getHealthIcon(status)}
                                                <span className="health-item__name">{name.replace(/_/g, ' ')}</span>
                                                <span className={`health-item__status health-item__status--${status}`}>
                                                    {status}
                                                </span>
                                            </div>
                                        ))}
                                    </div>
                                ) : (
                                    <div className="empty-state empty-state--small">
                                        <Activity size={32} />
                                        <p>No health data available</p>
                                    </div>
                                )}
                            </div>
                        </div>

                        {/* Last Updated */}
                        <div className="dashboard-footer">
                            <Clock size={14} />
                            <span>Last updated: {new Date(overview?.last_updated || Date.now()).toLocaleString()}</span>
                        </div>
                    </>
                )}
            </div>
        </div>
    );
}

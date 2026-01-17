'use client';

import { Boxes, RefreshCw, Layout, Link2, FileText, GitBranch } from 'lucide-react';

export default function Features() {
    const features = [
        {
            icon: Boxes,
            title: 'Visual Architecture',
            description: 'Drag-and-drop components to build system diagrams intuitively. From databases to APIs, visualize your entire infrastructure at a glance.'
        },
        {
            icon: RefreshCw,
            title: 'Real-time Collaboration',
            description: 'Design together with your team in real-time. Comment, annotate, and iterate on architectures simultaneously from anywhere in the world.'
        },
        {
            icon: Layout,
            title: 'Smart Templates',
            description: 'Start fast with 500+ battle-tested architecture templates. Microservices, event-driven, serverless — we\'ve got you covered.'
        },
        {
            icon: Link2,
            title: 'Auto-connections',
            description: 'Intelligent routing automatically draws clean connections between components. No more manual path adjustments — just focus on design.'
        },
        {
            icon: FileText,
            title: 'Documentation Export',
            description: 'Generate comprehensive architecture documentation automatically. Export to PDF, Markdown, or integrate directly with Confluence and Notion.'
        },
        {
            icon: GitBranch,
            title: 'Version Control',
            description: 'Track every change with built-in versioning. Compare revisions, rollback when needed, and maintain a complete history of your designs.'
        }
    ];

    return (
        <section className="features" id="features">
            <div className="features__header">
                <span className="tape-label">Core Capabilities</span>
                <h2 className="display-title display-md" style={{ marginTop: '1rem' }}>
                    ARCHITECT WITH CONFIDENCE
                </h2>
                <p style={{ color: 'var(--color-gray)', marginTop: '1rem', maxWidth: '600px', margin: '1rem auto 0' }}>
                    Everything you need to design, document, and share system architectures.
                    Built by engineers, for engineers who think in systems.
                </p>
            </div>

            <div className="features__grid">
                {features.map((feature, index) => {
                    const IconComponent = feature.icon;
                    return (
                        <div key={index} className="feature-card">
                            <div className="feature-card__icon">
                                <IconComponent size={40} strokeWidth={1.5} />
                            </div>
                            <h3 className="feature-card__title">{feature.title}</h3>
                            <p className="feature-card__description">{feature.description}</p>
                        </div>
                    );
                })}
            </div>
        </section>
    );
}

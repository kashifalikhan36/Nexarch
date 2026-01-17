'use client';

export default function CTASection() {
    return (
        <section className="cta-section halftone-bg">
            <div className="cta-section__content">
                <span className="tape-label">Free Forever Plan</span>

                <h2 className="cta-section__title display-title display-md" style={{ marginTop: '1.5rem' }}>
                    DESIGN YOUR FIRST<br />ARCHITECTURE TODAY
                </h2>

                <p className="cta-section__description">
                    Join 50,000+ engineers who trust NEXRCH for their system design needs.
                    Start with our free plan — no credit card required. Upgrade when
                    you're ready to scale.
                </p>

                <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
                    <button className="btn btn-primary" style={{ padding: '1rem 2rem', fontSize: '1rem' }}>
                        Start Designing Free
                    </button>
                    <button className="btn btn-secondary" style={{ padding: '1rem 2rem', fontSize: '1rem' }}>
                        Book a Demo
                    </button>
                </div>

                <p style={{
                    marginTop: '2rem',
                    fontSize: '0.75rem',
                    color: 'var(--color-gray-light)',
                    textTransform: 'uppercase',
                    letterSpacing: '0.1em'
                }}>
                    Unlimited diagrams • Real-time collaboration • Export anywhere
                </p>
            </div>
        </section>
    );
}

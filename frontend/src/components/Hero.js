'use client';

import Image from 'next/image';

export default function Hero() {
    return (
        <section className="hero">
            {/* Halftone decorations */}
            <div className="halftone-corner halftone-corner--top-right" />
            <div className="halftone-corner halftone-corner--bottom-left" />

            <div className="hero__content">
                {/* Text Content */}
                <div className="hero__text">
                    <div className="hero__badge">
                        <span className="tape-label">DESIGN SMARTER</span>
                        <span className="tape-label tape-label--rotated">v2.0</span>
                    </div>

                    <h1 className="hero__title display-title display-xl">
                        NEXRCH
                    </h1>

                    <p className="hero__subtitle">
                        Design, visualize, and iterate on complex system architectures
                        with ease. From microservices to distributed systems — bring your
                        architectural vision to life with our powerful diagramming and
                        collaboration platform.
                    </p>

                    <div className="hero__meta">
                        <div className="hero__meta-item">
                            <span className="hero__meta-label">Active Users</span>
                            <span className="hero__meta-value">50,000+</span>
                        </div>
                        <div className="hero__meta-item">
                            <span className="hero__meta-label">Diagrams Created</span>
                            <span className="hero__meta-value">2M+</span>
                        </div>
                        <div className="hero__meta-item">
                            <span className="hero__meta-label">Templates</span>
                            <span className="hero__meta-value">500+</span>
                        </div>
                    </div>

                    <div className="hero__actions">
                        <button className="btn btn-primary">Start Designing</button>
                        <button className="btn btn-secondary">View Examples</button>
                    </div>
                </div>

                {/* Cryptex Image */}
                <div className="hero__image-container">
                    <div className="hero__image-decoration" />
                    <Image
                        src="/cryptex-wheel.png"
                        alt="System architecture cipher wheel - visualizing complex systems"
                        width={600}
                        height={450}
                        className="hero__image"
                        priority
                    />
                </div>
            </div>

            {/* Partners Bar */}
            <div className="partners-bar">
                <div className="partners-bar__item">
                    <span className="partners-bar__logo">◈ NEXRCH</span>
                </div>
                <div className="partners-bar__item">
                    <span className="partners-bar__text">Trusted by engineers at</span>
                    <span className="partners-bar__highlight">Fortune 500</span>
                </div>
                <div className="partners-bar__item">
                    <span className="partners-bar__text">Architectures documented</span>
                    <span className="partners-bar__highlight">$2.5B+ Systems</span>
                </div>
                <div className="partners-bar__item">
                    <button className="btn btn-primary">Get Started Free</button>
                </div>
            </div>
        </section>
    );
}

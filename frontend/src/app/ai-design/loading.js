import { SkeletonCard, SkeletonBlock } from '@/components/Skeleton';

export default function AiDesignLoading() {
    return (
        <div className="dashboard-page">
            <div className="dashboard-content">
                <div className="dashboard-header">
                    <SkeletonBlock width="200px" height="32px" />
                </div>
                <SkeletonBlock width="100%" height="120px" style={{ marginTop: 24, borderRadius: 8 }} />
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 20, marginTop: 24 }}>
                    <SkeletonCard lines={7} />
                    <SkeletonCard lines={7} />
                </div>
            </div>
        </div>
    );
}

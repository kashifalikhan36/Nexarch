import { SkeletonCard, SkeletonBlock } from '@/components/Skeleton';

export default function WorkflowsLoading() {
    return (
        <div className="dashboard-page">
            <div className="dashboard-content">
                <div className="dashboard-header">
                    <SkeletonBlock width="220px" height="32px" />
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 20, marginTop: 24 }}>
                    <SkeletonCard lines={5} />
                    <SkeletonCard lines={5} />
                    <SkeletonCard lines={5} />
                </div>
            </div>
        </div>
    );
}

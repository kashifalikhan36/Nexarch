import { SkeletonMetricGrid, SkeletonCard, SkeletonBlock } from '@/components/Skeleton';

export default function ArchitectureLoading() {
    return (
        <div className="dashboard-page">
            <div className="dashboard-content">
                <div className="dashboard-header">
                    <SkeletonBlock width="240px" height="32px" />
                </div>
                <SkeletonMetricGrid cols={4} />
                {/* Graph canvas placeholder */}
                <SkeletonBlock width="100%" height="520px" style={{ marginTop: 24, borderRadius: 8 }} />
            </div>
        </div>
    );
}

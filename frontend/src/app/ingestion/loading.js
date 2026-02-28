import { SkeletonCard, SkeletonBlock, SkeletonTable } from '@/components/Skeleton';

export default function IngestionLoading() {
    return (
        <div className="dashboard-page">
            <div className="dashboard-content">
                <div className="dashboard-header">
                    <SkeletonBlock width="200px" height="32px" />
                </div>
                <SkeletonBlock width="100%" height="80px" style={{ marginTop: 24, borderRadius: 8 }} />
                <SkeletonTable rows={6} cols={5} style={{ marginTop: 24 }} />
            </div>
        </div>
    );
}

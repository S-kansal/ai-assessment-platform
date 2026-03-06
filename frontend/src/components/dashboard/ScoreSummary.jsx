export default function ScoreSummary({ capabilities, sampleSizes }) {
    if (!capabilities || Object.keys(capabilities).length === 0) {
        return (
            <div className="panel" style={{ opacity: 0.5 }}>
                <div className="panel-header">Capability Profile</div>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', fontStyle: 'italic' }}>No scores computed yet.</p>
            </div>
        );
    }

    return (
        <div className="panel animate-in">
            <div className="panel-header">Capability Profile</div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {Object.entries(capabilities).map(([cap, score]) => {
                    const samples = sampleSizes?.[cap] || 0;
                    const confidence = samples >= 3 ? 'high' : samples >= 2 ? 'medium' : 'low';
                    const confColor = confidence === 'high' ? 'var(--success)' : confidence === 'medium' ? 'var(--warning)' : 'var(--error)';
                    return (
                        <div key={cap}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.25rem' }}>
                                <span style={{ fontSize: '0.8rem', textTransform: 'capitalize' }}>{cap.replace(/_/g, ' ')}</span>
                                <span style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                                    <span style={{ fontSize: '0.65rem', color: confColor }}>{confidence}</span>
                                    <span style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--accent)' }}>{score}</span>
                                </span>
                            </div>
                            <div style={{ background: 'var(--bg-primary)', borderRadius: '999px', height: '6px', overflow: 'hidden' }}>
                                <div style={{
                                    width: `${score}%`, height: '100%',
                                    background: 'linear-gradient(90deg, #0ea5e9, #38bdf8)',
                                    borderRadius: '999px', transition: 'width 0.6s ease',
                                }} />
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}

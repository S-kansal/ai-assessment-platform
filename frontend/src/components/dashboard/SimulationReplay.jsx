export default function SimulationReplay({ events }) {
    // Filter simulation runs from telemetry
    const simEvents = (events || []).filter(
        (e) => e.event_type === 'simulation_run' || e.event_type === 'test_run'
    );

    if (simEvents.length === 0) {
        return (
            <div className="panel" style={{ opacity: 0.5 }}>
                <div className="panel-header">Simulation Replay</div>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', fontStyle: 'italic' }}>No simulation runs recorded.</p>
            </div>
        );
    }

    return (
        <div className="panel animate-in">
            <div className="panel-header">Simulation Replay</div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {simEvents.map((e, i) => (
                    <div key={i} className="chunk-card">
                        <div className="chunk-title">Run {i + 1}</div>
                        <div className="chunk-content">
                            {e.payload?.query && (
                                <div><strong style={{ color: 'var(--text-primary)' }}>Query:</strong> {e.payload.query}</div>
                            )}
                            {e.payload?.run_number && (
                                <div style={{ fontSize: '0.7rem', marginTop: '0.25rem', color: 'var(--text-secondary)' }}>
                                    Run #{e.payload.run_number}
                                </div>
                            )}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}

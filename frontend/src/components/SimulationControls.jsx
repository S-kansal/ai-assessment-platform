export default function SimulationControls({ onRun, loading, runCount }) {
    return (
        <div className="panel animate-in" style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <button
                id="run-simulation-btn"
                className="btn-primary"
                onClick={onRun}
                disabled={loading}
                style={{ minWidth: '160px' }}
            >
                {loading ? (
                    <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <span className="pulse-border" style={{ width: 12, height: 12, borderRadius: '50%', border: '2px solid currentColor' }} />
                        Running…
                    </span>
                ) : (
                    '▶ Run Simulation'
                )}
            </button>

            <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                Runs: <strong style={{ color: 'var(--accent)' }}>{runCount}</strong>
            </span>
        </div>
    );
}

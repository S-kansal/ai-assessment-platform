export default function SimulationOutput({ retrievedChunks, generatedAnswer }) {
    if (!generatedAnswer && (!retrievedChunks || retrievedChunks.length === 0)) {
        return (
            <div className="panel" style={{ opacity: 0.5 }}>
                <div className="panel-header">Simulation Output</div>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', fontStyle: 'italic' }}>
                    Run a simulation to see results here…
                </p>
            </div>
        );
    }

    return (
        <div className="panel animate-in">
            <div className="panel-header">Simulation Output</div>

            {/* Retrieved documents */}
            <div style={{ marginBottom: '1rem' }}>
                <h4 style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.5rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                    Retrieved Documents ({retrievedChunks?.length || 0})
                </h4>
                {retrievedChunks?.map((chunk, i) => (
                    <div key={i} className="chunk-card">
                        <div className="chunk-title">{chunk.id}: {chunk.title}</div>
                        <div className="chunk-content">{chunk.content}</div>
                    </div>
                ))}
            </div>

            {/* Generated answer */}
            <div>
                <h4 style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.5rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                    Generated Answer
                </h4>
                <div style={{
                    background: 'var(--bg-primary)',
                    border: '1px solid var(--border)',
                    borderRadius: '0.5rem',
                    padding: '0.75rem',
                    fontSize: '0.85rem',
                    lineHeight: 1.6,
                    color: 'var(--warning)',
                    fontFamily: "'JetBrains Mono', monospace",
                }}>
                    {generatedAnswer}
                </div>
            </div>
        </div>
    );
}

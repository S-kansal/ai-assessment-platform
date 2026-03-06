const EVENT_COLORS = {
    query_change: '#38bdf8',
    simulation_run: '#fbbf24',
    prompt_edit: '#a78bfa',
    retrieval_inspection: '#34d399',
    solution_submit: '#f87171',
    test_run: '#fbbf24',
};

const EVENT_ICONS = {
    query_change: '🔍',
    simulation_run: '▶',
    prompt_edit: '✏️',
    retrieval_inspection: '📄',
    solution_submit: '✅',
    test_run: '▶',
};

export default function TelemetryTimeline({ events, onEventClick }) {
    if (!events || events.length === 0) {
        return (
            <div className="panel" style={{ opacity: 0.5 }}>
                <div className="panel-header">Telemetry Timeline</div>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', fontStyle: 'italic' }}>No telemetry data.</p>
            </div>
        );
    }

    // Compute relative timestamps
    const firstTs = events[0]?.timestamp ? new Date(events[0].timestamp).getTime() : 0;

    return (
        <div className="panel animate-in">
            <div className="panel-header">Telemetry Timeline</div>

            {/* Visual bar */}
            <div style={{
                display: 'flex', gap: '2px', marginBottom: '1rem', padding: '0.5rem 0',
                borderBottom: '1px solid var(--border)',
            }}>
                {events.map((e, i) => (
                    <div
                        key={i}
                        title={`${e.event_type}`}
                        style={{
                            flex: 1, height: '8px', borderRadius: '2px',
                            background: EVENT_COLORS[e.event_type] || 'var(--border)',
                            cursor: 'pointer', transition: 'transform 0.15s',
                        }}
                        onClick={() => onEventClick?.(e, i)}
                        onMouseEnter={(ev) => { ev.currentTarget.style.transform = 'scaleY(2)'; }}
                        onMouseLeave={(ev) => { ev.currentTarget.style.transform = 'scaleY(1)'; }}
                    />
                ))}
            </div>

            {/* Event list */}
            <div style={{ maxHeight: '300px', overflowY: 'auto' }}>
                {events.map((e, i) => {
                    const ts = e.timestamp ? new Date(e.timestamp).getTime() : 0;
                    const delta = firstTs ? Math.round((ts - firstTs) / 1000) : 0;
                    const mins = Math.floor(delta / 60);
                    const secs = delta % 60;

                    return (
                        <div
                            key={i}
                            className="table-row"
                            style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '0.4rem 0.25rem', cursor: 'pointer' }}
                            onClick={() => onEventClick?.(e, i)}
                        >
                            <span style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', fontFamily: "'JetBrains Mono', monospace", width: '50px' }}>
                                {String(mins).padStart(2, '0')}:{String(secs).padStart(2, '0')}
                            </span>
                            <span style={{ fontSize: '0.9rem' }}>{EVENT_ICONS[e.event_type] || '•'}</span>
                            <span style={{
                                fontSize: '0.78rem', fontWeight: 600,
                                color: EVENT_COLORS[e.event_type] || 'var(--text-primary)',
                            }}>
                                {e.event_type.replace(/_/g, ' ')}
                            </span>
                        </div>
                    );
                })}
            </div>

            {/* Legend */}
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginTop: '0.75rem', paddingTop: '0.5rem', borderTop: '1px solid var(--border)' }}>
                {Object.entries(EVENT_COLORS).map(([type, color]) => (
                    <span key={type} style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', fontSize: '0.65rem', color: 'var(--text-secondary)' }}>
                        <span style={{ width: 8, height: 8, borderRadius: 2, background: color, display: 'inline-block' }} />
                        {type.replace(/_/g, ' ')}
                    </span>
                ))}
            </div>
        </div>
    );
}

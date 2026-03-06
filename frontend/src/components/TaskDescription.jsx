export default function TaskDescription({ description, taskId, status }) {
    return (
        <div className="panel animate-in">
            <div className="panel-header">Task Briefing</div>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
                <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
                    {taskId || '—'}
                </span>
                {status && (
                    <span className={`status-badge ${status === 'completed' ? 'status-completed' : 'status-running'}`}>
                        <span style={{ width: 6, height: 6, borderRadius: '50%', background: 'currentColor', display: 'inline-block' }} />
                        {status}
                    </span>
                )}
            </div>

            <p style={{ fontSize: '0.9rem', lineHeight: 1.6, color: 'var(--text-primary)' }}>
                {description || 'Loading task information…'}
            </p>
        </div>
    );
}

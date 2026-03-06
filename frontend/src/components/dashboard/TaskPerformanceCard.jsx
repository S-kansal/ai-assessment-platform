export default function TaskPerformanceCard({ tasks }) {
    if (!tasks || tasks.length === 0) {
        return (
            <div className="panel" style={{ opacity: 0.5 }}>
                <div className="panel-header">Task Performance</div>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', fontStyle: 'italic' }}>No task data.</p>
            </div>
        );
    }

    return (
        <div className="panel animate-in">
            <div className="panel-header">Task Performance</div>
            <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                    <thead>
                        <tr style={{ borderBottom: '1px solid var(--border)' }}>
                            <th className="table-th">Task</th>
                            <th className="table-th">Score</th>
                            <th className="table-th">Diagnostic</th>
                            <th className="table-th">Success</th>
                            <th className="table-th">Efficiency</th>
                            <th className="table-th">Iteration</th>
                            <th className="table-th">Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {tasks.map((t) => (
                            <tr key={t.task_run_id} className="table-row">
                                <td className="table-td" style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: '0.8rem' }}>{t.task_id}</td>
                                <td className="table-td">
                                    <span style={{ fontWeight: 700, color: (t.task_score ?? 0) >= 80 ? 'var(--success)' : (t.task_score ?? 0) >= 60 ? 'var(--warning)' : 'var(--error)' }}>
                                        {t.task_score ?? '—'}
                                    </span>
                                </td>
                                <td className="table-td score-cell">{t.diagnostic_score?.toFixed(1) ?? '—'}</td>
                                <td className="table-td score-cell">{t.success_score?.toFixed(1) ?? '—'}</td>
                                <td className="table-td score-cell">{t.efficiency_score?.toFixed(1) ?? '—'}</td>
                                <td className="table-td score-cell">{t.iteration_score?.toFixed(1) ?? '—'}</td>
                                <td className="table-td">
                                    <span className={`status-badge ${t.status === 'completed' ? 'status-completed' : 'status-running'}`}>{t.status}</span>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}

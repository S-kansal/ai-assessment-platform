import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import TaskPerformanceCard from '../components/dashboard/TaskPerformanceCard';
import { getCandidateTasks } from '../services/api';

export default function TaskAnalytics() {
    const { candidateId } = useParams();
    const navigate = useNavigate();
    const [tasks, setTasks] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        getCandidateTasks(candidateId)
            .then(setTasks)
            .catch(() => { })
            .finally(() => setLoading(false));
    }, [candidateId]);

    // Compute averages
    const completed = tasks.filter((t) => t.task_score != null);
    const avgDiag = completed.length ? (completed.reduce((s, t) => s + (t.diagnostic_score || 0), 0) / completed.length).toFixed(2) : '—';
    const avgEff = completed.length ? (completed.reduce((s, t) => s + (t.efficiency_score || 0), 0) / completed.length).toFixed(2) : '—';
    const avgIter = completed.length ? (completed.reduce((s, t) => s + (t.iteration_score || 0), 0) / completed.length).toFixed(2) : '—';

    return (
        <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '1.5rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                <h1 style={{ fontSize: '1.3rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                    📈 Task Analytics
                </h1>
                <button className="btn-primary" onClick={() => navigate(-1)} style={{ fontSize: '0.8rem', padding: '0.45rem 1rem' }}>
                    ← Back
                </button>
            </div>

            {/* Averages */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem', marginBottom: '1.5rem' }}>
                {[
                    { label: 'Avg Diagnostic', value: avgDiag },
                    { label: 'Avg Efficiency', value: avgEff },
                    { label: 'Avg Iteration', value: avgIter },
                ].map(({ label, value }) => (
                    <div key={label} className="panel animate-in" style={{ textAlign: 'center' }}>
                        <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--accent)' }}>{value}</div>
                        <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', textTransform: 'uppercase', marginTop: '0.25rem' }}>{label}</div>
                    </div>
                ))}
            </div>

            {loading ? (
                <div className="panel"><p style={{ textAlign: 'center', color: 'var(--text-secondary)' }}>Loading…</p></div>
            ) : (
                <TaskPerformanceCard tasks={tasks} />
            )}
        </div>
    );
}

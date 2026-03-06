import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import ScoreSummary from '../components/dashboard/ScoreSummary';
import CapabilityRadar from '../components/dashboard/CapabilityRadar';
import TaskPerformanceCard from '../components/dashboard/TaskPerformanceCard';
import { getCandidateProfile, getCandidateTasks, getTaskRunTelemetry } from '../services/api';

export default function CandidateReport() {
    const { candidateId } = useParams();
    const navigate = useNavigate();
    const [profile, setProfile] = useState(null);
    const [tasks, setTasks] = useState([]);
    const [telemetrySummary, setTelemetrySummary] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function load() {
            try {
                const [prof, taskList] = await Promise.all([
                    getCandidateProfile(candidateId),
                    getCandidateTasks(candidateId),
                ]);
                setProfile(prof);
                setTasks(taskList);

                // Build telemetry summary from first completed task run
                const completedTask = taskList.find((t) => t.status === 'completed');
                if (completedTask) {
                    try {
                        const events = await getTaskRunTelemetry(completedTask.task_run_id);
                        const summary = {
                            simulation_runs: events.filter((e) => e.event_type === 'simulation_run' || e.event_type === 'test_run').length,
                            prompt_edits: events.filter((e) => e.event_type === 'prompt_edit').length,
                            retrieval_inspections: events.filter((e) => e.event_type === 'retrieval_inspection').length,
                            total_events: events.length,
                        };
                        setTelemetrySummary(summary);
                    } catch { /* ignore */ }
                }
            } catch { /* ignore */ }
            setLoading(false);
        }
        load();
    }, [candidateId]);

    if (loading) {
        return (
            <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '1.5rem' }}>
                <div className="panel"><p style={{ textAlign: 'center', color: 'var(--text-secondary)' }}>Loading report…</p></div>
            </div>
        );
    }

    return (
        <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '1.5rem' }}>
            {/* Header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                <div>
                    <h1 style={{ fontSize: '1.3rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                        {profile?.name || 'Candidate'}
                    </h1>
                    <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{profile?.email}</p>
                </div>
                <div style={{ display: 'flex', gap: '0.5rem' }}>
                    <button className="btn-primary" onClick={() => navigate('/dashboard')} style={{ fontSize: '0.8rem', padding: '0.45rem 1rem' }}>
                        ← Dashboard
                    </button>
                    {tasks.find((t) => t.status === 'completed') && (
                        <button
                            className="btn-primary"
                            onClick={() => navigate(`/dashboard/candidate/${candidateId}/session/${tasks[0]?.task_run_id}`)}
                            style={{ fontSize: '0.8rem', padding: '0.45rem 1rem', background: 'linear-gradient(135deg, #7c3aed, #a78bfa)' }}
                        >
                            🔄 Session Replay
                        </button>
                    )}
                </div>
            </div>

            {/* Capability section */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
                <ScoreSummary capabilities={profile?.capabilities} sampleSizes={profile?.sample_sizes} />
                <CapabilityRadar capabilities={profile?.capabilities} />
            </div>

            {/* Task performance */}
            <div style={{ marginBottom: '1rem' }}>
                <TaskPerformanceCard tasks={tasks} />
            </div>

            {/* Telemetry summary */}
            {telemetrySummary && (
                <div className="panel animate-in">
                    <div className="panel-header">Telemetry Summary</div>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '0.75rem' }}>
                        {[
                            { label: 'Simulation Runs', value: telemetrySummary.simulation_runs },
                            { label: 'Prompt Edits', value: telemetrySummary.prompt_edits },
                            { label: 'Retrieval Inspections', value: telemetrySummary.retrieval_inspections },
                            { label: 'Total Events', value: telemetrySummary.total_events },
                        ].map(({ label, value }) => (
                            <div key={label} style={{
                                background: 'var(--bg-primary)', borderRadius: '0.5rem',
                                padding: '1rem', textAlign: 'center', border: '1px solid var(--border)',
                            }}>
                                <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--accent)' }}>{value}</div>
                                <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', marginTop: '0.25rem', textTransform: 'uppercase' }}>
                                    {label}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}

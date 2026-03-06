import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import TelemetryTimeline from '../components/dashboard/TelemetryTimeline';
import SimulationReplay from '../components/dashboard/SimulationReplay';
import { getTaskRunTelemetry } from '../services/api';

export default function SessionReplay() {
    const { taskRunId } = useParams();
    const navigate = useNavigate();
    const [events, setEvents] = useState([]);
    const [selectedEvent, setSelectedEvent] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        getTaskRunTelemetry(taskRunId)
            .then(setEvents)
            .catch(() => { })
            .finally(() => setLoading(false));
    }, [taskRunId]);

    function handleEventClick(event, idx) {
        setSelectedEvent({ ...event, index: idx });
    }

    if (loading) {
        return (
            <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '1.5rem' }}>
                <div className="panel"><p style={{ textAlign: 'center', color: 'var(--text-secondary)' }}>Loading replay…</p></div>
            </div>
        );
    }

    return (
        <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '1.5rem' }}>
            {/* Header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                <h1 style={{ fontSize: '1.3rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                    🔄 Session Replay
                </h1>
                <button className="btn-primary" onClick={() => navigate(-1)} style={{ fontSize: '0.8rem', padding: '0.45rem 1rem' }}>
                    ← Back
                </button>
            </div>

            <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '1rem' }}>
                Task Run: <code style={{ color: 'var(--accent)' }}>{taskRunId}</code> — {events.length} events captured
            </p>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                <TelemetryTimeline events={events} onEventClick={handleEventClick} />
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                    <SimulationReplay events={events} />

                    {/* Event detail pane */}
                    {selectedEvent && (
                        <div className="panel animate-in">
                            <div className="panel-header">Event Detail</div>
                            <div style={{ fontSize: '0.8rem' }}>
                                <div style={{ marginBottom: '0.5rem' }}>
                                    <strong style={{ color: 'var(--accent)' }}>Type: </strong>
                                    {selectedEvent.event_type}
                                </div>
                                <div style={{ marginBottom: '0.5rem' }}>
                                    <strong style={{ color: 'var(--accent)' }}>Time: </strong>
                                    {selectedEvent.timestamp ? new Date(selectedEvent.timestamp).toLocaleTimeString() : '—'}
                                </div>
                                <pre style={{
                                    background: 'var(--bg-primary)', border: '1px solid var(--border)',
                                    borderRadius: '0.5rem', padding: '0.75rem',
                                    fontSize: '0.75rem', color: 'var(--text-secondary)',
                                    overflow: 'auto', maxHeight: '200px',
                                    fontFamily: "'JetBrains Mono', monospace",
                                }}>
                                    {JSON.stringify(selectedEvent.payload, null, 2)}
                                </pre>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

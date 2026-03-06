import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, Tooltip } from 'recharts';

export default function CapabilityRadar({ capabilities }) {
    if (!capabilities || Object.keys(capabilities).length === 0) {
        return (
            <div className="panel" style={{ opacity: 0.5 }}>
                <div className="panel-header">Capability Radar</div>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', fontStyle: 'italic' }}>No data available.</p>
            </div>
        );
    }

    const data = Object.entries(capabilities).map(([cap, score]) => ({
        capability: cap.replace(/_/g, ' '),
        score,
        fullMark: 100,
    }));

    return (
        <div className="panel animate-in">
            <div className="panel-header">Capability Radar</div>
            <ResponsiveContainer width="100%" height={280}>
                <RadarChart outerRadius="70%" data={data}>
                    <PolarGrid stroke="var(--border)" />
                    <PolarAngleAxis dataKey="capability" tick={{ fill: 'var(--text-secondary)', fontSize: 11 }} />
                    <PolarRadiusAxis angle={90} domain={[0, 100]} tick={{ fill: 'var(--text-secondary)', fontSize: 10 }} />
                    <Tooltip
                        contentStyle={{ background: 'var(--bg-surface)', border: '1px solid var(--border)', borderRadius: '0.5rem', fontSize: '0.8rem' }}
                        labelStyle={{ color: 'var(--accent)' }}
                    />
                    <Radar name="Score" dataKey="score" stroke="#38bdf8" fill="#38bdf8" fillOpacity={0.25} strokeWidth={2} />
                </RadarChart>
            </ResponsiveContainer>
        </div>
    );
}

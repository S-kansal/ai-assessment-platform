import { useEffect, useState } from 'react';

import Panel from '../components/Panel.jsx';
import { useAuth } from '../context/useAuth.js';
import {
  createCandidate,
  getDashboardCandidateProfile,
  getDashboardCandidates,
  getDashboardTaskRuns,
  getReplay,
} from '../services/api.js';

export default function DashboardPage() {
  const { logout, user } = useAuth();
  const [candidates, setCandidates] = useState([]);
  const [selectedCandidateId, setSelectedCandidateId] = useState('');
  const [profile, setProfile] = useState(null);
  const [taskRuns, setTaskRuns] = useState([]);
  const [replay, setReplay] = useState(null);
  const [candidateForm, setCandidateForm] = useState({ name: '', email: '', password: '' });
  const [error, setError] = useState('');

  useEffect(() => {
    async function loadCandidates() {
      try {
        const rows = await getDashboardCandidates();
        setCandidates(rows);
        if (rows[0]) {
          setSelectedCandidateId(rows[0].id);
        }
      } catch (requestError) {
        setError(requestError.response?.data?.error?.message || 'Unable to load candidates');
      }
    }
    loadCandidates();
  }, []);

  useEffect(() => {
    if (!selectedCandidateId) {
      return;
    }
    async function loadCandidate() {
      try {
        const [candidateProfile, candidateTaskRuns] = await Promise.all([
          getDashboardCandidateProfile(selectedCandidateId),
          getDashboardTaskRuns(selectedCandidateId),
        ]);
        setProfile(candidateProfile);
        setTaskRuns(candidateTaskRuns);
        if (candidateTaskRuns[0]?.task_run?.id) {
          const replayData = await getReplay(candidateTaskRuns[0].task_run.id);
          setReplay(replayData);
        } else {
          setReplay(null);
        }
      } catch (requestError) {
        setError(requestError.response?.data?.error?.message || 'Unable to load candidate details');
      }
    }
    loadCandidate();
  }, [selectedCandidateId]);

  async function handleCreateCandidate(event) {
    event.preventDefault();
    try {
      await createCandidate(candidateForm);
      setCandidateForm({ name: '', email: '', password: '' });
      const rows = await getDashboardCandidates();
      setCandidates(rows);
    } catch (requestError) {
      setError(requestError.response?.data?.error?.message || 'Unable to create candidate');
    }
  }

  return (
    <main className="page">
      <header className="page-header">
        <div>
          <p className="eyebrow">Reviewer Dashboard</p>
          <h1>Assessment Review</h1>
        </div>
        <button className="secondary-button" onClick={logout}>
          Logout
        </button>
      </header>

      {error ? <p className="error-banner">{error}</p> : null}

      <div className="dashboard-grid">
        {user.role === 'admin' ? (
          <Panel title="Create Candidate">
            <form className="stack" onSubmit={handleCreateCandidate}>
              <input
                value={candidateForm.name}
                onChange={(event) => setCandidateForm({ ...candidateForm, name: event.target.value })}
                placeholder="Candidate name"
              />
              <input
                value={candidateForm.email}
                onChange={(event) => setCandidateForm({ ...candidateForm, email: event.target.value })}
                placeholder="candidate@company.com"
                type="email"
                autoComplete="username"
              />
              <input
                value={candidateForm.password}
                onChange={(event) => setCandidateForm({ ...candidateForm, password: event.target.value })}
                placeholder="temporary password"
                type="password"
                autoComplete="new-password"
              />
              <button className="primary-button" type="submit">
                Add Candidate
              </button>
            </form>
          </Panel>
        ) : null}

        <Panel title="Candidates">
          <div className="stack">
            {candidates.map((candidate) => (
              <button
                key={candidate.id}
                className={`list-button ${candidate.id === selectedCandidateId ? 'selected' : ''}`}
                onClick={() => setSelectedCandidateId(candidate.id)}
              >
                <span>{candidate.name}</span>
                <span>{candidate.email}</span>
              </button>
            ))}
          </div>
        </Panel>

        <Panel title="Capability Profile">
          {profile?.score ? (
            <div className="stack">
              <p>Aggregate score: <strong>{profile.score.aggregate_score}</strong></p>
              <pre>{JSON.stringify(profile.score.raw_scores, null, 2)}</pre>
            </div>
          ) : (
            <p>No scoring result available yet.</p>
          )}
        </Panel>

        <Panel title="Task Runs">
          <div className="stack">
            {taskRuns.map((row) => (
              <div key={row.task_run.id} className="data-card">
                <p><strong>{row.task_run.task_id}</strong></p>
                <p>Status: {row.task_run.status}</p>
                <p>Total score: {row.evaluation?.total_score ?? 'pending'}</p>
              </div>
            ))}
          </div>
        </Panel>

        <Panel title="Session Replay">
          {replay ? (
            <div className="stack">
              <p><strong>Telemetry Events</strong></p>
              <pre>{JSON.stringify(replay.events, null, 2)}</pre>
              <p><strong>Simulation Runs</strong></p>
              <pre>{JSON.stringify(replay.simulation_runs, null, 2)}</pre>
            </div>
          ) : (
            <p>No replay data available.</p>
          )}
        </Panel>
      </div>
    </main>
  );
}

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
  const [selectedTaskRunId, setSelectedTaskRunId] = useState(null);
  const [profile, setProfile] = useState(null);
  const [taskRuns, setTaskRuns] = useState([]);
  const [replay, setReplay] = useState(null);
  const [candidateForm, setCandidateForm] = useState({ name: '', email: '', password: '' });
  const [error, setError] = useState('');

  function sortTaskRuns(rows) {
    return [...rows].sort((left, right) => {
      const leftPriority = Number(Boolean(left.evaluation || left.latest_simulation));
      const rightPriority = Number(Boolean(right.evaluation || right.latest_simulation));
      if (leftPriority !== rightPriority) {
        return rightPriority - leftPriority;
      }
      return new Date(right.task_run.started_at).getTime() - new Date(left.task_run.started_at).getTime();
    });
  }

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
        const sortedTaskRuns = sortTaskRuns(candidateTaskRuns);
        setProfile(candidateProfile);
        setTaskRuns(sortedTaskRuns);
        const firstTaskRunId = sortedTaskRuns[0]?.task_run?.id ?? null;
        setSelectedTaskRunId((currentTaskRunId) => {
          if (currentTaskRunId && sortedTaskRuns.some((row) => row.task_run.id === currentTaskRunId)) {
            return currentTaskRunId;
          }
          return firstTaskRunId;
        });
        if (!firstTaskRunId) {
          setReplay(null);
        } else {
          const replayData = await getReplay(firstTaskRunId);
          setReplay(replayData);
        }
      } catch (requestError) {
        setError(requestError.response?.data?.error?.message || 'Unable to load candidate details');
      }
    }
    loadCandidate();
  }, [selectedCandidateId]);

  useEffect(() => {
    if (!selectedTaskRunId) {
      return;
    }

    async function loadReplay() {
      try {
        const replayData = await getReplay(selectedTaskRunId);
        setReplay(replayData);
      } catch (requestError) {
        setError(requestError.response?.data?.error?.message || 'Unable to load session replay');
      }
    }

    loadReplay();
  }, [selectedTaskRunId]);

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

  const selectedTaskRun = taskRuns.find((row) => row.task_run.id === selectedTaskRunId) ?? null;

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
              {Object.entries(profile.score.raw_scores).map(([capability, score]) => (
                <p key={capability}>
                  {capability}: <strong>{score}</strong>
                </p>
              ))}
            </div>
          ) : (
            <p>No scoring result available yet.</p>
          )}
        </Panel>

        <Panel title="Assessments">
          {profile?.assessments?.length ? (
            <div className="stack">
              {profile.assessments.map((assessment) => (
                <div key={assessment.id} className="data-card">
                  <p><strong>{assessment.title}</strong></p>
                  <p>Status: {assessment.status}</p>
                  <p>Tasks: {assessment.task_ids.length}</p>
                </div>
              ))}
            </div>
          ) : (
            <p>No assessments available yet.</p>
          )}
        </Panel>

        <Panel title="Task Runs">
          <div className="stack">
            {taskRuns.map((row) => (
              <button
                key={row.task_run.id}
                className={`data-card ${row.task_run.id === selectedTaskRunId ? 'selected' : ''}`}
                onClick={() => setSelectedTaskRunId(row.task_run.id)}
                style={{
                  textAlign: 'left',
                  border: row.task_run.id === selectedTaskRunId ? '2px solid #38bdf8' : undefined,
                  background: row.task_run.id === selectedTaskRunId ? 'rgba(56, 189, 248, 0.08)' : undefined,
                  cursor: 'pointer',
                }}
                type="button"
              >
                <p><strong>{row.task_run.task_id}</strong></p>
                <p>Status: {row.task_run.status}</p>
                <p>Total score: {row.evaluation?.total_score ?? 'pending'}</p>
              </button>
            ))}
          </div>
        </Panel>

        <Panel title="Session Replay">
          {replay ? (
            <div className="stack">
              <p>
                <strong>Currently Replaying:</strong>{' '}
                {selectedTaskRun ? `${selectedTaskRun.task_run.task_id} (${selectedTaskRun.task_run.status})` : 'No task run selected'}
              </p>
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

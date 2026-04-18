import { useEffect, useState } from 'react';

import CreateCandidateModal from '../components/CreateCandidateModal.jsx';
import Panel from '../components/Panel.jsx';
import StartAssessmentModal from '../components/StartAssessmentModal.jsx';
import { useAuth } from '../context/useAuth.js';
import {
  getDashboardCandidateProfile,
  getDashboardCandidates,
  getDashboardTaskRuns,
  getReplay,
} from '../services/api.js';

const STATUS_META = {
  no_assessment: { label: 'No Assessment', className: 'status-badge status-neutral' },
  active: { label: 'Active', className: 'status-badge status-active' },
  completed: { label: 'Completed', className: 'status-badge status-completed' },
  timed_out: { label: 'Timed Out', className: 'status-badge status-timed-out' },
  unknown: { label: 'Unknown', className: 'status-badge status-neutral' },
};

function normalizeAssessmentStatus(status) {
  switch (status) {
    case 'active':
    case 'started':
    case 'created':
      return 'active';
    case 'completed':
      return 'completed';
    case 'timed_out':
      return 'timed_out';
    default:
      return 'unknown';
  }
}

function deriveAssessmentStatus(assessments) {
  if (!assessments?.length) {
    return 'no_assessment';
  }

  const normalizedStatuses = assessments.map((assessment) => normalizeAssessmentStatus(assessment.status));

  if (normalizedStatuses.includes('active')) {
    return 'active';
  }
  if (normalizedStatuses.includes('timed_out')) {
    return 'timed_out';
  }
  if (normalizedStatuses.includes('completed')) {
    return 'completed';
  }

  return normalizedStatuses[0] ?? 'unknown';
}

function StatusBadge({ status }) {
  const meta = STATUS_META[status] ?? STATUS_META.unknown;
  return <span className={meta.className}>{meta.label}</span>;
}

export default function DashboardPage() {
  const { logout, user } = useAuth();
  const [candidates, setCandidates] = useState([]);
  const [selectedCandidateId, setSelectedCandidateId] = useState('');
  const [selectedTaskRunId, setSelectedTaskRunId] = useState(null);
  const [profile, setProfile] = useState(null);
  const [taskRuns, setTaskRuns] = useState([]);
  const [replay, setReplay] = useState(null);
  const [candidateStatuses, setCandidateStatuses] = useState({});
  const [isCreateCandidateModalOpen, setIsCreateCandidateModalOpen] = useState(false);
  const [isStartAssessmentModalOpen, setIsStartAssessmentModalOpen] = useState(false);
  const [isCandidatesLoading, setIsCandidatesLoading] = useState(false);
  const [isProfileLoading, setIsProfileLoading] = useState(false);
  const [isReplayLoading, setIsReplayLoading] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');
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

  async function hydrateCandidateStatuses(rows) {
    const statuses = await Promise.all(
      rows.map(async (candidate) => {
        try {
          const candidateProfile = await getDashboardCandidateProfile(candidate.id);
          return [candidate.id, deriveAssessmentStatus(candidateProfile.assessments)];
        } catch {
          return [candidate.id, null];
        }
      })
    );

    setCandidateStatuses((current) => ({
      ...current,
      ...Object.fromEntries(statuses.filter(([, status]) => Boolean(status))),
    }));
  }

  useEffect(() => {
    async function loadCandidates() {
      setIsCandidatesLoading(true);
      setError('');
      try {
        const rows = await getDashboardCandidates();
        setCandidates(rows);
        if (rows[0]) {
          setSelectedCandidateId(rows[0].id);
        }
        hydrateCandidateStatuses(rows);
      } catch (requestError) {
        setError(requestError.message || requestError.response?.data?.error?.message || 'Unable to load candidates');
      } finally {
        setIsCandidatesLoading(false);
      }
    }
    loadCandidates();
  }, []);

  useEffect(() => {
    if (!selectedCandidateId) {
      setProfile(null);
      setTaskRuns([]);
      setSelectedTaskRunId(null);
      setReplay(null);
      return;
    }
    async function loadCandidate() {
      setIsProfileLoading(true);
      setError('');
      try {
        const [candidateProfile, candidateTaskRuns] = await Promise.all([
          getDashboardCandidateProfile(selectedCandidateId),
          getDashboardTaskRuns(selectedCandidateId),
        ]);
        const sortedTaskRuns = sortTaskRuns(candidateTaskRuns);
        setProfile(candidateProfile);
        setTaskRuns(sortedTaskRuns);
        setCandidateStatuses((current) => ({
          ...current,
          [selectedCandidateId]: deriveAssessmentStatus(candidateProfile.assessments),
        }));
        const firstTaskRunId = sortedTaskRuns[0]?.task_run?.id ?? null;
        setSelectedTaskRunId((currentTaskRunId) => {
          if (currentTaskRunId && sortedTaskRuns.some((row) => row.task_run.id === currentTaskRunId)) {
            return currentTaskRunId;
          }
          return firstTaskRunId;
        });
        if (!firstTaskRunId) {
          setReplay(null);
        }
      } catch (requestError) {
        setError(requestError.message || requestError.response?.data?.error?.message || 'Unable to load candidate details');
      } finally {
        setIsProfileLoading(false);
      }
    }
    loadCandidate();
  }, [selectedCandidateId]);

  useEffect(() => {
    if (!selectedTaskRunId) {
      setReplay(null);
      return;
    }

    async function loadReplay() {
      setIsReplayLoading(true);
      setError('');
      try {
        const replayData = await getReplay(selectedTaskRunId);
        setReplay(replayData);
      } catch (requestError) {
        setError(requestError.message || requestError.response?.data?.error?.message || 'Unable to load session replay');
      } finally {
        setIsReplayLoading(false);
      }
    }

    loadReplay();
  }, [selectedTaskRunId]);

  const selectedTaskRun = taskRuns.find((row) => row.task_run.id === selectedTaskRunId) ?? null;
  const selectedCandidateStatus = selectedCandidateId ? candidateStatuses[selectedCandidateId] ?? deriveAssessmentStatus(profile?.assessments) : 'unknown';

  function handleCandidateCreated(newCandidate) {
    setCandidates((current) => [newCandidate, ...current.filter((candidate) => candidate.id !== newCandidate.id)]);
    setCandidateStatuses((current) => ({ ...current, [newCandidate.id]: 'no_assessment' }));
    setSelectedCandidateId(newCandidate.id);
    setSuccessMessage(`Candidate ${newCandidate.name} was created successfully.`);
    setError('');
  }

  function handleAssessmentStarted({ assessmentId, taskRunId, title }) {
    setProfile((current) => {
      if (!current) {
        return current;
      }
      return {
        ...current,
        assessments: [
          { id: assessmentId, title, status: 'active', task_ids: [] },
          ...(current.assessments ?? []),
        ],
      };
    });
    setCandidateStatuses((current) => ({ ...current, [selectedCandidateId]: 'active' }));
    setSelectedTaskRunId(taskRunId ?? null);
    setSuccessMessage(`Assessment "${title}" is now active.`);
    setError('');
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
      {successMessage ? <p className="success-banner">{successMessage}</p> : null}

      <CreateCandidateModal
        isOpen={isCreateCandidateModalOpen}
        onClose={() => setIsCreateCandidateModalOpen(false)}
        onSuccess={handleCandidateCreated}
      />
      <StartAssessmentModal
        candidate={profile?.candidate ?? null}
        isOpen={isStartAssessmentModalOpen}
        onClose={() => setIsStartAssessmentModalOpen(false)}
        onSuccess={handleAssessmentStarted}
      />

      <div className="dashboard-grid">
        <Panel
          title="Candidates"
          actions={
            user.role === 'admin' ? (
              <button className="primary-button" onClick={() => setIsCreateCandidateModalOpen(true)} type="button">
                Create Candidate
              </button>
            ) : null
          }
        >
          <div className="stack">
            {isCandidatesLoading ? <p>Loading candidates...</p> : null}
            {!isCandidatesLoading && !candidates.length ? <p>No candidates available yet.</p> : null}
            {candidates.map((candidate) => (
              <button
                key={candidate.id}
                className={`list-button ${candidate.id === selectedCandidateId ? 'selected' : ''}`}
                onClick={() => setSelectedCandidateId(candidate.id)}
                type="button"
              >
                <span className="candidate-list-copy">
                  <strong>{candidate.name}</strong>
                  <span>{candidate.email}</span>
                </span>
                <StatusBadge status={candidateStatuses[candidate.id] ?? 'unknown'} />
              </button>
            ))}
          </div>
        </Panel>

        <Panel
          title="Candidate Profile"
          actions={
            user.role === 'admin' && profile?.candidate ? (
              <button className="primary-button" onClick={() => setIsStartAssessmentModalOpen(true)} type="button">
                Start Assessment
              </button>
            ) : null
          }
        >
          {isProfileLoading ? (
            <p>Loading candidate profile...</p>
          ) : profile?.candidate ? (
            <div className="stack">
              <div className="profile-header">
                <div className="stack compact-stack">
                  <p><strong>{profile.candidate.name}</strong></p>
                  <p>{profile.candidate.email}</p>
                </div>
                <StatusBadge status={selectedCandidateStatus} />
              </div>
              <p>Candidate ID: {profile.candidate.id}</p>
            </div>
          ) : (
            <p>Select a candidate to review their profile.</p>
          )}
        </Panel>

        <Panel title="Capability Profile">
          {isProfileLoading ? (
            <p>Loading capability scores...</p>
          ) : profile?.score ? (
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
          {isProfileLoading ? (
            <p>Loading assessments...</p>
          ) : profile?.assessments?.length ? (
            <div className="stack">
              {profile.assessments.map((assessment) => (
                <div key={assessment.id} className="data-card">
                  <div className="profile-header">
                    <p><strong>{assessment.title}</strong></p>
                    <StatusBadge status={normalizeAssessmentStatus(assessment.status)} />
                  </div>
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
            {isProfileLoading ? <p>Loading task runs...</p> : null}
            {!isProfileLoading && !taskRuns.length ? <p>No task runs available yet.</p> : null}
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
          {isReplayLoading ? (
            <p>Loading session replay...</p>
          ) : replay ? (
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

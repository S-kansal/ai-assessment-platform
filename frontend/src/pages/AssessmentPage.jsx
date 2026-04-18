import { useEffect, useMemo, useRef, useState } from 'react';

import Panel from '../components/Panel.jsx';
import { useAuth } from '../context/useAuth.js';
import {
  createAssessment,
  getTask,
  runSimulation,
  sendTelemetry,
  submitAssessment,
} from '../services/api.js';

const defaultPrompt =
  'Answer only from the retrieved context. If the context is insufficient, say you do not know.';

function nextMonotonicTimestamp() {
  return Date.now();
}

export default function AssessmentPage() {
  const { user, logout } = useAuth();
  const [assessmentId, setAssessmentId] = useState('');
  const [taskRunId, setTaskRunId] = useState('');
  const [task, setTask] = useState(null);
  const [promptText, setPromptText] = useState(defaultPrompt);
  const [queryText, setQueryText] = useState('');
  const [simulation, setSimulation] = useState(null);
  const [rootCause, setRootCause] = useState('');
  const [fixSummary, setFixSummary] = useState('');
  const [status, setStatus] = useState('idle');
  const [error, setError] = useState('');
  const hasLoggedInspectionRef = useRef(false);

  const browserSessionId = useMemo(
    () => `session-${user.candidateId}-${Math.random().toString(36).slice(2, 10)}`,
    [user.candidateId]
  );

  useEffect(() => {
    let ignore = false;

    async function bootstrapAssessment() {
      setStatus('loading');
      setError('');
      try {
        const createdAssessment = await createAssessment({
          candidate_id: user.candidateId,
          title: 'AI Engineering Assessment',
          order_mode: 'fixed',
          browser_session_id: browserSessionId,
        });
        if (ignore) {
          return;
        }
        setAssessmentId(createdAssessment.assessment_id);
        setTaskRunId(createdAssessment.active_task_run_id);
        const taskPayload = await getTask(createdAssessment.active_task_run_id);
        setTask(taskPayload);
        setQueryText(taskPayload.task.expected_diagnostic_path.includes('identify_prompt_grounding_gap')
          ? 'How should the assistant behave if context is missing?'
          : 'What is the return policy for electronics?');
        await sendTelemetry({
          task_run_id: createdAssessment.active_task_run_id,
          event_type: 'task_started',
          monotonic_timestamp_ms: nextMonotonicTimestamp(),
          payload: {
            assessment_id: createdAssessment.assessment_id,
          },
        });
        setStatus('ready');
      } catch (requestError) {
        setError(requestError.response?.data?.error?.message || 'Unable to start assessment');
        setStatus('error');
      }
    }

    bootstrapAssessment();
    return () => {
      ignore = true;
    };
  }, [browserSessionId, user.candidateId]);

  async function handleRunSimulation() {
    try {
      hasLoggedInspectionRef.current = false;
      await sendTelemetry({
        task_run_id: taskRunId,
        event_type: 'prompt_submitted',
        monotonic_timestamp_ms: nextMonotonicTimestamp(),
        payload: {
          prompt_text: promptText,
        },
      });
      await sendTelemetry({
        task_run_id: taskRunId,
        event_type: 'query_submit',
        monotonic_timestamp_ms: nextMonotonicTimestamp(),
        payload: {
          query_text: queryText,
        },
      });
      const result = await runSimulation({
        task_run_id: taskRunId,
        prompt_text: promptText,
        query_text: queryText,
      });
      setSimulation(result);
      hasLoggedInspectionRef.current = false;
      await sendTelemetry({
        task_run_id: taskRunId,
        event_type: 'simulation_output_view',
        monotonic_timestamp_ms: nextMonotonicTimestamp(),
        payload: {
          simulation_run_id: result.id,
        },
      });
    } catch (requestError) {
      setError(requestError.response?.data?.error?.message || 'Unable to run simulation');
    }
  }

  async function handleLogsInspection() {
    if (!taskRunId || !simulation || hasLoggedInspectionRef.current) {
      return;
    }

    hasLoggedInspectionRef.current = true;
    try {
      await sendTelemetry({
        task_run_id: taskRunId,
        event_type: 'log_inspection',
        monotonic_timestamp_ms: nextMonotonicTimestamp(),
        payload: {
          task_run_id: taskRunId,
          simulation_run_id: simulation.id,
        },
      });
    } catch {
      hasLoggedInspectionRef.current = false;
    }
  }

  async function handleSubmit() {
    try {
      await sendTelemetry({
        task_run_id: taskRunId,
        event_type: 'solution_submitted',
        monotonic_timestamp_ms: nextMonotonicTimestamp(),
        payload: {
          prompt_length: promptText.length,
          query_length: queryText.length,
        },
      });
      const result = await submitAssessment(assessmentId, {
        task_run_id: taskRunId,
        final_prompt: promptText,
        final_query: queryText,
        submitted_root_cause: rootCause,
        submitted_fix_summary: fixSummary,
      });
      if (result.next_task_run_id) {
        setTaskRunId(result.next_task_run_id);
        const taskPayload = await getTask(result.next_task_run_id);
        setTask(taskPayload);
        setSimulation(null);
        setRootCause('');
        setFixSummary('');
      } else {
        setStatus('completed');
      }
    } catch (requestError) {
      setError(requestError.response?.data?.error?.message || 'Unable to submit task');
    }
  }

  async function emitPromptTelemetry(value) {
    if (!taskRunId) {
      return;
    }
    await sendTelemetry({
      task_run_id: taskRunId,
      event_type: 'prompt_edit',
      monotonic_timestamp_ms: nextMonotonicTimestamp(),
      payload: {
        prompt_preview: value.slice(0, 120),
      },
    });
  }

  return (
    <main className="page">
      <header className="page-header">
        <div>
          <p className="eyebrow">Candidate Workspace</p>
          <h1>Assessment Session</h1>
        </div>
        <button className="secondary-button" onClick={logout}>
          Logout
        </button>
      </header>

      {error ? <p className="error-banner">{error}</p> : null}

      {status === 'completed' ? (
        <Panel title="Assessment Complete">
          <p className="lede">All tasks were submitted. Your evaluation and scoring data are now available to reviewers.</p>
        </Panel>
      ) : (
        <div className="assessment-grid">
          <Panel title="Task">
            {task ? (
              <div className="stack">
                <p><strong>{task.task.title}</strong></p>
                <p>Task type: {task.task.task_type}</p>
                <p>Expected path: {task.task.expected_diagnostic_path.join(' -> ')}</p>
              </div>
            ) : (
              <p>Loading task...</p>
            )}
          </Panel>

          <Panel title="Prompt Editor">
            <div className="stack">
              <textarea
                value={promptText}
                onChange={(event) => {
                  setPromptText(event.target.value);
                  void emitPromptTelemetry(event.target.value);
                }}
                rows={6}
              />
              <input
                value={queryText}
                onChange={(event) => setQueryText(event.target.value)}
                placeholder="Enter a query"
              />
              <button className="primary-button" onClick={handleRunSimulation} disabled={!taskRunId}>
                Run Simulation
              </button>
            </div>
          </Panel>

          <Panel title="Simulation Output">
            {simulation ? (
              <div className="stack" onMouseEnter={() => void handleLogsInspection()}>
                <p><strong>Response</strong></p>
                <pre>{simulation.response_text}</pre>
                <p><strong>Retrieved Chunks</strong></p>
                <pre>{JSON.stringify(simulation.retrieved_chunks, null, 2)}</pre>
                <p><strong>Logs</strong></p>
                <pre>{simulation.debug_logs.join('\n')}</pre>
              </div>
            ) : (
              <p>Run the simulation to inspect retrieval, logs, and generated output.</p>
            )}
          </Panel>

          <Panel title="Solution Submission">
            <div className="stack">
              <textarea
                value={rootCause}
                onChange={(event) => setRootCause(event.target.value)}
                rows={4}
                placeholder="Describe the root failure mode."
              />
              <textarea
                value={fixSummary}
                onChange={(event) => setFixSummary(event.target.value)}
                rows={4}
                placeholder="Describe the corrective action."
              />
              <button
                className="primary-button"
                onClick={handleSubmit}
                disabled={!rootCause || !fixSummary || !simulation}
              >
                Submit Task
              </button>
            </div>
          </Panel>
        </div>
      )}
    </main>
  );
}

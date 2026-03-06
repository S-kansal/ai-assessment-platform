import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import TaskDescription from '../components/TaskDescription';
import QueryPanel from '../components/QueryPanel';
import PromptEditor from '../components/PromptEditor';
import SimulationControls from '../components/SimulationControls';
import SimulationOutput from '../components/SimulationOutput';
import DebugLogs from '../components/DebugLogs';
import SolutionSubmit from '../components/SolutionSubmit';
import {
    createCandidate,
    runSimulation,
    sendTelemetry,
    startAssessment,
    advanceAssessment,
} from '../services/api';

const DEFAULT_PROMPT = 'Use the provided context to answer the question.';

export default function TaskPage() {
    const navigate = useNavigate();

    // Assessment state
    const [candidateId, setCandidateId] = useState(null);
    const [sessionId, setSessionId] = useState(null);
    const [assessmentId, setAssessmentId] = useState(null);
    const [taskRunId, setTaskRunId] = useState(null);
    const [taskDescription, setTaskDescription] = useState('');
    const [taskId, setTaskId] = useState('');
    const [taskStatus, setTaskStatus] = useState('');

    // Progress
    const [currentTaskIndex, setCurrentTaskIndex] = useState(0);
    const [totalTasks, setTotalTasks] = useState(0);

    // Interaction state
    const [query, setQuery] = useState('What is the refund policy?');
    const [promptTemplate, setPromptTemplate] = useState(DEFAULT_PROMPT);
    const [retrievedChunks, setRetrievedChunks] = useState([]);
    const [generatedAnswer, setGeneratedAnswer] = useState('');
    const [debugLogs, setDebugLogs] = useState([]);
    const [solution, setSolution] = useState('');
    const [runCount, setRunCount] = useState(0);

    // UI state
    const [simLoading, setSimLoading] = useState(false);
    const [submitLoading, setSubmitLoading] = useState(false);
    const [submitted, setSubmitted] = useState(false);
    const [error, setError] = useState('');
    const [started, setStarted] = useState(false);
    const [setupLoading, setSetupLoading] = useState(false);
    const [results, setResults] = useState(null);
    const [assessmentComplete, setAssessmentComplete] = useState(false);

    // ── Setup: create candidate + assessment ──────────
    const isPilot = typeof window !== 'undefined' &&
        (new URLSearchParams(window.location.search).get('pilot') === 'true' ||
            localStorage.getItem('pilot_candidate_id'));

    async function handleStart() {
        setSetupLoading(true);
        setError('');
        try {
            let candId = localStorage.getItem('pilot_candidate_id');

            if (!candId) {
                // Non-pilot: create new candidate
                const cand = await createCandidate(
                    'Assessment Candidate',
                    `candidate_${Date.now()}@assessment.ai`
                );
                candId = cand.candidate_id;
            }

            setCandidateId(candId);

            const result = await startAssessment(candId);
            setAssessmentId(result.assessment_id);
            setSessionId(result.assessment_id); // for telemetry context
            setTaskRunId(result.task_run_id);
            setTaskDescription(result.description);
            setTaskId(result.first_task);
            setTaskStatus('running');
            setCurrentTaskIndex(result.current_task_index);
            setTotalTasks(result.total_tasks);
            setStarted(true);
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to start assessment');
        }
        setSetupLoading(false);
    }

    // ── Telemetry helper ──────────────────────────────
    const emitTelemetry = useCallback(
        (eventType, payload) => {
            if (sessionId && taskRunId) {
                sendTelemetry(sessionId, taskRunId, eventType, {
                    ...payload,
                    assessment_id: assessmentId,
                }).catch(() => { });
            }
        },
        [sessionId, taskRunId, assessmentId]
    );

    // ── Simulation ────────────────────────────────────
    async function handleRun() {
        if (!taskRunId) return;
        setSimLoading(true);
        setError('');
        try {
            const res = await runSimulation(taskRunId, query, promptTemplate);
            setRetrievedChunks(res.retrieved_chunks);
            setGeneratedAnswer(res.generated_answer);
            setDebugLogs(res.debug_logs);
            setRunCount((c) => c + 1);
            emitTelemetry('simulation_run', { query, run_number: runCount + 1 });
        } catch (err) {
            setError(err.response?.data?.detail || 'Simulation failed. Please retry.');
        }
        setSimLoading(false);
    }

    // ── Solution submission — advance to next task ────
    async function handleSubmit() {
        if (!taskRunId || !solution.trim()) return;
        setSubmitLoading(true);
        setError('');
        try {
            emitTelemetry('solution_submit', { solution_length: solution.length });

            const result = await advanceAssessment(assessmentId, taskRunId, solution);

            if (result.status === 'next_task') {
                // Transition to next task
                setTaskRunId(result.task_run_id);
                setTaskDescription(result.description);
                setTaskId(result.task_id);
                setCurrentTaskIndex(result.current_task_index);
                setTotalTasks(result.total_tasks);
                setTaskStatus('running');

                // Reset interaction state for new task
                setRetrievedChunks([]);
                setGeneratedAnswer('');
                setDebugLogs([]);
                setSolution('');
                setRunCount(0);
                setSubmitted(false);
                setPromptTemplate(DEFAULT_PROMPT);
                setQuery('What is the refund policy?');
                setResults(null);
            } else if (result.status === 'completed') {
                setAssessmentComplete(true);
                setTaskStatus('completed');
                setSubmitted(true);
                setResults(result.scores || {});
            }
        } catch (err) {
            setError(err.response?.data?.detail || 'Submission failed. Please retry.');
        }
        setSubmitLoading(false);
    }

    // ── Telemetry callbacks ───────────────────────────
    function onQueryChange(val) {
        emitTelemetry('query_change', { query: val });
    }
    function onPromptEdit(version) {
        emitTelemetry('prompt_edit', { version });
    }

    // ── Landing screen ────────────────────────────────
    if (!started) {
        return (
            <div style={{
                minHeight: '100vh',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                padding: '2rem',
            }}>
                <div style={{ textAlign: 'center', maxWidth: '500px' }}>
                    <div style={{ fontSize: '2.5rem', marginBottom: '0.5rem' }}>🔍</div>
                    <h1 style={{
                        fontSize: '1.5rem',
                        fontWeight: 700,
                        background: 'linear-gradient(135deg, #38bdf8, #818cf8)',
                        WebkitBackgroundClip: 'text',
                        WebkitTextFillColor: 'transparent',
                        marginBottom: '0.75rem',
                    }}>
                        AI Engineering Assessment
                    </h1>
                    <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '2rem', lineHeight: 1.6 }}>
                        You will complete <strong style={{ color: 'var(--accent)' }}>3 debugging tasks</strong> across a
                        RAG pipeline. Investigate retrieval, prompt, and generation stages
                        to diagnose each failure and submit your fix.
                    </p>
                    <button
                        id="start-assessment-btn"
                        className="btn-primary"
                        onClick={handleStart}
                        disabled={setupLoading}
                        style={{ fontSize: '1rem', padding: '0.75rem 2rem' }}
                    >
                        {setupLoading ? 'Setting up…' : 'Start Assessment'}
                    </button>
                    {error && (
                        <p style={{ color: 'var(--error)', marginTop: '1rem', fontSize: '0.85rem' }}>{error}</p>
                    )}
                </div>
            </div>
        );
    }

    // ── Assessment complete screen ────────────────────
    if (assessmentComplete) {
        return (
            <div style={{ maxWidth: '800px', margin: '0 auto', padding: '2rem' }}>
                <div className="panel animate-in" style={{ textAlign: 'center', padding: '2rem' }}>
                    <div style={{ fontSize: '3rem', marginBottom: '0.5rem' }}>🎉</div>
                    <h1 style={{
                        fontSize: '1.3rem', fontWeight: 700,
                        background: 'linear-gradient(135deg, #34d399, #38bdf8)',
                        WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
                    }}>
                        Assessment Complete
                    </h1>
                    <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', margin: '1rem 0' }}>
                        You have completed all {totalTasks} tasks. Thank you for your time.
                    </p>

                    {results?.capabilities && (
                        <div style={{ marginTop: '1.5rem', textAlign: 'left' }}>
                            <h4 style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.5rem', textTransform: 'uppercase' }}>
                                Capability Profile
                            </h4>
                            {Object.entries(results.capabilities).map(([cap, score]) => (
                                <div key={cap} style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
                                    <span style={{ fontSize: '0.8rem', color: 'var(--text-primary)', width: '180px', textTransform: 'capitalize' }}>
                                        {cap.replace(/_/g, ' ')}
                                    </span>
                                    <div style={{ flex: 1, background: 'var(--bg-primary)', borderRadius: '999px', height: '8px', overflow: 'hidden' }}>
                                        <div style={{
                                            width: `${score}%`, height: '100%',
                                            background: 'linear-gradient(90deg, #0ea5e9, #38bdf8)',
                                            borderRadius: '999px', transition: 'width 0.5s ease',
                                        }} />
                                    </div>
                                    <span style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--accent)', width: '40px', textAlign: 'right' }}>
                                        {score}
                                    </span>
                                </div>
                            ))}
                        </div>
                    )}

                    <button
                        className="btn-primary"
                        onClick={() => {
                            if (isPilot) {
                                navigate(`/pilot/feedback?candidateId=${candidateId}`);
                            } else {
                                navigate('/dashboard');
                            }
                        }}
                        style={{ marginTop: '1.5rem', fontSize: '0.9rem' }}
                    >
                        {isPilot ? '📝 Share Feedback' : '📊 View Dashboard'}
                    </button>
                </div>
            </div>
        );
    }

    // ── Assessment interface ──────────────────────────
    return (
        <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '1.5rem' }}>
            {/* Header */}
            <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginBottom: '1.5rem',
                paddingBottom: '1rem',
                borderBottom: '1px solid var(--border)',
            }}>
                <h1 style={{
                    fontSize: '1.1rem',
                    fontWeight: 700,
                    background: 'linear-gradient(135deg, #38bdf8, #818cf8)',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                }}>
                    🔍 AI Debugging Environment
                </h1>
                <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
                    {/* Progress indicator */}
                    <div style={{
                        display: 'flex', gap: '0.35rem', alignItems: 'center',
                    }}>
                        {Array.from({ length: totalTasks }).map((_, i) => (
                            <div key={i} style={{
                                width: i + 1 === currentTaskIndex ? '24px' : '8px',
                                height: '8px',
                                borderRadius: '999px',
                                background: i + 1 < currentTaskIndex
                                    ? 'var(--success)'
                                    : i + 1 === currentTaskIndex
                                        ? 'var(--accent)'
                                        : 'var(--border)',
                                transition: 'all 0.3s ease',
                            }} />
                        ))}
                    </div>
                    <span style={{
                        fontSize: '0.8rem', fontWeight: 600,
                        color: 'var(--accent)',
                        background: 'rgba(56,189,248,.1)',
                        padding: '0.25rem 0.75rem',
                        borderRadius: '999px',
                    }}>
                        Task {currentTaskIndex} of {totalTasks}
                    </span>
                </div>
            </div>

            {error && (
                <div style={{
                    background: 'rgba(248,113,113,.1)',
                    border: '1px solid var(--error)',
                    borderRadius: '0.5rem',
                    padding: '0.75rem',
                    marginBottom: '1rem',
                    fontSize: '0.85rem',
                    color: 'var(--error)',
                }}>
                    ⚠ {error}
                </div>
            )}

            {/* Task description */}
            <TaskDescription description={taskDescription} taskId={taskId} status={taskStatus} />

            {/* Middle: Query + Logs */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginTop: '1rem' }}>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                    <QueryPanel query={query} setQuery={setQuery} onQueryChange={onQueryChange} />
                    <PromptEditor
                        promptTemplate={promptTemplate}
                        setPromptTemplate={setPromptTemplate}
                        onPromptEdit={onPromptEdit}
                    />
                    <SimulationControls onRun={handleRun} loading={simLoading} runCount={runCount} />
                </div>
                <DebugLogs logs={debugLogs} />
            </div>

            {/* Simulation output */}
            <div style={{ marginTop: '1rem' }}>
                <SimulationOutput retrievedChunks={retrievedChunks} generatedAnswer={generatedAnswer} />
            </div>

            {/* Solution */}
            <div style={{ marginTop: '1rem' }}>
                <SolutionSubmit
                    solution={solution}
                    setSolution={setSolution}
                    onSubmit={handleSubmit}
                    submitted={submitted}
                    loading={submitLoading}
                />
            </div>
        </div>
    );
}

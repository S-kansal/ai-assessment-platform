import axios from 'axios';

const api = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
    headers: { 'Content-Type': 'application/json' },
});

// ── JWT interceptor ───────────────────────────────
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

export default api;


// ── Candidate & Session ───────────────────────────
export async function createCandidate(name, email, organizationId = null) {
    const { data } = await api.post('/candidates', {
        name,
        email,
        organization_id: organizationId,
    });
    return data;
}

export async function createSession(candidateId) {
    const { data } = await api.post('/sessions', { candidate_id: candidateId });
    return data;
}

// ── Tasks ─────────────────────────────────────────
export async function startTask(sessionId, taskId) {
    const { data } = await api.post('/tasks/start', {
        session_id: sessionId,
        task_id: taskId,
    });
    return data;
}

export async function getTaskStatus(taskRunId) {
    const { data } = await api.get(`/tasks/${taskRunId}`);
    return data;
}

export async function completeTask(taskRunId, solution) {
    const { data } = await api.post('/tasks/complete', {
        task_run_id: taskRunId,
        solution,
    });
    return data;
}

// ── Simulation ────────────────────────────────────
export async function runSimulation(taskRunId, query, promptTemplate) {
    const { data } = await api.post('/simulate/rag', {
        task_run_id: taskRunId,
        query,
        prompt_template: promptTemplate,
    });
    return data;
}

// ── Telemetry ─────────────────────────────────────
export async function sendTelemetry(sessionId, taskId, eventType, payload) {
    const { data } = await api.post('/telemetry', {
        session_id: sessionId,
        task_id: taskId,
        event_type: eventType,
        payload,
    });
    return data;
}

// ── Evaluation & Scoring ──────────────────────────
export async function runEvaluation(taskRunId) {
    const { data } = await api.post('/evaluation/run', {
        task_run_id: taskRunId,
    });
    return data;
}

export async function computeScores(candidateId) {
    const { data } = await api.post('/scores/compute', {
        candidate_id: candidateId,
    });
    return data;
}

// ── Dashboard (read-only) ─────────────────────────
export async function listCandidates() {
    const { data } = await api.get('/dashboard/candidates');
    return data;
}

export async function getCandidateProfile(candidateId) {
    const { data } = await api.get(`/dashboard/candidates/${candidateId}/profile`);
    return data;
}

export async function getCandidateTasks(candidateId) {
    const { data } = await api.get(`/dashboard/candidates/${candidateId}/tasks`);
    return data;
}

export async function getTaskRunTelemetry(taskRunId) {
    const { data } = await api.get(`/dashboard/task-runs/${taskRunId}/telemetry`);
    return data;
}

export async function getTaskRunEvaluation(taskRunId) {
    const { data } = await api.get(`/dashboard/task-runs/${taskRunId}/evaluation`);
    return data;
}

// ── Assessment Orchestrator ───────────────────────
export async function startAssessment(candidateId) {
    const { data } = await api.post('/assessments/start', {
        candidate_id: candidateId,
    });
    return data;
}

export async function advanceAssessment(assessmentId, taskRunId, solution) {
    const { data } = await api.post(`/assessments/${assessmentId}/advance`, {
        task_run_id: taskRunId,
        solution,
    });
    return data;
}

export async function getAssessmentStatus(assessmentId) {
    const { data } = await api.get(`/assessments/${assessmentId}`);
    return data;
}

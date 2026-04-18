import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL;
let authToken = localStorage.getItem('token');
let unauthorizedHandler = null;

const client = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export function setAuthToken(token) {
  authToken = token;
}

export function registerUnauthorizedHandler(handler) {
  unauthorizedHandler = handler;
}

client.interceptors.request.use((config) => {
  if (authToken) {
    config.headers.Authorization = `Bearer ${authToken}`;
  }
  return config;
});

client.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      authToken = null;
      localStorage.removeItem('token');
      unauthorizedHandler?.();
      if (window.location.pathname !== '/login') {
        window.location.assign('/login');
      }
    }
    return Promise.reject(error);
  }
);

function unwrap(response) {
  return response.data.data;
}

function getReadableError(error, fallbackMessage) {
  return error.response?.data?.error?.message || fallbackMessage;
}

function getCompatUrl(path) {
  if (API_BASE_URL === '/api') {
    return path;
  }
  if (API_BASE_URL.endsWith('/api')) {
    return `${API_BASE_URL.slice(0, -4)}${path}`;
  }
  return path;
}

export async function login(email, password) {
  return unwrap(await client.post('/auth/login', { email, password }));
}

export async function registerOrganization(payload) {
  return unwrap(await client.post('/organizations/register', payload));
}

export async function createCandidate(payload) {
  try {
    return unwrap(await client.post('/candidates', payload));
  } catch (error) {
    throw new Error(getReadableError(error, 'Unable to create candidate'));
  }
}

export async function listCandidates() {
  return unwrap(await client.get('/candidates'));
}

export async function createAssessment(payload) {
  const normalizedPayload = {
    order_mode: 'fixed',
    browser_session_id: `admin-${payload.candidate_id}-${Date.now()}`,
    ...payload,
  };

  try {
    const assessment = unwrap(await client.post('/assessments', normalizedPayload));
    const assessmentId = assessment.id ?? assessment.assessment_id ?? assessment.data?.id ?? assessment.data?.assessment_id;
    return assessmentId ? { ...assessment, id: assessmentId } : assessment;
  } catch (error) {
    throw new Error(getReadableError(error, 'Unable to create assessment'));
  }
}

export async function getAssessment(assessmentId) {
  return unwrap(await client.get(`/assessments/${assessmentId}`));
}

export async function getTask(taskRunId) {
  return unwrap(await client.get(`/tasks/${taskRunId}`));
}

export async function runSimulation(payload) {
  return unwrap(await client.post('/simulations/run', payload));
}

export async function sendTelemetry(payload) {
  return unwrap(await client.post('/telemetry', payload));
}

export async function submitAssessment(assessmentId, payload) {
  return unwrap(await client.post(`/assessments/${assessmentId}/submit`, payload));
}

export async function getDashboardCandidates() {
  return unwrap(await client.get('/dashboard/candidates'));
}

export async function getDashboardCandidateProfile(candidateId) {
  return unwrap(await client.get(`/dashboard/candidates/${candidateId}/profile`));
}

export async function getDashboardTaskRuns(candidateId) {
  return unwrap(await client.get(`/dashboard/candidates/${candidateId}/task-runs`));
}

export async function getReplay(taskRunId) {
  return unwrap(await client.get(`/dashboard/task-runs/${taskRunId}/replay`));
}

export async function startAssessment(assessmentId) {
  try {
    const result = unwrap(
      await client.post(getCompatUrl(`/assessments/${assessmentId}/start`), undefined, {
        baseURL: '',
      })
    );
    const taskRunId = result.task_run_id ?? result.first_task_run_id ?? result.data?.task_run_id;
    return taskRunId ? { ...result, task_run_id: taskRunId } : result;
  } catch (error) {
    throw new Error(getReadableError(error, 'Unable to start assessment'));
  }
}

export default client;

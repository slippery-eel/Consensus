import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

// ── Types ─────────────────────────────────────────────────────────────────────

export interface Statement {
  id: number
  survey_id: number
  text: string
  is_active: boolean
  created_at: string
}

export interface Survey {
  id: number
  title: string
  description: string | null
  created_at: string
  statements: Statement[]
}

export interface SurveyListItem {
  id: number
  title: string
  description: string | null
  created_at: string
}

export interface Participant {
  id: number
  survey_id: number
  created_at: string
}

export interface ResponseItem {
  id: number
  survey_id: number
  participant_id: number
  statement_id: number
  vote: 'agree' | 'disagree' | 'pass'
  created_at: string
}

export interface ParticipantPoint {
  id: number
  pca_x: number
  pca_y: number
  cluster: number
}

export interface StatementStat {
  id: number
  text: string
  agree_rate: number
  disagree_rate: number
  pass_rate: number
  agree_count: number
  disagree_count: number
  pass_count: number
  is_consensus: boolean
  is_divisive: boolean
  cluster_score: number
}

export interface ClusterSummary {
  k: number
  size: number
  mean_votes: Record<number, number>
}

export interface AnalysisResult {
  participants: ParticipantPoint[]
  statements: StatementStat[]
  clusters: ClusterSummary[]
  pca_variance_explained: number[]
  k: number
  n_participants: number
  n_statements: number
}

// ── Surveys ───────────────────────────────────────────────────────────────────

export const listSurveys = (): Promise<SurveyListItem[]> =>
  api.get('/surveys').then((r) => r.data)

export const createSurvey = (title: string, description?: string): Promise<Survey> =>
  api.post('/surveys', { title, description }).then((r) => r.data)

export const getSurvey = (id: number): Promise<Survey> =>
  api.get(`/surveys/${id}`).then((r) => r.data)

// ── Statements ────────────────────────────────────────────────────────────────

export const addStatement = (surveyId: number, text: string): Promise<Statement> =>
  api.post(`/surveys/${surveyId}/statements`, { text }).then((r) => r.data)

export const updateStatement = (
  id: number,
  data: { text?: string; is_active?: boolean }
): Promise<Statement> => api.patch(`/statements/${id}`, data).then((r) => r.data)

export const deleteStatement = (id: number): Promise<void> =>
  api.delete(`/statements/${id}`).then(() => undefined)

// ── Sessions ──────────────────────────────────────────────────────────────────

export const createSession = (surveyId: number): Promise<Participant> =>
  api.post(`/surveys/${surveyId}/sessions`).then((r) => r.data)

// ── Responses ─────────────────────────────────────────────────────────────────

export const submitResponses = (
  participantId: number,
  responses: { statement_id: number; vote: 'agree' | 'disagree' | 'pass' }[]
): Promise<ResponseItem[]> =>
  api.post(`/sessions/${participantId}/responses`, responses).then((r) => r.data)

export const getResponses = (surveyId: number): Promise<ResponseItem[]> =>
  api.get(`/surveys/${surveyId}/responses`).then((r) => r.data)

// ── Analysis ──────────────────────────────────────────────────────────────────

export const runAnalysis = (surveyId: number, k: number): Promise<AnalysisResult> =>
  api.post(`/surveys/${surveyId}/analyze?k=${k}`).then((r) => r.data)

// ── Summaries ─────────────────────────────────────────────────────────────────

export interface GroupSummary {
  cluster_idx: number
  label: string
  description: string
  core_beliefs: string[]
  key_disagreement: string
}

export interface SummarizeResult {
  summaries: GroupSummary[]
  cached: boolean
}

export const getSummaries = (surveyId: number, k: number): Promise<SummarizeResult> =>
  api.get(`/surveys/${surveyId}/summaries?k=${k}`).then((r) => r.data)

export const generateSummaries = (
  surveyId: number,
  k: number,
  force = false
): Promise<SummarizeResult> =>
  api.post(`/surveys/${surveyId}/summarize?k=${k}&force=${force}`).then((r) => r.data)

// ── Settings ──────────────────────────────────────────────────────────────────

export const getOpenAIKeyStatus = (): Promise<{ configured: boolean }> =>
  api.get('/settings/openai-key').then((r) => r.data)

export const saveOpenAIKey = (key: string): Promise<{ configured: boolean }> =>
  api.post('/settings/openai-key', { key }).then((r) => r.data)

import {
  ParseStatementResponse,
  RecommendationFeedbackRequest,
  RecommendationFeedbackResponse,
  StatementHistoryResponse,
  StatementSaveRequest,
  StatementSaveResponse,
} from '@/types';



const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface HealthStatus {
  status: string;
  service: string;
  version: string;
  timestamp: string;
  environment: string;
}

export interface ApiErrorDetails {
  error_code: string;
  message: string;
  details?: Record<string, unknown>;
}

export class ApiError extends Error {
  errorCode: string;
  details?: Record<string, unknown>;
  statusCode: number;

  constructor(status: number, data: ApiErrorDetails) {
    super(data.message || 'API request failed');
    this.name = 'ApiError';
    this.statusCode = status;
    this.errorCode = data.error_code || 'API_ERROR';
    this.details = data.details;
  }
}

/**
 * Perform a typed GET/POST request with JSON body to the CC Track API.
 */
export async function fetchFromApi<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`;
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!response.ok) {
    let errorData: ApiErrorDetails;
    try {
      errorData = await response.json();
    } catch {
      errorData = {
        error_code: 'HTTP_ERROR',
        message: `HTTP ${response.status}: ${response.statusText}`,
      };
    }
    throw new ApiError(response.status, errorData);
  }

  return response.json() as Promise<T>;
}

/**
 * Fetch backend health status.
 */
export async function getBackendHealth(): Promise<HealthStatus> {
  return fetchFromApi<HealthStatus>('/health');
}

/**
 * Upload and parse a credit card statement PDF stream.
 */
export async function parseStatementPdf(
  file: File | Blob,
  filename: string = 'statement.pdf'
): Promise<ParseStatementResponse> {
  const url = `${API_BASE_URL}/api/v1/statements/parse`;
  const formData = new FormData();
  formData.append('file', file, filename);

  const response = await fetch(url, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    let errorData: ApiErrorDetails;
    try {
      errorData = await response.json();
    } catch {
      errorData = {
        error_code: 'PARSING_HTTP_ERROR',
        message: `HTTP ${response.status}: ${response.statusText}`,
      };
    }
    throw new ApiError(response.status, errorData);
  }

  return response.json() as Promise<ParseStatementResponse>;
}

/**
 * Record user feedback & interaction on a recommendation.
 */
export async function recordRecommendationFeedbackApi(
  recommendationId: string,
  payload: RecommendationFeedbackRequest
): Promise<RecommendationFeedbackResponse> {
  return fetchFromApi<RecommendationFeedbackResponse>(
    `/api/v1/recommendations/${encodeURIComponent(recommendationId)}/feedback`,
    {
      method: 'POST',
      body: JSON.stringify(payload),
    }
  );
}

/**
 * Persist the current parsed statement session to storage vault.
 */
export async function saveStatementSessionApi(
  statementData: ParseStatementResponse,
  options?: {
    userId?: string;
    cardName?: string;
  }
): Promise<StatementSaveResponse> {
  const payload: StatementSaveRequest = {
    statement_data: statementData,
    user_id: options?.userId,
    card_name: options?.cardName,
    save_transactions: true,
    save_findings: true,
    save_recommendations: true,
  };

  return fetchFromApi<StatementSaveResponse>('/api/v1/statements/save', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

/**
 * Fetch list of historical saved statements.
 */
export async function getStatementHistoryApi(
  userId?: string,
  limit: number = 50
): Promise<StatementHistoryResponse> {
  const params = new URLSearchParams();
  if (userId) params.append('user_id', userId);
  if (limit) params.append('limit', String(limit));

  const query = params.toString();
  return fetchFromApi<StatementHistoryResponse>(
    `/api/v1/statements/history${query ? `?${query}` : ''}`
  );
}

/**
 * Fetch a complete parsed statement by ID.
 */
export async function getStatementByIdApi(
  statementId: string,
  userId?: string
): Promise<ParseStatementResponse> {
  const params = new URLSearchParams();
  if (userId) params.append('user_id', userId);

  const query = params.toString();
  return fetchFromApi<ParseStatementResponse>(
    `/api/v1/statements/${encodeURIComponent(statementId)}${query ? `?${query}` : ''}`
  );
}



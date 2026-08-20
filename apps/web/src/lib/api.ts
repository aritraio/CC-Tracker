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
 * Perform a typed GET request to the CC Track API.
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

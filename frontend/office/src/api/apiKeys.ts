// This file defines API helper functions for managing API keys

import { api } from './axios';
import type {
  APIKeyListResponse,
  APIKeyCreateResponse,
  APIKeyCreate,
  APIKeyUpdate,
} from '@/types/apiKeys';

export const listAPIKeys = () =>
  api.get<APIKeyListResponse[]>('/api-keys');

export const getAPIKey = (id: string) => 
  api.get<APIKeyListResponse>(`/api-keys/${id}`);

export const createAPIKey = (data: APIKeyCreate) => 
  api.post<APIKeyCreateResponse>('/api-keys', data);

export const updateAPIKey = (id: string, data: APIKeyUpdate) => 
  api.patch<APIKeyListResponse>(`/api-keys/${id}`, data);

export const deleteAPIKey = (id: string) => 
  api.delete<void>(`/api-keys/${id}`);

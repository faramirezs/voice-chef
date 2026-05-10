export interface APIKeyListResponse {
  id: string;
  name: string;
  key_preview: string;
  description: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  last_used_at: string | null;
  tenant_id: string;
}

export interface APIKeyCreateResponse {
  id: string;
  name: string;
  key: string;  // Full API key, only shown at creation time
  key_preview: string;
  description: string | null;
  is_active: boolean;
  created_at: string;
  tenant_id: string;
}

export interface APIKeyCreate {
  name: string;
  description?: string;
  is_active?: boolean;
}

export interface APIKeyUpdate {
  name?: string;
  description?: string;
  is_active?: boolean;
}

import { api } from "./axios";

export interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: {
    id: string;
    tenant_id: string;
    email: string;
    role: string;
    is_active: boolean;
  };
}

export const login = async (
  email: string,
  password: string
): Promise<LoginResponse> => {
  const body = new URLSearchParams();
  body.append("username", email);
  body.append("password", password);

  const response = await api.post<LoginResponse>("/auth/login", body.toString(), {
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
  });

  return response.data;
};

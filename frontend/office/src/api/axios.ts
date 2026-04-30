import axios from "axios"
import { getValidToken } from "@/hooks/useAuth"

export const api = axios.create({
  baseURL: "/api",
  headers: {
    "Content-Type": "application/json",
  },
});

// NOTE: Here we attach token to every request:
// 1. Reads the token from localStorage
// 2. Adds: Authorization: Bearer <token>

api.interceptors.request.use((config) => {
  const token = getValidToken()

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});
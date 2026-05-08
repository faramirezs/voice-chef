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

// Response Interceptor
// NOTE: mpeshko: TO DO need to be improved after PR "[FRONTEND/AUTH] 
// Add token expiration check on frontend" merged to main
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response && error.response.status === 401) {
      // Don't redirect if we're already on the login page
      // (allows login form to show the "Invalid email or password" error)
      const isLoginPage = window.location.pathname === "/login" || window.location.pathname === "/signup";
      
      if (!isLoginPage) {
        console.warn("Unauthorized! Redirecting to login...");
        localStorage.removeItem("token");
        localStorage.removeItem("user");
        window.location.href = "/login";
      }
    }

    // Still reject the promise so the calling component can handle local errors
    return Promise.reject(error);
  }
);

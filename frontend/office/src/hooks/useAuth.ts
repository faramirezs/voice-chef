export interface User {
  id: string
  email: string
  name?: string
  avatar?: string
  is_active: boolean
}

/** Save token and expiration time to localStorage */
export function saveToken(token: string, expiresIn: number): void {
  // Convert seconds to milliseconds
  const expiryTime = Date.now() + (expiresIn * 1000)
  localStorage.setItem("token", token)
  localStorage.setItem("token_expiry", expiryTime.toString())
}

/** @returns true if token expired or doesn't exist*/
export function isTokenExpired(): boolean {
  const expiry = localStorage.getItem("token_expiry")
  if (!expiry) return true
  
  const expiryTime = parseInt(expiry)
  const now = Date.now()
  
  // Token is expired if current time is PAST expiry time
  return now > expiryTime
}

/**
 * Get valid token, or clear storage and redirect if expired
 * @returns token string or null if expired/missing
 */
export function getValidToken(): string | null {
  const token = localStorage.getItem("token")
  
  // If no token at all, just return null (don't redirect)
  if (!token) return null
  
  if (isTokenExpired()) {
    localStorage.removeItem("token")
    localStorage.removeItem("user")
    localStorage.removeItem("token_expiry")
    
    // Redirect to login only if we're not already on login page
    if (!window.location.pathname.includes("/login")) {
      window.location.href = "/login"
    }
    return null
  }
  
  return token
}

export function useAuth() {
  const userJson = localStorage.getItem("user")
  const token = localStorage.getItem("token")

  if (isTokenExpired()) {
    localStorage.removeItem("token")
    localStorage.removeItem("user")
    localStorage.removeItem("token_expiry")
    return { user: null, token: null, isLoggedIn: false }
  }

  const user: User | null = userJson ? JSON.parse(userJson) : null
  const isLoggedIn = Boolean(token)

  return { user, token, isLoggedIn }
}

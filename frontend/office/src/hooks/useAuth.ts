import { useSyncExternalStore } from "react"

export interface User {
  id: string
  email: string
  name?: string
  avatar?: string
  is_active: boolean
}

const AUTH_CHANGE_EVENT = "authchange"

/** Save token and expiration time to localStorage */
export function saveToken(token: string, expiresIn: number): void {
  // Convert seconds to milliseconds
  const expiryTime = Date.now() + (expiresIn * 1000)
  localStorage.setItem("token", token)
  localStorage.setItem("token_expiry", expiryTime.toString())
  window.dispatchEvent(new Event(AUTH_CHANGE_EVENT))
}

export function clearAuthData(): void {
  localStorage.removeItem("token")
  localStorage.removeItem("user")
  localStorage.removeItem("token_expiry")
  window.dispatchEvent(new Event(AUTH_CHANGE_EVENT))
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
    clearAuthData()
    
    // Redirect to login only if we're not already on login page
    if (!window.location.pathname.includes("/login")) {
      window.location.href = "/login"
    }
    return null
  }
  
  return token
}

export function useAuth() {
  useSyncExternalStore(subscribeAuthChanges, getAuthSnapshotKey, getAuthSnapshotKey)

  const userJson = localStorage.getItem("user")
  const token = localStorage.getItem("token")

  if (!token || isTokenExpired()) {
    return { user: null, token: null, isLoggedIn: false, isExpired: Boolean(token) }
  }

  const user: User | null = userJson ? JSON.parse(userJson) : null
  return { user, token, isLoggedIn: true, isExpired: false }
}

function getAuthSnapshotKey() {
  return [
    localStorage.getItem("token"),
    localStorage.getItem("user"),
    localStorage.getItem("token_expiry"),
  ].join("|")
}

function subscribeAuthChanges(callback: () => void) {
  const readSnapshotKey = getAuthSnapshotKey

  let lastSnapshotKey = readSnapshotKey()

  const notifyIfChanged = () => {
    const nextSnapshotKey = readSnapshotKey()
    if (nextSnapshotKey !== lastSnapshotKey) {
      lastSnapshotKey = nextSnapshotKey
      callback()
    }
  }

  const handleStorage = (event: StorageEvent) => {
    if (event.key === "token" || event.key === "user" || event.key === "token_expiry") {
      callback()
    }
  }

  window.addEventListener("storage", handleStorage)
  window.addEventListener(AUTH_CHANGE_EVENT, callback)
  const pollId = window.setInterval(notifyIfChanged, 250)

  return () => {
    window.removeEventListener("storage", handleStorage)
    window.removeEventListener(AUTH_CHANGE_EVENT, callback)
    window.clearInterval(pollId)
  }
}

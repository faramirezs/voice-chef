## JWT flow in our app

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     LOGIN FLOW                                  │
└─────────────────────────────────────────────────────────────────┘

1. User enters email + password
   ↓
2. Frontend sends POST /api/auth/login
   ↓
3. Backend validates credentials
   ↓
4. Backend creates JWT token + prepares user data
   Backend RESPONDS: {access_token, user, expires_in}
   ↓
5. Frontend SAVES in localStorage:
   `token` + `user` + `token_expiry`
   ↓
6. Frontend REDIRECTS to /

┌─────────────────────────────────────────────────────────────────┐
│                   SUBSEQUENT REQUESTS                           │
└─────────────────────────────────────────────────────────────────┘

1. User clicks "Recipes" → GET /api/recipes
   ↓
2. Axios interceptor calls getValidToken()
   ↓
3. getValidToken() checks isTokenExpired():
   ✅ NOT expired? → Continue with request
   ❌ EXPIRED? → Clear localStorage + redirect to /login
   ↓ (if still valid)
4. Adds header to request:
   Authorization: Bearer eyJhbGc...
   ↓
5. Backend receives token
   ↓
6. Backend VALIDATES:
   - Token signature valid?
   - Token not expired?
   - User exists?
   ↓
7. Backend returns recipes (filtered by tenant_id from token)
   ↓
8. Frontend displays recipes

┌─────────────────────────────────────────────────────────────────┐
│                   TOKEN EXPIRATION FLOW                         │
└─────────────────────────────────────────────────────────────────┘

Timeline (if token expires in 10 minutes):

0:00   → User logs in
       → Token saved with expiry = Date.now() + 600000 ms

0:01-9:59 → Token valid ✅
       → All API requests work normally

10:00  → Token EXPIRES (backend + frontend agree)

10:01  → User tries to make any request (click, scroll, etc.)
       → Axios interceptor calls getValidToken()
       → isTokenExpired() returns true
       → localStorage cleared (token, user, token_expiry)
       → Automatic redirect to /login
       → User sees login page 🔄
```

---

## Data Flow Diagram Details

### 1. Login Flow: Extract & Save Token

File: `frontend/office/src/components/login-form.tsx`

- Backend returns JWT in response

```typescript
const data = await login(email, password)
// ↓ data contains:
// {
//   access_token: "eyJhbGciOiJIUzI1NiIs...",  ← JWT TOKEN
//   token_type: "bearer",
//   expires_in: 3600,
//   user: { id, email, role, ... }
// }
```

✅ Save token with expiration time using `saveToken()`

Token lives in localStorage until LogOut or its expiration

```typescript
saveToken(data.access_token, data.expires_in)
// Stores:
// - localStorage.token = "eyJhbGc..."
// - localStorage.token_expiry = Date.now() + (600 * 1000) ← milliseconds
```

✅ Redirect to home

```typescript
navigate("/", { replace: true })
```

### 2. Attach Token to Every Request

File: `frontend/office/src/api/axios.ts` - Request Interceptor

Before every API call:
1. Check if token is expired via `getValidToken()`
2. If expired: Clear storage + redirect to `/login`
3. If valid: Attach token to Authorization header

```typescript
api.interceptors.request.use((config) => {
  const token = getValidToken()
  if (token) {
    // Add to Authorization header
    config.headers.Authorization = `Bearer ${token}`
    // ↓ Header becomes:
    // Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
  }
  return config
})
```

### 3. How Frontend Knows Current User

User data from login response is saved in `localStorage`. Each browser has its OWN separate `localStorage`! 🔑

We have a custom hook `useAuth()` to access user data anywhere.

File: `frontend/office/src/hooks/useAuth.ts`

```typescript
// Reads from THIS browser's localStorage
const userJson = localStorage.getItem("user")
const token = localStorage.getItem("token")
const tokenExpiry = localStorage.getItem("token_expiry")
```

### 4. Use Current User in Components

Any component can call `useAuth()`

Example file: `frontend/office/src/components/nav-user.tsx`

```typescript
export function NavUser() {
  const navigate = useNavigate()
  const { user } = useAuth()  // ← Get user from hook
  // ...
}
```



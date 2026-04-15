# Authentication

## Overview

Notes:
1. Login on signup will be implememnted later.
2. `/api/user/me` is an example.

```
Login form          Backend                   Database
      │                        │                          │
      │──POST /auth/login─────>│                          │
      │                        │─────────verify user─────>│
      │                        │<─────────────────────────│
      │<──JWT token─────────── │                          │
      │                        │                          │
      │  (token saved in       │                          │
      │   localStorage /       │                          │
      │   cookie)              │                          │
      │                        │                          │
      │──GET /api/user/me─────>│                          │
      │  Authorization: Bearer │                          │
      │<──user data────────────│                          │
```

---

## Backend

### Authentication Strategy

The backend implements the **OAuth2 Password Flow** using **JWT Bearer Tokens**.

This means:
1.  The user provides their credentials (email and password) to a login endpoint.
2.  The server validates these credentials and, if successful, returns a JSON Web Token (JWT).
3.  The frontend must send this JWT back in the `Authorization` header for all future requests to protected endpoints.

## Key Libraries

-   `argon2-cffi`: For securely hashing and verifying user passwords. We **never** store passwords in plain text.
-   `PyJWT`: For creating and verifying the JSON Web Tokens (JWTs) used for session management.

### Password validation

Backend uses `password-validator` package for password validation.

The rule for a strong password is defined in `backend/app/utils/auth_utils.py`: it must be from 8 to 22 characters long, contains uppercase, lowercase, digits, symbols, and doesn't contain spaces.


### Login

The login endpoint expects `x-www-form-urlencoded` (not JSON) because it uses FastAPI's `OAuth2PasswordRequestForm`. The field is called `username` but we send the email.

Read more about login request in [API spec](./api-specification.md).

### JWT tokens

- Signed with `SECRET_KEY` using `HS256`
- Expire after **60 minutes**

## Required Environment Variables

The backend requires the following environment variable to be set for security operations:

-   `SECRET_KEY`: A long, random, and secret string used to sign the JWTs. This key is critical for ensuring that the tokens cannot be tampered with.

    Example for a `.env` file:
    ```
    SECRET_KEY=a_very_long_and_super_secret_random_string_that_is_hard_to_guess
    ```

---

## Frontend

## Authentication Flow for Frontend

### 1. User Login

-   **Success Response (200 OK):** The server returns an `access_token`.
    ```json
    {
      "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "token_type": "bearer"
    }
    ```
    The frontend must store this `access_token`.

### 2. Making Authenticated Requests

For any endpoint that requires authentication, the frontend must include the token in the `Authorization` header.

-   **Header Format:** `Authorization: Bearer <your_access_token>`

**Example:**
```
GET /api/some-protected-resource
Host: localhost:8000
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

(To be continued...)

---
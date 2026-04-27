from fastapi import status

# these dicts are just documentation/override metadata for OpenAPI, 
# not the actual runtime response shape.

# ─── SIGNUP ──────────────────────────────────────────────────────────────────

signup_responses = {
    status.HTTP_201_CREATED: {
        "description": "User created successfully",
        "content": {
            "application/json": {
                "example": {
                    "id": "c0a8012e-0000-0000-0000-000000000001",
                    "email": "user@example.com",
                }
            }
        },
    },
    status.HTTP_409_CONFLICT: {
        "description": "Conflict: Email or Nickname already exists",
        "content": {
            "application/json": {
                "examples": {
                    "email_exists": {
                        "summary": "Email already registered",
                        "value": {"detail": "E-Mail already registered."},
                    },
                }
            }
        },
    },
    status.HTTP_400_BAD_REQUEST: {
        "description": "Bad Request: Invalid input data",
        "content": {
            "application/json": {
                "examples": {
                    "weak_password": {
                        "summary": "Password is too weak",
                        "value": {
                            "detail": "Password is too weak. It must have a minimum of 8 characters, and include uppercase, lowercase, digits, and symbols."
                        },
                    },
                    "invalid_uuid": {
                        "summary": "Invalid UUID format",
                        "value": {"detail": "Invalid UUID format for tenant_id"},
                    },
                    "database_error": {
                        "summary": "A database error occurred",
                        "value": {"detail": "Database error: <specific_error_message>"},
                    },
                }
            }
        },
    },
    status.HTTP_503_SERVICE_UNAVAILABLE: {
        "description": "Default tenant not configured",
        "content": {
            "application/json": {
                "example": {
                    "value": "Default tenant not configured.",
                }
            }
        },
    },
}


# ─── LOGIN ──────────────────────────────────────────────────────────────────


login_responses = {
    status.HTTP_200_OK: {
        "description": "User logged in successfully",
        "content": {
            "application/json": {
                "example": {
                    "access_token": "<jwt>",
                    "token_type": "bearer",
                    "expires_in": 3600,
                    "user": {
                        "id": "b4cce9a0-7a56-4687-9aab-16cdf55f6961",
                        "tenant_id": "98aa2780-6ad4-4de0-8908-3fa799eb67db",
                        "email": "chef-admin@kitchen.local",
                        "role": "editor",
                        "is_active": "true"
                        }
                    }
                }
            },
        },
    status.HTTP_401_UNAUTHORIZED: {
        "description": "Unauthorized",
        "content": {
            "application/json": {
                "example": {
                    "detail": "Invalid email or password"
                }
            }
        }
    },
    status.HTTP_403_FORBIDDEN: {
        "description": "Forbidden",
        "content": {
            "application/json": {
                "example": {
                    "detail": "Account disabled. Please contact your administrator"
                }
            }
        }
    }
}

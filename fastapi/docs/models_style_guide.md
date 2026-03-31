# ORM Models Style Guide

This document outlines the conventions and best practices for creating SQLModel ORM classes in this project. The goal is to maintain a consistent and readable codebase.

### 1. ID and Default Value Generation

**Rule:** The database is the single source of truth for generating default values, especially for primary keys and timestamps. We do not generate these values in the Python application code.

**Implementation:**
- For primary keys (`id`), always delegate generation to the database using `server_default`.
- For timestamp fields (`created_at`, `updated_at`), also use `server_default` and `onupdate`.

### 2. Usage of `Field()` vs. `sa_column=Column()`

**Rule:** Prefer using "pure" `Field()` parameters whenever possible. Only use `sa_column=Column()` when you need to access database-specific features that `Field()` does not directly expose.

**When to use pure `Field()`:**
For simple constraints that `Field` supports directly.

```python
# Good: All constraints are available as Field parameters
name: str = Field(max_length=255, index=True, nullable=False)
is_active: bool = Field(default=True, nullable=False)
tenant_id: UUID | None = Field(default=None, foreign_key="tenants.id")
```

**When to use `sa_column=Column()`:**
When you need to define database-level logic or special column types.

The most common reason is for **`server_default`** and **`onupdate`** behavior, which are SQLAlchemy features. `Field()` does not have parameters for these.

```python
# Correct: `sa_column` is required here for `server_default` and `onupdate`
updated_at: datetime = Field(
    default=None,
    sa_column=Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
        onupdate=text("now()"), # This parameter is only available on `Column`
    ),
)
```

### 3. `Column` vs. `mapped_column`

**Decision:** We consistently use the classic `Column` with `sa_column` instead of the modern `mapped_column`.

**Reasoning:**
While `mapped_column` is the modern standard in SQLAlchemy 2.0, its integration with SQLModel can sometimes be tricky and lead to subtle type conflicts. `SQLModel` was designed around the `Column` object. Using `Column` provides a more stable and predictable integration.

```python
# Our standard: Reliable and compatible with SQLModel
email: str = Field(sa_column=Column(String(255), nullable=False))

# Avoid: May cause conflicts with SQLModel's internal logic
# email: str = Field(sa_column=mapped_column(String(255), nullable=False))
```

### 4. Nullable Types (`Optional`)

**Rule:** Always use the modern `| None` syntax (Union Type Operator) for nullable fields, which was introduced in Python 3.10. Avoid the older `Optional[X]` syntax.

**Reasoning:** This syntax is cleaner, more readable, and does not require an import from `typing`.

```python
# Good: Modern and clean
tenant_id: UUID | None = Field(default=None, foreign_key="tenants.id")
description: str | None = None

# Avoid: Old style
# from typing import Optional
# tenant_id: Optional[UUID] = Field(default=None, foreign_key="tenants.id")
```

### 5. Declaring Simple Nullable Fields

**Rule:** For a nullable field that has no other constraints or options, declare it directly without using `Field()`.

**Reasoning:** It's more concise and readable. `Field(default=None)` is redundant if that's the only parameter.

```python
# Preferred: Simple and direct
description: str | None = None

# Also acceptable, but verbose
# description: str | None = Field(default=None)
```

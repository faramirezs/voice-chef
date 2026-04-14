# ORM Models Style Guide

## Table of Contents

- [1. ID and Default Value Generation](#1-id-and-default-value-generation)
- [2. Usage of `Field()` vs. `sa_column=Column()`](#2-usage-of-field-vs-sa_columncolumn)
- [3. `Column` vs. `mapped_column`](#3-column-vs-mapped_column)
- [4. Nullable Types (`Optional`)](#4-nullable-types-optional)
- [5. Declaring Simple Nullable Fields](#5-declaring-simple-nullable-fields)
- [6. When to use `__table_args__`](#6-when-to-use-__table_args__)
- [7. `sa_column_kwargs` parameter in SQLModel's `Field()`](#7-sa_column_kwargs-parameter-in-sqlmodels-field)

This document outlines the conventions and best practices for creating SQLModel ORM classes in this project. The goal is to maintain a consistent and readable codebase.

### 1. ID and Default Value Generation

#### **MVP rule**

If in a table the column `id`, type `UUID` has no `Default` value - we implement app-side UUID generation.

```python
id: uuid.UUID = Field(
    default_factory=uuid.uuid4,
    primary_key=True,
)
```

If in a table the column `id`, type `UUID` has `gen_random_uuid()` - read **Post-MVP rule** below.

#### **Post-MVP rule**

We schedule DB-side UUID defaults as post-MVP hardening.

```python
id: uuid.UUID = Field(
    default=None,
    primary_key=True,
    sa_column_kwargs={"server_default": text("gen_random_uuid()")}
)
```

**Timestamp fields:**
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
updated_at: date = Field(
    default=None,
    sa_column=Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
        onupdate=text("now()"), # This parameter is only available on `Column`
    ),
)
```

The **text()** function tells SQLAlchemy: "Don't try to parse this, just insert this text into the SQL query as is."

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

**Exception: Optional Forward References in Relationships**

There is one exception. When defining an optional relationship to another model using a string forward reference, you **must** use the classic `Optional["ClassName"]` syntax.

**Reasoning:** The modern `"ClassName" | None` syntax will raise a `TypeError` at runtime. This is because Python tries to apply the `|` operator to a string and `None`, which is not a valid operation. The `Optional[X]` type is specifically designed to correctly handle string-based forward references.

```python
# Correct for optional forward references
from typing import Optional

class User(SQLModel, table=True):
    # ...
    tenant: Optional["Tenant"] = Relationship(back_populates="users")

# Incorrect: This will raise a TypeError
#     tenant: "Tenant" | None = Relationship(back_populates="users")
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

### 6. When to use `__table_args__`

**Rule:** Use the `__table_args__` attribute to define database constraints that cannot be described on a single column or require explicit naming that `Field()` does not support.

**Reasoning:** While `Field()` is great for simple constraints like `primary_key`, `unique`, or `foreign_key` on a single column, `__table_args__` is the standard SQLAlchemy way to handle more complex, table-wide rules.

**Common Use Cases:**

1.  **Explicitly Named Unique Constraints (`UniqueConstraint`):** This follows the same logic as named indexes. If the database has a unique constraint with a specific name that doesn't match SQLAlchemy's default naming convention, we must define it explicitly.

    In our `Users` model, the database has a constraint named `users_email_key`. The `unique=True` parameter on a `Field` would cause Alembic to expect a different, auto-generated name. To align the model with the database, we define it in `__table_args__`.

    ```python
    # Example from our Users model
    class Users(SQLModel, table=True):
        __table_args__ = (
            UniqueConstraint('email', name='users_email_key'),
        )

        # ... field definitions
        email: str = Field(max_length=255, index=True, nullable=False)
    ```

2.  **Check Constraints (`CheckConstraint`):** To enforce complex data validation rules at the database level.
    ```python
    # Example from our Recipe model
    __table_args__ = (
        CheckConstraint("portion_size_grams IS NULL OR portion_size_grams > 0", name="positive_portion_size_grams"),
    )
    ```

3.  **Explicitly Named Indexes (`Index`):** When you need to control the exact name of an index to match an existing database or to avoid naming conflicts. This is a key use case in our project.

    In our `Recipe` model, the database has indexes named with an `idx_` prefix (e.g., `idx_recipes_batch_number`). However, the default naming convention used by SQLAlchemy would expect `ix_recipes_batch_number`. To resolve this mismatch without generating a new migration, we explicitly define the index with its correct name in `__table_args__`.

    ```python
    # Example from our Recipe model
    class Recipe(SQLModel, table=True):
        __table_args__ = (
            # ... other constraints
            Index('idx_recipes_batch_number', 'batch_number'),
        )

        # ... field definitions
        batch_number: str | None = Field(default=None, max_length=100) # Note: index=True is removed here
    ```

### 7. **sa_column_kwargs parameter in SQLModel's Field()**

We use `sa_column_kwargs` instead of `sa_column=Column()` to modify the SQLAlchemy Column that SQLModel creates automatically, rather than completely **replacing** it.

Example: By using:

```python
sa_column_kwargs={"server_default": text("gen_random_uuid()")}
```
you are simply saying: "Hey SQLModel, go ahead and create the primary key column as you normally do, but just add this one extra argument (server_default) to it."

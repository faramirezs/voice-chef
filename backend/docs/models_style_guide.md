# ORM Models Style Guide

## Table of Contents

- [1. ID and Default Value Generation](#1-id-and-default-value-generation)
- [2. Usage of `Field()` vs. `sa_column`](#2-usage-of-field-vs-sa_column)
- [3. `Column` vs. `mapped_column`](#3-column-vs-mapped_column)
- [4. Declaring Simple Nullable Fields](#4-declaring-simple-nullable-fields)
- [5. When to use `__table_args__`](#5-when-to-use-__table_args__)
  - [5.1. Explicitly Named Unique Constraints (`UniqueConstraint`)](#51-explicitly-named-unique-constraints-uniqueconstraint)
  - [5.2. Check Constraints (`CheckConstraint`)](#52-check-constraints-checkconstraint)
  - [5.3. Explicitly Named Indexes (`Index`)](#53-explicitly-named-indexes-index)
  - [5.4. Explicitly Named Foreign Key Constraints (`ForeignKeyConstraint`)](#54-explicitly-named-foreign-key-constraints-foreignkeyconstraint)
- [6. Nullable Types (`Optional`)](#6-nullable-types-optional)
- [7. Relationship](#7-relationship)
- [8. sa_type](#8-sa_type)


This document outlines the conventions and best practices for creating SQLModel ORM classes in this project. The goal is to maintain a consistent and readable codebase.

### 1. ID and Default Value Generation

#### **Post-MVP rule**

We use DB-side UUID defaults.

```python
id: UUID = Field(
    default=None,
    primary_key=True,
    sa_column_kwargs={"server_default": text("gen_random_uuid()")}
)
```

### 2. Usage of `Field()` vs. `sa_column`

**Rule:** Follow this hierarchy of preference. Only move to the next level when the current one doesn't support the feature you need.

1.  **Level 1 (Preferred): Use "pure" `Field()` parameters.**
    *   **When:** For simple attributes where all database constraints are directly supported by `Field` parameters. This is the most concise and idiomatic SQLModel approach.
    *   **Parameters:** `default`, `default_factory`, `primary_key`, `index`, `unique`, `nullable`, `max_length`, `foreign_key`.

    ```python
    # Good: All constraints are available as Field parameters.
    # `max_length` here informs both the DB column and Pydantic validation.
    name: str = Field(max_length=255, index=True, nullable=False)
    ```

2.  **Level 2: Use `sa_column_kwargs` to add features.**
    *   **When:** When you are happy with the database column type SQLModel infers from your Python type hint (e.g., `UUID` -> `Uuid`), but you need to add a database-specific feature that `Field` doesn't have a parameter for.
    *   **Common Use Case:** Adding `server_default`.

    ```python
    # Good: `sa_column_kwargs` adds a DB-side default to the `Uuid` column
    # that SQLModel correctly infers from the type hint.
    id: UUID = Field(
        default=None,
        primary_key=True,
        sa_column_kwargs={"server_default": text("gen_random_uuid()")}
    )
    ```

3.  **Level 3 (Use when necessary): Use `sa_column=Column()` to replace the column.**
    *   **When:** When you need to take full control and completely replace the column that SQLModel would generate.
    *   **Reason:** This is necessary when the features you need cannot be expressed with Level 1 or 2. For example, SQLModel's `max_length` (Level 1) is a shortcut for `String(length)`, but you cannot use it in combination with `sa_column_kwargs` (Level 2). If you need both a specific string length *and* a `server_default`, you must escalate to Level 3.
    *   **Why avoid it if possible?** Using `sa_column=Column()` for everything defeats the purpose of SQLModel, which is to simplify ORM definitions by inferring columns from type hints. It makes the code more verbose and less "SQLModel-idiomatic". Reserve it for cases where it's truly needed.

    ```python
    # Correct: `sa_column=Column()` is required here because we need to 
    # define both a specific type (`String(50)`) and a `server_default`.
    # This combination cannot be achieved with Level 1 or 2.
    role: str = Field(
        sa_column=Column(
            'role',
            String(50),
            nullable=False,
            server_default=text("'editor'")
        )
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

### 4. Declaring Simple Nullable Fields

**Rule:** For a nullable field that has no other constraints or options, declare it directly without using `Field()`.

**Reasoning:** It's more concise and readable. `Field(default=None)` is redundant if that's the only parameter.

```python
# Preferred: Simple and direct
description: str | None = None

# Also acceptable, but verbose
# description: str | None = Field(default=None)
```

### 5. When to use `__table_args__`

**Rule:** Use the `__table_args__` attribute to define database constraints that cannot be described on a single column or require explicit naming that `Field()` does not support.

**Reasoning:** While `Field()` is great for simple constraints like `primary_key`, `unique`, or `foreign_key` on a single column, `__table_args__` is the standard SQLAlchemy way to handle more complex, table-wide rules.

**Common Use Cases:**

#### 5.1. Explicitly Named Unique Constraints (`UniqueConstraint`)
This follows the same logic as named indexes. If the database has a unique constraint with a specific name that doesn't match SQLAlchemy's default naming convention, we must define it explicitly.

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

#### 5.2. Check Constraints (`CheckConstraint`)
To enforce complex data validation rules at the database level.
```python
# Example from our Recipe model
__table_args__ = (
    CheckConstraint("portion_size_grams IS NULL OR portion_size_grams > 0", name="positive_portion_size_grams"),
)
```

#### 5.3. Explicitly Named Indexes (`Index`)
When you need to control the exact name of an index to match an existing database or to avoid naming conflicts. This is a key use case in our project.

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

#### 5.4. Explicitly Named Foreign Key Constraints (`ForeignKeyConstraint`)
To ensure foreign key constraints have stable, predictable names for migrations.

**Rule:** Always define foreign keys using `ForeignKeyConstraint` inside `__table_args__` to assign an explicit name.

**Reasoning:** While `Field(foreign_key="...")` is simple, it allows SQLAlchemy to auto-generate a constraint name (e.g., `users_tenant_id_fkey_...` with a random suffix). These unpredictable names are difficult to target in Alembic migrations, which can lead to errors or abandoned, unused constraints in your database.

By explicitly naming the constraint (e.g., `users_tenant_id_fkey`), we give Alembic a stable identifier to work with, making migrations that modify or drop foreign keys reliable and deterministic.

```python
# Good: Constraint is explicitly named, making migrations safe.
class Users(SQLModel, table=True):
    __table_args__ = (
        ForeignKeyConstraint(['tenant_id'], ['tenants.id'], name='users_tenant_id_fkey'),
        # ... other constraints
    )

    tenant_id: UUID = Field(sa_column=Column('tenant_id', Uuid, nullable=False))


# Avoid: Auto-generated constraint name is bad for migrations.
class Users(SQLModel, table=True):
    # ...
    tenant_id: UUID = Field(default=None, foreign_key="tenants.id")
```

### 6. Nullable Types (`Optional`)

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

### 7. Relationship

To connect a model to a Many-to-Many table (`t_ingredient_additives`), instead of `link_model`, we use `sa_relationship_kwargs`. 

`sa_relationship_kwargs` passes parameters directly to SQLAlchemy, bypassing the SQLModel's internal validation. Thus, we avoid an error: `TypeError: Boolean value of this clause is not defined`.

back_populates - ...

### 8. sa_type

Using `sa_type` is a good way to keep our SQLModel code clean and concise.

`sa_type` is a shortcut in SQLModel's `Field` for specifying the SQLAlchemy column type when you don't need other specific `Column` configurations.

**Rule**

Use `sa_type=...` when you only need to define the data type (like `Text`, `Numeric`, `Boolean`) and the database column name is the same as your model's attribute name.

Use the more verbose `sa_column=Column(...)` when you need to specify more details.

Example:
```python
description: str | None = Field(default=None, sa_type=Text)
```
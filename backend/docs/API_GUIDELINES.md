## Naming Conventions (Style)

### Endpoints

Style: **snake_case** (e.g., `/user_profiles/`)

**Pluralization** (The Industry Standard)

The rule of RESTful API design: **Resource-based naming**.

The general consensus in the industry (Google, GitHub, Stripe) is to always use plural nouns for collections.

Instead of: `/api/ingredient` ⮕ Plural: `/api/ingredients`

Why? Because `/api/ingredients` represents a collection (a cabinet of ingredients), and `/api/ingredients/{id}` represents one specific item from that collection.

### Schemas

Style: **PascalCase (or UpperCamelCase)** (e.g., `RecipeResponse`)

**Exceptions**: >   * OAuth2 Authentication: We use the standard `OAuth2PasswordRequestForm`. The generated schema name (e.g., `Body_login...`) and its fields are kept as-is to maintain compatibility with the OAuth2 protocol and OpenApi UI's built-in authorization.


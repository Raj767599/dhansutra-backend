## Architecture overview

This backend is a **local-first, production-grade starter** for the **DhanSutra** finance / budget tracker mobile app.

- **Framework**: FastAPI
- **DB**: SQLite (async SQLAlchemy 2.0), designed to migrate to PostgreSQL later
- **Migrations**: Alembic
- **Auth**: JWT access tokens + **DB-persisted refresh tokens** (rotated on refresh)
- **Testing**: pytest + httpx ASGI transport (no network, deterministic)
- **Logging**: structured JSON logs

### Layer responsibilities

- **Routers (`app/api/v1/routers`)**
  - HTTP-only concerns: parsing inputs, query params, status codes
  - Depends injection (`current_user`, db session)
  - Never implement business rules here
- **Services (`app/services`)**
  - Business rules and invariants (ownership, archived constraints, balance rules)
  - Transactional correctness (reverse/apply)
  - Orchestrate repositories and other services
- **Repositories (`app/repositories`)**
  - SQLAlchemy statements and persistence logic
  - No HTTP logic, no cross-cutting auth checks (ownership passed in)
- **Schemas (`app/schemas`)**
  - Request/response DTOs
  - No ORM objects in responses
- **Models (`app/models`)**
  - SQLAlchemy entities + relationships + constraints
- **Core (`app/core`)**
  - Configuration, DI helpers, security, logging, centralized exceptions

## Authentication design

- **Access token**: JWT signed with `JWT_SECRET_KEY` containing:
  - `sub` (user id), `tv` (token version), issuer/audience, type=`access`
- **Refresh token**:
  - Opaque random token returned once to client
  - Only its SHA-256 hash is stored in `refresh_tokens`
  - On refresh, token is **rotated**: old revoked + new inserted
- **Revocation**:
  - `User.token_version` increment (e.g., on password change) invalidates existing access tokens
  - Refresh tokens are also revokable in DB

## Transaction balance handling strategy

Balance updates are enforced in `TransactionService`:

- **Income**: source account balance \(+\) amount
- **Expense**: source account balance \(-\) amount
- **Transfer**: source \(-\) amount, destination \(+\) amount

### Updates and deletes

Edits/deletes are implemented by:

1. **Reverse** previous impact from the involved accounts
2. Validate and **apply** the new impact
3. Persist transaction changes (or soft-delete)

This guarantees correctness even across account changes in updates.

## Budget calculation strategy

Budgets are monthly:

- optional `category_id` makes it category-specific
- **spent** is computed from **expense transactions only** within the month and (optional) category
- `remaining = amount - spent`
- `usage_pct = spent/amount * 100`

## Goal progress strategy

Goals track contributions:

- `goal_contributions` is append-only history
- `SavingsGoal.current_amount` is updated with each contribution
- goal auto-completes when `current_amount >= target_amount`

## Testing strategy

- Uses a **separate SQLite DB file per test** (`tmp_path/test.db`)
- Creates schema via `Base.metadata.create_all` for speed and determinism
- Tests:
  - auth, profile, settings
  - CRUD for accounts/categories/transactions/budgets/goals
  - balance reversal correctness
  - analytics/dashboard aggregations

## Future scalability notes

- **Rate limiting**: best added at the API gateway or middleware layer later (not included)
- **PostgreSQL migration**:
  - swap `DATABASE_URL` to `postgresql+asyncpg://...`
  - run Alembic migrations against Postgres
  - keep types/indexes/relationships; remove SQLite-specific grouping functions where needed


## DhanSutra backend (FastAPI)

Production-grade local-first backend starter for the **DhanSutra** finance / budget tracker mobile app.

### Tech stack

- FastAPI
- SQLite + SQLAlchemy 2.0 (async)
- Alembic migrations
- Pydantic v2
- pytest + httpx
- structured JSON logging
- `.env` configuration
- GitHub Actions CI/CD (no containers)
- ruff + black + mypy + coverage

### Local setup (venv)

From `backend/`:

```bash
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install -U pip
python -m pip install -e ".[dev]"
```

Copy env:

```bash
copy .env.example .env
```

### Migrations

```bash
make migrate
```

### Run API

```bash
make run
```

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

#### Using Swagger "Authorize" (JWT Bearer)

1. Call `POST /api/v1/auth/login` to get an `access_token`
2. Open Swagger UI (`/docs`)
3. Click **Authorize**
4. Paste: `Bearer <access_token>`
5. Execute authenticated endpoints directly from Swagger

### Seed demo data

```bash
make seed
```

Creates:
- demo user: `demo@finance.local` / `DemoPassword1!`
- system categories, accounts, transactions, budgets, goal + contributions

### Run tests

```bash
make test
```

### Architecture

See:
- `docs/architecture.md`
- `docs/api_mapping.md`
- `docs/frontend_handoff.md`
- `docs/ci_cd.md`
- `docs/contribution_guide.md`
- `docs/release_process.md`

### Notes on future PostgreSQL migration

- Replace `DATABASE_URL` with `postgresql+asyncpg://...`
- Run Alembic migrations on Postgres
- Most code remains unchanged (SQLAlchemy core + repos/services); only SQLite-specific date grouping may need adjustment for analytics.



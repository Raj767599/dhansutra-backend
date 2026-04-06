## Contribution guide

### Local setup

From `backend/`:

```bash
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install -U pip
python -m pip install -e ".[dev]"
copy .env.example .env
```

### Coding rules

- Routers handle HTTP concerns only
- Business logic belongs in services
- DB access belongs in repositories
- Do not return ORM models directly from endpoints
- Preserve user isolation everywhere

### Branch naming

- `feature/<name>`
- `fix/<name>`
- `chore/<name>`

### Commit / PR expectations

- Prefer small PRs with clear descriptions
- Add/adjust tests for behavioral changes
- Update docs when API contracts change

### Testing expectations

- Run `make test` (or `make ci`) locally before PR
- No flaky tests; keep fixtures deterministic

### Lint/typecheck expectations

- `make lint`
- `make typecheck`
- `make format-check`


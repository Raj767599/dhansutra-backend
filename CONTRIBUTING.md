## Contributing

### Setup

From `backend/`:

```bash
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install -U pip
python -m pip install -e ".[dev]"
```

### Code quality

Run locally before opening a PR:

```bash
make ci
```

Optional (recommended) pre-commit:

```bash
python -m pip install pre-commit
pre-commit install
```

### Branching

Suggested:
- `feature/<short-name>`
- `fix/<short-name>`
- `chore/<short-name>`

### PR expectations

- Keep changes scoped
- Add/adjust tests for behavior changes
- Update docs if endpoints or contracts change


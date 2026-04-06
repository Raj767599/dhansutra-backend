## CI/CD

This repo is **local-first** and does not use Docker/Kubernetes. CI/CD is designed for:
- fast feedback on PRs
- safe packaging on version tags

### CI workflow (`.github/workflows/ci.yml`)

Triggers:
- pull requests
- pushes to `main` and `develop`

Runs:
- `ruff` lint
- `black --check` and `ruff format --check`
- `mypy`
- `pytest` with coverage (`coverage.xml` uploaded as artifact)

### CD workflow (`.github/workflows/cd.yml`)

Triggers:
- git tags matching `v*` (e.g., `v0.1.0`)

Runs:
- builds `sdist` and `wheel` via `python -m build`
- attaches artifacts to a GitHub Release

No cloud deployment is assumed. Deployment is manual (see `docs/release_process.md`).

### Branch strategy assumptions

- `main`: stable, release-ready
- `develop`: integration branch
- feature branches: PR into `develop` or `main` (team preference)

### Required secrets

None required for CI/CD as configured.

### Run CI checks locally

From `backend/`:

```bash
make ci
```


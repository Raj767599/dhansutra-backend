## Release process

### Version bump

1. Update `backend/pyproject.toml` version
2. Update `CHANGELOG.md` under a new version heading

### Tag + release

Create a tag `vX.Y.Z`:

```bash
git tag v0.1.0
git push origin v0.1.0
```

This triggers the CD workflow, which:
- builds `sdist` and `wheel`
- attaches them to a GitHub Release

### Manual deployment guidance (local-first)

Recommended production deployment pattern (no containers assumed):
- provision a Linux VM
- install Python + create venv
- install wheel from GitHub Release artifacts
- configure `.env` (use strong `JWT_SECRET_KEY`, production DB URL, log level)
- run via a process manager (e.g., `systemd`) and a reverse proxy if needed

### Rollback (documentation-level)

- redeploy previous release artifact
- point service back to previous code version
- database migrations: ensure downgrade strategy before applying destructive schema changes


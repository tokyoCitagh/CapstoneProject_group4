Cleanup and Revert Instructions (run after successful migration)

This file contains safe, copy-paste instructions to remove the temporary `/store/run-migrations/` endpoint and related changes after you have successfully applied the migrations on production.

1) Revert the commit that added the endpoint

The commit that added the endpoint was pushed as `fce87a2` on `main` (see push output). To revert that commit:

```bash
cd /Users/mac/Documents/EcomApp
# Create a branch as a safe backup
git checkout -b cleanup/remove-run-migrations

# Revert the commit that added the endpoint
git revert fce87a2 --no-edit

# Push the revert branch or merge to main as you prefer
git push origin cleanup/remove-run-migrations
# Optionally create a PR and merge, or push directly to main:
# git checkout main
# git merge cleanup/remove-run-migrations
# git push origin main
```

2) Redeploy the `web` service

```bash
railway redeploy --service web --yes
```

3) Verify the endpoint is gone

```bash
curl -i https://web-production-20e5.up.railway.app/store/run-migrations/ || true
# Expect 404 or redirect
```

---

If you prefer to remove the endpoint manually instead of reverting the commit, remove the `path('run-migrations/', ...)` line from `store/urls.py` and remove the `run_migrations` view from `store/views.py`, then commit and push.

Security note: The `run-migrations` endpoint is intentionally temporary. Do not leave it enabled in production after you have applied and verified migrations.

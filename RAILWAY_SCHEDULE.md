Scheduling session cleanup on Railway
===================================

This project provides a management command to clear expired sessions:

  python manage.py cleanup_sessions

We recommend running this once daily to avoid DB session table growth.

Railway scheduled job example
-----------------------------

1. Open your Railway project dashboard and go to the **Schedules** (or **Jobs**) section.
2. Create a new scheduled job with these values:

   - **Command**: `python manage.py cleanup_sessions`
   - **Service**: `web` (or a designated worker service)
   - **Environment**: `production`
   - **Schedule**: `0 3 * * *`  (run daily at 03:00 UTC) — adjust to your timezone
   - **Timeout**: 60s (default) or higher if you expect DB operations to take longer

3. Save the job. Railway will execute the command in the chosen service environment on schedule.

Alternate: Use Railway CLI to run the command manually (ad-hoc):

```bash
railway run --service web -- bash -lc "python manage.py cleanup_sessions"
```

Notes
-----
- The management command delegates to Django's built-in `clearsessions` which removes session rows whose expiry date has passed.
- If you enable `SESSION_ENSURE_ENABLED` (see `my_ecommerce_site/settings.py`), the site will create lightweight sessions for anonymous HTML visitors. Running `cleanup_sessions` daily will remove expired sessions created by that behavior.

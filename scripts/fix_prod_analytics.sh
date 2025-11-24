#!/usr/bin/env bash
set -euo pipefail

# fix_prod_analytics.sh
# Run this inside your production service shell (Railway "Run" or your server)
# It will: show migrations, attempt a DB backup (if pg_dump available), run migrate,
# verify PageView table rows, and POST a test pageview to the record endpoint.
# Usage: run this from your project root where manage.py is located.

echo "Running production analytics fix script"

if [ ! -f manage.py ]; then
  echo "Error: must be run from project root where manage.py exists" >&2
  exit 1
fi

echo "1) Show store migrations"
python manage.py showmigrations store || true

echo
echo "2) Attempt DB backup if pg_dump available and DATABASE_URL is set"
if command -v pg_dump >/dev/null 2>&1 && [ -n "${DATABASE_URL-}" ]; then
  BACKUP_FILE="/tmp/db-backup-$(date +%F_%H%M%S).dump"
  echo "pg_dump found and DATABASE_URL present — creating binary backup to $BACKUP_FILE"
  pg_dump "$DATABASE_URL" -Fc -f "$BACKUP_FILE" && echo "Backup saved to $BACKUP_FILE"
else
  echo "pg_dump not available or DATABASE_URL not set — skipping DB backup. Proceed with caution."
fi

echo
echo "3) Run migrations"
set +e
MIGRATE_OUT=$(python manage.py migrate --noinput 2>&1)
MIGRATE_EXIT=$?
set -e
echo "$MIGRATE_OUT"

if [ $MIGRATE_EXIT -ne 0 ]; then
  echo "migrate exited with code $MIGRATE_EXIT"
  # Common case: index already exists — try faking the index migration if present
  if echo "$MIGRATE_OUT" | grep -i "index .* already exists" >/dev/null 2>&1; then
    echo "Detected index exists error. Attempting to fake the index migration '0012_pageview_indexes' if present."
    python manage.py migrate store 0012_pageview_indexes --fake || true
    echo "Retrying migrate"
    python manage.py migrate --noinput
  else
    echo "Unexpected migrate error. Please inspect output above or paste here for help." >&2
    exit $MIGRATE_EXIT
  fi
fi

echo
echo "4) Verify PageView table and counts"
python manage.py shell -c "from django.db.models import Count; from store.models import PageView; print('total pageviews:', PageView.objects.count()); print('top paths:', list(PageView.objects.values('path').annotate(c=Count('id')).order_by('-c')[:20])); print('latest 10 rows:', list(PageView.objects.order_by('-timestamp').values('path','title','session_key','ip_address')[:10]))"

echo
echo "5) Test the record endpoint (local request from this host)"
if command -v curl >/dev/null 2>&1; then
  # Attempt to use the public URL if RAILWAY_STATIC_URL is present, else prompt
  PROD_URL=${PRODUCTION_PUBLIC_URL-}
  if [ -z "$PROD_URL" ]; then
    echo "No PRODUCTION_PUBLIC_URL environment variable set. Please set PRODUCTION_PUBLIC_URL to your public site URL (e.g. https://your.up.railway.app)"
    echo "Skipping remote POST test. You can run: curl -i -X POST 'https://<your>/store/analytics/record/' -H \"Content-Type: application/json\" -d '{\"path\":\"/store/\",\"title\":\"Prod test\",\"duration\":0.1}'"
  else
    echo "Posting test pageview to $PROD_URL/store/analytics/record/"
    curl -i -m 10 -X POST "$PROD_URL/store/analytics/record/" -H "Content-Type: application/json" -d '{"path":"/store/","title":"Prod test","duration":0.1}' || true
  fi
else
  echo "curl not available; unable to POST test. Run the curl command from your machine instead."
fi

echo
echo "Script complete. If any step failed, please copy the output here and I'll advise next steps."

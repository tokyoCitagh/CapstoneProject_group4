#!/bin/bash
# Quick command to sync database from Railway
# Usage: ./quick_sync.sh

echo "🔄 Starting quick database sync from Railway..."
echo ""

# Run the main sync script
./sync_db.sh

echo ""
echo "🎉 Done! Your local database is now up to date."
echo ""
echo "Start your server with:"
echo "  python manage.py runserver 8001"
echo ""
echo "Access your site at:"
echo "  http://127.0.0.1:8001/"
echo ""

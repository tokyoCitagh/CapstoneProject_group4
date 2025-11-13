#!/bin/bash
# Script to sync Railway database to local SQLite
# This will download all data from Railway and restore it locally

set -e

echo "=========================================="
echo "Railway to Local Database Sync"
echo "=========================================="
echo ""

# Check if railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Install it first:"
    echo "npm install -g @railway/cli"
    exit 1
fi

echo "Step 1: Backing up current local database..."
if [ -f "db.sqlite3" ]; then
    backup_name="db.sqlite3.backup_$(date +%s)"
    cp db.sqlite3 "$backup_name"
    echo "✅ Backed up to $backup_name"
else
    echo "ℹ️  No existing database to backup"
fi
echo ""

echo "Step 2: Exporting data from Railway..."
echo "This will create railway_dump.json..."

# Export data from Railway using dumpdata
railway run python manage.py dumpdata \
    --natural-foreign \
    --natural-primary \
    --indent 2 \
    --exclude contenttypes \
    --exclude auth.permission \
    --exclude admin.logentry \
    --exclude sessions.session \
    > railway_dump.json

echo "✅ Data exported from Railway"
echo ""

echo "Step 3: Creating fresh local database..."
rm -f db.sqlite3
python manage.py migrate --run-syncdb
echo "✅ Database structure created"
echo ""

echo "Step 4: Loading Railway data into local database..."
python manage.py loaddata railway_dump.json
echo "✅ Data loaded successfully"
echo ""

echo "=========================================="
echo "Sync Complete! ✅"
echo "=========================================="
echo ""
echo "Your local database now has all data from Railway:"
echo "  • Products"
echo "  • Orders"
echo "  • Customers"
echo "  • Categories"
echo "  • Service Requests"
echo ""
echo "⚠️  Important: Images are in Cloudinary"
echo "They will load automatically if you have Cloudinary"
echo "credentials in your .env file."
echo ""
echo "Need local Cloudinary access? Add to .env:"
echo "  USE_CLOUDINARY=true"
echo "  CLOUDINARY_URL=<get from Railway variables>"
echo ""

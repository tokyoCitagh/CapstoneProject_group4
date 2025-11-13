#!/usr/bin/env python
"""
Script to sync Railway PostgreSQL database to local SQLite database.
This will download all products, orders, customers, and other data from Railway.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_ecommerce_site.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.core.management import call_command
import subprocess
import json

def main():
    print("=" * 60)
    print("Railway Database Sync Tool")
    print("=" * 60)
    print()
    
    # Step 1: Get Railway database URL
    print("Step 1: Getting Railway database credentials...")
    try:
        result = subprocess.run(
            ['railway', 'variables', '--json'],
            capture_output=True,
            text=True,
            check=True
        )
        variables = json.loads(result.stdout)
        database_url = variables.get('DATABASE_URL')
        
        if not database_url:
            print("❌ DATABASE_URL not found in Railway variables")
            return
        
        print(f"✅ Found Railway database")
        print()
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error getting Railway variables: {e}")
        print("Make sure you're logged in: railway login")
        return
    except json.JSONDecodeError:
        print("❌ Error parsing Railway variables")
        return
    
    # Step 2: Backup current local database
    print("Step 2: Backing up current local database...")
    if os.path.exists('db.sqlite3'):
        backup_name = f'db.sqlite3.backup_{int(os.path.getmtime("db.sqlite3"))}'
        os.rename('db.sqlite3', backup_name)
        print(f"✅ Backed up to {backup_name}")
    else:
        print("ℹ️  No existing database to backup")
    print()
    
    # Step 3: Create new empty database
    print("Step 3: Creating fresh local database...")
    call_command('migrate', '--run-syncdb')
    print("✅ Database structure created")
    print()
    
    # Step 4: Dump data from Railway
    print("Step 4: Downloading data from Railway...")
    print("This may take a few minutes...")
    
    try:
        # Use Railway run to execute dumpdata on production
        dump_file = 'railway_data.json'
        
        # Dump only the data we need (exclude contenttypes, sessions, admin logs)
        apps_to_dump = [
            'store',
            'services',
            'auth.user',
            'allauth.emailaddress',
        ]
        
        cmd = [
            'railway', 'run',
            'python', 'manage.py', 'dumpdata',
            '--natural-foreign', '--natural-primary',
            '--indent', '2',
            '-o', dump_file
        ] + apps_to_dump
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Error dumping data: {result.stderr}")
            return
        
        # Download the file
        subprocess.run(['railway', 'run', 'cat', dump_file], 
                      stdout=open(dump_file, 'w'), check=True)
        
        print(f"✅ Data downloaded to {dump_file}")
        print()
        
    except Exception as e:
        print(f"❌ Error downloading data: {e}")
        return
    
    # Step 5: Load data into local database
    print("Step 5: Loading data into local database...")
    try:
        call_command('loaddata', dump_file)
        print("✅ Data loaded successfully")
        print()
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        print("You may need to fix conflicts manually")
        return
    
    # Step 6: Summary
    print("=" * 60)
    print("Sync Complete! ✅")
    print("=" * 60)
    print()
    print("Your local database now matches Railway production.")
    print()
    print("⚠️  Note about images:")
    print("Images are stored in Cloudinary and will load from there.")
    print("Make sure USE_CLOUDINARY=true in your .env file.")
    print()
    print("To use local storage instead:")
    print("1. Set USE_CLOUDINARY=false in .env")
    print("2. Download images from Cloudinary manually")
    print()

if __name__ == '__main__':
    main()

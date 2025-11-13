from django.core.management.base import BaseCommand, CommandError
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db import transaction
import os

from store.models import ProductImage


class Command(BaseCommand):
    help = (
        "Migrate ProductImage files that live on the old/default filesystem storage"
        " into the currently configured default storage (e.g. Cloudinary)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            dest='dry_run',
            default=False,
            help='Show what would be migrated without performing uploads.',
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        qs = ProductImage.objects.all()
        total = qs.count()
        if total == 0:
            self.stdout.write('No ProductImage records found.')
            return

        self.stdout.write(f'Found {total} ProductImage records. Dry run: {dry_run}')
        migrated = 0
        skipped = 0

        for pi in qs:
            name = pi.image.name
            if not name:
                self.stdout.write(f'SKIP id={pi.pk}: no image.name')
                skipped += 1
                continue

            storage_class_name = pi.image.storage.__class__.__name__
            # If the image already appears to be stored via the current default
            # storage class, skip it. We only act on images stored via the
            # local/default filesystem (DefaultStorage/FileSystemStorage).
            default_cls_name = default_storage.__class__.__name__

            if storage_class_name == default_cls_name:
                self.stdout.write(f'SKIP id={pi.pk}: already using default storage ({storage_class_name})')
                skipped += 1
                continue

            # Only attempt migration for common filesystem-backed names
            # (e.g. names starting with 'site_static/' or 'product_photos/' etc.)
            basename = os.path.basename(name)

            try:
                # Attempt to open the file from the current storage (may fail if
                # files are not available in the running container).
                with pi.image.storage.open(name, 'rb') as fh:
                    content = fh.read()
            except Exception as e:
                self.stdout.write(f'FAIL id={pi.pk}: could not read "{name}" from {storage_class_name}: {e}')
                skipped += 1
                continue

            self.stdout.write(f'WILL MIGRATE id={pi.pk}: "{name}" -> new name "{basename}"')

            if dry_run:
                migrated += 1
                continue

            # Perform actual upload to the current default_storage
            try:
                with transaction.atomic():
                    saved_name = default_storage.save(basename, ContentFile(content))
                    # Update the DB record to point to the newly saved file
                    pi.image.name = saved_name
                    pi.save(update_fields=['image'])
                    migrated += 1
                    self.stdout.write(f'MIGRATED id={pi.pk}: saved as "{saved_name}"')
            except Exception as e:
                self.stdout.write(f'ERROR id={pi.pk}: failed to save to default storage: {e}')
                skipped += 1

        self.stdout.write('')
        self.stdout.write(f'Done. Migrated: {migrated}. Skipped: {skipped}.')
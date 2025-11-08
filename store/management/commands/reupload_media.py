from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.files import File
from store.models import ProductImage
import os


class Command(BaseCommand):
    help = 'Re-upload local media files to configured storage (e.g., Cloudinary) and update image fields.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--media-root',
            dest='media_root',
            help='Override settings.MEDIA_ROOT with this path (useful when running with Cloudinary enabled).',
            default=None,
        )

    def handle(self, *args, **options):
        # Allow passing an explicit media_root to override settings (useful when CLOUDINARY is enabled)
        media_root = options.get('media_root') or getattr(settings, 'MEDIA_ROOT', None)
        if not media_root:
            self.stderr.write('MEDIA_ROOT is not set in settings; aborting.')
            return

        total = 0
        uploaded = 0
        for img in ProductImage.objects.all():
            total += 1
            local_path = os.path.join(str(media_root), img.image.name)
            if os.path.exists(local_path):
                try:
                    with open(local_path, 'rb') as f:
                        img.image.save(os.path.basename(img.image.name), File(f), save=True)
                    uploaded += 1
                    self.stdout.write(self.style.SUCCESS(f'Uploaded {img.id} -> {img.image.url}'))
                except Exception as e:
                    self.stderr.write(f'Failed to upload {img.id} ({img.image.name}): {e}')
            else:
                self.stdout.write(self.style.WARNING(f'File not found locally, skipping {img.id}: {img.image.name}'))

        self.stdout.write(self.style.SUCCESS(f'Done. Processed {total} records, uploaded {uploaded} files.'))

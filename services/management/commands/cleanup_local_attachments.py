# services/management/commands/cleanup_local_attachments.py

from django.core.management.base import BaseCommand
from services.models import ServiceAttachment

class Command(BaseCommand):
    help = 'Delete service attachments that have local /media/ URLs (not on Cloudinary)'

    def handle(self, *args, **options):
        # Find all attachments with local file paths
        local_attachments = []
        
        for attachment in ServiceAttachment.objects.all():
            url = attachment.file.url
            # Local files have /media/ URLs, Cloudinary has https://res.cloudinary.com/
            if url.startswith('/media/') or not url.startswith('http'):
                local_attachments.append(attachment)
        
        count = len(local_attachments)
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('No local attachments found. All attachments are on Cloudinary!'))
            return
        
        self.stdout.write(f'Found {count} attachments with local /media/ URLs:')
        for att in local_attachments:
            self.stdout.write(f'  - Attachment #{att.id} for Request #{att.request.id}: {att.file.name}')
        
        confirm = input(f'\nDelete these {count} attachments? (yes/no): ')
        
        if confirm.lower() in ['yes', 'y']:
            deleted_count = 0
            for att in local_attachments:
                att.delete()
                deleted_count += 1
            
            self.stdout.write(self.style.SUCCESS(f'✅ Deleted {deleted_count} local attachments'))
            self.stdout.write('Users can now re-upload attachments that will be stored on Cloudinary.')
        else:
            self.stdout.write(self.style.WARNING('Cancelled. No attachments were deleted.'))

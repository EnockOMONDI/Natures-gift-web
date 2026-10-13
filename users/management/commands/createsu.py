# File: createsu.py
# Custom management command to create superuser for NaturesGift Expeditions
#
import os
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Creates a superuser for NaturesGift Expeditions.'

    def handle(self, *args, **options):
        # Use environment variables for credentials, with fallbacks
        username = os.getenv('DJANGO_SUPERUSER_USERNAME', 'naturesgiftexpeditions')
        email = os.getenv('DJANGO_SUPERUSER_EMAIL', 'admin@naturesgiftexpeditions.com')
        password = os.getenv('DJANGO_SUPERUSER_PASSWORD', 'naturesgiftexpeditionspassword')

        if not User.objects.filter(username=username).exists():
            try:
                User.objects.create_superuser(
                    username=username,
                    email=email,
                    password=password
                )
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Superuser "{username}" has been created successfully.')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Error creating superuser: {e}')
                )
        else:
            self.stdout.write(
                self.style.WARNING(f'⚠️  Superuser "{username}" already exists. Skipped.')
            )

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Create demo user for testing'

    def handle(self, *args, **options):
        # Create demo user if it doesn't exist
        if not User.objects.filter(username='demo').exists():
            User.objects.create_user(
                username='demo',
                password='demo123',
                email='demo@example.com',
                first_name='Demo',
                last_name='User'
            )
            self.stdout.write(
                self.style.SUCCESS('Successfully created demo user')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Demo user already exists')
            )
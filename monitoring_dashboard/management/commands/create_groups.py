# monitoring_dashboard/management/commands/create_groups.py

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group

class Command(BaseCommand):
    help = 'Creates initial groups for the application'

    def handle(self, *args, **kwargs):
        operators_group, created = Group.objects.get_or_create(name='Operators')
        if created:
            self.stdout.write(self.style.SUCCESS('Operators group created successfully'))
        else:
            self.stdout.write(self.style.WARNING('Operators group already exists'))

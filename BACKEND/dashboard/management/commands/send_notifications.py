from django.core.management.base import BaseCommand
from dashboard.tasks import send_periodic_notifications

class Command(BaseCommand):
    help = 'Sends periodic notifications'

    def handle(self, *args, **options):
        send_periodic_notifications.delay()
        self.stdout.write(self.style.SUCCESS('Successfully sent notifications'))

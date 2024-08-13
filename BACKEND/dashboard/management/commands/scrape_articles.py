from django.core.management.base import BaseCommand
from dashboard.scrape_articles import scrape_articles

class Command(BaseCommand):
    help = 'Fetch and import articles from various websites into the database'

    def handle(self, *args, **kwargs):
        try:
            scrape_articles()
            self.stdout.write(self.style.SUCCESS('Successfully scraped articles'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'An error occurred: {e}'))
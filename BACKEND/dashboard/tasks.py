from celery import shared_task

@shared_task(name='dashboard.tasks.scrape_articles')
def scrape_articles_task():
    from .scrape_articles import scrape_articles
    scrape_articles()

from dashboard.views import send_read_later_reminders, send_weekly_summary

@shared_task(name='dashboard.tasks.send_periodic_notifications')
def send_periodic_notifications():
    send_read_later_reminders()
    send_weekly_summary()

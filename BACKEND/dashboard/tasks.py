from celery import shared_task

@shared_task(name='dashboard.tasks.scrape_articles')
def scrape_articles_task():
    from .scrape_articles import scrape_articles
    scrape_articles()
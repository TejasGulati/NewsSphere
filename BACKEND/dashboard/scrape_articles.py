from functools import wraps
import logging
import requests
import requests_cache
from bs4 import BeautifulSoup
from django.utils import timezone
from dashboard.models import Article
import re
from urllib.parse import urljoin
import random
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import urllib3
import json
import lxml
from lxml import etree

# Disable SSL warnings (use with caution)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Set up caching
requests_cache.install_cache('news_cache', expire_after=3600)  # Cache for 1 hour

# Define the lists of websites by category
WEBSITES = {
    'technology': [
        'https://www.medianama.com/',
        'https://www.news18.com/technology/',
        'https://www.theverge.com/tech',
        'https://www.cnet.com/tech/',
        'https://www.techcrunch.com/',
        'https://www.wired.com/',
    ],
    'sports': [
        'https://www.news18.com/sports/',
        'https://www.indianexpress.com/sports/',
        'https://www.espn.com/',
        'https://www.skysports.com/',
        'https://www.bbc.com/sport',
        'https://www.cbssports.com/',
        'https://www.foxsports.com/',
    ],
    'entertainment': [
        'https://www.radioandmusic.com/',
        'https://www.news18.com/movies/',
        'https://www.news18.com/entertainment/',
        'https://variety.com/',
        'https://www.ew.com/',
    ],
    'politics': [
        'https://www.washingtonpost.com/politics/',
        'https://www.news18.com/politics/',
        'https://www.msnbc.com/',
        'https://www.politico.com/',
        'https://www.theguardian.com/us-news/us-politics',
        'https://www.bbc.com/news/politics',
        'https://www.aljazeera.com/politics/',
        'https://www.reuters.com/politics/'
    ],
    'science': [
        'https://www.scientificamerican.com/',
        'https://www.sciencenews.org/',
        'https://www.livescience.com/',
        'https://www.nationalgeographic.com/science',
        'https://www.sciencedaily.com/',
        'https://www.newscientist.com/',
        'https://www.space.com/',
        'https://www.discovermagazine.com/',
        'https://www.popularmechanics.com/science/'
    ]
}


MAX_ARTICLES_PER_CATEGORY = 250

def retry_request(max_retries=5, backoff_factor=0.5):
    """Decorator to retry failed requests with exponential backoff."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except requests.exceptions.RequestException as e:
                    wait = backoff_factor * (2 ** retries)
                    logger.warning(f"Request failed. Retrying in {wait:.2f} seconds...")
                    time.sleep(wait)
                    retries += 1
            logger.error("Max retries reached. Request failed.")
            return None
        return wrapper
    return decorator

@retry_request(max_retries=5, backoff_factor=0.5)
def make_request(session, url):
    """Make a GET request with retries and SSL verification disabled."""
    return session.get(url, timeout=30, verify=False)  # Disable SSL verification

def clean_text(text):
    """Remove extra whitespace, special characters, and HTML/XML tags."""
    if not isinstance(text, str):
        return ""
    
    # Remove HTML/XML tags using BeautifulSoup
    soup = BeautifulSoup(text, 'html.parser')
    text = soup.get_text()
    
    # Remove extra whitespace and specific special characters
    text = re.sub(r'\s+', ' ', text).strip()
    text = re.sub(r'[\'"""\'•]', '', text)
    
    return text


def extract_summary(article_soup, title):
    """Extract and summarize article content while ensuring relevance to the title."""
    try:
        # Check for JSON-LD data
        json_ld = article_soup.find('script', type='application/ld+json')
        if json_ld and json_ld.string:
            try:
                data = json.loads(json_ld.string)
                if isinstance(data, list):
                    data = data[0]  # Some sites use a list of JSON-LD objects
                if isinstance(data, dict) and 'description' in data:
                    return clean_text(data['description'])
            except json.JSONDecodeError:
                logger.warning("Failed to parse JSON-LD data")

        main_content = article_soup.find(['article', 'main', 'div', 'section'], class_=re.compile(r'(content|article|story|post-content)'))
        if not main_content:
            main_content = article_soup

        # Extract text from paragraphs and list items
        content = []
        for elem in main_content.find_all(['p', 'li', 'h2', 'h3']):
            if not elem.find(['script', 'style']):
                text = elem.get_text(strip=True)
                if len(text) > 20:
                    if elem.name == 'li':
                        content.append(f"• {text}")
                    elif elem.name in ['h2', 'h3']:
                        content.append(f"\n{text}\n")
                    else:
                        content.append(text)

        text_content = ' '.join(content)

        # Remove specific metadata mentions and phrases
        metadata_patterns = [
            r'Published By:.*',
            r'Last Updated:.*',
            r'Trending Desk.*',
            r'Updated By:.*',
            r'Writtend By:.*',
            r'Updated on:.*',
            r'Curated By:.*',
            r'Created By:.*',
            r'End-to-end encryption.*',
            r'Privacy control.*',
            r'Free* in calls.*',
            r'^\w+ \d{1,2}:\d{2} (am|pm) IST.*',
            r'Subscribe.*',
            r'Enroll.*',
            r'Join.*',
            r'Sign Up.*',
            r'Register.*',
            r'Get Started.*',
            r'Start Your Free Trial.*',
            r'Free Access.*',
            r'Advertisement.*',
            r'Become a Member.*',
            r'Unlimited Access.*',
            r'MEDIANAMA.*',
            r'\b\d{1,2} \w{3,9} \d{4}\b',
            r'\b\d{1,2} min read\b',
            r'\b\d{1,2} \w{3,9} \d{4}\b.*\b\d{1,2} min read\b',
            r'UPDATE \(.*\)',
            r'To revisit this article, visit My Profile, thenView saved stories',
            r'By\s*\.{3,}',
        ]

        for pattern in metadata_patterns:
            text_content = re.sub(pattern, '', text_content, flags=re.IGNORECASE)

        if text_content:
            # Check relevance to title
            title_keywords = set(re.findall(r'\w+', title.lower()))
            content_keywords = set(re.findall(r'\w+', text_content.lower()))
            relevance_score = len(title_keywords.intersection(content_keywords)) / len(title_keywords)

            if relevance_score < 0.3:
                logger.warning(f"Low relevance score ({relevance_score}) for article: {title}")
                return 'Content may not be relevant to the title'

            sentences = re.split(r'(?<=[.!?])\s+', text_content)
            if len(sentences) > 15:
                summary = ' '.join(sentences[:15]) + '... [Click on source to read more.]'
            else:
                summary = text_content
            
            return clean_text(summary)

        return 'No summary available'
    except Exception as e:
        logger.error(f"Error extracting summary: {e}")
        return 'Error extracting summary'

def extract_media(article_soup, base_url):
    """Extract media URL from article."""
    try:
        media_url = None
        og_image = article_soup.find('meta', property='og:image')
        if og_image and og_image.get('content'):
            media_url = og_image['content']

        if not media_url:
            schema_image = article_soup.find('meta', itemprop='image')
            if schema_image and schema_image.get('content'):
                media_url = schema_image['content']

        if not media_url:
            img_tag = article_soup.find('img', class_=re.compile(r'(featured|hero|main)'))
            if img_tag and img_tag.get('src'):
                media_url = img_tag['src']

        if media_url and not media_url.startswith(('http', 'https')):
            media_url = urljoin(base_url, media_url)

        return media_url
    except Exception as e:
        logger.error(f"Error extracting media: {e}")
        return None

def get_article_content(session, article_url):
    """Fetch and parse article content with improved error handling and retries."""
    try:
        response = make_request(session, article_url)
        if response is None:
            return None
        content = response.text
        article_soup = BeautifulSoup(content, 'lxml')
        return article_soup
    except Exception as e:
        logger.error(f"Unexpected error while fetching article: {article_url}. Error: {e}")
    return None

def fetch_articles_from_page(session, category, page_url, max_articles_per_page=50):
    """Fetch articles from a single page with improved content extraction and error handling."""
    articles = []
    try:
        logger.info(f"Fetching articles from: {page_url}")
        page_soup = get_article_content(session, page_url)
        if page_soup:
            # Extract article links from the page
            article_links = set(
                urljoin(page_url, a['href'])
                for a in page_soup.find_all('a', href=True)
                if a['href'].startswith(('http', 'https')) or a['href'].startswith('/')
            )
            article_count = 0  # Counter for articles

            for link in article_links:
                if len(articles) >= MAX_ARTICLES_PER_CATEGORY or article_count >= max_articles_per_page:
                    break
                try:
                    # Fetch the detailed content of the article
                    article_soup = get_article_content(session, link)
                    if article_soup:
                        title_tag = article_soup.find('title') or article_soup.find('h1') or article_soup.find('h2')
                        title = clean_text(title_tag.get_text()) if title_tag else 'No title available'
                        summary = extract_summary(article_soup, title)
                        media_url = extract_media(article_soup, link)

                        # Check if the summary indicates low relevance
                        if summary != 'Content may not be relevant to the title':
                            if summary and media_url and summary != 'No summary available' and summary != 'Error extracting summary' and len(title.split()) > 1:
                                articles.append({
                                    'title': title,
                                    'content': summary,
                                    'media_url': media_url,
                                    'source_url': link,
                                    'category': category,
                                    'created_at': timezone.now(),
                                    'updated_at': timezone.now()
                                })
                                article_count += 1  # Increment the counter
                                time.sleep(random.uniform(1, 3))  # Add a random delay between requests
                        else:
                            logger.info(f"Skipping article due to low relevance: {title}")

                except Exception as e:
                    logger.error(f"Error processing article link {link}: {e}")
        else:
            logger.warning(f"No articles found on page: {page_url}")
    except Exception as e:
        logger.error(f"Error fetching articles from page {page_url}: {e}")
    return articles

def scrape_articles():
    """Main function to scrape articles from all categories and save to database."""
    session = requests.Session()
    retry = HTTPAdapter(max_retries=Retry(total=5, backoff_factor=0.5))
    session.mount('http://', retry)
    session.mount('https://', retry)

    for category, urls in WEBSITES.items():
        logger.info(f"Scraping category: {category}")
        category_articles = []
        for url in urls:
            articles = fetch_articles_from_page(session, category, url)
            if articles:
                category_articles.extend(articles)
            if len(category_articles) >= MAX_ARTICLES_PER_CATEGORY:
                break  # Move to the next category if the limit is reached

        # Save articles to the database
        logger.info(f"Fetched a total of {len(category_articles)} articles for category: {category}")
        for article_data in category_articles:
            try:
                Article.objects.update_or_create(
                    title=article_data['title'],
                    defaults={
                        'content': article_data['content'],
                        'media_url': article_data['media_url'],
                        'source_url': article_data['source_url'],
                        'category': article_data['category'],
                        'created_at': article_data['created_at'],
                        'updated_at': article_data['updated_at']
                    }
                )
                logger.info(f"Article '{article_data['title']}' saved to database.")
            except Exception as e:
                logger.error(f"Error saving article '{article_data['title']}': {e}")


if __name__ == "__main__":
    scrape_articles()
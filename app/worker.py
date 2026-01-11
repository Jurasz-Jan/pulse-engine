from celery import Celery
import requests
from bs4 import BeautifulSoup
from app.settings import settings

celery_app = Celery(
    "worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

@celery_app.task
def scrape_url(url: str):
    print(f"Scraping {url}...")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.extract()
            
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        print(f"Scraping complete for {url}. Length: {len(text)}")
        return text[:500] + "..." # Return preview for now
        
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return f"Error: {e}"

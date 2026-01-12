from celery import Celery
import requests
from bs4 import BeautifulSoup
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.settings import settings
from app.models import Document

celery_app = Celery(
    "worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

# Initialize embeddings model globally (loads on worker start)
embeddings_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Sync engine for worker (Celery task is blocking anyway)
sync_db_url = settings.DATABASE_URL.replace("postgresql+asyncpg", "postgresql")
engine = create_engine(sync_db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

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
        clean_text = '\n'.join(chunk for chunk in chunks if chunk)
        
        # Chunking
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        docs = text_splitter.create_documents([clean_text])
        
        print(f"Split into {len(docs)} chunks. Embedding and storing...")
        
        with SessionLocal() as session:
            for doc in docs:
                embedding = embeddings_model.embed_query(doc.page_content)
                db_doc = Document(content=doc.page_content, embedding=embedding)
                session.add(db_doc)
            session.commit()
            
        print(f"Ingestion complete for {url}.")
        return f"Ingested {len(docs)} chunks."
        
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return f"Error: {e}"

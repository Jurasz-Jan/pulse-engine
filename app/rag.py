from langchain_community.chat_models import ChatOllama
from langchain_community.embeddings import HuggingFaceEmbeddings
from sqlalchemy import select, text
from app.database import get_session
from app.models import Document

# Initialize models
llm = ChatOllama(model="llama3", base_url="http://ollama:11434")
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

async def search_docs(session, query: str, limit: int = 3):
    query_vector = embeddings.embed_query(query)
    
    # pgvector L2 distance operator <->
    stmt = select(Document).order_by(Document.embedding.l2_distance(query_vector)).limit(limit)
    result = await session.execute(stmt)
    return result.scalars().all()

async def generate_answer(query: str, context_docs):
    context_text = "\n\n".join([doc.content for doc in context_docs])
    
    prompt = f"""You are a helpful assistant. Answer the question based ONLY on the context below.
    
    Context:
    {context_text}
    
    Question: {query}
    """
    
    response = llm.invoke(prompt)
    return response.content

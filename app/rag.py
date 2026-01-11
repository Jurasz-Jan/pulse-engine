from typing import List, Dict, Any
from langchain_community.chat_models import ChatOllama
from langchain_community.embeddings import HuggingFaceEmbeddings
from sqlalchemy import select
from app.database import get_session
from app.models import Document

# Initialize models
llm = ChatOllama(model="llama3", base_url="http://ollama:11434")
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

async def search_docs(session, query: str, limit: int = 3) -> List[Document]:
    query_vector = embeddings.embed_query(query)
    stmt = select(Document).order_by(Document.embedding.l2_distance(query_vector)).limit(limit)
    result = await session.execute(stmt)
    return result.scalars().all()

async def grade_answer(query: str, context: str, answer: str) -> float:
    prompt = f"""Rate the relevance of the answer to the query based on the context. 
    Return ONLY a number between 0.0 and 1.0.
    
    Query: {query}
    Answer: {answer}
    Context: {context}
    """
    try:
        score_str = llm.invoke(prompt).content.strip()
        # Clean up any extra text if LLM ignores instructions
        import re
        match = re.search(r"0\.\d+|1\.0|0", score_str)
        return float(match.group(0)) if match else 0.5
    except:
        return 0.5

async def rewrite_query(query: str) -> str:
    prompt = f"""Rewrite this query to be more specific for a vector search. Return ONLY the new query.
    Original: {query}"""
    return llm.invoke(prompt).content.strip()

async def generate_answer(query: str, context_docs: List[Document]) -> str:
    context_text = "\n\n".join([doc.content for doc in context_docs])
    prompt = f"""You are a helpful assistant. Answer the question based ONLY on the context below.
    Context: {context_text}
    Question: {query}"""
    return llm.invoke(prompt).content

async def rag_flow(session, query: str) -> Dict[str, Any]:
    trace = []
    
    # Attempt 1
    trace.append(f"Searching for: {query}")
    docs = await search_docs(session, query)
    if not docs:
        return {"answer": "No information found.", "trace": trace, "sources": []}
        
    answer = await generate_answer(query, docs)
    trace.append("Draft answer generated.")
    
    context_text = "\n".join([d.content for d in docs])
    grade = await grade_answer(query, context_text, answer)
    trace.append(f"Grade: {grade}")
    
    if grade < 0.7:
        trace.append("Confidence low. Rewriting query...")
        new_query = await rewrite_query(query)
        trace.append(f"New Query: {new_query}")
        
        docs = await search_docs(session, new_query)
        answer = await generate_answer(new_query, docs)
        trace.append("New answer generated.")
        
    return {
        "answer": answer,
        "trace": trace,
        "sources": [doc.content[:200] + "..." for doc in docs]
    }

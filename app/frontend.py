import streamlit as st
import requests
import json
import time

# Configuration
API_URL = "http://web:8000"

st.set_page_config(page_title="Pulse - AI Knowledge Engine", layout="wide")

st.title("Pulse 🧠")
st.caption("Self-Healing Knowledge Engine")

# Sidebar - Ingestion
with st.sidebar:
    st.header("Knowledge Base")
    url_input = st.text_input("Ingest URL", placeholder="https://example.com")
    
    if st.button("Scrape & Embed"):
        if url_input:
            with st.spinner("Dispatching scraper..."):
                try:
                    res = requests.post(f"{API_URL}/scrape", json={"url": url_input})
                    if res.status_code == 200:
                        data = res.json()
                        st.success(f"Task Started! ID: {data['task_id']}")
                        st.info("Check docker logs for progress.")
                    else:
                        st.error(f"Error: {res.status_code}")
                except Exception as e:
                    st.error(f"Connection Error: {e}")

# Main - Chat
st.header("Chat with your Data")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "trace" in message:
            with st.expander("Thought Process"):
                for step in message["trace"]:
                    st.write(f"- {step}")
        if "sources" in message and message["sources"]:
             with st.expander("Sources"):
                for src in message["sources"]:
                    st.caption(src)

if prompt := st.chat_input("Ask a question..."):
    # User message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Bot response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        with st.spinner("Thinking (this may take a moment)..."):
            try:
                res = requests.post(f"{API_URL}/chat", json={"query": prompt})
                if res.status_code == 200:
                    data = res.json()
                    full_response = data["answer"]
                    trace = data.get("trace", [])
                    sources = data.get("sources", [])
                    
                    message_placeholder.markdown(full_response)
                    
                    if trace:
                        with st.expander("Thought Process"):
                            for step in trace:
                                st.write(f"- {step}")
                    if sources:
                        with st.expander("Sources"):
                             for src in sources:
                                st.caption(src)
                                
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": full_response,
                        "trace": trace,
                        "sources": sources
                    })
                else:
                    st.error(f"API Error: {res.status_code}")
            except Exception as e:
                st.error(f"Connection Error: {e}")

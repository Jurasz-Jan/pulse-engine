import streamlit as st
import requests
import json
import time

# Configuration
API_URL = "http://web:8000"

st.set_page_config(page_title="Pulse - AI Knowledge Engine", layout="wide")

st.title("Pulse 🧠")
st.caption("Local Document-based Knowledge Engine")

# Sidebar - Ingestion
with st.sidebar:
    st.header("Job History")
    if st.button("Refresh Jobs"):
        st.session_state.last_refresh = time.time()
        
    try:
        jobs_res = requests.get(f"{API_URL}/jobs")
        if jobs_res.status_code == 200:
            jobs = jobs_res.json()
            if jobs:
                # Simple display
                for job in jobs:
                    status_color = "🟢" if job['status'] == "COMPLETED" else "🔴" if job['status'] == "FAILED" else "md"
                    if job['status'] == "PENDING": status_color = "⚪"
                    if job['status'] == "PROCESSING": status_color = "aaa"
                    
                    with st.expander(f"{status_color} {job['url'][:30]}...", expanded=False):
                        st.write(f"**Status:** {job['status']}")
                        st.write(f"**Created:** {job['created_at']}")
                        if job['finished_at']:
                            st.write(f"**Finished:** {job['finished_at']}")
                        if job['result']:
                            st.caption(f"Result: {job['result']}")
            else:
                st.info("No jobs found")
        else:
            st.error("Could not fetch jobs")
    except Exception as e:
         st.warning(f"Worker unavailable? {e}")
    st.divider()

    url_input = st.text_input("Ingest URL", placeholder="https://example.com")
    
    if st.button("Scrape & Embed"):
        if url_input:
            with st.spinner("Dispatching scraper..."):
                try:
                    res = requests.post(f"{API_URL}/scrape", json={"url": url_input})
                    if res.status_code == 200:
                        data = res.json()
                        st.success(f"Task Started! ID: {data['task_id']}")
                        st.info("Ingestion runs in the background. Please wait a moment and click 'Refresh Sources' below to see the new document.")
                        
                        # Invalidate cache so the user sees the new source (eventually)
                        if "sources" in st.session_state:
                            del st.session_state["sources"]
                    else:
                        st.error(f"Error: {res.status_code}")
                except Exception as e:
                    st.error(f"Connection Error: {e}")

    st.divider()
    st.header("Manage Documents")
    
    # Refresh button
    if st.button("Refresh Sources"):
        try:
             res = requests.get(f"{API_URL}/sources")
             if res.status_code == 200:
                 st.session_state.sources = res.json()
             else:
                 st.error("Failed to fetch sources")
        except Exception as e:
            st.error(f"Error: {e}")

    # Initial fetch if not present
    if "sources" not in st.session_state:
        try:
             res = requests.get(f"{API_URL}/sources")
             if res.status_code == 200:
                 st.session_state.sources = res.json()
        except:
             pass

    # Display sources
    if "sources" in st.session_state and st.session_state.sources:
        for src in st.session_state.sources:
            col1, col2 = st.columns([3, 1])
            col1.write(src)
            if col2.button("Delete", key=src):
                try:
                    res = requests.delete(f"{API_URL}/sources", params={"source": src})
                    if res.status_code == 200:
                        st.success(f"Deleted {src}")
                        # Remove from local state
                        st.session_state.sources.remove(src)
                        st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
    else:
        st.info("No sources found.")

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

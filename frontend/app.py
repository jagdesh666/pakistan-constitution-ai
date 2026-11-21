"""
Module: frontend/app.py
Package: pakistan-constitution-ai
Purpose: Enterprise-Grade Legal Research & Statutory Analysis Interface.
"""

import streamlit as st
import requests
import uuid
import pandas as pd

import os
API_BASE_URL = os.getenv("API_BASE_URL", "https://pakistan-constitution-ai.onrender.com")

st.set_page_config(
    page_title="Pakistan Legal Intelligence Platform",
    page_icon="§",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# 1. ENTERPRISE LEGAL SAAS DESIGN SYSTEM
# -----------------------------------------------------------------------------
ENTERPRISE_UI_CSS = """
<style>
/* Base Theme & Font Stack */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    background-color: #0b0f19 !important;
    color: #e2e8f0 !important;
}

.stApp {
    background-color: #0b0f19 !important;
}

header[data-testid="stHeader"] {
    background: transparent !important;
}

/* Layout Dimensions */
.block-container {
    max-width: 1000px !important;
    padding-top: 1.8rem !important;
    padding-bottom: 6.5rem !important;
    margin: 0 auto !important;
}

/* 1. PROFESSIONAL SIDEBAR */
section[data-testid="stSidebar"] {
    background-color: #0f172a !important;
    border-right: 1px solid #1e293b !important;
}

section[data-testid="stSidebar"] div[data-testid="stSidebarContent"] {
    padding: 1.4rem !important;
}

.sidebar-title {
    font-size: 0.95rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.05em !important;
    text-transform: uppercase !important;
    color: #94a3b8 !important;
    margin-bottom: 14px !important;
}

/* Action Button */
.new-consultation-btn button {
    background-color: #1e293b !important;
    color: #f8fafc !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    border: 1px solid #334155 !important;
    border-radius: 8px !important;
    padding: 9px 14px !important;
    transition: all 0.2s ease !important;
    width: 100% !important;
}

.new-consultation-btn button:hover {
    background-color: #334155 !important;
    border-color: #475569 !important;
    color: #ffffff !important;
}

/* History Items */
.history-item button {
    background: transparent !important;
    border: 1px solid transparent !important;
    border-radius: 6px !important;
    text-align: left !important;
    color: #94a3b8 !important;
    font-size: 0.85rem !important;
    padding: 8px 10px !important;
    transition: all 0.15s ease !important;
    margin-bottom: 2px !important;
}

.history-item button:hover {
    background-color: #1e293b !important;
    color: #f1f5f9 !important;
}

.history-item-active button {
    background-color: #1e293b !important;
    border: 1px solid #334155 !important;
    color: #38bdf8 !important;
    font-weight: 600 !important;
}

/* 2. EXECUTIVE HERO HEADER */
.exec-header {
    border: 1px solid #1e293b !important;
    background: #0f172a !important;
    border-radius: 12px !important;
    padding: 22px 26px !important;
    margin-bottom: 22px !important;
}

.platform-heading {
    font-size: 1.65rem !important;
    font-weight: 700 !important;
    color: #f8fafc !important;
    letter-spacing: -0.02em !important;
    margin: 0 !important;
    display: inline-flex !important;
    align-items: center !important;
    gap: 12px !important;
}

.status-badge {
    display: inline-flex !important;
    align-items: center !important;
    gap: 6px !important;
    background: #064e3b !important;
    border: 1px solid #059669 !important;
    color: #6ee7b7 !important;
    font-size: 0.72rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.04em !important;
    text-transform: uppercase !important;
    padding: 2px 9px !important;
    border-radius: 4px !important;
    vertical-align: middle !important;
}

.status-dot {
    width: 6px !important;
    height: 6px !important;
    background: #34d399 !important;
    border-radius: 50% !important;
}

.platform-subtext {
    font-size: 0.88rem !important;
    color: #94a3b8 !important;
    margin: 6px 0 0 0 !important;
}

.telemetry-summary {
    display: flex !important;
    gap: 18px !important;
    font-size: 0.8rem !important;
    color: #94a3b8 !important;
    padding-top: 14px !important;
    margin-top: 14px !important;
    border-top: 1px solid #1e293b !important;
}

.telemetry-summary b {
    color: #cbd5e1 !important;
}

/* 3. TABS STYLING */
div[data-testid="stTabs"] button {
    font-size: 0.88rem !important;
    font-weight: 600 !important;
    color: #94a3b8 !important;
    padding: 8px 16px !important;
    border: none !important;
}

div[data-testid="stTabs"] button[aria-selected="true"] {
    color: #f8fafc !important;
    border-bottom: 2px solid #38bdf8 !important;
    background: transparent !important;
}

/* 4. CHAT MESSAGES */
div[data-testid="stChatMessage"] {
    background-color: #0f172a !important;
    border: 1px solid #1e293b !important;
    border-radius: 10px !important;
    padding: 18px 22px !important;
    margin-bottom: 16px !important;
    font-size: 0.94rem !important;
    line-height: 1.65 !important;
    color: #e2e8f0 !important;
}

div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) {
    background-color: #111c33 !important;
    border-left: 3px solid #38bdf8 !important;
}

div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-assistant"]) {
    border-left: 3px solid #10b981 !important;
}

/* 5. ELEVATED FLOATING CHAT DOCK (LIFTED OFF THE BOTTOM VIEWPORT) */
div[data-testid="stBottom"] {
    background: transparent !important;
}

.stChatInputContainer {
    border-radius: 12px !important;
    padding: 8px 14px !important;
    background-color: #0f172a !important;
    border: 1px solid #334155 !important;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.45) !important;
    margin-bottom: 1.8rem !important; /* Lifts the dock comfortably above the bottom border */
}

.stChatInputContainer:focus-within {
    border-color: #38bdf8 !important;
    box-shadow: 0 10px 35px rgba(0, 0, 0, 0.6) !important;
}

.stChatInputContainer button {
    border-radius: 6px !important;
    background-color: #1e293b !important;
    color: #f8fafc !important;
    border: 1px solid #334155 !important;
}

.stChatInputContainer button:hover {
    background-color: #334155 !important;
}

/* 6. CLEAN STATUTORY CITATION CARDS */
.statute-card {
    background-color: #111827 !important;
    border: 1px solid #1f2937 !important;
    border-left: 3px solid #10b981 !important;
    padding: 10px 14px !important;
    border-radius: 6px !important;
    margin: 6px 0 !important;
    font-size: 0.85rem !important;
}

.statute-title {
    font-weight: 600 !important;
    color: #f9fafb !important;
}

.statute-meta {
    font-size: 0.78rem !important;
    color: #9ca3af !important;
    margin-top: 2px !important;
}

/* Suggested Inquiry Chips */
.query-suggestion button {
    background-color: #111c2e !important;
    color: #94a3b8 !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    border: 1px solid #1e293b !important;
    border-radius: 6px !important;
    padding: 8px 12px !important;
    text-align: left !important;
    transition: all 0.15s ease !important;
}

.query-suggestion button:hover {
    background-color: #1e293b !important;
    color: #f8fafc !important;
    border-color: #334155 !important;
}

/* Telemetry Pills */
.telemetry-tag {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.75rem !important;
    color: #64748b !important;
    background: #0f172a !important;
    border: 1px solid #1e293b !important;
    padding: 2px 7px !important;
    border-radius: 4px !important;
    margin-right: 6px !important;
}
</style>
"""
st.markdown(ENTERPRISE_UI_CSS, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. SESSION STATE MANAGEMENT
# -----------------------------------------------------------------------------
if "session_id" not in st.session_state:
    query_params = st.query_params
    if "session_id" in query_params:
        st.session_state.session_id = query_params["session_id"]
    else:
        new_sid = str(uuid.uuid4())[:12]
        st.session_state.session_id = new_sid
        st.query_params["session_id"] = new_sid

if "messages" not in st.session_state:
    st.session_state.messages = []
    try:
        resp = requests.get(f"{API_BASE_URL}/sessions/{st.session_state.session_id}/messages", timeout=4)
        if resp.status_code == 200:
            st.session_state.messages = resp.json()
    except Exception:
        st.session_state.messages = []

if "feedback_submitted" not in st.session_state:
    st.session_state.feedback_submitted = set()
if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None

# -----------------------------------------------------------------------------
# 3. EXECUTIVE SIDEBAR
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown('<div class="sidebar-title">Research Workspace</div>', unsafe_allow_html=True)

    st.markdown('<div class="new-consultation-btn">', unsafe_allow_html=True)
    if st.button("New Consultation", use_container_width=True):
        new_sid = str(uuid.uuid4())[:12]
        st.session_state.session_id = new_sid
        st.session_state.messages = []
        st.session_state.feedback_submitted = set()
        st.session_state.pending_prompt = None
        st.query_params["session_id"] = new_sid
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.divider()
    st.markdown('<div class="sidebar-title" style="font-size: 0.78rem;">Recent Consultations</div>', unsafe_allow_html=True)

    try:
        sessions_resp = requests.get(f"{API_BASE_URL}/sessions", timeout=3)
        if sessions_resp.status_code == 200:
            all_sessions = sessions_resp.json()
            if not all_sessions:
                st.caption("No historical sessions recorded.")
            for s in all_sessions:
                is_active = (s["id"] == st.session_state.session_id)
                wrapper_class = "history-item-active" if is_active else "history-item"
                title_clean = s["title"].replace("\n", " ")[:26]

                col_s1, col_s2 = st.columns([0.84, 0.16])
                with col_s1:
                    st.markdown(f'<div class="{wrapper_class}">', unsafe_allow_html=True)
                    if st.button(title_clean, key=f"s_{s['id']}", use_container_width=True):
                        st.session_state.session_id = s["id"]
                        st.query_params["session_id"] = s["id"]
                        m_resp = requests.get(f"{API_BASE_URL}/sessions/{s['id']}/messages", timeout=4)
                        st.session_state.messages = m_resp.json() if m_resp.status_code == 200 else []
                        st.session_state.feedback_submitted = set()
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
                with col_s2:
                    if st.button("✕", key=f"del_{s['id']}", help="Delete consultation"):
                        requests.delete(f"{API_BASE_URL}/sessions/{s['id']}")
                        if s["id"] == st.session_state.session_id:
                            new_sid = str(uuid.uuid4())[:12]
                            st.session_state.session_id = new_sid
                            st.session_state.messages = []
                            st.query_params["session_id"] = new_sid
                        st.rerun()
        else:
            st.caption("Session store offline.")
    except Exception:
        st.caption("Session store offline.")

# -----------------------------------------------------------------------------
# 4. EXECUTIVE HERO HEADER
# -----------------------------------------------------------------------------
st.markdown("""
<div class="exec-header">
    <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap;">
        <div>
            <div class="platform-heading">
                Pakistan Legal Intelligence Platform
                <span class="status-badge"><span class="status-dot"></span> System Ready</span>
            </div>
            <p class="platform-subtext">
                Statutory Grounded RAG &bull; Constitution of Pakistan (1973) &bull; Pakistan Penal Code (1860) &bull; Hybrid Reciprocal Rank Fusion
            </p>
        </div>
    </div>
    <div class="telemetry-summary">
        <span>Statutory Provisions: <b>818</b></span>
        <span>Discrete Chunks: <b>2,837</b></span>
        <span>Retrieval Architecture: <b>Dense HNSW + Sparse BM25</b></span>
        <span>Inference Engine: <b>Groq LPU</b></span>
    </div>
</div>
""", unsafe_allow_html=True)

with st.expander("Statutory Compliance & Anti-Hallucination Framework"):
    st.markdown("""
    - **Strict Statutory Grounding**: Analytical assertions derive exclusively from verified statutory texts ingested in PostgreSQL.
    - **Anti-Hallucination Guardrails**: Where context is legally insufficient, the model explicitly declines extrapolation.
    - **Audit Trail Persistence**: Every query, latency profile, and citation map is committed to relational audit logs.
    """)

tab_chat, tab_explorer, tab_analytics = st.tabs([
    "Research & Consultation",
    "Statutory Codex",
    "Observability & Telemetry"
])

# -----------------------------------------------------------------------------
# TAB 1: CONVERSATIONAL RESEARCH
# -----------------------------------------------------------------------------
with tab_chat:
    # Recommended Research Inquiries (Clean, Non-Playful Buttons)
    if not st.session_state.messages:
        st.markdown("<p style='color: #64748b; font-size: 0.82rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em; margin-bottom: 8px;'>Recommended Research Inquiries</p>", unsafe_allow_html=True)
        pill_col1, pill_col2, pill_col3, pill_col4 = st.columns(4)
        with pill_col1:
            st.markdown('<div class="query-suggestion">', unsafe_allow_html=True)
            if st.button("Equality of Citizens (Art. 25)", use_container_width=True):
                st.session_state.pending_prompt = "Can citizens be discriminated against on the basis of sex under Article 25?"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with pill_col2:
            st.markdown('<div class="query-suggestion">', unsafe_allow_html=True)
            if st.button("Criminal Intimidation (PPC 506)", use_container_width=True):
                st.session_state.pending_prompt = "What is the legal definition and penalty for criminal intimidation under the PPC?"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with pill_col3:
            st.markdown('<div class="query-suggestion">', unsafe_allow_html=True)
            if st.button("Motor Vehicle Theft (PPC 381A)", use_container_width=True):
                st.session_state.pending_prompt = "What are the specific penal consequences for motor vehicle theft under PPC Section 381A?"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with pill_col4:
            st.markdown('<div class="query-suggestion">', unsafe_allow_html=True)
            if st.button("Arrest Safeguards (Art. 10)", use_container_width=True):
                st.session_state.pending_prompt = "Within what statutory timeframe must an arrested individual be produced before a magistrate?"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    # Render Conversation Thread
    for idx, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

            if msg.get("rewritten_query"):
                st.markdown(
                    f"<div style='font-size: 0.78rem; color: #64748b; margin: 6px 0;'>"
                    f"Contextual Intent Condensation: <code style='color: #38bdf8; background: #0f172a; padding: 2px 6px;'>{msg['rewritten_query']}</code>"
                    f"</div>",
                    unsafe_allow_html=True
                )

            if msg.get("citations"):
                with st.expander(f"Statutory Citations ({len(msg['citations'])})"):
                    for cit in msg["citations"]:
                        st.markdown(
                            f"""<div class="statute-card">
                                <div class="statute-title">{cit['article']} — {cit.get('title', '')}</div>
                                <div class="statute-meta">{cit.get('part', '')} | Clause {cit.get('clause', 'N/A')}</div>
                            </div>""",
                            unsafe_allow_html=True
                        )

            if "latency" in msg and msg["latency"]:
                lat = msg["latency"]
                st.markdown(
                    f"<div style='margin-top: 8px;'>"
                    f"<span class='telemetry-tag'>Total: {lat['total_ms']}ms</span>"
                    f"<span class='telemetry-tag'>Retrieval: {lat['retrieval_ms']}ms</span>"
                    f"<span class='telemetry-tag'>Inference: {lat['llm_ms']}ms</span>"
                    f"</div>",
                    unsafe_allow_html=True
                )

            # Professional Feedback Actions
            if msg["role"] == "assistant" and msg.get("request_id"):
                req_id = msg["request_id"]
                if req_id not in st.session_state.feedback_submitted:
                    fb_col1, fb_col2, _ = st.columns([0.14, 0.16, 0.70])
                    with fb_col1:
                        if st.button("Verify Accurate", key=f"up_{idx}"):
                            try:
                                requests.post(f"{API_BASE_URL}/feedback", json={"request_id": req_id, "rating": 1})
                                st.session_state.feedback_submitted.add(req_id)
                                st.rerun()
                            except Exception:
                                pass
                    with fb_col2:
                        if st.button("Report Discrepancy", key=f"down_{idx}"):
                            try:
                                requests.post(
                                    f"{API_BASE_URL}/feedback",
                                    json={"request_id": req_id, "rating": -1, "reason_category": "IRRELEVANT"}
                                )
                                st.session_state.feedback_submitted.add(req_id)
                                st.rerun()
                            except Exception:
                                pass
                else:
                    st.caption("Feedback logged to audit repository.")

    # Native Streamlit Chat Input (Elevated via Custom CSS)
    chat_input_val = st.chat_input("Enter a statutory query, legal question, or request for simplification...")
    active_prompt = chat_input_val or st.session_state.pending_prompt

    if active_prompt:
        st.session_state.pending_prompt = None

        history_payload = [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages
            if m["role"] in ["user", "assistant"]
        ]

        st.session_state.messages.append({"role": "user", "content": active_prompt})
        try:
            requests.post(
                f"{API_BASE_URL}/sessions/{st.session_state.session_id}/messages",
                json={"role": "user", "content": active_prompt},
                timeout=4
            )
        except Exception:
            pass

        with st.chat_message("user"):
            st.markdown(active_prompt)

        with st.chat_message("assistant"):
            with st.spinner("Analyzing legal corpus via hybrid retrieval and Groq LPU..."):
                try:
                    resp = requests.post(
                        f"{API_BASE_URL}/query",
                        json={"query": active_prompt, "history": history_payload},
                        timeout=35
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        st.markdown(data["answer"])

                        if data.get("rewritten_query"):
                            st.markdown(
                                f"<div style='font-size: 0.78rem; color: #64748b; margin: 6px 0;'>"
                                f"Contextual Intent Condensation: <code style='color: #38bdf8; background: #0f172a; padding: 2px 6px;'>{data['rewritten_query']}</code>"
                                f"</div>",
                                unsafe_allow_html=True
                            )

                        if data.get("citations"):
                            with st.expander(f"Statutory Citations ({len(data['citations'])})"):
                                for cit in data["citations"]:
                                    st.markdown(
                                        f"""<div class="statute-card">
                                            <div class="statute-title">{cit['article']} — {cit.get('title', '')}</div>
                                            <div class="statute-meta">{cit.get('part', '')} | Clause {cit.get('clause', 'N/A')}</div>
                                        </div>""",
                                        unsafe_allow_html=True
                                    )

                        lat = data.get("latency", {})
                        if lat:
                            st.markdown(
                                f"<div style='margin-top: 8px;'>"
                                f"<span class='telemetry-tag'>Total: {lat.get('total_ms', 0)}ms</span>"
                                f"<span class='telemetry-tag'>Retrieval: {lat.get('retrieval_ms', 0)}ms</span>"
                                f"<span class='telemetry-tag'>Inference: {lat.get('llm_ms', 0)}ms</span>"
                                f"</div>",
                                unsafe_allow_html=True
                            )

                        assistant_record = {
                            "role": "assistant",
                            "request_id": data.get("request_id"),
                            "content": data["answer"],
                            "rewritten_query": data.get("rewritten_query"),
                            "citations": data.get("citations", []),
                            "latency": data.get("latency", {})
                        }
                        st.session_state.messages.append(assistant_record)

                        try:
                            requests.post(
                                f"{API_BASE_URL}/sessions/{st.session_state.session_id}/messages",
                                json={
                                    "role": "assistant",
                                    "content": data["answer"],
                                    "rewritten_query": data.get("rewritten_query"),
                                    "citations": data.get("citations", []),
                                    "latency": data.get("latency", {}),
                                    "request_id": data.get("request_id")
                                },
                                timeout=4
                            )
                        except Exception:
                            pass

                        st.rerun()
                    else:
                        st.error(f"API Error ({resp.status_code}): {resp.text}")
                except Exception as e:
                    st.error(f"Failed to connect to gateway: {e}. Confirm FastAPI service is online.")

# -----------------------------------------------------------------------------
# TAB 2: CANONICAL STATUTORY CODEX
# -----------------------------------------------------------------------------
with tab_explorer:
    st.markdown("### Statutory Codex Navigator")
    st.caption("Inspect authentic, unedited statutory text directly from the PostgreSQL store.")

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        art_num = st.number_input("Article or Section Number", min_value=1, max_value=511, value=25, step=1)
    with col2:
        art_suffix = st.text_input("Suffix Identifier (e.g. 'A' for Article 25A)", value="")
    with col3:
        st.write("")
        st.write("")
        fetch_btn = st.button("Fetch Verbatim Text", use_container_width=True)

    if fetch_btn:
        try:
            resp = requests.get(f"{API_BASE_URL}/articles/{art_num}?suffix={art_suffix.strip().upper()}")
            if resp.status_code == 200:
                art = resp.json()
                st.markdown(f"""
                <div style="background-color: #0f172a; border: 1px solid #1e293b; border-left: 3px solid #38bdf8; border-radius: 8px; padding: 18px; margin-top: 14px;">
                    <div style="font-size: 1.15rem; font-weight: 700; color: #f8fafc; margin-bottom: 4px;">{art['title']}</div>
                    <div style="font-size: 0.82rem; color: #94a3b8;">{art['part_number']} &bull; {art['part_title']}</div>
                </div>
                """, unsafe_allow_html=True)

                if art.get("chapter_title"):
                    st.caption(f"Chapter: {art['chapter_number']} — {art['chapter_title']}")

                st.markdown("#### Official Statutory Text")
                st.code(art["full_text"], language="text")

                with st.expander(f"Discrete Ingested Clauses ({len(art['clauses'])})"):
                    for cl in art["clauses"]:
                        st.markdown(f"**Clause ({cl['clause_number']}):** {cl['content']}")
            else:
                st.warning(resp.json().get("detail", "Provision not found in canonical index."))
        except Exception as e:
            st.error(f"Could not reach API Gateway: {e}")

# -----------------------------------------------------------------------------
# TAB 3: SYSTEM OBSERVABILITY & TELEMETRY
# -----------------------------------------------------------------------------
with tab_analytics:
    st.markdown("### Production System Observability")
    st.caption("Live telemetry computed directly from PostgreSQL query_logs and cache manager.")

    col_btn, _ = st.columns([0.22, 0.78])
    with col_btn:
        if st.button("Refresh Telemetry", use_container_width=True):
            st.rerun()

    try:
        a_resp = requests.get(f"{API_BASE_URL}/analytics/dashboard", timeout=4)
        if a_resp.status_code == 200:
            stats = a_resp.json()
            ov = stats["overview"]
            cache_info = stats["cache"]

            # Key Telemetry Metrics
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total Queries Processed", ov["total_queries"])
            c2.metric("Mean Latency", f"{ov['avg_latency_ms']} ms")
            c3.metric("Cache Hit Rate", f"{cache_info['hit_rate_pct']}%")
            c4.metric("Total Tokens Consumed", f"{ov['total_tokens_consumed']:,}")

            st.divider()

            # Latency Breakdown
            st.markdown("#### Latency Budget Allocation")
            col_l1, col_l2 = st.columns(2)
            with col_l1:
                st.markdown(f"""
                <div style="background-color: #0f172a; border: 1px solid #1e293b; border-radius: 8px; padding: 14px; margin-bottom: 8px;">
                    <span style="color: #94a3b8; font-size: 0.82rem; font-weight: 600; text-transform: uppercase;">Average Retrieval Latency (Dense + Sparse RRF)</span>
                    <h3 style="color: #38bdf8; margin: 4px 0 0 0; font-family: 'JetBrains Mono', monospace;">{ov['avg_retrieval_ms']} ms</h3>
                </div>
                """, unsafe_allow_html=True)
            with col_l2:
                st.markdown(f"""
                <div style="background-color: #0f172a; border: 1px solid #1e293b; border-radius: 8px; padding: 14px; margin-bottom: 8px;">
                    <span style="color: #94a3b8; font-size: 0.82rem; font-weight: 600; text-transform: uppercase;">Average Inference Latency (Groq LPU)</span>
                    <h3 style="color: #10b981; margin: 4px 0 0 0; font-family: 'JetBrains Mono', monospace;">{ov['avg_llm_ms']} ms</h3>
                </div>
                """, unsafe_allow_html=True)

            # Cache Metrics
            st.markdown("#### Cache Telemetry")
            col_c1, col_c2, col_c3 = st.columns(3)
            col_c1.write(f"• **Active Cached Entries:** `{cache_info['cached_entries']}`")
            col_c2.write(f"• **Cumulative Cache Hits:** `{cache_info['cache_hits']}`")
            col_c3.write(f"• **Cumulative Cache Misses:** `{cache_info['cache_misses']}`")

            # PostgreSQL Audit Log Table
            st.markdown("#### PostgreSQL Query Audit Trail")
            if stats["recent_queries"]:
                df = pd.DataFrame(stats["recent_queries"])
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("No queries recorded in audit logs yet.")

        else:
            st.warning("Could not retrieve telemetry from API Gateway.")
    except Exception as e:
        st.error(f"Telemetry retrieval failure: {e}")
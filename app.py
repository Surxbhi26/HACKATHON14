import streamlit as st
import os
import uuid
from dotenv import load_dotenv
from agent import run_agent
from rag import load_documents, has_documents
from memory import init_db, clear_history

load_dotenv()
init_db()

st.set_page_config(
    page_title="ZeroTrace · Sustainability AI",
    page_icon="🍃",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
    --moss:       #2D5016;
    --fern:       #4A7C2F;
    --sage:       #7BAE5A;
    --mint:       #B8D9A0;
    --cream:      #F5F0E8;
    --soil:       #3D2B1A;
    --gold:       #C9832A;
    --warm-white: #FDFAF5;
}

/* ── Force light background on every Streamlit layer ── */
html, body,
.stApp,
.stApp > div,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"],
[data-testid="stVerticalBlock"],
.main,
.main .block-container {
    background-color: var(--cream) !important;
    color: #1A3A0A !important;
}

/* ── Chat input floating bar ── */
[data-testid="stBottom"],
[data-testid="stBottom"] > div,
[data-testid="stBottomBlockContainer"],
.stChatFloatingInputContainer,
.stChatFloatingInputContainer > div {
    background-color: var(--cream) !important;
    border-top: 1px solid rgba(122,174,90,0.2) !important;
}

/* ── Hide default header BUT keep the sidebar toggle visible ── */
#MainMenu  { visibility: hidden; }
footer     { visibility: hidden; }

/* Show the header bar just enough for the toggle arrow */
header[data-testid="stHeader"] {
    background: transparent !important;
    height: 3rem !important;
    visibility: visible !important;
}

/* The sidebar collapse/expand button */
button[data-testid="collapsedControl"],
button[kind="header"] {
    visibility: visible !important;
    display: flex !important;
    background: var(--fern) !important;
    color: white !important;
    border: none !important;
    border-radius: 0 8px 8px 0 !important;
    width: 2rem !important;
    height: 2rem !important;
    align-items: center !important;
    justify-content: center !important;
    cursor: pointer !important;
    box-shadow: 2px 0 8px rgba(45,80,22,0.2) !important;
}
button[data-testid="collapsedControl"]:hover,
button[kind="header"]:hover {
    background: var(--moss) !important;
}
button[data-testid="collapsedControl"] svg,
button[kind="header"] svg {
    fill: white !important;
    stroke: white !important;
}

/* Also target the sidebar toggle that lives inside the sidebar itself */
section[data-testid="stSidebar"] button[data-testid="baseButton-header"],
section[data-testid="stSidebar"] button[kind="header"] {
    visibility: visible !important;
    background: rgba(255,255,255,0.15) !important;
    border-radius: 6px !important;
    color: white !important;
}

.block-container {
    padding: 1rem 2.5rem 6rem 2.5rem !important;
    max-width: 100% !important;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"],
section[data-testid="stSidebar"] > div {
    background: linear-gradient(180deg, var(--moss) 0%, var(--soil) 100%) !important;
    border-right: none !important;
}
section[data-testid="stSidebar"] > div {
    padding: 1.5rem 1rem !important;
}
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] div {
    color: var(--mint) !important;
}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #FDFAF5 !important;
}
section[data-testid="stSidebar"] .stButton > button {
    background: rgba(255,255,255,0.1) !important;
    color: #FDFAF5 !important;
    border: 1px solid rgba(184,217,160,0.3) !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    width: 100% !important;
    transition: all 0.2s !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255,255,255,0.18) !important;
    border-color: rgba(184,217,160,0.6) !important;
}
section[data-testid="stSidebar"] [data-testid="stFileUploader"] {
    border: 1.5px dashed rgba(122,174,90,0.5) !important;
    border-radius: 12px !important;
    background: rgba(184,217,160,0.08) !important;
}
section[data-testid="stSidebar"] [data-testid="stFileUploader"] * {
    color: rgba(184,217,160,0.75) !important;
}

/* ── Main buttons ── */
.stButton > button {
    background: var(--fern) !important;
    color: white !important;
    border: none !important;
    border-radius: 20px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    background: var(--moss) !important;
    box-shadow: 0 4px 12px rgba(45,80,22,0.25) !important;
}

/* ── Chat input ── */
.stChatInput,
.stChatInput > div,
[data-testid="stChatInput"],
[data-testid="stChatInput"] > div {
    background: var(--cream) !important;
}
.stChatInput > div > div,
[data-testid="stChatInput"] > div > div {
    border: 1.5px solid var(--sage) !important;
    border-radius: 28px !important;
    background: var(--warm-white) !important;
    box-shadow: 0 2px 12px rgba(45,80,22,0.08) !important;
}
.stChatInput textarea,
[data-testid="stChatInput"] textarea {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.95rem !important;
    color: var(--moss) !important;
    background: var(--warm-white) !important;
}
.stChatInput textarea::placeholder {
    color: rgba(45,80,22,0.45) !important;
}

/* ── Chat messages ── */
.stChatMessage {
    background: transparent !important;
    border: none !important;
    padding: 0.25rem 0 !important;
}
[data-testid="stChatMessageContent"] {
    background: var(--warm-white) !important;
    border: 1px solid rgba(74,124,47,0.18) !important;
    border-radius: 16px !important;
    padding: 0.85rem 1.1rem !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.9rem !important;
    color: #1A3A0A !important;
    line-height: 1.7 !important;
}
[data-testid="stChatMessageContent"] p {
    margin-bottom: 0.4rem !important;
    color: #1A3A0A !important;
}

/* ── Expander ── */
.streamlit-expanderHeader {
    background: rgba(184,217,160,0.15) !important;
    border: 1px solid rgba(122,174,90,0.25) !important;
    border-radius: 8px !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    color: var(--moss) !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: var(--cream); }
::-webkit-scrollbar-thumb { background: var(--sage); border-radius: 3px; }

/* ── Mode pills ── */
.mode-pill {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 3px 11px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    font-family: 'DM Sans', sans-serif;
    letter-spacing: 0.03em;
    margin-bottom: 6px;
}
.mode-general { background: rgba(74,124,47,0.12);  color: #2D5016; border: 1px solid #7BAE5A; }
.mode-web     { background: rgba(201,131,42,0.12); color: #7A4510; border: 1px solid #C9832A; }
.mode-rag     { background: rgba(45,80,22,0.10);   color: #1A3A0A; border: 1px solid #4A7C2F; }

/* ── Source badge ── */
.source-badge {
    display: inline-block;
    background: rgba(184,217,160,0.3);
    border: 1px solid var(--sage);
    color: var(--moss);
    border-radius: 20px;
    padding: 2px 10px;
    font-size: 0.73rem;
    font-weight: 500;
    margin: 2px 4px 2px 0;
    font-family: 'DM Sans', sans-serif;
}

/* ── Metrics ── */
[data-testid="stMetric"] {
    background: var(--warm-white) !important;
    border: 1px solid rgba(74,124,47,0.18) !important;
    border-radius: 12px !important;
    padding: 0.75rem 1rem !important;
}
[data-testid="stMetricValue"] {
    color: var(--moss) !important;
    font-size: 1.4rem !important;
    font-weight: 600 !important;
}
[data-testid="stMetricLabel"] {
    font-size: 0.72rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
    color: var(--sage) !important;
}

/* ── Radio ── */
section[data-testid="stSidebar"] .stRadio > label {
    color: var(--cream) !important;
    font-size: 0.85rem !important;
}

hr { border-color: rgba(122,174,90,0.2) !important; }
.stCaption { color: rgba(45,80,22,0.6) !important; font-size: 0.78rem !important; }
.stSpinner > div { border-top-color: var(--sage) !important; }
</style>
""", unsafe_allow_html=True)

# ─── Session state ─────────────────────────────────────────────────────────────
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []
if "docs_loaded" not in st.session_state:
    st.session_state.docs_loaded = False
if "mode" not in st.session_state:
    st.session_state.mode = "auto"

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 0.5rem 0 1.2rem;">
        <div style="font-size: 2.4rem; line-height:1;">🌿</div>
        <div style="font-family:'DM Serif Display',serif; font-size:1.4rem;
                    color:#FDFAF5; letter-spacing:0.02em; margin-top:4px;">ZeroTrace</div>
        <div style="font-size:0.62rem; letter-spacing:0.14em; text-transform:uppercase;
                    color:#7BAE5A; margin-top:3px;">Sustainability AI Agent</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr style='border-color:rgba(184,217,160,0.2); margin:0 0 1rem;'>",
                unsafe_allow_html=True)

    # Agent mode
    st.markdown(
        "<p style='font-size:0.7rem; letter-spacing:0.1em; text-transform:uppercase;"
        " color:#7BAE5A; margin-bottom:0.5rem; font-weight:600;'>Agent Mode</p>",
        unsafe_allow_html=True,
    )
    mode_choice = st.radio(
        label="mode",
        options=["  Auto (Smart Routing)", "  General Chat", "  Web Search", "  Document RAG"],
        label_visibility="collapsed",
    )
    mode_map = {
        "  Auto (Smart Routing)": "auto",
        "  General Chat":         "general",
        "  Web Search":           "web",
        "  Document RAG":         "rag",
    }
    st.session_state.mode = mode_map.get(mode_choice, "auto")

    st.markdown("<hr style='border-color:rgba(184,217,160,0.15); margin:1rem 0;'>",
                unsafe_allow_html=True)

    # Documents
    st.markdown(
        "<p style='font-size:0.65rem; letter-spacing:0.12em; text-transform:uppercase;"
        " color:#7BAE5A; margin-bottom:0.5rem; font-weight:600;'>📄 Documents</p>",
        unsafe_allow_html=True,
    )
    uploaded_files = st.file_uploader(
        "Drop your sustainability doc",
        type=["pdf"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )
    if uploaded_files:
        if st.button("📥 Index Documents", use_container_width=True):
            os.makedirs("documents", exist_ok=True)
            file_paths = []
            for f in uploaded_files:
                path = f"documents/{f.name}"
                with open(path, "wb") as fh:
                    fh.write(f.getbuffer())
                file_paths.append(path)
            with st.spinner("Indexing..."):
                result = load_documents(file_paths)
            st.success(result)
            st.session_state.docs_loaded = True

    if has_documents():
        st.markdown("""
        <div style="background:rgba(184,217,160,0.15); border:1px solid rgba(122,174,90,0.3);
                    border-radius:8px; padding:0.45rem 0.7rem; margin-top:0.5rem;
                    font-size:0.78rem; color:#B8D9A0;">
            ✓ Documents indexed &amp; ready
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background:rgba(255,255,255,0.05); border:1px solid rgba(184,217,160,0.15);
                    border-radius:8px; padding:0.45rem 0.7rem; margin-top:0.5rem;
                    font-size:0.78rem; color:rgba(184,217,160,0.5);">
            No documents indexed yet
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr style='border-color:rgba(184,217,160,0.15); margin:1rem 0;'>",
                unsafe_allow_html=True)

    # Session stats
    st.markdown(
        "<p style='font-size:0.65rem; letter-spacing:0.12em; text-transform:uppercase;"
        " color:#7BAE5A; margin-bottom:0.7rem; font-weight:600;'>📊 Session</p>",
        unsafe_allow_html=True,
    )
    assistant_msgs = [m for m in st.session_state.messages if m["role"] == "assistant"]
    modes_used = [m.get("mode", "general") for m in assistant_msgs]

    c1, c2 = st.columns(2)
    with c1:
        st.metric("Exchanges", len(assistant_msgs))
    with c2:
        st.metric("Docs", "✓" if has_documents() else "–")

    if modes_used:
        st.markdown(
            "<p style='font-size:0.65rem; letter-spacing:0.1em; text-transform:uppercase;"
            " color:#7BAE5A; margin:0.8rem 0 0.4rem; font-weight:600;'>Tool usage</p>",
            unsafe_allow_html=True,
        )
        g = modes_used.count("general")
        w = modes_used.count("web")
        r = modes_used.count("rag")
        total = max(len(modes_used), 1)
        for lbl, count, color in [("💬 General", g, "#7BAE5A"),
                                   ("🌐 Web",     w, "#C9832A"),
                                   ("📄 RAG",     r, "#4A7C2F")]:
            pct = int(count / total * 100)
            st.markdown(f"""
            <div style="margin-bottom:6px;">
                <div style="display:flex; justify-content:space-between;
                            font-size:0.72rem; color:rgba(184,217,160,0.8); margin-bottom:3px;">
                    <span>{lbl}</span><span>{count}</span>
                </div>
                <div style="background:rgba(255,255,255,0.08); border-radius:4px; height:4px;">
                    <div style="background:{color}; width:{pct}%; height:4px; border-radius:4px;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown(
        f"<p style='font-size:0.65rem; color:rgba(184,217,160,0.4); margin-top:0.6rem;'>"
        f"ID: {st.session_state.session_id[:8]}…</p>",
        unsafe_allow_html=True,
    )

    st.markdown("<hr style='border-color:rgba(184,217,160,0.15); margin:1rem 0;'>",
                unsafe_allow_html=True)

    # Examples
    st.markdown(
        "<p style='font-size:0.65rem; letter-spacing:0.12em; text-transform:uppercase;"
        " color:#7BAE5A; margin-bottom:0.6rem; font-weight:600;'>💡 Try asking</p>",
        unsafe_allow_html=True,
    )
    for icon, text in [("💬", "What are the 5 R's of zero waste?"),
                        ("🌐", "Latest plastic ban news"),
                        ("📄", "Summarize uploaded doc"),
                        ("💬", "Tips for a sustainable kitchen")]:
        st.markdown(
            f"<div style='font-size:0.75rem; color:rgba(184,217,160,0.7);"
            f" padding:3px 0; line-height:1.4;'>{icon} {text}</div>",
            unsafe_allow_html=True,
        )

    st.markdown("<hr style='border-color:rgba(184,217,160,0.15); margin:1rem 0;'>",
                unsafe_allow_html=True)

    if st.button("🗑  Clear Conversation", use_container_width=True):
        clear_history(st.session_state.session_id)
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()

    st.markdown("""
    <div style="text-align:center; margin-top:1.2rem;">
        <div style="font-size:0.6rem; color:rgba(184,217,160,0.3);
                    letter-spacing:0.05em; line-height:1.8;">
            Groq · FAISS · Llama 3<br>DuckDuckGo · Streamlit
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─── Main area ────────────────────────────────────────────────────────────────

# Hero
st.markdown("""
<div style="
    background: linear-gradient(130deg, #2D5016 0%, #4A7C2F 50%, #7BAE5A 100%);
    border-radius: 18px;
    padding: 2.2rem 2.5rem 2rem;
    margin-bottom: 1.8rem;
    position: relative;
    overflow: hidden;
">
    <div style="position:absolute; top:-40px; right:-40px; width:180px; height:180px;
                border-radius:50%; background:rgba(255,255,255,0.05);"></div>
    <div style="position:absolute; bottom:-50px; left:8%; width:240px; height:240px;
                border-radius:50%; background:rgba(255,255,255,0.04);"></div>
    <div style="position:relative; z-index:1;">
        <div style="font-size:0.65rem; letter-spacing:0.18em; text-transform:uppercase;
                    color:#B8D9A0; margin-bottom:0.5rem; font-family:'DM Sans',sans-serif;">
            🌱 &nbsp;Zero Waste · Circular Economy · Green Living
        </div>
        <div style="font-family:'DM Serif Display',serif; font-size:2.2rem; color:#FDFAF5;
                    line-height:1.15; margin-bottom:0.6rem;">
            Your Intelligent <em>Sustainability</em> Guide
        </div>
        <div style="font-size:0.88rem; color:rgba(253,250,245,0.78); line-height:1.65;
                    max-width:520px; font-family:'DM Sans',sans-serif;">
            Ask about zero waste living, get real-time eco-news, or query your own 
            sustainability documents — the agent routes intelligently across all three modes.
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Mode cards
mc1, mc2, mc3 = st.columns(3)
for col, pill_cls, icon, title, desc in [
    (mc1, "mode-general", "💬", "General Chat",  "Answers from LLM knowledge"),
    (mc2, "mode-web",     "🌐", "Web Search",    "Real-time internet results"),
    (mc3, "mode-rag",     "📄", "Document RAG",  "Your uploaded documents"),
]:
    with col:
        st.markdown(f"""
        <div style="background:#FDFAF5; border:1px solid rgba(74,124,47,0.2);
                    border-radius:12px; padding:0.8rem 1rem; margin-bottom:1rem;">
            <span class="mode-pill {pill_cls}">{icon} {title}</span>
            <div style="font-size:0.78rem; color:rgba(45,80,22,0.6);
                        margin-top:2px; font-family:'DM Sans',sans-serif;">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

# Chat history
for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.write(msg["content"])
    else:
        with st.chat_message("assistant"):
            mode = msg.get("mode", "general")
            pill_map = {
                "general": ("mode-general", "💬 General"),
                "web":     ("mode-web",     "🌐 Web Search"),
                "rag":     ("mode-rag",     "📄 Document RAG"),
            }
            cls, label = pill_map.get(mode, pill_map["general"])
            st.markdown(f'<span class="mode-pill {cls}">{label}</span>',
                        unsafe_allow_html=True)
            st.write(msg["content"])
            if msg.get("sources"):
                with st.expander("📚 Sources"):
                    for src in msg["sources"]:
                        st.markdown(f'<span class="source-badge">🔗 {src}</span>',
                                    unsafe_allow_html=True)

# Chat input
user_input = st.chat_input("Ask about zero waste, sustainability, eco-news…")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        with st.spinner("🌿 Thinking…"):
            result = run_agent(
                user_input,
                st.session_state.session_id,
                st.session_state.mode,
            )

        mode    = result["mode"]
        answer  = result["answer"]
        sources = result["sources"]

        pill_map = {
            "general": ("mode-general", "💬 General"),
            "web":     ("mode-web",     "🌐 Web Search"),
            "rag":     ("mode-rag",     "📄 Document RAG"),
        }
        cls, label = pill_map.get(mode, pill_map["general"])
        st.markdown(f'<span class="mode-pill {cls}">{label}</span>',
                    unsafe_allow_html=True)
        st.write(answer)
        if sources:
            with st.expander("📚 Sources"):
                for src in sources:
                    st.markdown(f'<span class="source-badge">🔗 {src}</span>',
                                unsafe_allow_html=True)

    st.session_state.messages.append({
        "role":    "assistant",
        "content": answer,
        "mode":    mode,
        "sources": sources,
    })

# Footer
st.markdown("""
<div style="text-align:center; padding:2rem 1rem 1rem;
    font-family:'DM Sans',sans-serif; font-size:0.72rem;
    color:rgba(74,124,47,0.55); letter-spacing:0.05em;">
    🌿 &nbsp; ZeroTrace · CHRIST University Innovation Sprint · NEOSTATS 2026
</div>
""", unsafe_allow_html=True)
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
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Styles ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,600;1,400&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
    --moss:       #1E3D0A;
    --fern:       #3A6B22;
    --sage:       #6A9E48;
    --mint:       #A8CC88;
    --pale:       #D6ECC0;
    --cream:      #F4F0E6;
    --warm-white: #FDFAF4;
    --soil:       #2A1F12;
    --gold:       #B8711A;
    --text-dark:  #182B08;
    --text-mid:   #3A5520;
    --text-soft:  #6A8050;
}

/* ── Base ── */
.stApp {
    background-color: var(--cream);
}

.block-container {
    color: var(--text-dark);
    max-width: 1200px;
    margin: auto;
}
.block-container {
    padding: 0 2rem 7rem 2rem !important;
    max-width: 100% !important;
}

/* ── Header ── */
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }
header[data-testid="stHeader"] {
    background: transparent !important;
    height: 3rem !important;
    visibility: visible !important;
}
button[data-testid="collapsedControl"],
button[kind="header"] {
    visibility: visible !important;
    display: flex !important;
    background: var(--fern) !important;
    color: white !important;
    border: none !important;
    border-radius: 0 8px 8px 0 !important;
    width: 2.2rem !important;
    height: 2.2rem !important;
    align-items: center !important;
    justify-content: center !important;
    cursor: pointer !important;
    box-shadow: 2px 0 10px rgba(30,61,10,0.25) !important;
}
button[data-testid="collapsedControl"]:hover { background: var(--moss) !important; }
button[data-testid="collapsedControl"] svg,
button[kind="header"] svg { fill: white !important; stroke: white !important; }

/* ── Chat input strip bg ── */
[data-testid="stBottom"],
[data-testid="stBottom"] > div,
[data-testid="stBottomBlockContainer"],
.stChatFloatingInputContainer,
.stChatFloatingInputContainer > div {
    background: linear-gradient(to top, var(--cream) 80%, transparent) !important;
    border-top: none !important;
}

/* ══ SIDEBAR ══ */
section[data-testid="stSidebar"],
section[data-testid="stSidebar"] > div {
    background: linear-gradient(160deg, #1A3808 0%, #2A5010 55%, #1E2A10 100%) !important;
    border-right: 1px solid rgba(106,158,72,0.2) !important;
}
section[data-testid="stSidebar"] > div { padding: 1.2rem 1rem 1.5rem !important; }

section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] div { color: var(--pale) !important; }

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 { color: #FDFAF4 !important; }

section[data-testid="stSidebar"] .stButton > button {
    background: rgba(255,255,255,0.07) !important;
    color: #FDFAF4 !important;
    border: 1px solid rgba(168,204,136,0.25) !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.82rem !important;
    width: 100% !important;
    padding: 0.45rem 1rem !important;
    transition: all 0.2s !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255,255,255,0.13) !important;
    border-color: rgba(168,204,136,0.5) !important;
}

/* Fix dark overlay on file uploader */
section[data-testid="stSidebar"] [data-testid="stFileUploader"] {
    border: 1.5px dashed rgba(106,158,72,0.45) !important;
    border-radius: 10px !important;
    background: rgba(168,204,136,0.06) !important;
    padding: 0.3rem !important;
}
section[data-testid="stSidebar"] [data-testid="stFileUploader"] > div,
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {
    background: transparent !important;
    border: none !important;
}
section[data-testid="stSidebar"] [data-testid="stFileUploader"] * {
    color: rgba(168,204,136,0.8) !important;
    background: transparent !important;
}
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button {
    background: rgba(106,158,72,0.2) !important;
    color: var(--pale) !important;
    border: 1px solid rgba(106,158,72,0.4) !important;
    border-radius: 8px !important;
    font-size: 0.78rem !important;
}

section[data-testid="stSidebar"] .stRadio > div { gap: 2px !important; }
section[data-testid="stSidebar"] .stRadio label {
    font-size: 0.83rem !important;
    font-family: 'DM Sans', sans-serif !important;
    color: rgba(214,236,192,0.85) !important;
    padding: 0.3rem 0.5rem !important;
    border-radius: 6px !important;
    transition: background 0.15s !important;
}
section[data-testid="stSidebar"] .stRadio label:hover {
    background: rgba(255,255,255,0.07) !important;
}

section[data-testid="stSidebar"] [data-testid="stMetric"] {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(106,158,72,0.2) !important;
    border-radius: 10px !important;
    padding: 0.6rem 0.8rem !important;
}
section[data-testid="stSidebar"] [data-testid="stMetricValue"] {
    color: var(--pale) !important;
    font-size: 1.3rem !important;
    font-weight: 600 !important;
}
section[data-testid="stSidebar"] [data-testid="stMetricLabel"] {
    font-size: 0.65rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
    color: rgba(168,204,136,0.7) !important;
}

/* ══ MAIN BUTTONS ══ */
.stButton > button {
    background: var(--fern) !important;
    color: white !important;
    border: none !important;
    border-radius: 22px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.85rem !important;
    padding: 0.5rem 1.4rem !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 2px 8px rgba(30,61,10,0.18) !important;
}
.stButton > button:hover {
    background: var(--moss) !important;
    box-shadow: 0 4px 16px rgba(30,61,10,0.28) !important;
    transform: translateY(-1px) !important;
}

/* ══ CHAT INPUT FIXED ══ */
.stChatInput, 
[data-testid="stChatInput"],
[data-testid="stChatInput"] > div { 
    background-color: transparent !important;
    color: var(--text-dark) !important;
}

.stChatInput > div > div,
[data-testid="stChatInput"] > div > div {
    border: 1.5px solid rgba(106,158,72,0.45) !important;
    border-radius: 32px !important;
    background-color: var(--warm-white) !important;
    box-shadow: 0 2px 16px rgba(30,61,10,0.07), 0 0 0 4px rgba(106,158,72,0.04) !important;
    transition: box-shadow 0.2s, border-color 0.2s !important;
}

.stChatInput [data-baseweb="textarea"],
[data-testid="stChatInput"] [data-baseweb="textarea"],
.stChatInput [data-baseweb="base-input"],
[data-testid="stChatInput"] [data-baseweb="base-input"] {
    background-color: var(--warm-white) !important;
    color: var(--text-dark) !important;
}

.stChatInput > div > div:focus-within,
[data-testid="stChatInput"] > div > div:focus-within {
    border-color: var(--sage) !important;
    box-shadow: 0 2px 20px rgba(30,61,10,0.12), 0 0 0 4px rgba(106,158,72,0.1) !important;
}

.stChatInput textarea,
[data-testid="stChatInput"] textarea {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.93rem !important;
    color: var(--text-dark) !important;
    background: transparent !important;
    caret-color: var(--text-dark) !important;
    opacity: 1 !important;
    -webkit-text-fill-color: var(--text-dark) !important;
}
.stChatInput textarea::placeholder,
[data-testid="stChatInput"] textarea::placeholder { 
    color: rgba(30,61,10,0.45) !important; 
}

.stChatInput textarea::-webkit-input-placeholder,
[data-testid="stChatInput"] textarea::-webkit-input-placeholder {
    color: rgba(30,61,10,0.45) !important;
}

.stChatInput textarea::-moz-placeholder,
[data-testid="stChatInput"] textarea::-moz-placeholder {
    color: rgba(30,61,10,0.45) !important;
    opacity: 1 !important;
}

/* ══ CHAT MESSAGES ══ */
.stChatMessage {
    background: transparent !important;
    border: none !important;
    padding: 0.2rem 0 !important;
}
[data-testid="stChatMessageContent"] {
    background: var(--warm-white) !important;
    border: 1px solid rgba(58,107,34,0.14) !important;
    border-radius: 18px !important;
    padding: 0.9rem 1.15rem !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.9rem !important;
    color: var(--text-dark) !important;
    line-height: 1.75 !important;
    box-shadow: 0 1px 6px rgba(30,61,10,0.05) !important;
}
[data-testid="stChatMessageContent"] p {
    margin-bottom: 0.35rem !important;
    color: var(--text-dark) !important;
}

/* ══ EXPANDER ══ */
.streamlit-expanderHeader {
    background: rgba(168,204,136,0.12) !important;
    border: 1px solid rgba(106,158,72,0.22) !important;
    border-radius: 8px !important;
    font-size: 0.78rem !important;
    font-weight: 500 !important;
    color: var(--fern) !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* ══ PILLS ══ */
.mode-pill {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 3px 12px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 600;
    font-family: 'DM Sans', sans-serif;
    letter-spacing: 0.04em;
    margin-bottom: 7px;
    text-transform: uppercase;
}
.mode-general { background: rgba(58,107,34,0.1);  color: #1E3D0A; border: 1px solid rgba(106,158,72,0.5); }
.mode-web     { background: rgba(184,113,26,0.1); color: #7A4510; border: 1px solid rgba(184,113,26,0.45); }
.mode-rag     { background: rgba(30,61,10,0.09);  color: #1A3A0A; border: 1px solid rgba(58,107,34,0.4); }

/* Source badges */
.source-badge {
    display: inline-block;
    background: rgba(168,204,136,0.25);
    border: 1px solid rgba(106,158,72,0.4);
    color: var(--fern);
    border-radius: 20px;
    padding: 3px 11px;
    font-size: 0.72rem;
    font-weight: 500;
    margin: 2px 4px 2px 0;
    font-family: 'DM Sans', sans-serif;
}

/* Mode cards on main page */
.mode-card {
    background: var(--warm-white);
    border: 1px solid rgba(58,107,34,0.16);
    border-radius: 14px;
    padding: 1rem 1.1rem 0.9rem;
    margin-bottom: 1rem;
    transition: border-color 0.2s, box-shadow 0.2s;
}
.mode-card:hover {
    border-color: rgba(106,158,72,0.4);
    box-shadow: 0 3px 14px rgba(30,61,10,0.09);
}

/* ══ MISC ══ */
hr { border-color: rgba(106,158,72,0.18) !important; }
.stCaption { color: rgba(30,61,10,0.5) !important; font-size: 0.76rem !important; }
.stSpinner > div { border-top-color: var(--sage) !important; }
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--cream); }
::-webkit-scrollbar-thumb { background: var(--sage); border-radius: 3px; }
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
    # Logo
    st.markdown("""
    <div style="text-align:center; padding:0.8rem 0 1.4rem;">
        <div style="width:52px; height:52px; border-radius:50%;
                    background:rgba(106,158,72,0.2); border:1px solid rgba(106,158,72,0.35);
                    display:flex; align-items:center; justify-content:center;
                    margin:0 auto 0.7rem; font-size:1.6rem; line-height:1;">🌿</div>
        <div style="font-family:'Lora',serif; font-size:1.35rem;
                    color:#FDFAF4; letter-spacing:0.01em; font-weight:600;">ZeroTrace</div>
        <div style="font-size:0.58rem; letter-spacing:0.16em; text-transform:uppercase;
                    color:#6A9E48; margin-top:4px; font-family:'DM Sans',sans-serif;">
            Sustainability AI Agent
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr style='border-color:rgba(168,204,136,0.18); margin:0 0 1rem;'>",
                unsafe_allow_html=True)

    # Agent mode
    st.markdown(
        "<p style='font-size:0.63rem; letter-spacing:0.13em; text-transform:uppercase;"
        " color:#6A9E48; margin-bottom:0.5rem; font-weight:600;"
        " font-family:DM Sans,sans-serif;'>Agent Mode</p>",
        unsafe_allow_html=True,
    )
    mode_choice = st.radio(
        label="mode",
        options=["⚡ Auto (Smart Routing)", "💬 General Chat", "🌐 Web Search", "📄 Document RAG"],
        label_visibility="collapsed",
    )
    mode_map = {
        "⚡ Auto (Smart Routing)": "auto",
        "💬 General Chat":         "general",
        "🌐 Web Search":           "web",
        "📄 Document RAG":         "rag",
    }
    st.session_state.mode = mode_map.get(mode_choice, "auto")

    st.markdown("<hr style='border-color:rgba(168,204,136,0.15); margin:1rem 0;'>",
                unsafe_allow_html=True)

    # Documents
    st.markdown(
        "<p style='font-size:0.63rem; letter-spacing:0.13em; text-transform:uppercase;"
        " color:#6A9E48; margin-bottom:0.5rem; font-weight:600;"
        " font-family:DM Sans,sans-serif;'>Documents</p>",
        unsafe_allow_html=True,
    )
    uploaded_files = st.file_uploader(
        "Drop your sustainability doc",
        type=["pdf"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )
    if uploaded_files:
        if st.button("Index Documents", use_container_width=True):
            os.makedirs("documents", exist_ok=True)
            file_paths = []
            for f in uploaded_files:
                path = f"documents/{f.name}"
                with open(path, "wb") as fh:
                    fh.write(f.getbuffer())
                file_paths.append(path)
            with st.spinner("Indexing…"):
                result = load_documents(file_paths)
            st.success(result)
            st.session_state.docs_loaded = True

    if has_documents():
        st.markdown("""
        <div style="background:rgba(168,204,136,0.12); border:1px solid rgba(106,158,72,0.3);
                    border-radius:8px; padding:0.45rem 0.75rem; margin-top:0.6rem;
                    font-size:0.78rem; color:#A8CC88; font-family:'DM Sans',sans-serif;
                    display:flex; align-items:center; gap:6px;">
            <span style="color:#6A9E48;">✓</span> Documents indexed &amp; ready
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background:rgba(255,255,255,0.04); border:1px solid rgba(168,204,136,0.12);
                    border-radius:8px; padding:0.45rem 0.75rem; margin-top:0.6rem;
                    font-size:0.78rem; color:rgba(168,204,136,0.45);
                    font-family:'DM Sans',sans-serif;">
            No documents indexed yet
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr style='border-color:rgba(168,204,136,0.15); margin:1rem 0;'>",
                unsafe_allow_html=True)

    # Session stats
    st.markdown(
        "<p style='font-size:0.63rem; letter-spacing:0.13em; text-transform:uppercase;"
        " color:#6A9E48; margin-bottom:0.7rem; font-weight:600;"
        " font-family:DM Sans,sans-serif;'>Session</p>",
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
            "<p style='font-size:0.62rem; letter-spacing:0.1em; text-transform:uppercase;"
            " color:#6A9E48; margin:0.9rem 0 0.5rem; font-weight:600;"
            " font-family:DM Sans,sans-serif;'>Tool usage</p>",
            unsafe_allow_html=True,
        )
        g = modes_used.count("general")
        w = modes_used.count("web")
        r = modes_used.count("rag")
        total = max(len(modes_used), 1)
        for lbl, count, color in [
            ("💬 General", g, "#6A9E48"),
            ("🌐 Web",     w, "#B8711A"),
            ("📄 RAG",     r, "#3A6B22"),
        ]:
            pct = int(count / total * 100)
            st.markdown(f"""
            <div style="margin-bottom:7px;">
                <div style="display:flex; justify-content:space-between;
                            font-size:0.71rem; color:rgba(168,204,136,0.8);
                            margin-bottom:4px; font-family:'DM Sans',sans-serif;">
                    <span>{lbl}</span><span>{count}</span>
                </div>
                <div style="background:rgba(255,255,255,0.07); border-radius:4px; height:3px;">
                    <div style="background:{color}; width:{pct}%; height:3px;
                                border-radius:4px; transition:width 0.4s;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown(
        f"<p style='font-size:0.62rem; color:rgba(168,204,136,0.3); margin-top:0.5rem;"
        f" font-family:DM Sans,sans-serif;'>"
        f"ID: {st.session_state.session_id[:8]}…</p>",
        unsafe_allow_html=True,
    )

    st.markdown("<hr style='border-color:rgba(168,204,136,0.15); margin:1rem 0;'>",
                unsafe_allow_html=True)

    # Try asking prompts
    st.markdown(
        "<p style='font-size:0.63rem; letter-spacing:0.13em; text-transform:uppercase;"
        " color:#6A9E48; margin-bottom:0.6rem; font-weight:600;"
        " font-family:DM Sans,sans-serif;'>Try asking</p>",
        unsafe_allow_html=True,
    )
    for icon, text in [
        ("💬", "What are the 5 R's of zero waste?"),
        ("🌐", "Latest plastic ban news"),
        ("📄", "Summarize uploaded doc"),
        ("💬", "Tips for a sustainable kitchen"),
    ]:
        st.markdown(
            f"<div style='font-size:0.75rem; color:rgba(168,204,136,0.65);"
            f" padding:3px 0; line-height:1.45; font-family:DM Sans,sans-serif;'>"
            f"{icon} {text}</div>",
            unsafe_allow_html=True,
        )

    st.markdown("<hr style='border-color:rgba(168,204,136,0.15); margin:1rem 0;'>",
                unsafe_allow_html=True)

    if st.button("🗑   Clear Conversation", use_container_width=True):
        clear_history(st.session_state.session_id)
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()

    st.markdown("""
    <div style="text-align:center; margin-top:1.2rem;">
        <div style="font-size:0.58rem; color:rgba(168,204,136,0.25);
                    letter-spacing:0.05em; line-height:2; font-family:'DM Sans',sans-serif;">
            Groq · FAISS · Llama 3<br>DuckDuckGo · Streamlit
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─── Main area ────────────────────────────────────────────────────────────────

# Top spacer
st.markdown("<div style='height:1.5rem;'></div>", unsafe_allow_html=True)

# Hero banner
st.markdown("""
<div style="
    background: linear-gradient(130deg, #1E3D0A 0%, #3A6B22 48%, #6A9E48 100%);
    border-radius: 20px;
    padding: 2.4rem 2.8rem 2.2rem;
    margin-bottom: 1.6rem;
    position: relative;
    overflow: hidden;
">
    <div style="position:absolute; top:-60px; right:-60px; width:220px; height:220px;
                border-radius:50%; background:rgba(255,255,255,0.04);"></div>
    <div style="position:absolute; bottom:-70px; left:5%; width:280px; height:280px;
                border-radius:50%; background:rgba(255,255,255,0.03);"></div>
    <div style="position:absolute; top:20px; right:100px; width:6px; height:6px;
                border-radius:50%; background:rgba(168,204,136,0.4);"></div>
    <div style="position:absolute; top:50px; right:60px; width:4px; height:4px;
                border-radius:50%; background:rgba(168,204,136,0.3);"></div>
    <div style="position:relative; z-index:1;">
        <div style="font-size:0.6rem; letter-spacing:0.2em; text-transform:uppercase;
                    color:rgba(168,204,136,0.85); margin-bottom:0.6rem;
                    font-family:'DM Sans',sans-serif; font-weight:500;">
            🌱 &nbsp;Zero Waste · Circular Economy · Green Living
        </div>
        <div style="font-family:'Lora',serif; font-size:2.3rem; color:#FDFAF4;
                    line-height:1.18; margin-bottom:0.75rem; font-weight:600;">
            Your Intelligent <em style="font-weight:400; color:#A8CC88;">Sustainability</em> Guide
        </div>
        <div style="font-size:0.87rem; color:rgba(253,250,244,0.72); line-height:1.7;
                    max-width:500px; font-family:'DM Sans',sans-serif; font-weight:300;">
            Ask about zero-waste living, get real-time eco-news, or query your own
            sustainability documents — the agent routes intelligently across all three modes.
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Mode cards
mc1, mc2, mc3 = st.columns(3)
cards = [
    (mc1, "mode-general", "💬", "General Chat",   "Answers from LLM knowledge",   "#3A6B22"),
    (mc2, "mode-web",     "🌐", "Web Search",     "Real-time internet results",   "#B8711A"),
    (mc3, "mode-rag",     "📄", "Document RAG",   "Your uploaded documents",      "#1E3D0A"),
]
for col, pill_cls, icon, title, desc, accent in cards:
    with col:
        st.markdown(f"""
        <div style="background:var(--warm-white,#FDFAF4); border:1px solid rgba(58,107,34,0.16);
                    border-radius:14px; padding:1rem 1.1rem 0.9rem; margin-bottom:1rem;
                    transition: border-color 0.2s;">
            <span class="mode-pill {pill_cls}">{icon} {title}</span>
            <div style="font-size:0.78rem; color:rgba(30,61,10,0.55);
                        margin-top:4px; font-family:'DM Sans',sans-serif;
                        line-height:1.5;">{desc}</div>
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
    font-family:'DM Sans',sans-serif; font-size:0.7rem;
    color:rgba(58,107,34,0.45); letter-spacing:0.06em;">
    🌿 &nbsp; ZeroTrace · CHRIST University Innovation Sprint · NEOSTATS 2026
</div>
""", unsafe_allow_html=True)

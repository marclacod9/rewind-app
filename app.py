import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from openai import OpenAI
import re
import json

# ─────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Rewind",
    page_icon="⏮",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────────────────────
# DESIGN SYSTEM
# ─────────────────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,500;1,400&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;1,9..40,300&display=swap');

:root {
    --bg:           #ffffff;
    --bg-subtle:    #f9f9f8;
    --surface:      #ffffff;
    --surface-hover:#f5f4f2;
    --border:       #e8e5e0;
    --border-light: #f0ede8;
    --text:         #1a1916;
    --text-secondary: #6b6860;
    --text-muted:   #a8a49e;
    --accent:       #d97757;
    --accent-light: #fdf0ec;
    --accent-hover: #c96844;
    --user-bg:      #1a1916;
    --user-text:    #ffffff;
    --guest-bg:     #f5f4f2;
    --guest-text:   #1a1916;
    --shadow-sm:    0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
    --shadow-md:    0 4px 12px rgba(0,0,0,0.08), 0 2px 4px rgba(0,0,0,0.04);
    --radius:       12px;
    --radius-sm:    8px;
}

/* ── Base ── */
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stApp"] {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'DM Sans', -apple-system, sans-serif !important;
}

#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"] { display: none !important; }

.block-container {
    max-width: 660px !important;
    padding: 0 1.5rem 5rem !important;
}

/* ── Masthead ── */
.masthead {
    padding: 3rem 0 2.5rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 2.5rem;
}

.masthead-title {
    font-family: 'Lora', Georgia, serif;
    font-size: 5rem;
    font-weight: 500;
    letter-spacing: -0.03em;
    color: var(--text);
    line-height: 1;
    margin-bottom: 0.8rem;
}

.masthead-sub {
    font-family: 'DM Sans', sans-serif;
    font-size: 1.05rem;
    font-weight: 400;
    color: var(--text);
    line-height: 1.5;
}

/* ── Speaker card ── */
.speaker-card {
    border-radius: var(--radius);
    overflow: hidden;
    border: 1px solid var(--border);
    box-shadow: var(--shadow-sm);
    margin: 0 0 1.5rem;
    background: var(--surface);
}

.speaker-thumbnail-wrap {
    position: relative;
    height: 220px;
    overflow: hidden;
    background: var(--bg-subtle);
}

.speaker-thumbnail {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
}

.speaker-thumbnail-gradient {
    position: absolute;
    inset: 0;
    background: linear-gradient(
        to bottom,
        transparent 30%,
        rgba(255,255,255,0.95) 100%
    );
}

.speaker-card-body {
    padding: 1.2rem 1.5rem 1.5rem;
}

.speaker-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    font-size: 0.7rem;
    font-weight: 500;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: var(--accent);
    background: var(--accent-light);
    border-radius: 20px;
    padding: 0.25rem 0.7rem;
    margin-bottom: 0.7rem;
}

.speaker-name {
    font-family: 'Lora', Georgia, serif;
    font-size: 1.5rem;
    font-weight: 500;
    color: var(--text);
    letter-spacing: -0.01em;
    margin-bottom: 0.2rem;
}

.speaker-role {
    font-size: 0.85rem;
    font-weight: 400;
    color: var(--text-secondary);
    margin-bottom: 0.6rem;
}

.speaker-style {
    font-family: 'Lora', serif;
    font-style: italic;
    font-size: 0.85rem;
    color: var(--text-muted);
}

/* ── Divider ── */
.rw-divider {
    border: none;
    border-top: 1px solid var(--border-light);
    margin: 1.5rem 0;
}

/* ── Section labels ── */
.section-label {
    font-size: 0.7rem;
    font-weight: 500;
    letter-spacing: 0.07em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 1rem;
}

/* ── Chat ── */
.chat-wrap {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.msg-user-row {
    display: flex;
    justify-content: flex-end;
    gap: 0.6rem;
    align-items: flex-end;
}

.msg-guest-row {
    display: flex;
    justify-content: flex-start;
    gap: 0.6rem;
    align-items: flex-end;
}

.bubble-user {
    background: var(--user-bg);
    color: var(--user-text);
    padding: 0.85rem 1.1rem;
    border-radius: 16px 16px 4px 16px;
    max-width: 76%;
    font-size: 0.9rem;
    line-height: 1.6;
    font-weight: 400;
}

.bubble-guest {
    background: var(--guest-bg);
    color: var(--guest-text);
    padding: 0.95rem 1.15rem;
    border-radius: 16px 16px 16px 4px;
    max-width: 82%;
    font-family: 'Lora', Georgia, serif;
    font-size: 0.97rem;
    line-height: 1.75;
}

.bubble-guest p {
    margin: 0 0 0.7em;
}

.bubble-guest p:last-child {
    margin-bottom: 0;
}

.msg-meta {
    font-size: 0.65rem;
    font-weight: 500;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-top: 0.35rem;
    padding: 0 0.3rem;
}

.avatar-thumb {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    object-fit: cover;
    border: 1.5px solid var(--border);
    flex-shrink: 0;
}

.avatar-you {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background: var(--text);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.6rem;
    font-weight: 600;
    color: white;
    letter-spacing: 0.04em;
    flex-shrink: 0;
}

/* ── Suggestion chips ── */
.suggestions-wrap {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.suggestion-chip {
    background: var(--bg-subtle);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    padding: 0.7rem 1rem;
    font-size: 0.88rem;
    color: var(--text-secondary);
    line-height: 1.4;
    cursor: pointer;
}

/* ── Inputs ── */
.stTextInput input {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.9rem !important;
    background: var(--bg) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text) !important;
    padding: 0.7rem 1rem !important;
    box-shadow: var(--shadow-sm) !important;
}

.stTextInput input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(217,119,87,0.12) !important;
    outline: none !important;
}

.stTextInput input::placeholder {
    color: var(--text-muted) !important;
}

.stTextArea textarea {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.9rem !important;
    background: var(--bg) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text) !important;
    padding: 0.75rem 1rem !important;
    line-height: 1.6 !important;
    box-shadow: var(--shadow-sm) !important;
}

.stTextArea textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(217,119,87,0.12) !important;
    outline: none !important;
}

.stTextArea textarea::placeholder {
    color: var(--text-muted) !important;
}

/* ── Buttons ── */
.stButton > button {
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.85rem !important;
    background: var(--accent) !important;
    color: white !important;
    border: none !important;
    border-radius: var(--radius-sm) !important;
    padding: 0.55rem 1.3rem !important;
    box-shadow: var(--shadow-sm) !important;
    transition: all 0.15s !important;
}

.stButton > button:hover {
    background: var(--accent-hover) !important;
    box-shadow: var(--shadow-md) !important;
    transform: translateY(-1px) !important;
}

div[data-testid="column"]:not(:first-child) .stButton > button {
    background: transparent !important;
    color: var(--text-secondary) !important;
    border: 1.5px solid var(--border) !important;
    box-shadow: none !important;
}

div[data-testid="column"]:not(:first-child) .stButton > button:hover {
    border-color: var(--text-secondary) !important;
    background: var(--surface-hover) !important;
    box-shadow: none !important;
    color: var(--text) !important;
    transform: none !important;
}

/* ── Alerts ── */
[data-testid="stAlert"] {
    background: var(--bg-subtle) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text-secondary) !important;
    font-size: 0.85rem !important;
}

/* ── Spinner ── */
.stSpinner > div {
    border-top-color: var(--accent) !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--bg-subtle) !important;
    border-right: 1px solid var(--border) !important;
}

[data-testid="stSidebar"] input {
    background: white !important;
}

/* ── Welcome state ── */
.welcome-text {
    text-align: center;
    padding: 2.5rem 1rem;
    color: var(--text-secondary);
    font-size: 0.95rem;
    line-height: 1.8;
}

.welcome-arrow {
    display: inline-block;
    font-size: 0.8rem;
    font-weight: 500;
    color: var(--accent);
    background: var(--accent-light);
    border-radius: 20px;
    padding: 0.35rem 1rem;
    margin-top: 1rem;
}

</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────

def extract_video_id(url):
    if "v=" in url:
        return url.split("v=")[1].split("&")[0]
    elif "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]
    return url.strip()


def get_transcript(url):
    video_id = extract_video_id(url)
    try:
        fetched = YouTubeTranscriptApi().fetch(video_id)
        text = " ".join([s.text for s in fetched])
        return text, video_id
    except Exception as e:
        return None, str(e)


def get_thumbnail_url(video_id):
    return f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"


def identify_speaker(client, transcript):
    response = client.chat.completions.create(
        model="deepseek-ai/DeepSeek-R1-0528",
        messages=[{
            "role": "user",
            "content": f"""Read this transcript excerpt and identify the main speaker or guest.
Return ONLY a valid JSON object with no extra text:
- "name": their full name (or "The Speaker" if unknown)
- "role": their role/title in one short phrase
- "style": 3-4 words describing their speaking style

Transcript:
{transcript[:3000]}"""
        }],
        temperature=0.1,
    )
    raw = response.choices[0].message.content
    raw = re.sub(r'<think>.*?</think>', '', raw, flags=re.DOTALL).strip()
    match = re.search(r'\{.*?\}', raw, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except:
            pass
    return {"name": "The Speaker", "role": "Video guest", "style": "thoughtful and direct"}


def get_reply(client, transcript, speaker, history, question):
    system = f"""You ARE {speaker['name']} — {speaker['role']}.

You just gave a talk or interview. Here is your transcript:
---
{transcript[:35000]}
---

Someone is continuing the conversation with you. Respond as {speaker['name']} would:
- First person, present tense
- Natural speaking style: {speaker['style']}
- Draw on the transcript AND your broader knowledge and views
- Be direct, specific, and genuinely opinionated
- No hedging, no "great question", no lists — just conversation
- 2-4 paragraphs maximum
- Stay completely in character"""

    messages = [{"role": "system", "content": system}]
    messages += history
    messages.append({"role": "user", "content": question})

    response = client.chat.completions.create(
        model="deepseek-ai/DeepSeek-R1-0528",
        messages=messages,
        temperature=0.72,
    )

    answer = response.choices[0].message.content
    answer = re.sub(r'<think>.*?</think>', '', answer, flags=re.DOTALL).strip()
    tokens = response.usage.total_tokens
    cost = tokens * 0.0000024

    return answer, tokens, cost


# ─────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────

defaults = {
    "transcript": None,
    "speaker": None,
    "history": [],
    "total_cost": 0.0,
    "video_loaded": False,
    "video_id": None,
    "thumbnail_url": None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## ⏮ Rewind")
    st.caption("Turn any podcast into a conversation.")
    st.markdown("---")

    api_key = st.text_input(
        "Nebius Token Factory API Key",
        type="password",
        placeholder="eyJh...",
        help="Get your free key at tokenfactory.nebius.com"
    )
    st.markdown("**Get your free API key:**")
    st.markdown("[tokenfactory.nebius.com →](https://tokenfactory.nebius.com)")
    st.caption("Sign in with Google → Settings → API Keys")

    if st.session_state.total_cost > 0:
        st.markdown("---")
        st.markdown(f"**Session cost:** `${st.session_state.total_cost:.5f}`")

    st.markdown("---")
    st.markdown("**Powered by**")
    st.markdown("[Nebius Token Factory](https://nebius.com/services/token-factory) · DeepSeek R1")

    st.markdown("---")
    st.caption(
        "⚠️ **Disclaimer:** Rewind generates AI responses based on YouTube transcripts. "
        "Responses are not real statements by the speakers and should not be attributed to them. "
        "For educational and exploratory use only."
    )
    st.caption(
        "Rewind does not store, reproduce, or redistribute video content. "
        "Transcripts are fetched in real time and processed ephemerally. "
        "YouTube content remains the property of its respective creators and rights holders."
    )
    st.caption("© 2026 Rewind. All rights reserved.")

# ─────────────────────────────────────────────────────────
# MASTHEAD
# ─────────────────────────────────────────────────────────

st.markdown("""
<div class="masthead">
    <div class="masthead-title">Rewind</div>
    <div class="masthead-sub">Turn any podcast into a conversation — there's always time for one more question.</div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
# NO KEY
# ─────────────────────────────────────────────────────────

if not api_key:
    st.markdown("""
    <div class="welcome-text">
        Paste a YouTube URL and Rewind identifies who's speaking.<br>
        Then ask them anything — push further, challenge them,<br>
        take the conversation wherever you want.<br>
        <div class="welcome-arrow">← Open sidebar to begin</div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

client = OpenAI(
    base_url="https://api.tokenfactory.nebius.com/v1/",
    api_key=api_key
)

# ─────────────────────────────────────────────────────────
# URL INPUT
# ─────────────────────────────────────────────────────────

if not st.session_state.video_loaded:

    st.markdown('<div class="section-label">Paste a YouTube link</div>', unsafe_allow_html=True)

    url = st.text_input(
        "",
        placeholder="https://www.youtube.com/watch?v=...",
        label_visibility="collapsed"
    )

    col1, col2 = st.columns([2, 5])
    with col1:
        load_btn = st.button("Load video")

    if load_btn and url:
        with st.spinner("Fetching transcript..."):
            transcript, result = get_transcript(url)

        if not transcript:
            st.error(f"Couldn't get transcript: {result}")
        else:
            video_id = extract_video_id(url)
            with st.spinner("Identifying speaker..."):
                speaker = identify_speaker(client, transcript)

            st.session_state.transcript = transcript
            st.session_state.speaker = speaker
            st.session_state.video_id = video_id
            st.session_state.thumbnail_url = get_thumbnail_url(video_id)
            st.session_state.history = []
            st.session_state.video_loaded = True
            st.rerun()

# ─────────────────────────────────────────────────────────
# CONVERSATION VIEW
# ─────────────────────────────────────────────────────────

else:
    speaker = st.session_state.speaker
    thumbnail = st.session_state.thumbnail_url
    video_id = st.session_state.video_id
    first_name = speaker['name'].split()[0]

    # ── Speaker card ──────────────────────────────────────
    st.markdown(f"""
    <div class="speaker-card">
        <div class="speaker-thumbnail-wrap">
            <img class="speaker-thumbnail"
                 src="{thumbnail}"
                 onerror="this.src='https://img.youtube.com/vi/{video_id}/hqdefault.jpg'"
                 alt="{speaker['name']}" />
            <div class="speaker-thumbnail-gradient"></div>
        </div>
        <div class="speaker-card-body">
            <div class="speaker-badge">🎙 Now speaking</div>
            <div class="speaker-name">{speaker['name']}</div>
            <div class="speaker-role">{speaker['role']}</div>
            <div class="speaker-style">{speaker['style']}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Controls ──────────────────────────────────────────
    col1, col2, col3 = st.columns([2, 2, 4])
    with col1:
        if st.button("Load new video"):
            for k, v in defaults.items():
                st.session_state[k] = v
            st.rerun()
    with col2:
        if st.session_state.history:
            if st.button("Clear chat"):
                st.session_state.history = []
                st.rerun()

    # ── Chat history ──────────────────────────────────────
    if st.session_state.history:
        st.markdown('<hr class="rw-divider">', unsafe_allow_html=True)
        st.markdown('<div class="section-label">Conversation</div>', unsafe_allow_html=True)

        chat_html = '<div class="chat-wrap">'
        for msg in st.session_state.history:
            if msg["role"] == "user":
                chat_html += f"""
                <div>
                    <div class="msg-user-row">
                        <div class="bubble-user">{msg['content']}</div>
                        <div class="avatar-you">You</div>
                    </div>
                </div>"""
            else:
                content = msg["content"]
                content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', content)
                content = re.sub(r'\*(.*?)\*', r'<em>\1</em>', content)
                paras = "".join(f"<p>{p.strip()}</p>" for p in content.split('\n\n') if p.strip())
                if not paras:
                    paras = f"<p>{content}</p>"
                chat_html += f"""
                <div>
                    <div class="msg-guest-row">
                        <img class="avatar-thumb"
                             src="{thumbnail}"
                             onerror="this.src='https://img.youtube.com/vi/{video_id}/hqdefault.jpg'"
                             alt="{first_name}" />
                        <div class="bubble-guest">{paras}</div>
                    </div>
                    <div class="msg-meta" style="padding-left: 2.5rem;">{first_name}</div>
                </div>"""
        chat_html += '</div>'
        st.markdown(chat_html, unsafe_allow_html=True)

    # ── Question input ─────────────────────────────────────
    st.markdown('<hr class="rw-divider">', unsafe_allow_html=True)
    st.markdown(f'<div class="section-label">Ask {first_name} a question</div>', unsafe_allow_html=True)

    question = st.text_area(
        "",
        placeholder=f"Push further, challenge them, take it somewhere new...",
        height=90,
        label_visibility="collapsed",
        key="q_input"
    )

    col1, col2 = st.columns([2, 5])
    with col1:
        ask_btn = st.button("Ask", key="ask_btn")

    if ask_btn and question.strip():
        with st.spinner(f"{first_name} is thinking..."):
            answer, tokens, cost = get_reply(
                client,
                st.session_state.transcript,
                speaker,
                st.session_state.history,
                question
            )

        st.session_state.history.append({"role": "user", "content": question})
        st.session_state.history.append({"role": "assistant", "content": answer})
        st.session_state.total_cost += cost

        if len(st.session_state.history) > 20:
            st.session_state.history = st.session_state.history[-20:]

        st.rerun()

    # ── Suggestions ────────────────────────────────────────
    if not st.session_state.history:
        st.markdown('<hr class="rw-divider">', unsafe_allow_html=True)
        st.markdown('<div class="section-label">Ways to start</div>', unsafe_allow_html=True)

        prompts = [
            "What's the most uncomfortable implication of what you just said?",
            "If you had to bet your career on one prediction from this talk — what would it be?",
            "What did your harshest critics get right?",
            "What did you leave out of this talk — deliberately?",
            "What would you say differently if you gave this talk tomorrow?",
        ]

        chips = '<div class="suggestions-wrap">'
        for p in prompts:
            chips += f'<div class="suggestion-chip">{p}</div>'
        chips += '</div>'
        st.markdown(chips, unsafe_allow_html=True)

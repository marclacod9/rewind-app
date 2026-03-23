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
# DESIGN SYSTEM — Late-night radio aesthetic
# Deep black, warm gold, cinematic typography
# ─────────────────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;0,700;1,300;1,400&family=Syne:wght@400;500;600;700;800&family=Syne+Mono&display=swap');

:root {
    --bg:        #0e0e0f;
    --surface:   #161618;
    --surface2:  #1e1e21;
    --gold:      #c9a84c;
    --gold-dim:  #8a6f2e;
    --text:      #e8e4dc;
    --text-dim:  #7a7570;
    --text-muted:#3d3b38;
    --accent:    #c9a84c;
    --border:    #2a2825;
    --user-bg:   #c9a84c;
    --user-text: #0e0e0f;
    --guest-bg:  #1e1e21;
    --guest-text:#e8e4dc;
}

/* ── Reset ── */
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stApp"] {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Syne', sans-serif !important;
}

[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed;
    inset: 0;
    background:
        radial-gradient(ellipse 80% 50% at 50% -10%, rgba(201,168,76,0.08) 0%, transparent 70%),
        radial-gradient(ellipse 60% 40% at 100% 100%, rgba(201,168,76,0.04) 0%, transparent 60%);
    pointer-events: none;
    z-index: 0;
}

#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"] { display: none !important; }

.block-container {
    max-width: 680px !important;
    padding: 0 1.5rem 4rem !important;
    position: relative;
    z-index: 1;
}

/* ── Masthead ── */
.masthead {
    padding: 3.5rem 0 2.5rem;
    text-align: center;
    position: relative;
}

.masthead::after {
    content: '';
    display: block;
    width: 1px;
    height: 40px;
    background: linear-gradient(to bottom, var(--gold), transparent);
    margin: 2rem auto 0;
}

.logo-mark {
    font-family: 'Syne Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.3em;
    color: var(--gold);
    text-transform: uppercase;
    margin-bottom: 1.2rem;
    opacity: 0.8;
}

.main-title {
    font-family: 'Cormorant Garamond', serif;
    font-size: 5.5rem;
    font-weight: 300;
    letter-spacing: -0.03em;
    line-height: 0.9;
    color: var(--text);
    margin-bottom: 1.2rem;
    background: linear-gradient(135deg, #e8e4dc 0%, #c9a84c 60%, #e8e4dc 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.main-sub {
    font-family: 'Cormorant Garamond', serif;
    font-style: italic;
    font-size: 1.1rem;
    font-weight: 300;
    color: var(--text-dim);
    letter-spacing: 0.01em;
    line-height: 1.5;
    max-width: 380px;
    margin: 0 auto;
}

/* ── URL input section ── */
.url-section {
    margin-top: 1.5rem;
}

.field-label {
    font-family: 'Syne Mono', monospace;
    font-size: 0.6rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--gold-dim);
    margin-bottom: 0.6rem;
    display: block;
}

/* ── Inputs ── */
.stTextInput input,
.stTextArea textarea {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 4px !important;
    color: var(--text) !important;
    font-family: 'Syne Mono', monospace !important;
    font-size: 0.8rem !important;
    padding: 0.8rem 1rem !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}

.stTextInput input:focus,
.stTextArea textarea:focus {
    border-color: var(--gold-dim) !important;
    box-shadow: 0 0 0 3px rgba(201,168,76,0.08) !important;
    outline: none !important;
}

.stTextInput input::placeholder,
.stTextArea textarea::placeholder {
    color: var(--text-muted) !important;
}

/* ── Buttons ── */
.stButton > button {
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    background: transparent !important;
    color: var(--gold) !important;
    border: 1px solid var(--gold-dim) !important;
    border-radius: 3px !important;
    padding: 0.55rem 1.4rem !important;
    transition: all 0.2s !important;
}

.stButton > button:hover {
    background: var(--gold) !important;
    color: var(--bg) !important;
    border-color: var(--gold) !important;
    box-shadow: 0 0 20px rgba(201,168,76,0.25) !important;
}

/* ── Speaker hero card ── */
.speaker-hero {
    position: relative;
    border-radius: 6px;
    overflow: hidden;
    margin: 2rem 0;
    border: 1px solid var(--border);
}

.speaker-thumbnail {
    width: 100%;
    height: 280px;
    object-fit: cover;
    display: block;
    filter: brightness(0.6) saturate(0.8);
}

.speaker-overlay {
    position: absolute;
    inset: 0;
    background: linear-gradient(
        to top,
        rgba(14,14,15,0.98) 0%,
        rgba(14,14,15,0.7) 40%,
        rgba(14,14,15,0.1) 100%
    );
}

.speaker-info-overlay {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    padding: 2rem;
}

.speaker-tag {
    display: inline-block;
    font-family: 'Syne Mono', monospace;
    font-size: 0.6rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--gold);
    background: rgba(201,168,76,0.1);
    border: 1px solid rgba(201,168,76,0.3);
    padding: 0.25rem 0.6rem;
    border-radius: 2px;
    margin-bottom: 0.8rem;
}

.speaker-hero-name {
    font-family: 'Cormorant Garamond', serif;
    font-size: 2.4rem;
    font-weight: 600;
    color: var(--text);
    line-height: 1.1;
    margin-bottom: 0.4rem;
    letter-spacing: -0.01em;
}

.speaker-hero-role {
    font-family: 'Syne', sans-serif;
    font-size: 0.75rem;
    font-weight: 400;
    color: var(--text-dim);
    letter-spacing: 0.05em;
}

.speaker-style-badge {
    display: inline-block;
    font-family: 'Cormorant Garamond', serif;
    font-style: italic;
    font-size: 0.85rem;
    color: var(--gold);
    margin-top: 0.5rem;
    opacity: 0.8;
}

/* ── Divider ── */
.rw-divider {
    border: none;
    border-top: 1px solid var(--border);
    margin: 1.5rem 0;
}

/* ── Chat ── */
.chat-container {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
    margin: 1.5rem 0;
}

.msg-row-user {
    display: flex;
    justify-content: flex-end;
    gap: 0.8rem;
    align-items: flex-end;
}

.msg-row-guest {
    display: flex;
    justify-content: flex-start;
    gap: 0.8rem;
    align-items: flex-end;
}

.bubble-user {
    background: var(--gold);
    color: var(--bg);
    padding: 1rem 1.3rem;
    border-radius: 16px 16px 4px 16px;
    max-width: 78%;
    font-family: 'Syne', sans-serif;
    font-size: 0.88rem;
    font-weight: 500;
    line-height: 1.6;
    box-shadow: 0 4px 20px rgba(201,168,76,0.15);
}

.bubble-guest {
    background: var(--surface2);
    color: var(--text);
    padding: 1.1rem 1.4rem;
    border-radius: 16px 16px 16px 4px;
    max-width: 85%;
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.05rem;
    font-weight: 400;
    line-height: 1.75;
    border: 1px solid var(--border);
}

.bubble-guest strong, .bubble-guest b {
    color: var(--gold);
    font-weight: 600;
}

.bubble-guest em, .bubble-guest i {
    color: var(--text-dim);
}

.msg-label {
    font-family: 'Syne Mono', monospace;
    font-size: 0.58rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-top: 0.4rem;
    padding: 0 0.3rem;
}

.msg-label-right {
    text-align: right;
}

.avatar-circle {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    object-fit: cover;
    border: 1px solid var(--border);
    flex-shrink: 0;
    filter: brightness(0.85);
}

.avatar-you {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: var(--gold);
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'Syne', sans-serif;
    font-size: 0.65rem;
    font-weight: 700;
    color: var(--bg);
    flex-shrink: 0;
    letter-spacing: 0.05em;
}

/* ── Suggested prompts ── */
.prompts-grid {
    display: flex;
    flex-direction: column;
    gap: 0.6rem;
    margin: 1.2rem 0;
}

.prompt-chip {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 0.75rem 1rem;
    font-family: 'Cormorant Garamond', serif;
    font-style: italic;
    font-size: 0.95rem;
    color: var(--text-dim);
    cursor: pointer;
    transition: all 0.2s;
    line-height: 1.4;
}

.prompt-chip:hover {
    border-color: var(--gold-dim);
    color: var(--gold);
    background: rgba(201,168,76,0.05);
}

/* ── Cost indicator ── */
.cost-line {
    font-family: 'Syne Mono', monospace;
    font-size: 0.58rem;
    letter-spacing: 0.1em;
    color: var(--text-muted);
    text-align: right;
    margin-top: 0.3rem;
}

/* ── Loading ── */
.stSpinner > div {
    border-color: var(--gold) transparent transparent transparent !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] div {
    color: var(--text-dim) !important;
}
[data-testid="stSidebar"] input {
    background: var(--surface2) !important;
    border-color: var(--border) !important;
    color: var(--text) !important;
}
[data-testid="stSidebar"] h3 {
    color: var(--gold) !important;
    font-family: 'Cormorant Garamond', serif !important;
}

/* ── Alerts ── */
[data-testid="stAlert"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-dim) !important;
    border-radius: 4px !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 0.85rem !important;
}

/* ── Section header ── */
.section-head {
    font-family: 'Syne Mono', monospace;
    font-size: 0.58rem;
    letter-spacing: 0.25em;
    text-transform: uppercase;
    color: var(--gold-dim);
    margin-bottom: 0.8rem;
    display: flex;
    align-items: center;
    gap: 0.8rem;
}

.section-head::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--border);
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
    """YouTube always has a thumbnail at this URL."""
    return f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"


def identify_speaker(client, transcript):
    """Ask the model to identify who is speaking."""
    response = client.chat.completions.create(
        model="deepseek-ai/DeepSeek-R1-0528",
        messages=[{
            "role": "user",
            "content": f"""Read this transcript excerpt and identify the main speaker or guest.
Return ONLY a JSON object (no markdown, no explanation) with:
- "name": their full name (or "The Speaker" if unknown)
- "role": their role/title in one short phrase
- "style": 3 words describing how they speak (e.g. "razor-sharp, provocative, witty")

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
    return {"name": "The Speaker", "role": "Video guest", "style": "thoughtful, direct, clear"}


def get_reply(client, transcript, speaker, history, question):
    """Generate a reply in the speaker's voice."""

    system = f"""You ARE {speaker['name']} — {speaker['role']}.

You just gave a talk. Here is your transcript:
---
{transcript[:35000]}
---

Someone is now talking to you directly. Your job:
- Respond as {speaker['name']} would, in first person
- Your natural style: {speaker['style']}
- Draw on the transcript AND your broader views and knowledge
- Be direct, specific, and opinionated
- If pushed on something uncomfortable, don't dodge — engage
- No academic hedging. No "that's a great question."
- 2-4 paragraphs, conversational, never listy
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

for key, default in [
    ("transcript", None),
    ("speaker", None),
    ("history", []),
    ("total_cost", 0.0),
    ("video_loaded", False),
    ("video_id", None),
    ("thumbnail_url", None),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ─────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("### ⏮ Rewind")
    st.markdown("---")
    api_key = st.text_input(
        "Nebius Token Factory API Key",
        type="password",
        placeholder="eyJh...",
        help="Free at tokenfactory.nebius.com"
    )
    if st.session_state.total_cost > 0:
        st.markdown(f"**Session cost:** `${st.session_state.total_cost:.5f}`")
    st.markdown("---")
    st.markdown("Get your free key:")
    st.markdown("[tokenfactory.nebius.com](https://tokenfactory.nebius.com)")
    st.markdown("Sign in with Google → Settings → API Keys")
    st.markdown("---")
    st.markdown("*Powered by DeepSeek R1 on Nebius Token Factory*")

# ─────────────────────────────────────────────────────────
# MASTHEAD
# ─────────────────────────────────────────────────────────

st.markdown("""
<div class="masthead">
    <div class="logo-mark">⏮ &nbsp; Rewind</div>
    <div class="main-title">Rewind</div>
    <div class="main-sub">Turn podcasts into conversations,<br>always time for one more question</div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
# NO KEY STATE
# ─────────────────────────────────────────────────────────

if not api_key:
    st.markdown("""
    <div style="text-align:center; padding: 2rem 0;">
        <div style="font-family:'Cormorant Garamond',serif; font-style:italic; font-size:1.05rem; color:#7a7570; line-height:2;">
            Paste any YouTube URL.<br>
            Rewind figures out who's speaking.<br>
            Then the conversation continues — on your terms.<br><br>
            <span style="color:#c9a84c; font-style:normal; font-family:'Syne Mono',monospace; font-size:0.7rem; letter-spacing:0.15em;">
            ← OPEN SIDEBAR TO BEGIN
            </span>
        </div>
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

    st.markdown('<div class="section-head">Load a video</div>', unsafe_allow_html=True)

    url = st.text_input(
        "",
        placeholder="https://www.youtube.com/watch?v=...",
        label_visibility="collapsed"
    )

    col1, col2 = st.columns([2, 5])
    with col1:
        load_btn = st.button("Load →")

    if load_btn and url:
        with st.spinner("Fetching transcript..."):
            transcript, result = get_transcript(url)

        if not transcript:
            st.error(f"Couldn't get transcript. Make sure the video has captions enabled.")
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

    # ── Speaker hero card with thumbnail ──────────────────
    st.markdown(f"""
    <div class="speaker-hero">
        <img class="speaker-thumbnail"
             src="{thumbnail}"
             onerror="this.src='https://img.youtube.com/vi/{video_id}/hqdefault.jpg'"
             alt="{speaker['name']}" />
        <div class="speaker-overlay"></div>
        <div class="speaker-info-overlay">
            <div class="speaker-tag">Now speaking</div>
            <div class="speaker-hero-name">{speaker['name']}</div>
            <div class="speaker-hero-role">{speaker['role']}</div>
            <div class="speaker-style-badge">"{speaker['style']}"</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Controls ──────────────────────────────────────────
    col1, col2, col3 = st.columns([2, 2, 4])
    with col1:
        if st.button("← New video"):
            for k in ["video_loaded", "transcript", "speaker", "history", "video_id", "thumbnail_url"]:
                st.session_state[k] = None if k != "video_loaded" else False
                if k == "history":
                    st.session_state[k] = []
            st.rerun()
    with col2:
        if st.session_state.history and st.button("Clear chat"):
            st.session_state.history = []
            st.rerun()

    # ── Chat history ──────────────────────────────────────
    if st.session_state.history:
        st.markdown('<hr class="rw-divider">', unsafe_allow_html=True)
        st.markdown('<div class="section-head">Conversation</div>', unsafe_allow_html=True)

        chat_html = '<div class="chat-container">'
        for msg in st.session_state.history:
            if msg["role"] == "user":
                chat_html += f"""
                <div>
                    <div class="msg-row-user">
                        <div class="bubble-user">{msg['content']}</div>
                        <div class="avatar-you">YOU</div>
                    </div>
                </div>"""
            else:
                content = msg["content"].replace('\n\n', '</p><p>').replace('\n', '<br>')
                content = f"<p>{content}</p>"
                chat_html += f"""
                <div>
                    <div class="msg-row-guest">
                        <img class="avatar-circle"
                             src="{thumbnail}"
                             onerror="this.src='https://img.youtube.com/vi/{video_id}/hqdefault.jpg'"
                             alt="{speaker['name']}" />
                        <div class="bubble-guest">{content}</div>
                    </div>
                    <div class="msg-label" style="padding-left:2.8rem;">{speaker['name'].upper().split()[0]}</div>
                </div>"""
        chat_html += '</div>'
        st.markdown(chat_html, unsafe_allow_html=True)

    # ── Question input ─────────────────────────────────────
    st.markdown('<hr class="rw-divider">', unsafe_allow_html=True)
    st.markdown(f'<div class="section-head">Your question</div>', unsafe_allow_html=True)

    question = st.text_area(
        "",
        placeholder=f"Ask {speaker['name'].split()[0]} anything — push further, challenge them, redirect...",
        height=90,
        label_visibility="collapsed",
        key="q_input"
    )

    col1, col2 = st.columns([2, 5])
    with col1:
        ask_btn = st.button("Ask →", key="ask")

    if ask_btn and question.strip():
        with st.spinner(f"{speaker['name'].split()[0]} is thinking..."):
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

    # ── Suggested prompts (only when no history) ──────────
    if not st.session_state.history:
        st.markdown('<hr class="rw-divider">', unsafe_allow_html=True)
        st.markdown('<div class="section-head">Start the conversation</div>', unsafe_allow_html=True)

        prompts = [
            "What's the most uncomfortable implication of what you just said?",
            "If you had to bet your career on one prediction from this talk — what is it?",
            "What did your harshest critics get right about your argument?",
            "What did you leave out of this talk — deliberately?",
            "What would you say differently if you gave this talk tomorrow?",
        ]

        chips_html = '<div class="prompts-grid">'
        for p in prompts:
            chips_html += f'<div class="prompt-chip">→ {p}</div>'
        chips_html += '</div>'
        st.markdown(chips_html, unsafe_allow_html=True)

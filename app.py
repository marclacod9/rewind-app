import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from openai import OpenAI

# ─────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Rewind — Talk to any video",
    page_icon="⏮",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────────────────────
# STYLING
# ─────────────────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=DM+Mono:wght@300;400&family=DM+Sans:wght@300;400;500&display=swap');

:root {
    --ink: #1a1a1a;
    --paper: #f5f0e8;
    --accent: #c0392b;
    --muted: #8a8070;
    --border: #d4cfc4;
    --bubble-user: #1a1a1a;
    --bubble-guest: #ffffff;
}

html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--paper) !important;
    font-family: 'DM Sans', sans-serif;
    color: var(--ink);
}

[data-testid="stAppViewContainer"] {
    background-image: 
        radial-gradient(ellipse at 20% 50%, rgba(192,57,43,0.04) 0%, transparent 60%),
        radial-gradient(ellipse at 80% 20%, rgba(26,26,26,0.03) 0%, transparent 50%);
}

/* Hide Streamlit chrome */
#MainMenu, footer, header, [data-testid="stToolbar"] { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }

/* Main container */
.block-container {
    max-width: 720px !important;
    padding: 3rem 2rem !important;
}

/* Masthead */
.masthead {
    text-align: center;
    padding: 2rem 0 3rem;
    border-bottom: 2px solid var(--ink);
    margin-bottom: 2.5rem;
}

.masthead-title {
    font-family: 'Playfair Display', serif;
    font-size: 3.2rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    color: var(--ink);
    line-height: 1;
    margin-bottom: 0.4rem;
}

.masthead-sub {
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    font-weight: 300;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--muted);
}

.masthead-rule {
    width: 40px;
    height: 2px;
    background: var(--accent);
    margin: 1rem auto;
}

/* Speaker card */
.speaker-card {
    background: var(--ink);
    color: var(--paper);
    border-radius: 2px;
    padding: 1.5rem 2rem;
    margin: 0 0 2rem;
    display: flex;
    align-items: center;
    gap: 1.5rem;
}

.speaker-avatar {
    font-size: 2.5rem;
    line-height: 1;
    flex-shrink: 0;
}

.speaker-info {}

.speaker-name {
    font-family: 'Playfair Display', serif;
    font-size: 1.4rem;
    font-weight: 700;
    letter-spacing: -0.01em;
    margin-bottom: 0.2rem;
}

.speaker-role {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: rgba(245,240,232,0.5);
}

.speaker-ready {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.8rem;
    color: rgba(245,240,232,0.7);
    margin-top: 0.5rem;
    font-style: italic;
}

/* Section labels */
.section-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 0.8rem;
}

/* Chat messages */
.chat-wrapper {
    display: flex;
    flex-direction: column;
    gap: 1.2rem;
    margin-bottom: 1.5rem;
}

.msg-user {
    display: flex;
    justify-content: flex-end;
}

.msg-guest {
    display: flex;
    justify-content: flex-start;
}

.bubble-user {
    background: var(--bubble-user);
    color: var(--paper);
    padding: 0.9rem 1.2rem;
    border-radius: 2px 2px 2px 12px;
    max-width: 80%;
    font-size: 0.9rem;
    line-height: 1.6;
}

.bubble-guest {
    background: var(--bubble-guest);
    color: var(--ink);
    padding: 0.9rem 1.2rem;
    border-radius: 2px 2px 12px 2px;
    max-width: 85%;
    font-size: 0.9rem;
    line-height: 1.7;
    border: 1px solid var(--border);
    box-shadow: 2px 2px 0px var(--border);
}

.bubble-meta {
    font-family: 'DM Mono', monospace;
    font-size: 0.6rem;
    color: var(--muted);
    margin-top: 0.4rem;
    letter-spacing: 0.05em;
}

/* Input area */
.stTextArea textarea {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.9rem !important;
    background: white !important;
    border: 1px solid var(--border) !important;
    border-radius: 2px !important;
    color: var(--ink) !important;
    padding: 0.8rem 1rem !important;
    line-height: 1.6 !important;
}

.stTextArea textarea:focus {
    border-color: var(--ink) !important;
    box-shadow: 2px 2px 0 var(--ink) !important;
}

/* Buttons */
.stButton > button {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    background: var(--ink) !important;
    color: var(--paper) !important;
    border: none !important;
    border-radius: 2px !important;
    padding: 0.6rem 1.5rem !important;
    cursor: pointer !important;
    transition: all 0.15s !important;
}

.stButton > button:hover {
    background: var(--accent) !important;
    transform: translate(-1px, -1px) !important;
    box-shadow: 2px 2px 0 var(--ink) !important;
}

/* URL input */
.stTextInput input {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.8rem !important;
    background: white !important;
    border: 1px solid var(--border) !important;
    border-radius: 2px !important;
    color: var(--ink) !important;
    padding: 0.7rem 1rem !important;
}

.stTextInput input:focus {
    border-color: var(--ink) !important;
    box-shadow: 2px 2px 0 var(--ink) !important;
}

/* Divider */
.editorial-rule {
    border: none;
    border-top: 1px solid var(--border);
    margin: 2rem 0;
}

/* Cost chip */
.cost-chip {
    display: inline-block;
    font-family: 'DM Mono', monospace;
    font-size: 0.6rem;
    letter-spacing: 0.08em;
    color: var(--muted);
    background: rgba(138,128,112,0.1);
    padding: 0.2rem 0.5rem;
    border-radius: 2px;
    margin-top: 0.3rem;
}

/* Sidebar API key */
[data-testid="stSidebar"] {
    background: var(--ink) !important;
}

[data-testid="stSidebar"] * {
    color: var(--paper) !important;
}

[data-testid="stSidebar"] input {
    background: rgba(255,255,255,0.1) !important;
    border-color: rgba(255,255,255,0.2) !important;
    color: var(--paper) !important;
}

/* Alert / info */
.stAlert {
    border-radius: 2px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.85rem !important;
}

/* Spinner */
.stSpinner > div {
    border-top-color: var(--accent) !important;
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


def identify_speaker(client, transcript):
    """Ask the LLM to identify who is speaking in the video."""
    response = client.chat.completions.create(
        model="deepseek-ai/DeepSeek-R1-0528",
        messages=[{
            "role": "user",
            "content": f"""Read this transcript excerpt and identify the main speaker or guest.
Return ONLY a JSON object with these fields:
- "name": their full name (or "The Speaker" if unknown)
- "role": their role/title in one short phrase (e.g. "Renaissance historian & novelist" or "AI researcher at Google")
- "style": 2-3 words describing their speaking style (e.g. "sharp, provocative, analytical")

Transcript excerpt:
{transcript[:3000]}

Return only valid JSON, nothing else."""
        }],
        temperature=0.1,
    )
    import json
    import re
    raw = response.choices[0].message.content
    # Strip thinking tags if present
    raw = re.sub(r'<think>.*?</think>', '', raw, flags=re.DOTALL).strip()
    # Extract JSON
    match = re.search(r'\{.*?\}', raw, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except:
            pass
    return {"name": "The Speaker", "role": "Video guest", "style": "thoughtful, direct"}


def get_reply(client, transcript, speaker, history, question):
    """Generate a reply in the speaker's voice."""

    system = f"""You ARE {speaker['name']} — {speaker['role']}.

You just gave a talk/interview. Here is your transcript:
---
{transcript[:35000]}
---

Someone is now continuing the conversation with you directly. Respond exactly as {speaker['name']} would:
- First person, present tense
- Your style: {speaker['style']}
- Draw on what you said in the transcript AND your broader knowledge and views
- Be direct, opinionated, and specific — not academic or hedging
- If pushed on something controversial, lean into it
- Stay completely in character — never break the fourth wall
- Keep responses conversational (2-4 paragraphs max)"""

    messages = [{"role": "system", "content": system}]
    messages += history
    messages.append({"role": "user", "content": question})

    response = client.chat.completions.create(
        model="deepseek-ai/DeepSeek-R1-0528",
        messages=messages,
        temperature=0.7,
    )

    answer = response.choices[0].message.content
    # Remove thinking tags
    import re
    answer = re.sub(r'<think>.*?</think>', '', answer, flags=re.DOTALL).strip()
    tokens = response.usage.total_tokens
    cost = tokens * 0.0000024  # DeepSeek R1 base ~$2.4/M output blended

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
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ─────────────────────────────────────────────────────────
# SIDEBAR — API KEY
# ─────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("### ⏮ Rewind")
    st.markdown("---")
    api_key = st.text_input(
        "Nebius Token Factory API Key",
        type="password",
        placeholder="eyJh...",
        help="Get your free key at tokenfactory.nebius.com"
    )
    st.markdown("---")
    st.markdown("**Get a free API key:**")
    st.markdown("→ [tokenfactory.nebius.com](https://tokenfactory.nebius.com)")
    st.markdown("Sign in with Google → Settings → API Keys")
    st.markdown("---")
    if st.session_state.total_cost > 0:
        st.markdown(f"**Session cost:** `${st.session_state.total_cost:.5f}`")
    st.markdown("---")
    st.markdown("*Built on [Nebius Token Factory](https://nebius.com/services/token-factory)*")
    st.markdown("*Model: DeepSeek R1*")

# ─────────────────────────────────────────────────────────
# MASTHEAD
# ─────────────────────────────────────────────────────────

st.markdown("""
<div class="masthead">
    <div class="masthead-title">Rewind</div>
    <div class="masthead-rule"></div>
    <div class="masthead-sub">Continue any conversation. Redirect any mind.</div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
# MAIN FLOW
# ─────────────────────────────────────────────────────────

if not api_key:
    st.info("👈 Open the sidebar and paste your Nebius Token Factory API key to begin.")
    st.markdown("""
    <div style="font-family: 'DM Mono', monospace; font-size: 0.75rem; color: #8a8070; margin-top: 2rem; line-height: 2;">
    WHAT IS THIS?<br><br>
    Paste any YouTube URL.<br>
    Rewind identifies who's speaking.<br>
    Then talk to them — directly.<br><br>
    Ask what the video didn't.<br>
    Push back. Go deeper.<br>
    Redirect the conversation wherever you want.
    </div>
    """, unsafe_allow_html=True)
    st.stop()

client = OpenAI(
    base_url="https://api.tokenfactory.nebius.com/v1/",
    api_key=api_key
)

# ── URL INPUT ─────────────────────────────────────────────

if not st.session_state.video_loaded:
    st.markdown('<div class="section-label">Load a video</div>', unsafe_allow_html=True)

    url = st.text_input(
        "",
        placeholder="https://www.youtube.com/watch?v=...",
        label_visibility="collapsed"
    )

    col1, col2 = st.columns([1, 3])
    with col1:
        load_btn = st.button("Load video →")

    if load_btn and url:
        with st.spinner("Fetching transcript..."):
            transcript, error = get_transcript(url)

        if not transcript:
            st.error(f"Couldn't get transcript: {error}. Try a video with captions enabled.")
        else:
            with st.spinner("Identifying speaker..."):
                speaker = identify_speaker(client, transcript)

            st.session_state.transcript = transcript
            st.session_state.speaker = speaker
            st.session_state.history = []
            st.session_state.video_loaded = True
            st.rerun()

# ── CONVERSATION ──────────────────────────────────────────

else:
    speaker = st.session_state.speaker

    # Speaker card
    st.markdown(f"""
    <div class="speaker-card">
        <div class="speaker-avatar">🎙</div>
        <div class="speaker-info">
            <div class="speaker-name">{speaker['name']}</div>
            <div class="speaker-role">{speaker['role']}</div>
            <div class="speaker-ready">Ready to continue the conversation</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Reset button
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("← New video"):
            st.session_state.video_loaded = False
            st.session_state.transcript = None
            st.session_state.speaker = None
            st.session_state.history = []
            st.rerun()

    st.markdown('<hr class="editorial-rule">', unsafe_allow_html=True)

    # Chat history
    if st.session_state.history:
        st.markdown('<div class="section-label">Conversation</div>', unsafe_allow_html=True)
        chat_html = '<div class="chat-wrapper">'
        for msg in st.session_state.history:
            if msg["role"] == "user":
                chat_html += f"""
                <div class="msg-user">
                    <div>
                        <div class="bubble-user">{msg["content"]}</div>
                        <div class="bubble-meta" style="text-align:right">YOU</div>
                    </div>
                </div>"""
            else:
                content = msg["content"].replace('\n', '<br>')
                chat_html += f"""
                <div class="msg-guest">
                    <div>
                        <div class="bubble-guest">{content}</div>
                        <div class="bubble-meta">{speaker['name'].upper()}</div>
                    </div>
                </div>"""
        chat_html += '</div>'
        st.markdown(chat_html, unsafe_allow_html=True)
        st.markdown('<hr class="editorial-rule">', unsafe_allow_html=True)

    # Question input
    st.markdown('<div class="section-label">Your question</div>', unsafe_allow_html=True)

    question = st.text_area(
        "",
        placeholder=f"Ask {speaker['name']} anything — push back, go deeper, redirect...",
        height=100,
        label_visibility="collapsed",
        key="question_input"
    )

    col1, col2, col3 = st.columns([2, 2, 3])
    with col1:
        ask_btn = st.button("Ask →")
    with col2:
        if st.button("Clear chat"):
            st.session_state.history = []
            st.rerun()

    if ask_btn and question.strip():
        with st.spinner(f"{speaker['name']} is thinking..."):
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

        # Keep history manageable
        if len(st.session_state.history) > 20:
            st.session_state.history = st.session_state.history[-20:]

        st.rerun()

    # Suggested prompts
    if not st.session_state.history:
        st.markdown('<hr class="editorial-rule">', unsafe_allow_html=True)
        st.markdown('<div class="section-label">Suggested openers</div>', unsafe_allow_html=True)
        suggestions = [
            "What's the most uncomfortable implication of what you just said?",
            "If you had to bet your career on one prediction from this talk — what is it?",
            "What would your harshest critic say about your argument?",
            "What did you leave out of this talk — deliberately or not?",
        ]
        for s in suggestions:
            st.markdown(f"<div style='font-size:0.8rem; color:#8a8070; padding:0.3rem 0; font-style:italic;'>→ {s}</div>", unsafe_allow_html=True)

from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import re
from langchain_mistralai import ChatMistralAI
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage

st.set_page_config(page_title="Mood AI", page_icon="🎭", layout="centered")

PHOTO_URL = "https://raw.githubusercontent.com/vaibhavcor8/mood-ai/main/WhatsApp%20Image%202026-05-10%20at%205.04.39%20PM.jpeg"

MOODS = {
    "1": {"color": "#ff4444", "emoji": "😤", "label": "ANGRY", "desc": "Hot-headed & savage replies", "tone": "angry AI agent, always answer in very angry aggressive mode"},
    "2": {"color": "#f5e642", "emoji": "😄", "label": "FUNNY", "desc": "Jokes, puns & chaos",         "tone": "funny AI agent, always answer in very funny humorous mode"},
    "3": {"color": "#4fc3f7", "emoji": "😢", "label": "SAD",   "desc": "Melancholic & moody vibes",   "tone": "sad AI agent, always answer in very sad emotional mode"},
}

# ── Name detection via model ──────────────────────────────────────────────────
def detect_name_intent(text, model):
    try:
        from langchain_core.messages import HumanMessage as HM, SystemMessage as SM
        resp = model.invoke([
            SM(content="You are a name-detection assistant. The user may or may not be setting a new name for an AI chatbot. If the user is giving/setting/changing a name for the bot, reply with ONLY that name in UPPERCASE, nothing else. If the user is NOT setting a name, reply with exactly: NO"),
            HM(content=text)
        ])
        result = resp.content.strip().upper()
        if result != "NO" and len(result.split()) == 1 and len(result) >= 2:
            return result
    except:
        pass
    return None

NAME_QUESTION_PATTERNS = [
    r'\bwhat\s+is\s+your\s+name\b', r'\bwhats\s+your\s+name\b',
    r'\byour\s+name\b', r'\bnaam\s+(kya|btao|bato|batao|kya\s+hai|kya\s+he|bolo)\b',
    r'\b(aapka|tumhara|tera|apna)\s+naam\b',
    r'\btum\s+kaun\s+ho\b', r'\bwho\s+are\s+you\b', r'\bapna\s+naam\b',
]

def is_name_question(text):
    t = text.lower().strip()
    return any(re.search(p, t) for p in NAME_QUESTION_PATTERNS)

def get_system_prompt(tone, name):
    return (
        f"You are a {tone}. Your name is {name}. "
        f"Always respond in the same language the user writes in. "
        f"Keep answers short — max 2-3 sentences."
    )

# ── Session state ─────────────────────────────────────────────────────────────
if "mood_key"  not in st.session_state: st.session_state.mood_key  = None
if "model"     not in st.session_state: st.session_state.model     = ChatMistralAI(model="mistral-small-2506", temperature=0.9)
if "chat"      not in st.session_state: st.session_state.chat      = []
if "bot_name"  not in st.session_state: st.session_state.bot_name  = None

# ── Pehli baar naam lo ────────────────────────────────────────────────────────
if not st.session_state.bot_name:
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:1rem;margin-bottom:2rem;">
        <img src="{PHOTO_URL}" width="56" height="56"
             style="border-radius:50%;border:2px solid #f5e642;object-fit:cover;">
        <div>
            <div style="font-family:'Syne',sans-serif;font-weight:800;font-size:1.8rem;color:#f5e642;">🎭 Mood AI</div>
            <div style="font-size:0.7rem;color:#555;letter-spacing:0.1em;text-transform:uppercase;">by Vaibhav Srivastava</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    with st.form("name_form"):
        user_name = st.text_input("AI ka naam kya rakhna hai?", placeholder="e.g. CHAT_SHERA")
        submitted = st.form_submit_button("Shuru Karo →")
        if submitted and user_name.strip():
            st.session_state.bot_name = user_name.strip().upper()
            st.rerun()
    st.stop()

mood    = MOODS.get(st.session_state.mood_key)
primary = mood["color"] if mood else "#f5e642"
name    = st.session_state.bot_name

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=DM+Mono:wght@300;400;500&display=swap');
html, body, [class*="css"] {{ font-family: 'DM Mono', monospace; background-color: #0d0d0d; color: #f0ede6; }}
.stApp {{ background: #0d0d0d; }}
.title {{ font-family: 'Syne', sans-serif; font-weight: 800; font-size: 2.4rem; color: {primary}; letter-spacing: -0.03em; line-height: 1; margin-bottom: 0.2rem; }}
.subtitle {{ font-size: 0.72rem; color: #444; text-transform: uppercase; letter-spacing: 0.12em; margin-bottom: 2rem; }}
.badge {{ display: inline-block; background: {primary}; color: #000; font-family: 'Syne', sans-serif; font-weight: 800; font-size: 0.68rem; letter-spacing: 0.12em; padding: 3px 10px; border-radius: 4px; margin-bottom: 1rem; }}
[data-testid="stChatMessage"] p {{ font-family: 'DM Mono', monospace !important; font-size: 0.875rem !important; line-height: 1.7 !important; }}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {{ background: #111 !important; border-left: 3px solid {primary} !important; border-radius: 0 8px 8px 0 !important; padding: 0.7rem 1rem !important; margin-left: 2rem !important; }}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {{ background: #0a0a0a !important; border-left: 3px solid #333 !important; border-radius: 0 8px 8px 0 !important; padding: 0.7rem 1rem !important; margin-right: 2rem !important; }}
[data-testid="stChatInput"] textarea {{ background: #111 !important; color: #f0ede6 !important; font-family: 'DM Mono', monospace !important; font-size: 0.875rem !important; border: 1px solid #222 !important; border-radius: 8px !important; }}
[data-testid="stChatInput"] textarea:focus {{ border-color: {primary} !important; box-shadow: 0 0 0 1px {primary} !important; }}
.stButton > button {{ font-family: 'Syne', sans-serif !important; font-weight: 700 !important; background: transparent !important; border: 1.5px solid #222 !important; color: #666 !important; border-radius: 8px !important; padding: 0.5rem 1rem !important; font-size: 0.82rem !important; width: 100% !important; transition: all 0.2s !important; }}
.stButton > button:hover {{ border-color: {primary} !important; color: {primary} !important; }}
hr {{ border-color: #1a1a1a !important; margin: 1rem 0 !important; }}
::-webkit-scrollbar {{ width: 3px; }} ::-webkit-scrollbar-thumb {{ background: #2a2a2a; border-radius: 2px; }}
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="display:flex;align-items:center;gap:1rem;margin-bottom:1.5rem;">
    <img src="{PHOTO_URL}" width="52" height="52"
         style="border-radius:50%;border:2px solid {primary};object-fit:cover;">
    <div>
        <div class="title">🎭 {name}</div>
        <div style="font-size:0.68rem;color:#444;text-transform:uppercase;letter-spacing:0.12em;">by Vaibhav Srivastava</div>
    </div>
</div>
""", unsafe_allow_html=True)
st.markdown('<div class="subtitle">Choose a mood · Start chatting</div>', unsafe_allow_html=True)

# ── Mood selector ─────────────────────────────────────────────────────────────
cols = st.columns(3)
for i, (key, cfg) in enumerate(MOODS.items()):
    with cols[i]:
        is_active  = st.session_state.mood_key == key
        color      = cfg["color"]
        border     = f"border:2px solid {color};" if is_active else "border:1.5px solid #222;"
        bg         = "background:#1a1a1a;" if is_active else "background:#111;"
        lbl_color  = color if is_active else "#555"
        st.markdown(f"""
        <div style="{border}{bg}border-radius:10px;padding:1.1rem 0.8rem;text-align:center;margin-bottom:0.5rem;">
            <div style="font-size:2rem;">{cfg['emoji']}</div>
            <div style="font-family:'Syne',sans-serif;font-weight:800;font-size:0.85rem;color:{lbl_color};letter-spacing:0.08em;margin:0.3rem 0 0.2rem;">{cfg['label']}</div>
            <div style="font-size:0.67rem;color:#444;line-height:1.4;">{cfg['desc']}</div>
        </div>""", unsafe_allow_html=True)
        if st.button(f"{'✓ ' if is_active else ''}Select {cfg['emoji']}", key=f"btn_{key}"):
            st.session_state.mood_key = key
            st.rerun()

st.divider()

# ── Chat area ─────────────────────────────────────────────────────────────────
if mood:
    st.markdown(f'<div class="badge">{mood["emoji"]} {mood["label"]} MODE — {mood["desc"]}</div>', unsafe_allow_html=True)

    for role, content in st.session_state.chat:
        with st.chat_message(role):
            st.write(content)

    if prompt := st.chat_input(f"Talk to {name} {mood['emoji']}..."):

        # ── 1. Naam change? (model decides) ──────────────────────────────────
        new_name = detect_name_intent(prompt, st.session_state.model)
        if new_name:
            old_name = st.session_state.bot_name
            st.session_state.bot_name = new_name
            st.session_state.chat.append(("user", prompt))
            reply = f"Naam change ho gaya: {old_name} → {new_name}"
            st.session_state.chat.append(("assistant", reply))
            st.rerun()

        # ── 2. Naam poochha? ──────────────────────────────────────────────────
        if is_name_question(prompt):
            st.session_state.chat.append(("user", prompt))
            st.session_state.chat.append(("assistant", name))
            st.rerun()

        # ── 3. Normal message → model ─────────────────────────────────────────
        st.session_state.chat.append(("user", prompt))
        with st.chat_message("user"):
            st.write(prompt)

        full_messages = [SystemMessage(content=get_system_prompt(mood["tone"], name))]
        for role, content in st.session_state.chat:
            if role == "user": full_messages.append(HumanMessage(content=content))
            else:              full_messages.append(AIMessage(content=content))

        with st.chat_message("assistant"):
            response = st.write_stream(
                chunk.content for chunk in st.session_state.model.stream(full_messages)
            )
        st.session_state.chat.append(("assistant", response))

else:
    st.markdown("""
    <div style="text-align:center;color:#2a2a2a;padding:3rem 0;
    font-size:0.75rem;letter-spacing:0.15em;font-family:'DM Mono',monospace;">
        ↑ SELECT A MOOD ABOVE TO BEGIN
    </div>""", unsafe_allow_html=True)

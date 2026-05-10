"""
╔══════════════════════════════════════════════╗
║         RupAI Alarm — Paisa Manager          ║
║       Made by Vaibhav Srivastava             ║
╚══════════════════════════════════════════════╝
Streamlit app — run with:  streamlit run rupai_alarm.py

Deploy on Streamlit Cloud:
  1. Push to GitHub
  2. Go to share.streamlit.io → New app
  3. Set ANTHROPIC_API_KEY in Secrets
"""

import streamlit as st
import time
import random
import requests as req
from datetime import date, datetime

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="RupAI Alarm 💰",
    page_icon="💰",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
#  CONSTANTS
# ─────────────────────────────────────────────
UPI_APPS = [
    {"name": "PhonePe",  "color": "#6739B7", "icon": "📱"},
    {"name": "Paytm",    "color": "#00BAF2", "icon": "💙"},
    {"name": "GPay",     "color": "#34A853", "icon": "🟢"},
    {"name": "BHIM",     "color": "#FF6B00", "icon": "🏛️"},
    {"name": "Amazon",   "color": "#FF9900", "icon": "📦"},
    {"name": "Cash",     "color": "#22c55e", "icon": "💵"},
    {"name": "Other",    "color": "#888888", "icon": "💸"},
]

CATS = [
    {"name": "Food",          "icon": "🍔", "color": "#f97316"},
    {"name": "Shopping",      "icon": "🛍️", "color": "#a855f7"},
    {"name": "Petrol/Travel", "icon": "⛽", "color": "#3b82f6"},
    {"name": "Bills",         "icon": "🧾", "color": "#ef4444"},
    {"name": "EMI/Loan",      "icon": "🏦", "color": "#f43f5e"},
    {"name": "Ghar/Rent",     "icon": "🏠", "color": "#8b5cf6"},
    {"name": "Health",        "icon": "💊", "color": "#06b6d4"},
    {"name": "Entertainment", "icon": "🎬", "color": "#ec4899"},
    {"name": "Friends",       "icon": "👥", "color": "#22c55e"},
    {"name": "Other",         "icon": "💸", "color": "#888888"},
]

DEFAULT_FIXED = [
    {"id": "rent",         "label": "Rent / Kiraya",         "icon": "🏠"},
    {"id": "emi_home",     "label": "Home Loan EMI",          "icon": "🏦"},
    {"id": "emi_car",      "label": "Car Loan EMI",           "icon": "🚘"},
    {"id": "emi_personal", "label": "Personal Loan EMI",      "icon": "💳"},
    {"id": "lic",          "label": "LIC / Insurance",        "icon": "🛡️"},
    {"id": "rd",           "label": "RD (Recurring Deposit)", "icon": "🏧"},
    {"id": "electricity",  "label": "Bijli Bill",             "icon": "⚡"},
    {"id": "mobile",       "label": "Mobile Recharge",        "icon": "📶"},
    {"id": "internet",     "label": "Internet / WiFi",        "icon": "🌐"},
    {"id": "milk",         "label": "Doodh (Milk)",           "icon": "🥛"},
    {"id": "sabji",        "label": "Sabji / Rashan",         "icon": "🥦"},
    {"id": "school",       "label": "School Fees",            "icon": "🎒"},
    {"id": "petrol",       "label": "Petrol / CNG",           "icon": "⛽"},
    {"id": "ghar",         "label": "Ghar Bhejna",            "icon": "🏡"},
    {"id": "gym",          "label": "Gym / Fitness",          "icon": "💪"},
    {"id": "ott",          "label": "OTT (Netflix/Prime)",    "icon": "📺"},
    {"id": "medicine",     "label": "Dawai / Medicine",       "icon": "💊"},
    {"id": "paper",        "label": "Newspaper",              "icon": "📰"},
]

# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────
def fmt(n):
    try:
        return "₹{:,.0f}".format(float(n or 0))
    except Exception:
        return "₹0"

def today_str():
    return date.today().isoformat()

def cur_month():
    return date.today().isoformat()[:7]

def now_time():
    return datetime.now().strftime("%I:%M %p")

def calc_pct(a, b):
    return min(100, round((a / b) * 100)) if b > 0 else 0

def get_upi(name):
    return next((a for a in UPI_APPS if a["name"] == name), UPI_APPS[-1])

def get_cat(name):
    return next((c for c in CATS if c["name"] == name), CATS[-1])

# ─────────────────────────────────────────────
#  SESSION STATE INIT
# ─────────────────────────────────────────────
def init_state():
    defaults = {
        "profile":      None,
        "payments":     [],
        "tasks":        [],
        "notifs":       [],
        "ai_chat":      [],
        "screen":       "home",
        "setup_step":   0,
        "setup_name":   "",
        "setup_salary": 0.0,
        "setup_limit":  0.0,
        "setup_fixed":  [
            {"id": f["id"], "label": f["label"], "icon": f["icon"], "amount": 0.0, "active": True}
            for f in DEFAULT_FIXED
        ],
        "sel_app":      "PhonePe",
        "sel_cat":      "Food",
        "toast_queue":  [],
        "nudge_ts":     0.0,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ─────────────────────────────────────────────
#  PUSH NOTIFICATION
# ─────────────────────────────────────────────
def push_notif(msg, ntype="info"):
    n = {
        "id":   time.time() + random.random(),
        "msg":  msg,
        "type": ntype,
        "time": now_time(),
        "read": False,
    }
    st.session_state.notifs     = [n] + st.session_state.notifs[:39]
    st.session_state.toast_queue = st.session_state.toast_queue + [n]

# ─────────────────────────────────────────────
#  GLOBAL CSS  — dark theme + SMS slide-down toast + sound
# ─────────────────────────────────────────────
st.markdown("""
<style>
/* ── Base dark theme ── */
html, body, [data-testid="stAppViewContainer"],
[data-testid="stMain"], .main {
    background: #0a0a14 !important;
    color: #e8e8f0 !important;
    font-family: 'Segoe UI', sans-serif !important;
}
[data-testid="stSidebar"]           { display: none !important; }
header[data-testid="stHeader"]      { background: transparent !important; }
[data-testid="stToolbar"]           { display: none !important; }
.block-container {
    padding: 12px 16px 100px !important;
    max-width: 480px !important;
    margin: auto !important;
}

/* inputs */
input, textarea { background: #0d0d1a !important; color: #fff !important; border: 1px solid #2a2a4a !important; border-radius: 10px !important; }
label { color: #888 !important; font-size: 11px !important; text-transform: uppercase; letter-spacing: 0.5px; }
[data-testid="stChatInput"] textarea { background: #0d0d1a !important; color: #fff !important; }

/* buttons */
.stButton > button {
    background: #6C3FD4 !important; color: #fff !important;
    border: none !important; border-radius: 12px !important;
    font-weight: 700 !important; width: 100% !important;
    padding: 10px 0 !important;
}
.stButton > button:hover { opacity: 0.85 !important; }

/* cards */
.rupai-card {
    background: #161625; border: 1px solid #252545;
    border-radius: 18px; padding: 14px 16px; margin-bottom: 10px;
}

/* gradient text */
.gradient-text {
    background: linear-gradient(90deg, #a78bfa, #38bdf8);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    font-weight: 900; font-size: 20px; display: inline-block;
}

/* ═══════════════════════════════════════
   SMS-STYLE SLIDE-DOWN TOAST  ← NEW
   Slides in from top like an Android SMS
═══════════════════════════════════════ */
@keyframes smsSlide {
    0%   { transform: translateX(-50%) translateY(-120%); opacity: 0;   }
    12%  { transform: translateX(-50%) translateY(0);     opacity: 1;   }
    78%  { transform: translateX(-50%) translateY(0);     opacity: 1;   }
    100% { transform: translateX(-50%) translateY(-120%); opacity: 0;   }
}
.sms-toast {
    position: fixed;
    top: 0; left: 50%;
    transform: translateX(-50%) translateY(-120%);
    width: min(460px, 96vw);
    z-index: 99999;
    border-radius: 0 0 22px 22px;
    padding: 14px 18px 16px;
    display: flex; align-items: center; gap: 12px;
    box-shadow: 0 10px 50px #000d;
    animation: smsSlide 4.5s cubic-bezier(.22,.61,.36,1) forwards;
    pointer-events: none;
}
.sms-toast.info   { background:#12121f; border:1px solid #2a2a5a; border-top:none; }
.sms-toast.warn   { background:#1a1200; border:1px solid #713f12; border-top:none; }
.sms-toast.danger { background:#1f0808; border:1px solid #7f1d1d; border-top:none; }
.sms-toast.tip    { background:#0a1a0a; border:1px solid #14532d; border-top:none; }
.sms-toast.remind { background:#080820; border:1px solid #1e3a7f; border-top:none; }

.toast-icon  { font-size: 28px; flex-shrink: 0; }
.toast-body  { flex: 1; min-width: 0; }
.toast-app   { font-size: 10px; color: #a78bfa; font-weight: 700; letter-spacing: 1px; text-transform: uppercase; }
.toast-msg   { font-size: 13px; color: #e8e8f0; line-height: 1.45; margin-top: 2px; }
.toast-time  { font-size: 10px; color: #555; margin-top: 3px; }

/* sound-wave visual bars */
@keyframes bar {
    0%, 100% { height: 5px;  }
    50%       { height: 18px; }
}
.snd { display:flex; gap:3px; align-items:center; flex-shrink:0; }
.snd span {
    width:3px; background:#a78bfa; border-radius:2px; height:10px;
    animation: bar 0.55s ease-in-out infinite;
}
.snd span:nth-child(2){ animation-delay:.1s; }
.snd span:nth-child(3){ animation-delay:.2s; }
.snd span:nth-child(4){ animation-delay:.3s; }
.snd span:nth-child(5){ animation-delay:.15s; }

/* ── Bottom nav ── */
.bottom-nav {
    position: fixed; bottom: 0; left: 50%; transform: translateX(-50%);
    width: min(480px, 100vw); background: #0d0d18;
    border-top: 1px solid #1a1a2e;
    display: flex; justify-content: space-around;
    padding: 6px 0 14px; z-index: 40;
}

/* footer */
.footer-credit {
    text-align: center; padding: 16px 0 6px;
    font-size: 11px; color: #333;
}
.footer-credit b { color: #a78bfa; }

/* Progress bar steps */
.step-bar {
    height: 4px; border-radius: 4px; margin: 2px;
    transition: background 0.3s;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  SMS TOAST RENDERER  (with Web Audio sound)
# ─────────────────────────────────────────────
TOAST_ICON  = {"info":"💰","warn":"⚠️","danger":"🚨","tip":"💡","remind":"⏰"}

# Web Audio one-liners per notification type
SOUND_JS = {
    "danger": """(()=>{try{const c=new(window.AudioContext||window.webkitAudioContext)();
        [[880,.0,.18,.35],[660,.18,.36,.5]].forEach(([f,s,e,stop])=>{
        const o=c.createOscillator(),g=c.createGain();o.connect(g);g.connect(c.destination);
        o.frequency.setValueAtTime(f,c.currentTime+s);
        g.gain.setValueAtTime(.32,c.currentTime+s);
        g.gain.exponentialRampToValueAtTime(.001,c.currentTime+stop);
        o.start(c.currentTime+s);o.stop(c.currentTime+stop);});}catch(e){}})()""",

    "warn": """(()=>{try{const c=new(window.AudioContext||window.webkitAudioContext)();
        const o=c.createOscillator(),g=c.createGain();o.connect(g);g.connect(c.destination);
        o.frequency.setValueAtTime(660,c.currentTime);
        o.frequency.setValueAtTime(550,c.currentTime+.15);
        g.gain.setValueAtTime(.22,c.currentTime);
        g.gain.exponentialRampToValueAtTime(.001,c.currentTime+.4);
        o.start();o.stop(c.currentTime+.4);}catch(e){}})()""",

    "info": """(()=>{try{const c=new(window.AudioContext||window.webkitAudioContext)();
        const o=c.createOscillator(),g=c.createGain();o.type='sine';
        o.connect(g);g.connect(c.destination);
        o.frequency.setValueAtTime(523,c.currentTime);
        o.frequency.linearRampToValueAtTime(784,c.currentTime+.18);
        g.gain.setValueAtTime(.16,c.currentTime);
        g.gain.exponentialRampToValueAtTime(.001,c.currentTime+.38);
        o.start();o.stop(c.currentTime+.38);}catch(e){}})()""",

    "tip": """(()=>{try{const c=new(window.AudioContext||window.webkitAudioContext)();
        [440,554,659].forEach((f,i)=>{
        const o=c.createOscillator(),g=c.createGain();o.type='sine';
        o.connect(g);g.connect(c.destination);
        o.frequency.setValueAtTime(f,c.currentTime+i*.1);
        g.gain.setValueAtTime(.14,c.currentTime+i*.1);
        g.gain.exponentialRampToValueAtTime(.001,c.currentTime+i*.1+.18);
        o.start(c.currentTime+i*.1);o.stop(c.currentTime+i*.1+.2);});}catch(e){}})()""",

    "remind": """(()=>{try{const c=new(window.AudioContext||window.webkitAudioContext)();
        [0,.2,.4].forEach(t=>{const o=c.createOscillator(),g=c.createGain();
        o.connect(g);g.connect(c.destination);
        o.frequency.setValueAtTime(740,c.currentTime+t);
        g.gain.setValueAtTime(.2,c.currentTime+t);
        g.gain.exponentialRampToValueAtTime(.001,c.currentTime+t+.14);
        o.start(c.currentTime+t);o.stop(c.currentTime+t+.16);});}catch(e){}})()""",
}

def render_toasts():
    queue = st.session_state.get("toast_queue", [])
    if not queue:
        return
    n    = queue[-1]
    icon = TOAST_ICON.get(n["type"], "🔔")
    snd  = SOUND_JS.get(n["type"], SOUND_JS["info"])

    st.markdown(f"""
    <div class="sms-toast {n['type']}">
        <div class="toast-icon">{icon}</div>
        <div class="toast-body">
            <div class="toast-app">💰 RupAI Alarm</div>
            <div class="toast-msg">{n['msg']}</div>
            <div class="toast-time">{n['time']}</div>
        </div>
        <div class="snd"><span></span><span></span><span></span><span></span><span></span></div>
    </div>
    <script>(function(){{ {snd} }})();</script>
    """, unsafe_allow_html=True)

    st.session_state.toast_queue = []

# ─────────────────────────────────────────────
#  DERIVED CALCULATIONS
# ─────────────────────────────────────────────
def get_derived():
    p        = st.session_state.profile
    payments = st.session_state.payments
    cm       = cur_month()
    month_pay   = [x for x in payments if x["date"][:7] == cm]
    month_spent = sum(x["amount"] for x in month_pay)
    today_pay   = [x for x in payments if x["date"] == today_str()]
    today_spent = sum(x["amount"] for x in today_pay)
    fixed_total = (
        sum(float(f["amount"] or 0) for f in p["fixedExpenses"] if f["active"] and f["amount"])
        if p else 0
    )
    salary_num = float(p["salary"]     or 0) if p else 0
    limit_num  = float(p["spendLimit"] or 0) if p else 0
    available  = salary_num - fixed_total - month_spent
    spend_pct  = calc_pct(month_spent, limit_num)
    return dict(
        month_pay=month_pay, month_spent=month_spent,
        today_pay=today_pay, today_spent=today_spent,
        fixed_total=fixed_total, salary_num=salary_num,
        limit_num=limit_num, available=available, spend_pct=spend_pct,
    )

# ─────────────────────────────────────────────
#  NUDGE ENGINE
# ─────────────────────────────────────────────
def maybe_nudge(d):
    p = st.session_state.profile
    if not p:
        return
    now_ts = time.time()
    if now_ts - st.session_state.nudge_ts < 90:
        return
    st.session_state.nudge_ts = now_ts
    opts = [
        (d["spend_pct"] > 90,
         f"🚨 {p['name']} ji! Limit ka {d['spend_pct']}% kharcha ho gaya! Ruko thoda!", "danger"),
        (d["spend_pct"] > 70,
         f"⚠️ {p['name']} ji, {d['spend_pct']}% limit use ho gayi. Sambhalo!", "warn"),
        (d["available"] < 3000 and d["salary_num"] > 0,
         f"💸 Sirf {fmt(d['available'])} bacha hai! Bahut sochke kharcho.", "warn"),
        (True, f"📊 Aaj ka kharcha: {fmt(d['today_spent'])}. Kal ka bhi socho!", "info"),
        (True, "💡 Tip: Chhote chhote kharche milke bade ho jaate hain. Track karte raho!", "tip"),
        (d["available"] > 0,
         f"✅ Abhi {fmt(d['available'])} bachane ki gunjayish hai is mahine.", "info"),
    ]
    valid = [(m, t) for cond, m, t in opts if cond]
    if valid:
        msg, typ = random.choice(valid)
        push_notif(msg, typ)

# ─────────────────────────────────────────────
#  HEADER
# ─────────────────────────────────────────────
def render_header():
    p      = st.session_state.profile
    unread = sum(1 for n in st.session_state.notifs if not n.get("read"))
    badge  = f"🔔 {unread}" if unread > 0 else "🔔"
    col1, col2 = st.columns([5, 1])
    with col1:
        name_txt = f"&nbsp;&nbsp;<span style='font-size:12px;color:#666'>Namaste {p['name']} ji 👋</span>" if p else ""
        st.markdown(f"<div style='display:flex;align-items:center;gap:8px'>"
                    f"<span class='gradient-text'>💰 RupAI Alarm</span>{name_txt}</div>",
                    unsafe_allow_html=True)
    with col2:
        if st.button(badge, key="notif_btn"):
            st.session_state.notifs = [dict(n, read=True) for n in st.session_state.notifs]
            st.session_state.screen = "notifs"
            st.rerun()
    st.markdown("<hr style='border-color:#1a1a2e;margin:6px 0 12px'/>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  BOTTOM NAV
# ─────────────────────────────────────────────
def render_nav():
    tabs = [
        ("🏠", "home",   "Home"),
        ("➕", "add",    "Add"),
        ("💼", "budget", "Budget"),
        ("📋", "tasks",  "Kaam"),
        ("📊", "chart",  "Chart"),
        ("🤖", "ai",     "AI"),
    ]
    cols = st.columns(len(tabs))
    for i, (icon, sid, label) in enumerate(tabs):
        with cols[i]:
            active = st.session_state.screen == sid
            clr = "#a78bfa" if active else "#444"
            if st.button(icon, key=f"nav_{sid}"):
                st.session_state.screen = sid
                st.rerun()
            st.markdown(
                f"<p style='text-align:center;font-size:9px;color:{clr};"
                f"margin:-10px 0 0;font-weight:{'700' if active else '400'}'>{label}</p>",
                unsafe_allow_html=True,
            )

# ─────────────────────────────────────────────
#  SETUP WIZARD
# ─────────────────────────────────────────────
def render_setup():
    step  = st.session_state.setup_step
    steps = ["Naam", "Income", "Limit", "Fixed Kharche"]

    st.markdown("""
    <div style='text-align:center;padding:20px 0 10px'>
        <div style='font-size:52px'>💰</div>
        <h1 style='background:linear-gradient(90deg,#a78bfa,#38bdf8);
                   -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                   margin:0;font-size:26px;font-weight:900'>RupAI Alarm</h1>
        <p style='color:#555;font-size:13px;margin:4px 0 0'>AI-powered paisa manager</p>
        <p style='color:#444;font-size:11px;margin:2px 0 16px'>
            Made by <b style='color:#a78bfa'>Vaibhav Srivastava</b>
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Progress bars
    prog = st.columns(len(steps))
    for i, s in enumerate(steps):
        with prog[i]:
            col = "#a78bfa" if i <= step else "#252535"
            st.markdown(f"<div class='step-bar' style='background:{col}'></div>",
                        unsafe_allow_html=True)

    st.markdown("<br/>", unsafe_allow_html=True)

    # ── Step 0: Name ──
    if step == 0:
        st.markdown("#### 👋 Apna naam batao")
        st.caption("Main tumhara financial dost banunga!")
        name = st.text_input("Naam", value=st.session_state.setup_name,
                             placeholder="Jaise: Rahul, Priya...",
                             label_visibility="collapsed", key="inp_name")
        st.session_state.setup_name = name
        if st.button("Aage chalo →", key="s0"):
            if name.strip():
                st.session_state.setup_step = 1
                st.rerun()
            else:
                st.warning("Pehle naam daalo!")

    # ── Step 1: Salary ──
    elif step == 1:
        st.markdown("#### 💼 Monthly Income")
        st.caption("Salary / business income kitni hai?")
        sal = st.number_input("Salary (₹)", value=st.session_state.setup_salary,
                              min_value=0.0, step=1000.0, label_visibility="collapsed")
        st.session_state.setup_salary = sal
        c1, c2 = st.columns([2, 3])
        with c1:
            if st.button("← Back", key="s1b"):
                st.session_state.setup_step = 0; st.rerun()
        with c2:
            if st.button("Aage →", key="s1"):
                st.session_state.setup_step = 2; st.rerun()

    # ── Step 2: Spending limit ──
    elif step == 2:
        st.markdown("#### 🎯 Spending Limit")
        st.caption("Monthly kitna kharcha karna chahte ho?")
        if st.session_state.setup_salary:
            st.success(f"💡 Suggestion: {fmt(st.session_state.setup_salary * 0.3)} (salary ka 30%)")
        lim = st.number_input("Limit (₹)", value=st.session_state.setup_limit,
                              min_value=0.0, step=500.0, label_visibility="collapsed")
        st.session_state.setup_limit = lim
        c1, c2 = st.columns([2, 3])
        with c1:
            if st.button("← Back", key="s2b"):
                st.session_state.setup_step = 1; st.rerun()
        with c2:
            if st.button("Aage →", key="s2"):
                st.session_state.setup_step = 3; st.rerun()

    # ── Step 3: Fixed expenses ──
    elif step == 3:
        st.markdown("#### 📋 Fixed Monthly Kharche")
        st.caption("Jo jo monthly fix hai wo daalo (optional)")
        fixed      = st.session_state.setup_fixed
        total_fixed = 0.0
        for i, f in enumerate(fixed):
            cc1, cc2, cc3 = st.columns([0.5, 3, 2])
            with cc1:
                act = st.checkbox("", value=f["active"], key=f"fix_{f['id']}",
                                  label_visibility="collapsed")
                fixed[i]["active"] = act
            with cc2:
                clr = "#ccc" if act else "#444"
                st.markdown(f"<span style='color:{clr};font-size:12px'>{f['icon']} {f['label']}</span>",
                            unsafe_allow_html=True)
            with cc3:
                if act:
                    amt = st.number_input("₹", value=float(f["amount"] or 0),
                                          min_value=0.0, step=100.0,
                                          key=f"amt_{f['id']}", label_visibility="collapsed")
                    fixed[i]["amount"] = amt
                    total_fixed += amt
        st.session_state.setup_fixed = fixed
        if total_fixed > 0:
            st.info(f"Total fixed: **{fmt(total_fixed)}**")
        c1, c2 = st.columns([2, 3])
        with c1:
            if st.button("← Back", key="s3b"):
                st.session_state.setup_step = 2; st.rerun()
        with c2:
            if st.button("🚀 Shuru!", key="s3"):
                st.session_state.profile = {
                    "name":          st.session_state.setup_name.strip(),
                    "salary":        st.session_state.setup_salary,
                    "spendLimit":    st.session_state.setup_limit,
                    "fixedExpenses": st.session_state.setup_fixed,
                }
                push_notif(
                    f"🎉 Welcome {st.session_state.setup_name.strip()} ji! RupAI Alarm shuru ho gaya!",
                    "info",
                )
                st.rerun()

# ─────────────────────────────────────────────
#  SCREEN: HOME
# ─────────────────────────────────────────────
def screen_home(d):
    p = st.session_state.profile

    # Top stats
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""<div class='rupai-card'>
            <p style='margin:0;font-size:10px;color:#555;text-transform:uppercase'>Aaj ka kharcha</p>
            <p style='margin:4px 0 0;font-size:22px;font-weight:900;color:#f87171'>{fmt(d['today_spent'])}</p>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class='rupai-card'>
            <p style='margin:0;font-size:10px;color:#555;text-transform:uppercase'>Is mahine</p>
            <p style='margin:4px 0 0;font-size:22px;font-weight:900;color:#fb923c'>{fmt(d['month_spent'])}</p>
        </div>""", unsafe_allow_html=True)

    # Available balance
    aclr = "#f87171" if d["available"] < 0 else "#4ade80"
    st.markdown(f"""
    <div style='background:#0d1a0d;border:1px solid #14532d;border-radius:14px;padding:14px 16px;margin-bottom:12px'>
        <p style='margin:0;font-size:11px;color:#4ade80'>💚 Bacha hai is mahine</p>
        <p style='margin:4px 0 0;font-size:28px;font-weight:900;color:{aclr}'>{fmt(d['available'])}</p>
        <p style='margin:4px 0 0;font-size:11px;color:#555'>
            Salary: {fmt(d['salary_num'])} &nbsp;|&nbsp;
            Fixed: −{fmt(d['fixed_total'])} &nbsp;|&nbsp;
            Spent: −{fmt(d['month_spent'])}
        </p>
    </div>""", unsafe_allow_html=True)

    # Spend-limit bar
    if d["limit_num"] > 0:
        sp  = d["spend_pct"]
        bclr = "#ef4444" if sp > 90 else "#f97316" if sp > 70 else "#22c55e"
        warn_txt = (f"<p style='font-size:11px;color:#ef4444;margin:5px 0 0'>"
                    f"⚠️ {p['name']} ji! Limit ka {sp}% ho gaya — sambhalo!</p>") if sp > 80 else ""
        st.markdown(f"""
        <div style='margin-bottom:14px'>
            <div style='display:flex;justify-content:space-between;margin-bottom:5px'>
                <span style='font-size:11px;color:#666'>Limit: {fmt(d['month_spent'])} / {fmt(d['limit_num'])}</span>
                <span style='font-size:11px;font-weight:700;color:{bclr}'>{sp}%</span>
            </div>
            <div style='height:8px;background:#1a1a2e;border-radius:4px;overflow:hidden'>
                <div style='height:100%;width:{sp}%;background:{bclr};border-radius:4px'></div>
            </div>
            {warn_txt}
        </div>""", unsafe_allow_html=True)

    # Today payments
    st.markdown("<p style='font-size:11px;color:#444;text-transform:uppercase;letter-spacing:1px;margin:0 0 8px'>Aaj ki payments</p>",
                unsafe_allow_html=True)
    if not d["today_pay"]:
        st.markdown("<div style='text-align:center;padding:24px 0;color:#333'>"
                    "<p style='font-size:32px'>💸</p>"
                    "<p style='font-size:13px'>Aaj koi payment nahi — achha hai!</p></div>",
                    unsafe_allow_html=True)
    else:
        for pay in d["today_pay"]:
            a = get_upi(pay["app"])
            c = get_cat(pay["category"])
            cols = st.columns([0.6, 3.5, 1.5])
            with cols[0]:
                st.markdown(f"<div style='width:36px;height:36px;border-radius:10px;"
                            f"background:{a['color']}22;border:1.5px solid {a['color']}44;"
                            f"display:flex;align-items:center;justify-content:center;"
                            f"font-size:18px'>{a['icon']}</div>", unsafe_allow_html=True)
            with cols[1]:
                st.markdown(
                    f"<p style='margin:0;font-size:13px;font-weight:600'>{pay['note']}</p>"
                    f"<p style='margin:2px 0 0;font-size:11px;color:#444'>"
                    f"<span style='color:{a['color']}'>{pay['app']}</span> "
                    f"· {c['icon']}{pay['category']} · {pay['time']}</p>",
                    unsafe_allow_html=True,
                )
            with cols[2]:
                st.markdown(f"<p style='margin:0;font-size:14px;font-weight:800;"
                            f"color:#f87171;text-align:right'>−{fmt(pay['amount'])}</p>",
                            unsafe_allow_html=True)
            st.markdown("<hr style='border-color:#1a1a2e;margin:4px 0'/>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  SCREEN: ADD PAYMENT
# ─────────────────────────────────────────────
def screen_add(d):
    st.markdown("### 💳 Nayi Payment")

    pay_date = st.date_input("Date", value=date.today())

    # UPI app selector
    st.caption("UPI APP")
    app_cols = st.columns(len(UPI_APPS))
    for i, a in enumerate(UPI_APPS):
        with app_cols[i]:
            active = st.session_state.sel_app == a["name"]
            border = f"2px solid {a['color']}" if active else "1px solid #2a2a4a"
            bg     = f"{a['color']}22"         if active else "#161625"
            st.markdown(
                f"<div style='background:{bg};border:{border};border-radius:10px;"
                f"text-align:center;padding:6px 2px;cursor:pointer;font-size:18px'>{a['icon']}</div>",
                unsafe_allow_html=True,
            )
            if st.button(a["name"], key=f"app_{a['name']}",
                         help=a["name"]):
                st.session_state.sel_app = a["name"]
                st.rerun()

    amount = st.number_input("Amount (₹)", min_value=0.0, step=10.0,
                             placeholder="Kitne rupaye?", label_visibility="visible")
    note   = st.text_input("Kahan ki payment?",
                           placeholder="Jaise: Swiggy, Petrol, Amazon...")

    # Category selector
    st.caption("CATEGORY")
    cat_names = [c["name"] for c in CATS]
    sel_cat = st.selectbox("Category", cat_names,
                           index=cat_names.index(st.session_state.sel_cat),
                           label_visibility="collapsed")
    st.session_state.sel_cat = sel_cat

    st.markdown("<br/>", unsafe_allow_html=True)
    if st.button("✅ Add Karo", type="primary", key="add_pay"):
        if amount > 0 and note.strip():
            pay = {
                "id":       time.time(),
                "date":     pay_date.isoformat(),
                "app":      st.session_state.sel_app,
                "amount":   float(amount),
                "note":     note.strip(),
                "category": sel_cat,
                "time":     now_time(),
            }
            st.session_state.payments = [pay] + st.session_state.payments
            new_total = d["month_spent"] + pay["amount"]
            pname     = st.session_state.profile["name"]
            if d["limit_num"] > 0 and new_total > d["limit_num"] * 0.8:
                push_notif(
                    f"😤 {pname} ji! {fmt(pay['amount'])} aur kharcha? "
                    f"Ab limit ka {calc_pct(new_total, d['limit_num'])}% ho gaya!", "warn")
            else:
                push_notif(f"✅ {fmt(pay['amount'])} add hua — {pay['app']} se {pay['note']}", "info")
            st.session_state.screen = "home"
            st.rerun()
        else:
            st.error("Amount aur description dono bharo!")

# ─────────────────────────────────────────────
#  SCREEN: BUDGET
# ─────────────────────────────────────────────
def screen_budget(d):
    p = st.session_state.profile
    st.markdown("### 💼 Budget")

    summary = [
        ("Monthly Salary",  fmt(d["salary_num"]), "#a78bfa"),
        ("Fixed Kharche",   fmt(d["fixed_total"]), "#f97316"),
        ("Spending Limit",  fmt(d["limit_num"]),   "#38bdf8"),
        ("Bacha Hai",       fmt(d["available"]),   "#f87171" if d["available"] < 0 else "#4ade80"),
    ]
    c1, c2 = st.columns(2)
    for i, (lbl, val, col) in enumerate(summary):
        with (c1 if i % 2 == 0 else c2):
            st.markdown(f"""<div class='rupai-card'>
                <p style='margin:0;font-size:10px;color:#555;text-transform:uppercase'>{lbl}</p>
                <p style='margin:4px 0 0;font-size:18px;font-weight:800;color:{col}'>{val}</p>
            </div>""", unsafe_allow_html=True)

    st.markdown("<p style='font-size:11px;color:#555;text-transform:uppercase;letter-spacing:1px;margin:8px 0 6px'>Fixed Monthly Kharche</p>",
                unsafe_allow_html=True)
    for f in p["fixedExpenses"]:
        if f["active"] and float(f["amount"] or 0) > 0:
            cols = st.columns([0.5, 3.5, 1.5])
            with cols[0]:
                st.markdown(f"<span style='font-size:16px'>{f['icon']}</span>", unsafe_allow_html=True)
            with cols[1]:
                st.markdown(f"<span style='font-size:13px;color:#ccc'>{f['label']}</span>", unsafe_allow_html=True)
            with cols[2]:
                st.markdown(f"<span style='font-size:13px;font-weight:700;color:#f87171'>{fmt(float(f['amount']))}</span>",
                            unsafe_allow_html=True)
            st.markdown("<hr style='border-color:#1a1a2e;margin:3px 0'/>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  SCREEN: TASKS
# ─────────────────────────────────────────────
def screen_tasks():
    st.markdown("### 📋 Kaam & Events")

    with st.expander("➕ Naya Kaam / Event Add Karo"):
        title  = st.text_input("Kya karna hai?", placeholder="Jaise: Bijli bill bharo, Birthday party...", key="t_title")
        t_type = st.radio("Type", ["📋 Kaam", "🎉 Event", "🎂 Birthday"], horizontal=True, key="t_type")
        t_date = st.date_input("Date", value=date.today(), key="t_date")
        t_time = st.time_input("Time", key="t_time")
        t_note = st.text_input("Note (optional)", key="t_note")
        if st.button("✅ Kaam Add Karo", key="add_task"):
            if title.strip():
                task = {
                    "id":    time.time(),
                    "title": title.strip(),
                    "type":  t_type.split()[1].lower(),
                    "date":  t_date.isoformat(),
                    "time":  t_time.strftime("%H:%M"),
                    "note":  t_note,
                    "done":  False,
                }
                st.session_state.tasks = [task] + st.session_state.tasks
                push_notif(f"📋 Kaam add hua: \"{title.strip()}\" — {t_date}", "info")
                st.rerun()
            else:
                st.warning("Title daalo!")

    tasks    = st.session_state.tasks
    today_t  = [t for t in tasks if t["date"] == today_str()]
    upcoming = sorted([t for t in tasks if t["date"] > today_str() and not t["done"]],
                      key=lambda x: x["date"])

    def task_row(t):
        TYPE_ICON = {"birthday": "🎂", "event": "🎉", "task": "📋"}
        icon = TYPE_ICON.get(t.get("type", "task"), "📋")
        cols = st.columns([0.5, 3.5, 1, 0.5])
        with cols[0]:
            done = st.checkbox("", value=t["done"], key=f"done_{t['id']}", label_visibility="collapsed")
            if done != t["done"]:
                for x in st.session_state.tasks:
                    if x["id"] == t["id"]:
                        x["done"] = done
                st.rerun()
        with cols[1]:
            s = "text-decoration:line-through;color:#555" if t["done"] else ""
            st.markdown(f"<span style='{s};font-size:13px'>{icon} {t['title']}</span>", unsafe_allow_html=True)
        with cols[2]:
            st.markdown(f"<span style='font-size:11px;color:#444'>{t.get('time','')}</span>", unsafe_allow_html=True)
        with cols[3]:
            if st.button("🗑", key=f"del_{t['id']}"):
                st.session_state.tasks = [x for x in st.session_state.tasks if x["id"] != t["id"]]
                st.rerun()
        st.markdown("<hr style='border-color:#1a1a2e;margin:3px 0'/>", unsafe_allow_html=True)

    if today_t:
        st.markdown("**Aaj**")
        for t in today_t:
            task_row(t)

    if upcoming:
        st.markdown("**Aane wala**")
        for t in upcoming:
            task_row(t)

    if not tasks:
        st.markdown("<div style='text-align:center;padding:40px 0;color:#333'>"
                    "<p style='font-size:36px'>📋</p>"
                    "<p style='font-size:13px'>Koi kaam nahi — enjoy karo!</p></div>",
                    unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  SCREEN: ANALYTICS
# ─────────────────────────────────────────────
def screen_chart(d):
    st.markdown("### 📊 Analytics")
    st.markdown(f"""<div class='rupai-card' style='text-align:center'>
        <p style='margin:0;color:#555;font-size:11px'>Is mahine total ({len(d['month_pay'])} payments)</p>
        <p style='margin:4px 0 0;font-size:30px;font-weight:900;color:#f87171'>{fmt(d['month_spent'])}</p>
    </div>""", unsafe_allow_html=True)

    if not d["month_pay"]:
        st.info("Is mahine koi payment nahi")
        return

    # Category breakdown
    cat_data = {}
    for pay in d["month_pay"]:
        cat_data[pay["category"]] = cat_data.get(pay["category"], 0) + pay["amount"]

    try:
        import plotly.graph_objects as go
        labels = list(cat_data.keys())
        values = list(cat_data.values())
        colors = [get_cat(l)["color"] for l in labels]
        fig = go.Figure(go.Pie(
            labels=labels, values=values, hole=0.4,
            marker_colors=colors, textinfo="percent+label",
        ))
        fig.update_layout(
            paper_bgcolor="#161625", plot_bgcolor="#161625",
            font_color="#e8e8f0", showlegend=False,
            margin=dict(t=20, b=20, l=20, r=20),
        )
        st.plotly_chart(fig, use_container_width=True)

        app_data = {}
        for pay in d["month_pay"]:
            app_data[pay["app"]] = app_data.get(pay["app"], 0) + pay["amount"]
        if app_data:
            fig2 = go.Figure(go.Bar(
                x=list(app_data.keys()), y=list(app_data.values()),
                marker_color=[get_upi(k)["color"] for k in app_data],
                text=[fmt(v) for v in app_data.values()], textposition="outside",
            ))
            fig2.update_layout(
                paper_bgcolor="#161625", plot_bgcolor="#161625",
                font_color="#e8e8f0", margin=dict(t=20, b=20, l=20, r=20),
            )
            fig2.update_xaxes(showgrid=False)
            fig2.update_yaxes(showgrid=False, showticklabels=False)
            st.plotly_chart(fig2, use_container_width=True)

    except ImportError:
        # Fallback bars without plotly
        for cname, amt in sorted(cat_data.items(), key=lambda x: -x[1]):
            c = get_cat(cname)
            ratio = amt / d["month_spent"] if d["month_spent"] > 0 else 0
            st.markdown(f"""
            <div style='display:flex;align-items:center;gap:10px;margin-bottom:8px'>
                <span style='font-size:16px'>{c['icon']}</span>
                <div style='flex:1'>
                    <div style='display:flex;justify-content:space-between;margin-bottom:3px'>
                        <span style='font-size:13px'>{cname}</span>
                        <span style='font-size:13px;font-weight:700;color:{c['color']}'>{fmt(amt)}</span>
                    </div>
                    <div style='height:5px;background:#1a1a2e;border-radius:3px'>
                        <div style='height:100%;width:{ratio*100:.0f}%;background:{c['color']};border-radius:3px'></div>
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  SCREEN: AI ADVISOR
# ─────────────────────────────────────────────
def screen_ai(d):
    p = st.session_state.profile
    st.markdown("### 🤖 RupAI Advisor")
    st.caption("Apna financial dost — poocho kuch bhi!")

    # Quick prompts
    if not st.session_state.ai_chat:
        prompts = [
            "Mera kharcha kaisa chal raha hai?",
            "Mujhe paisa kaise bachana chahiye?",
            "Is mahine kahan jyada kharcha hua?",
            "Meri EMI ke baad kitna bacha?",
            "Paisa bachane ke tips do",
        ]
        cols = st.columns(2)
        for i, q in enumerate(prompts):
            with cols[i % 2]:
                if st.button(q, key=f"qp_{i}"):
                    st.session_state.ai_chat.append({"role": "user", "content": q})
                    st.rerun()

    # Chat history display
    for m in st.session_state.ai_chat:
        role = "user" if m["role"] == "user" else "assistant"
        with st.chat_message(role, avatar="🧑" if role == "user" else "🤖"):
            st.write(m["content"])

    # Input
    user_msg = st.chat_input("Poocho kuch bhi...")
    if user_msg:
        st.session_state.ai_chat.append({"role": "user", "content": user_msg})
        cat_data = {}
        for pay in d["month_pay"]:
            cat_data[pay["category"]] = cat_data.get(pay["category"], 0) + pay["amount"]
        system_prompt = (
            f"Tu RupAI Alarm hai — ek smart Hindi financial advisor.\n"
            f"User: {p['name']} | Salary: {fmt(d['salary_num'])} | "
            f"Limit: {fmt(d['limit_num'])} | Fixed: {fmt(d['fixed_total'])}\n"
            f"Is mahine kharcha: {fmt(d['month_spent'])} | Bacha: {fmt(d['available'])} | "
            f"Limit use: {d['spend_pct']}%\n"
            f"Categories: {', '.join(f'{k}={fmt(v)}' for k,v in cat_data.items())}\n"
            f"Hinglish mein baat kar. Friendly + helpful. Jyada kharche pe thoda daato. Max 5 sentences."
        )
        api_key = st.secrets.get("ANTHROPIC_API_KEY", "")
        try:
            resp = req.post(
                "https://api.anthropic.com/v1/messages",
                json={
                    "model":      "claude-sonnet-4-20250514",
                    "max_tokens": 500,
                    "system":     system_prompt,
                    "messages":   [
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.ai_chat[-8:]
                    ],
                },
                headers={
                    "Content-Type": "application/json",
                    "x-api-key":    api_key,
                    "anthropic-version": "2023-06-01",
                },
                timeout=30,
            )
            data  = resp.json()
            reply = data.get("content", [{}])[0].get("text", "Kuch dikkat aayi, dobara try karo!")
        except Exception:
            reply = "Network issue! Thodi der mein try karo."
        st.session_state.ai_chat.append({"role": "assistant", "content": reply})
        st.rerun()

# ─────────────────────────────────────────────
#  SCREEN: NOTIFICATIONS
# ─────────────────────────────────────────────
def screen_notifs():
    st.markdown("### 🔔 Notifications")
    if st.button("← Wapas Jao"):
        st.session_state.screen = "home"; st.rerun()

    notifs = st.session_state.notifs
    if not notifs:
        st.info("Koi notification nahi")
        return

    TYPE_BG  = {"danger":"#1f0a0a","warn":"#1a1200","info":"#0f1520","tip":"#0a1a0a","remind":"#080820"}
    TYPE_BDR = {"danger":"#7f1d1d","warn":"#713f12","info":"#1e293b","tip":"#14532d","remind":"#1e3a7f"}

    for n in notifs:
        bg  = TYPE_BG.get(n["type"],  "#0f1520")
        bdr = TYPE_BDR.get(n["type"], "#1e293b")
        st.markdown(f"""
        <div style='background:{bg};border:1px solid {bdr};border-radius:12px;
                    padding:12px 14px;margin-bottom:8px'>
            <p style='margin:0;font-size:13px;line-height:1.5'>{n['msg']}</p>
            <p style='margin:4px 0 0;font-size:10px;color:#444'>{n['time']}</p>
        </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────
def main():
    # ① SMS toast rendered first (fixed position overlay)
    render_toasts()

    # ② Setup wizard if no profile yet
    if not st.session_state.profile:
        render_setup()
        return

    # ③ Derived data + nudge
    d = get_derived()
    maybe_nudge(d)

    # ④ Header
    render_header()

    # ⑤ Screen
    scr = st.session_state.screen
    if   scr == "home":   screen_home(d)
    elif scr == "add":    screen_add(d)
    elif scr == "budget": screen_budget(d)
    elif scr == "tasks":  screen_tasks()
    elif scr == "chart":  screen_chart(d)
    elif scr == "ai":     screen_ai(d)
    elif scr == "notifs": screen_notifs()

    # ⑥ Footer credit
    st.markdown("""
    <div class='footer-credit'>
        Made with ❤️ by <b>Vaibhav Srivastava</b> &nbsp;·&nbsp; RupAI Alarm v1.0
    </div>
    """, unsafe_allow_html=True)

    # ⑦ Bottom nav
    render_nav()

main()

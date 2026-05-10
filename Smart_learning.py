import streamlit as st
from dotenv import load_dotenv
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
import re
import base64
import io

load_dotenv()

st.set_page_config(page_title="Smart Learning Assistant", page_icon="📘", layout="centered") 

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=DM+Mono:wght@300;400&family=DM+Sans:wght@300;400;500&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; background: #0a0a0f; color: #e8e6f0; }
.stApp { background: #0a0a0f; }
.main-title { font-family: 'Syne', sans-serif; font-weight: 800; font-size: 2.2rem; background: linear-gradient(135deg, #a78bfa, #60a5fa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0.1rem; line-height: 1.1; }
.main-sub { font-size: 0.72rem; color: #555; letter-spacing: 0.12em; text-transform: uppercase; }
textarea { background: #111118 !important; color: #e8e6f0 !important; font-family: 'DM Mono', monospace !important; font-size: 0.85rem !important; border: 1px solid #2a2a3a !important; border-radius: 10px !important; }
textarea:focus { border-color: #a78bfa !important; box-shadow: 0 0 0 1px #a78bfa !important; }
.stButton > button { font-family: 'Syne', sans-serif !important; font-weight: 700 !important; background: linear-gradient(135deg, #a78bfa, #60a5fa) !important; color: #000 !important; border: none !important; border-radius: 8px !important; padding: 0.6rem 2rem !important; font-size: 0.9rem !important; transition: opacity 0.2s !important; }
.stButton > button:hover { opacity: 0.85 !important; }
.q-card { background: #111118; border: 1px solid #2a2a3a; border-radius: 14px; padding: 1.5rem; margin: 1.5rem 0 0.5rem 0; }
.q-number { font-family: 'Syne', sans-serif; font-weight: 800; font-size: 0.7rem; letter-spacing: 0.15em; color: #a78bfa; text-transform: uppercase; margin-bottom: 0.6rem; }
.q-text { font-family: 'DM Sans', sans-serif; font-size: 1.05rem; font-weight: 500; color: #e8e6f0; line-height: 1.6; margin-bottom: 1rem; }
.option-row { font-family: 'DM Mono', monospace; font-size: 0.85rem; color: #aaa; background: #0d0d14; border-radius: 6px; padding: 0.45rem 0.8rem; margin-bottom: 0.35rem; }
.answer-pill { display: inline-block; background: linear-gradient(135deg, #1a3a1a, #1a4a1a); border: 1px solid #2d6a2d; color: #6ee86e; font-family: 'Syne', sans-serif; font-weight: 700; font-size: 0.95rem; padding: 0.5rem 1.2rem; border-radius: 8px; margin-top: 0.3rem; }
.exam-badge { display: inline-block; background: #1a1a2e; border: 1px solid #3a3a5a; color: #a78bfa; font-family: 'DM Mono', monospace; font-size: 0.72rem; padding: 0.3rem 0.8rem; border-radius: 20px; margin-top: 0.8rem; }
.invalid-box { background: #1a0a0a; border: 1px solid #5a1a1a; border-radius: 10px; padding: 1rem 1.2rem; color: #ff6b6b; font-size: 0.88rem; margin: 1rem 0; }
.code-block { background: #0d0d14; border: 1px solid #2a2a3a; border-radius: 8px; padding: 1rem; font-family: 'DM Mono', monospace; font-size: 0.82rem; color: #a8e6cf; margin: 0.5rem 0; white-space: pre-wrap; }
[data-testid="stExpander"] { background: #0d0d14 !important; border: 1px solid #2a2a3a !important; border-radius: 10px !important; margin: 0.3rem 0 !important; }
[data-testid="stExpander"] summary { font-family: 'Syne', sans-serif !important; font-weight: 700 !important; font-size: 0.82rem !important; color: #888 !important; }
[data-testid="stExpander"] p { font-family: 'DM Sans', sans-serif !important; font-size: 0.88rem !important; color: #ccc !important; line-height: 1.8 !important; }
hr { border-color: #1a1a2a !important; margin: 2rem 0 !important; }
[data-testid="stFileUploader"] { background: #111118 !important; border: 1px dashed #2a2a3a !important; border-radius: 10px !important; }
</style>
""", unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="display:flex; align-items:center; gap:1rem; margin-bottom:1.8rem;">
    <img src="https://raw.githubusercontent.com/vaibhavcor8/mood-ai/main/WhatsApp%20Image%202026-05-10%20at%205.04.39%20PM.jpeg"
         width="56" height="56" style="border-radius:50%; border:2px solid #a78bfa; object-fit:cover;">
    <div>
        <div class="main-title">📘 Smart Learning</div>
        <div class="main-sub">by Vaibhav Srivastava</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Model ──────────────────────────────────────────────────────────────────────
@st.cache_resource
def load_model():
    return ChatMistralAI(model="mistral-small-2506")

model = load_model()

SYSTEM_PROMPT = """
You are an expert teacher for Quantitative Aptitude, Reasoning, English, Grammar, General Studies, Computer Science, and Coding.

VERY IMPORTANT:
- Never use LaTeX like \\( \\) or \\[ \\] or $ for math. Write plain text only.
- Write "10%" not "\\(10\\%\\)", write "Rs. 120" not "Rs.\\(120\\)"
- For code questions, write actual code in the CODE section.

VALIDATION: First check if the input contains valid exam/study questions. If not (e.g. random text, greetings, irrelevant content), respond with ONLY:
---INVALID---
[Brief reason why it's not a valid question]
---INVALID_END---

If valid questions found, for EACH question respond in EXACTLY this format:

---QUESTION_START---
[Full question in plain text]
---OPTIONS_START---
A) [option]
B) [option]
C) [option]
D) [option]
(if no options, write NONE)
---ANSWER_START---
[Correct answer text only, no slash, no LaTeX]
---EXAM_INFO_START---
[MUST FILL THIS. List all exams where this type of question appears with years if known. Example: "SSC CGL 2019, SSC CHSL 2021, RRB NTPC 2020, IBPS PO 2022". If exact year unknown, write exam names only like "SSC CGL, RRB NTPC, UPSC Prelims". Never leave blank.]
---SHORT_TRICK_START---
[A clear short trick — 3 to 5 lines. Give the core formula or pattern, show one quick calculation step, then state the answer. Should be easy to remember but not too brief.]
---LONG_METHOD_START---
[Detailed step by step solution in plain text]
---CHILD_START---
[Explain like a 5 year old — simple, fun, with an everyday example]
---WRONG_OPTIONS_START---
A) Wrong because [clear reason]
B) Wrong because [clear reason]
C) Wrong because [clear reason]
(one per line, skip the correct option)
---CODE_START---
[If question involves code/programming, write the code solution here. Otherwise write NONE]
---BLOCK_END---

Repeat for every question. Never mix. Never skip sections.
"""

prompt_template = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "Questions extracted from input:\n{question}")
])

# ── Helpers ────────────────────────────────────────────────────────────────────
def clean(text):
    text = re.sub(r'\\\(|\\\)', '', text)
    text = re.sub(r'\\\[|\\\]', '', text)
    text = re.sub(r'\$+', '', text)
    text = re.sub(r'\\text\{([^}]*)\}', r'\1', text)
    text = re.sub(r'\\frac\{([^}]*)\}\{([^}]*)\}', r'\1/\2', text)
    text = re.sub(r'\\[a-zA-Z]+\{([^}]*)\}', r'\1', text)
    text = re.sub(r'\\[a-zA-Z]+', '', text)
    return text.strip().strip('/')

def get_section(start_tag, end_tag, text):
    pattern = re.escape(start_tag) + r"(.*?)" + re.escape(end_tag)
    m = re.search(pattern, text, re.DOTALL)
    return clean(m.group(1)) if m else ""

def extract_text_from_pdf(file):
    try:
        import pypdf
        reader = pypdf.PdfReader(file)
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception as e:
        return f"PDF read error: {e}"

def extract_text_from_docx(file):
    try:
        import docx
        doc = docx.Document(file)
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    except Exception as e:
        return f"DOCX read error: {e}"

def extract_text_from_image(file):
    try:
        img_bytes = file.read()
        b64 = base64.b64encode(img_bytes).decode()
        ext = file.name.split(".")[-1].lower()
        mime = "image/jpeg" if ext in ["jpg","jpeg"] else f"image/{ext}"
        from langchain_mistralai import ChatMistralAI as CMist
        from langchain_core.messages import HumanMessage
        vision_model = CMist(model="mistral-small-2506")
        msg = HumanMessage(content=[
            {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}},
            {"type": "text", "text": "Extract all text from this image exactly as it appears. Return only the extracted text, nothing else."}
        ])
        resp = vision_model.invoke([msg])
        return resp.content
    except Exception as e:
        return f"Image read error: {e}"

# ── Input Section ──────────────────────────────────────────────────────────────
st.markdown("### Enter Questions")

tab1, tab2 = st.tabs(["✏️ Type / Paste", "📎 Upload File"])

extracted_text = ""

if "results_output" not in st.session_state:
    st.session_state.results_output = None

with tab1:
    question_input = st.text_area(
        "Type or paste your questions",
        height=200,
        placeholder="Paste questions here...\n\nExample:\n1. What is 25% of 200?\nA) 25  B) 50  C) 75  D) 100"
    )
    extracted_text = question_input

with tab2:
    uploaded_file = st.file_uploader(
        "Upload PDF, Word Doc, or Image",
        type=["pdf", "docx", "doc", "png", "jpg", "jpeg", "webp"]
    )
    if uploaded_file:
        with st.spinner("Extracting text from file..."):
            ext = uploaded_file.name.split(".")[-1].lower()
            if ext == "pdf":
                extracted_text = extract_text_from_pdf(uploaded_file)
            elif ext in ["docx", "doc"]:
                extracted_text = extract_text_from_docx(uploaded_file)
            elif ext in ["png", "jpg", "jpeg", "webp"]:
                extracted_text = extract_text_from_image(uploaded_file)

        if extracted_text and "error" not in extracted_text.lower():
            st.success("Text extracted successfully!")
            with st.expander("👁 Preview extracted text"):
                st.text(extracted_text[:2000])
        else:
            st.error(extracted_text)
            extracted_text = ""

# ── Submit ─────────────────────────────────────────────────────────────────────
col_btn1, col_btn2 = st.columns([3, 1])
with col_btn1:
    get_answers = st.button("✦ Get Answers")
with col_btn2:
    if st.button("🔄 Reset"):
        st.session_state.results_output = None
        st.rerun()

if get_answers:
    if not extracted_text.strip():
        st.warning("Please enter or upload questions first.")
    else:
        with st.spinner("Solving..."):
            final_prompt = prompt_template.invoke({"question": extracted_text})
            response = model.invoke(final_prompt)
            st.session_state.results_output = response.content

        output = st.session_state.results_output
        # Check for invalid
        if "---INVALID---" in output:
            reason = get_section("---INVALID---", "---INVALID_END---", output)
            st.markdown(f"""
            <div class="invalid-box">
                ⚠️ <strong>Invalid Input</strong><br><br>
                {reason if reason else "The input does not contain valid content. Please enter a question, code, or topic."}
            </div>
            """, unsafe_allow_html=True)

        # ── Code explanation ──────────────────────────────────────────────────
        elif "---CODE_EXPLAIN_START---" in output:
            explanation  = get_section("---CODE_EXPLAIN_START---", "---CODE_OUTPUT_START---", output)
            code_output  = get_section("---CODE_OUTPUT_START---",  "---CODE_ISSUES_START---", output)
            code_issues  = get_section("---CODE_ISSUES_START---",  "---CODE_BLOCK_START---",  output)
            code_block   = get_section("---CODE_BLOCK_START---",   "---CODE_END---",          output)

            st.markdown(f"""
            <div class="q-card">
                <div class="q-number">💻 Code Analysis</div>
                <div class="q-text">{explanation}</div>
            </div>
            """, unsafe_allow_html=True)

            if code_output and code_output.upper() != "NO DIRECT OUTPUT.":
                st.markdown(f"""<div style='background:#0d1a0d;border:1px solid #2d6a2d;border-radius:8px;padding:1rem;margin:0.5rem 0;'>
                <div style='font-size:0.7rem;color:#555;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.5rem;'>Expected Output</div>
                <div style='font-family:monospace;font-size:0.85rem;color:#6ee86e;white-space:pre-wrap;'>{code_output}</div></div>""", unsafe_allow_html=True)

            if code_issues and code_issues.upper() != "NO ISSUES FOUND.":
                st.markdown(f"""<div style='background:#1a0a0a;border:1px solid #5a2a2a;border-radius:8px;padding:1rem;margin:0.5rem 0;'>
                <div style='font-size:0.7rem;color:#555;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.5rem;'>Issues / Improvements</div>
                <div style='font-size:0.88rem;color:#ffaa6e;'>{code_issues}</div></div>""", unsafe_allow_html=True)

            if code_block and code_block.upper() != "NONE":
                st.markdown(f'<div class="code-block">{code_block}</div>', unsafe_allow_html=True)

        # ── General question ──────────────────────────────────────────────────
        elif "---GENERAL_START---" in output:
            explanation    = get_section("---GENERAL_START---",        "---GENERAL_EXAMPLE_START---", output)
            example        = get_section("---GENERAL_EXAMPLE_START---","---GENERAL_CHILD_START---",   output)
            child_explain  = get_section("---GENERAL_CHILD_START---",  "---GENERAL_END---",           output)

            st.markdown(f"""
            <div class="q-card">
                <div class="q-number">📖 Explanation</div>
                <div class="q-text">{explanation}</div>
            </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                with st.expander("💡 Real-World Example"):
                    st.write(example or "Not available")
            with col2:
                with st.expander("🧒 5-Year-Old Explanation"):
                    st.write(child_explain or "Not available")

        else:
            blocks = output.split("---QUESTION_START---")
            count = 0

            for block in blocks:
                if not block.strip():
                    continue

                full = "---QUESTION_START---" + block

                question_text = get_section("---QUESTION_START---", "---OPTIONS_START---",    full)
                options_text  = get_section("---OPTIONS_START---",   "---ANSWER_START---",     full)
                answer_text   = get_section("---ANSWER_START---",    "---EXAM_INFO_START---",  full)
                exam_info     = get_section("---EXAM_INFO_START---", "---SHORT_TRICK_START---",full)
                short_trick   = get_section("---SHORT_TRICK_START---","---LONG_METHOD_START---",full)
                long_method   = get_section("---LONG_METHOD_START---","---CHILD_START---",      full)
                child_explain = get_section("---CHILD_START---",      "---WRONG_OPTIONS_START---",full)
                wrong_options = get_section("---WRONG_OPTIONS_START---","---CODE_START---",     full)
                code_section  = get_section("---CODE_START---",       "---BLOCK_END---",        full)

                if not question_text:
                    continue

                count += 1

                # Options HTML
                options_html = ""
                if options_text and options_text.upper() != "NONE":
                    for line in options_text.split("\n"):
                        line = line.strip()
                        if line:
                            options_html += f'<div class="option-row">{line}</div>'

                # Exam badge
                exam_badge = f'<div class="exam-badge">🎓 {exam_info}</div>' if exam_info else ""

                st.markdown(f"""
                <div class="q-card">
                    <div class="q-number">Question {count}</div>
                    <div class="q-text">{question_text}</div>
                    {options_html}
                    <div style="font-size:0.72rem; color:#555; text-transform:uppercase;
                         letter-spacing:0.1em; margin: 1rem 0 0.3rem;">Final Answer</div>
                    <div class="answer-pill">✓ {answer_text}</div>
                    {exam_badge}
                </div>
                """, unsafe_allow_html=True)

                # Code block if present
                if code_section and code_section.upper() != "NONE":
                    st.markdown(f'<div class="code-block">{code_section}</div>', unsafe_allow_html=True)

                col1, col2 = st.columns(2)
                with col1:
                    with st.expander("⚡ Short Trick"):
                        st.write(short_trick or "Not available")
                with col2:
                    with st.expander("📖 Long Method"):
                        st.write(long_method or "Not available")

                col3, col4 = st.columns(2)
                with col3:
                    with st.expander("🧒 5-Year-Old Explanation"):
                        st.write(child_explain or "Not available")
                with col4:
                    with st.expander("❌ Why Other Options Are Wrong"):
                        if wrong_options and wrong_options.upper() != "NONE":
                            for line in wrong_options.split("\n"):
                                line = line.strip()
                                if line:
                                    st.markdown(f"- {line}")
                        else:
                            st.write("Not available")

            if count == 0:
                st.error("Could not parse response. Please try again.")

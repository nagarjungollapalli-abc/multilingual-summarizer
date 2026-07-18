import io
import os
import time
import base64
import threading
from datetime import date
import streamlit as st

st.set_page_config(page_title="Bhasha Setu", page_icon="🌉", layout="centered")

LOGO_SVG = """
<svg width="44" height="44" viewBox="0 0 44 44" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bsGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#8B6CFF"/>
      <stop offset="100%" stop-color="#E8B84B"/>
    </linearGradient>
  </defs>
  <circle cx="9" cy="30" r="5" fill="url(#bsGrad)"/>
  <circle cx="35" cy="30" r="5" fill="url(#bsGrad)"/>
  <path d="M9 30 C 9 12, 35 12, 35 30" stroke="url(#bsGrad)" stroke-width="3" fill="none" stroke-linecap="round"/>
</svg>
"""


def apply_custom_theme():
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&family=Noto+Sans+Telugu:wght@600;800&family=Noto+Sans+Devanagari:wght@500;600&display=swap');

    :root {{
        --bs-bg: #0B0D14;
        --bs-panel: #12141E;
        --bs-border: #232739;
        --bs-text: #ECEEF5;
        --bs-muted: #8B90A6;
        --bs-accent: #8B6CFF;
        --bs-accent-2: #E8B84B;
    }}

    .stApp {{
        background: radial-gradient(ellipse 1200px 600px at 50% -10%, rgba(139,108,255,0.14), transparent),
                    var(--bs-bg);
        color: var(--bs-text);
        font-family: 'Inter', sans-serif;
    }}

    h1, h2, h3, .stMarkdown h1, .stMarkdown h2 {{
        font-family: 'Space Grotesk', sans-serif !important;
        letter-spacing: -0.01em;
    }}

    /* Buttons */
    .stButton > button {{
        background: linear-gradient(135deg, var(--bs-accent), #6A4FE0);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        letter-spacing: 0.01em;
        transition: filter 0.15s ease, transform 0.1s ease;
    }}
    .stButton > button:hover {{
        filter: brightness(1.12);
        transform: translateY(-1px);
    }}

    /* Inputs, textareas, selects */
    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] > div {{
        background-color: var(--bs-panel) !important;
        border: 1px solid var(--bs-border) !important;
        color: var(--bs-text) !important;
        border-radius: 8px !important;
    }}

    /* Sidebar */
    section[data-testid="stSidebar"] {{
        background-color: var(--bs-panel);
        border-right: 1px solid var(--bs-border);
    }}

    /* Metric (used in admin panel) */
    div[data-testid="stMetricValue"] {{
        font-family: 'JetBrains Mono', monospace;
        color: var(--bs-accent-2);
    }}

    /* Captions / timer text */
    .stCaption, [data-testid="stCaptionContainer"] {{
        font-family: 'JetBrains Mono', monospace !important;
        color: var(--bs-muted) !important;
    }}

    /* Hide default Streamlit chrome for a cleaner branded look */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}

    .bs-header {{
        display: flex;
        align-items: flex-start;
        gap: 16px;
        margin-bottom: 4px;
    }}
    .bs-logo {{
        margin-top: 4px;
        flex-shrink: 0;
    }}
    .bs-title-block {{
        display: flex;
        flex-direction: column;
        gap: 2px;
    }}
    .bs-telugu {{
        font-family: 'Noto Sans Telugu', sans-serif;
        font-weight: 800;
        font-size: 40px;
        line-height: 1.1;
        background: linear-gradient(135deg, var(--bs-text), var(--bs-accent-2));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}
    .bs-sub {{
        display: flex;
        align-items: baseline;
        gap: 10px;
        color: var(--bs-muted);
    }}
    .bs-sub .bs-english {{
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 600;
        font-size: 15px;
        letter-spacing: 0.02em;
    }}
    .bs-sub .bs-devanagari {{
        font-family: 'Noto Sans Devanagari', sans-serif;
        font-weight: 600;
        font-size: 15px;
    }}
    .bs-sub .bs-sep {{
        color: var(--bs-border);
    }}
    .bs-fixed-tagline {{
        color: var(--bs-accent-2);
        font-size: 13px;
        font-family: 'Inter', sans-serif;
        font-style: italic;
        margin-top: 2px;
    }}
    .bs-tagline {{
        color: var(--bs-muted);
        font-size: 14px;
        margin-bottom: 20px;
    }}
    .bs-divider {{
        height: 2px;
        background: linear-gradient(90deg, var(--bs-accent), var(--bs-accent-2), transparent);
        border-radius: 2px;
        margin: 8px 0 24px 0;
    }}
    </style>
    """, unsafe_allow_html=True)


def render_brand_header():
    st.markdown(f"""
    <div class="bs-header">
        <div class="bs-logo">{LOGO_SVG}</div>
        <div class="bs-title-block">
            <div class="bs-telugu">భాష సేతు</div>
            <div class="bs-sub">
                <span class="bs-english">Bhasha Setu</span>
                <span class="bs-sep">·</span>
                <span class="bs-devanagari">भाषा सेतु</span>
            </div>
            <div class="bs-fixed-tagline">Your personalized translator</div>
        </div>
    </div>
    <div class="bs-divider"></div>
    """, unsafe_allow_html=True)


apply_custom_theme()

LANGUAGES = ["English", "Telugu", "Hindi", "Tamil", "Kannada", "French", "Spanish", "German"]

PROVIDERS = {
    "Claude (Anthropic)": {
        "env_var": "ANTHROPIC_API_KEY",
        "default_model": "claude-sonnet-4-6",
        "supports_image": True,
        "get_key_url": "https://console.anthropic.com",
    },
    "ChatGPT (OpenAI)": {
        "env_var": "OPENAI_API_KEY",
        "default_model": "gpt-5.6",
        "supports_image": True,
        "get_key_url": "https://platform.openai.com/api-keys",
    },
    "Gemini (Google)": {
        "env_var": "GOOGLE_API_KEY",
        "default_model": "gemini-flash-latest",
        "supports_image": True,
        "get_key_url": "https://aistudio.google.com/apikey",
    },
    "Sarvam AI": {
        "env_var": "SARVAM_API_KEY",
        "default_model": "sarvam-105b",
        "supports_image": False,  # text-only as of writing
        "get_key_url": "https://dashboard.sarvam.ai",
    },
}

# ---------- Usage limits (protects the admin's API budget once this is public) ----------
MAX_CHARS_PER_REQUEST = 6000
MAX_REQUESTS_PER_SESSION = 5
MAX_REQUESTS_PER_DAY_GLOBAL = 100


@st.cache_resource
def _usage_counter():
    return {"date": date.today(), "count": 0, "lock": threading.Lock()}


def record_usage(is_admin: bool) -> str | None:
    """Returns a blocking error message for non-admins over their limit;
    always records the request (for stats) and returns None otherwise."""
    if "session_request_count" not in st.session_state:
        st.session_state.session_request_count = 0

    if not is_admin and st.session_state.session_request_count >= MAX_REQUESTS_PER_SESSION:
        return (
            f"You've reached the limit of {MAX_REQUESTS_PER_SESSION} requests "
            f"for this session. Refresh the page to reset."
        )

    counter = _usage_counter()
    with counter["lock"]:
        if counter["date"] != date.today():
            counter["date"] = date.today()
            counter["count"] = 0
        if not is_admin and counter["count"] >= MAX_REQUESTS_PER_DAY_GLOBAL:
            return "This app has reached its shared daily usage limit. Please try again tomorrow."
        counter["count"] += 1

    st.session_state.session_request_count += 1
    return None


def format_elapsed(seconds: float) -> str:
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{minutes} min : {secs} sec : {millis} ms"


def get_secret(name: str) -> str:
    try:
        return st.secrets.get(name, "") or os.environ.get(name, "")
    except Exception:
        return os.environ.get(name, "")


# ---------- File extraction helpers ----------

def extract_text_from_pdf(file_bytes: bytes) -> str:
    from pypdf import PdfReader
    reader = PdfReader(io.BytesIO(file_bytes))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def extract_text_from_docx(file_bytes: bytes) -> str:
    from docx import Document
    doc = Document(io.BytesIO(file_bytes))
    return "\n".join(p.text for p in doc.paragraphs)


def build_prompt(language: str, text_input, has_image: bool) -> str:
    structure_instructions = (
        f"Structure your response with exactly these 5 sections, each as a "
        f"bold heading followed by its content, in this order:\n"
        f"1. Topic — one line naming what this is about\n"
        f"2. Background — 2-3 sentences of context, what situation or subject this comes from\n"
        f"3. Summary — a clear paragraph covering the main content\n"
        f"4. Important points — 3-5 bullet points of the key facts, numbers, or takeaways\n"
        f"5. Conclusion — 1-2 sentences on the overall implication or outcome\n\n"
        f"Write the heading words themselves AND all content in {language} "
        f"(translate the headings 'Topic', 'Background', 'Summary', "
        f"'Important points', 'Conclusion' into {language} too — do not leave "
        f"them in English unless {language} is English). "
        f"Do not add any preamble before section 1 or any text after section 5."
    )

    if has_image:
        return (
            f"Look at this image and analyze what's shown or written in it. "
            f"{structure_instructions}"
        )
    return (
        f"Analyze the following text. {structure_instructions}\n\n"
        f'Text:\n"""{text_input}"""'
    )


# ---------- Provider calls ----------

def call_claude(api_key, model, prompt, image_bytes=None, image_mime=None):
    from anthropic import Anthropic
    client = Anthropic(api_key=api_key)
    content = []
    if image_bytes:
        content.append({
            "type": "image",
            "source": {"type": "base64", "media_type": image_mime,
                       "data": base64.b64encode(image_bytes).decode("utf-8")},
        })
    content.append({"type": "text", "text": prompt})
    response = client.messages.create(
        model=model, max_tokens=1500,
        messages=[{"role": "user", "content": content}],
    )
    return "".join(b.text for b in response.content if b.type == "text")


def call_openai(api_key, model, prompt, image_bytes=None, image_mime=None):
    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    content = [{"type": "text", "text": prompt}]
    if image_bytes:
        b64 = base64.b64encode(image_bytes).decode("utf-8")
        content.append({"type": "image_url",
                         "image_url": {"url": f"data:{image_mime};base64,{b64}"}})
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": content}],
    )
    return response.choices[0].message.content


def call_gemini(api_key, model, prompt, image_bytes=None, image_mime=None):
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=api_key)
    parts = [prompt]
    if image_bytes:
        parts.append(types.Part.from_bytes(data=image_bytes, mime_type=image_mime))
    response = client.models.generate_content(model=model, contents=parts)
    return response.text


def call_sarvam(api_key, model, prompt):
    from openai import OpenAI
    client = OpenAI(api_key=api_key, base_url="https://api.sarvam.ai/v1")
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content


# ======================================================================
# HOME / LOGIN SCREEN
# ======================================================================

if "username" not in st.session_state:
    st.session_state.username = None
    st.session_state.is_admin = False
    st.session_state.pending_admin_check = False

if st.session_state.username is None:
    render_brand_header()
    st.caption("Enter your name to continue.")
    name_input = st.text_input("Your name")
    if st.button("Continue", type="primary"):
        if not name_input.strip():
            st.warning("Please enter a name.")
        else:
            st.session_state.username = name_input.strip()
            admin_names = [a.strip().lower() for a in get_secret("ADMIN_USERNAMES").split(",") if a.strip()]
            st.session_state.pending_admin_check = st.session_state.username.lower() in admin_names
            st.rerun()
    st.stop()

if st.session_state.pending_admin_check:
    render_brand_header()
    st.caption(f"Welcome, {st.session_state.username}. This name matches an admin account. Enter the admin password to unlock admin access, or continue as a regular user.")
    pw = st.text_input("Admin password", type="password")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Unlock admin access", type="primary"):
            real_pw = get_secret("ADMIN_PASSWORD")
            if real_pw and pw == real_pw:
                st.session_state.is_admin = True
                st.session_state.pending_admin_check = False
                st.rerun()
            else:
                st.error("Incorrect password.")
    with col2:
        if st.button("Continue as regular user"):
            st.session_state.is_admin = False
            st.session_state.pending_admin_check = False
            st.rerun()
    st.stop()


# ======================================================================
# MAIN APP
# ======================================================================

render_brand_header()
st.caption(f"Welcome, {st.session_state.username} — paste text, or upload an image, PDF, or Word document.")

with st.sidebar:
    role_label = " (admin)" if st.session_state.is_admin else ""
    st.write(f"Signed in as **{st.session_state.username}**{role_label}")
    if st.button("Switch user"):
        for key in ["username", "is_admin", "pending_admin_check", "session_request_count"]:
            st.session_state.pop(key, None)
        st.rerun()

    st.header("Provider settings")
    provider_name = st.selectbox("Provider", list(PROVIDERS.keys()))
    provider = PROVIDERS[provider_name]

    if st.session_state.is_admin:
        api_key = get_secret(provider["env_var"])
        if api_key:
            st.success(f"{provider_name} key loaded from app secrets.")
        else:
            st.warning(f"No {provider_name} key found in secrets. Add {provider['env_var']} to Secrets.")
        model = st.text_input("Model", value=provider["default_model"])
    else:
        st.info(f"{provider_name} requires your own API key.")
        api_key = st.text_input(f"{provider_name} API key", type="password")
        model = st.text_input("Model", value=provider["default_model"])
        with st.expander("How do I get an API key?"):
            st.markdown(f"Get a key from [{provider_name}]({provider['get_key_url']}), then paste it above.")

    if st.session_state.is_admin:
        with st.expander("Admin: today's usage"):
            counter = _usage_counter()
            with counter["lock"]:
                today_count = counter["count"] if counter["date"] == date.today() else 0
            st.metric("Requests today (all users, since last restart)", today_count)
            st.caption(f"Daily cap for regular users: {MAX_REQUESTS_PER_DAY_GLOBAL}. Resets when the app process restarts.")

content_type = st.selectbox("What are you summarizing?", ["Text", "Image", "PDF", "Word Document"])

text_input = None
image_bytes = None
image_mime = None

if content_type == "Text":
    text_input = st.text_area("Text to summarize", height=200, placeholder="Paste your text here...")

elif content_type == "Image":
    if not provider["supports_image"]:
        st.warning(f"{provider_name} doesn't support images here. Switch to Claude, ChatGPT, or Gemini for image input.")
    else:
        uploaded = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])
        if uploaded:
            file_bytes = uploaded.read()
            ext = uploaded.name.lower().split(".")[-1]
            image_mime = "image/png" if ext == "png" else "image/jpeg"
            image_bytes = file_bytes
            st.image(file_bytes, caption=uploaded.name, use_container_width=True)

elif content_type == "PDF":
    uploaded = st.file_uploader("Upload a PDF", type=["pdf"])
    if uploaded:
        with st.spinner("Extracting text from PDF..."):
            text_input = extract_text_from_pdf(uploaded.read())
        with st.expander("Preview extracted text"):
            st.text(text_input[:3000])

elif content_type == "Word Document":
    uploaded = st.file_uploader("Upload a Word document", type=["docx"])
    if uploaded:
        with st.spinner("Extracting text from Word document..."):
            text_input = extract_text_from_docx(uploaded.read())
        with st.expander("Preview extracted text"):
            st.text(text_input[:3000])

language = st.selectbox("Target language", LANGUAGES, index=1)

if not st.session_state.is_admin:
    used = st.session_state.get("session_request_count", 0)
    st.caption(f"Requests used this session: {used}/{MAX_REQUESTS_PER_SESSION}")

if st.button("Summarize", type="primary"):
    if not text_input and not image_bytes:
        st.warning("Add some text or upload a file first.")
    elif not api_key:
        st.warning(f"Enter your {provider_name} API key in the sidebar first.")
    else:
        if text_input and len(text_input) > MAX_CHARS_PER_REQUEST:
            text_input = text_input[:MAX_CHARS_PER_REQUEST]
            st.info(f"Text was trimmed to the first {MAX_CHARS_PER_REQUEST} characters to keep requests within budget.")

        limit_error = record_usage(st.session_state.is_admin)
        if limit_error:
            st.error(limit_error)
        else:
            prompt = build_prompt(language, text_input, has_image=bool(image_bytes))
            with st.spinner(f"Summarizing with {provider_name}..."):
                try:
                    start_time = time.perf_counter()

                    if provider_name == "Claude (Anthropic)":
                        summary = call_claude(api_key, model, prompt, image_bytes, image_mime)
                    elif provider_name == "ChatGPT (OpenAI)":
                        summary = call_openai(api_key, model, prompt, image_bytes, image_mime)
                    elif provider_name == "Gemini (Google)":
                        summary = call_gemini(api_key, model, prompt, image_bytes, image_mime)
                    elif provider_name == "Sarvam AI":
                        summary = call_sarvam(api_key, model, prompt)

                    elapsed = time.perf_counter() - start_time

                    st.subheader("Summary")
                    st.write(summary)
                    st.caption(f"The summary has been extracted in {format_elapsed(elapsed)}")
                except Exception as e:
                    st.error(f"Something went wrong: {e}")

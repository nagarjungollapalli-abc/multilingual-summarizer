import io
import os
import base64
import streamlit as st

st.set_page_config(page_title="Multilingual Summarizer", layout="centered")

LANGUAGES = ["English", "Telugu", "Hindi", "Tamil", "Kannada", "French", "Spanish", "German"]

PROVIDERS = {
    "Claude (Anthropic)": {
        "env_var": "ANTHROPIC_API_KEY",
        "default_model": "claude-sonnet-4-6",
        "supports_image": True,
    },
    "ChatGPT (OpenAI)": {
        "env_var": "OPENAI_API_KEY",
        "default_model": "gpt-5.6",
        "supports_image": True,
    },
    "Gemini (Google)": {
        "env_var": "GOOGLE_API_KEY",
        "default_model": "gemini-flash-latest",
        "supports_image": True,
    },
    "Sarvam AI": {
        "env_var": "SARVAM_API_KEY",
        "default_model": "sarvam-105b",
        "supports_image": False,  # text-only as of writing
    },
}


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
    if has_image:
        return (
            f"Describe and summarize what's shown or written in this image "
            f"in exactly 3 concise bullet points, written in {language}. "
            f"Return only the 3 bullet points, no preamble."
        )
    return (
        f"Summarize the following text in exactly 3 concise bullet points, "
        f"written in {language} regardless of the original language. "
        f"Return only the 3 bullet points, no preamble.\n\n"
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
        model=model, max_tokens=1000,
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
    # Sarvam exposes an OpenAI-compatible /v1/chat/completions endpoint
    from openai import OpenAI
    client = OpenAI(api_key=api_key, base_url="https://api.sarvam.ai/v1")
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content


# ---------- UI ----------

st.title("Multilingual summarizer")
st.caption("Paste text, or upload an image, PDF, or Word document. Pick a provider and a language.")

with st.sidebar:
    st.header("Provider settings")
    provider_name = st.selectbox("Provider", list(PROVIDERS.keys()))
    provider = PROVIDERS[provider_name]

    env_key = os.environ.get(provider["env_var"], "")
    api_key = st.text_input(
        f"{provider_name} API key",
        value=env_key,
        type="password",
        help=f"Reads from {provider['env_var']} if set, or paste one here.",
    )
    model = st.text_input("Model", value=provider["default_model"])

input_mode = st.radio("Input type", ["Paste text", "Upload file"], horizontal=True)

text_input = None
image_bytes = None
image_mime = None

if input_mode == "Paste text":
    text_input = st.text_area("Text to summarize", height=200, placeholder="Paste your text here...")
else:
    allowed_types = ["pdf", "docx", "txt"] + (["png", "jpg", "jpeg"] if provider["supports_image"] else [])
    uploaded = st.file_uploader("Upload a file", type=allowed_types)
    if uploaded:
        file_bytes = uploaded.read()
        ext = uploaded.name.lower().split(".")[-1]

        if ext == "pdf":
            with st.spinner("Extracting text from PDF..."):
                text_input = extract_text_from_pdf(file_bytes)
        elif ext == "docx":
            with st.spinner("Extracting text from Word document..."):
                text_input = extract_text_from_docx(file_bytes)
        elif ext == "txt":
            text_input = file_bytes.decode("utf-8", errors="ignore")
        elif ext in ("png", "jpg", "jpeg"):
            image_mime = "image/png" if ext == "png" else "image/jpeg"
            image_bytes = file_bytes
            st.image(file_bytes, caption=uploaded.name, use_container_width=True)

        if text_input:
            with st.expander("Preview extracted text"):
                st.text(text_input[:3000])

    if not provider["supports_image"]:
        st.caption(f"Note: {provider_name} is text-only here — image uploads won't work with this provider.")

language = st.selectbox("Target language", LANGUAGES, index=1)

if st.button("Summarize", type="primary"):
    if not text_input and not image_bytes:
        st.warning("Add some text or upload a file first.")
    elif not api_key:
        st.warning(f"Enter your {provider_name} API key in the sidebar first.")
    else:
        prompt = build_prompt(language, text_input, has_image=bool(image_bytes))
        with st.spinner(f"Summarizing with {provider_name}..."):
            try:
                if provider_name == "Claude (Anthropic)":
                    summary = call_claude(api_key, model, prompt, image_bytes, image_mime)
                elif provider_name == "ChatGPT (OpenAI)":
                    summary = call_openai(api_key, model, prompt, image_bytes, image_mime)
                elif provider_name == "Gemini (Google)":
                    summary = call_gemini(api_key, model, prompt, image_bytes, image_mime)
                elif provider_name == "Sarvam AI":
                    summary = call_sarvam(api_key, model, prompt)

                st.subheader("Summary")
                st.write(summary)
            except Exception as e:
                st.error(f"Something went wrong: {e}")

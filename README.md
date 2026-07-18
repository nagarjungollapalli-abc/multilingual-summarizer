# Multilingual Summarizer (local app)

A local web app that accepts pasted text, or an uploaded image, PDF, or Word
document, and returns a 3-point summary in a language of your choice
(Telugu, Hindi, Tamil, Kannada, English, French, Spanish, German).

You can switch between four providers right in the app's sidebar:
Claude (Anthropic), ChatGPT (OpenAI), Gemini (Google), and Sarvam AI
(strong on Indian languages, text-only — no image support yet).

## 1. Get API key(s)

You only need a key for the provider(s) you plan to use — you don't need
all four.

| Provider | Where to get a key |
|---|---|
| Claude | https://console.anthropic.com → API Keys |
| ChatGPT | https://platform.openai.com → API keys |
| Gemini | https://aistudio.google.com → Get API key |
| Sarvam AI | https://dashboard.sarvam.ai → API Keys |

## 2. Install Python dependencies

Open a terminal in this folder and run:

```
pip install -r requirements.txt
```

(If you're on the same machine you tested Claude Code setup on, you likely
already have Python and pip.)

## 3. Set your API key(s) — optional

You can either set these as environment variables (so they auto-fill in the
sidebar), or just paste a key directly into the app's sidebar each time you
run it. Environment variable names:

| Provider | Variable name |
|---|---|
| Claude | `ANTHROPIC_API_KEY` |
| ChatGPT | `OPENAI_API_KEY` |
| Gemini | `GOOGLE_API_KEY` |
| Sarvam AI | `SARVAM_API_KEY` |
| Admin login (comma-separated names) | `ADMIN_USERNAMES` |
| Admin password | `ADMIN_PASSWORD` |

**Windows (PowerShell):**
```
$env:ANTHROPIC_API_KEY="your-key-here"
```

**Mac/Linux:**
```
export ANTHROPIC_API_KEY="your-key-here"
```

## 4. Run the app

```
streamlit run app.py
```

This opens a browser tab at `http://localhost:8501` with the tool running
locally on your machine.

## Notes

- **Home screen:** everyone enters their name first. If the name matches one
  listed in `ADMIN_USERNAMES` (comma-separated, e.g. `Nagarjun,Priya`), they're
  prompted for `ADMIN_PASSWORD` to unlock admin mode.
- **Admin mode:** API keys load automatically from Secrets (no typing needed),
  and a "today's usage" stat panel appears in the sidebar. Admin requests are
  not capped by the session/daily limits.
- **Regular users:** never see the admin's API keys or usage stats. They're
  shown a link to get their own key for whichever provider they pick, and
  their requests count against the session and daily limits.
- **Content type dropdown:** choose Text, Image, PDF, or Word Document —
  the matching input widget appears. Image input is disabled automatically
  for Sarvam AI, since it's text-only.
- Pick a provider from the sidebar dropdown; the model name field is
  editable, so you can swap in a different version any time without
  touching the code.
- PDFs and Word docs: text is extracted automatically before sending to the
  model.
- Each API key only goes to that provider's own servers, directly from your
  machine — nothing is routed through claude.ai or any third party.
- Each provider bills separately per its own API pricing, independent of
  any claude.ai, ChatGPT, or Gemini subscription you already have.

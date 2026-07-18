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

- Pick a provider from the sidebar dropdown; the model name field is
  editable, so you can swap in a different version any time without
  touching the code.
- PDFs and Word docs: text is extracted automatically before sending to the
  model.
- Images: supported for Claude, ChatGPT, and Gemini. Sarvam AI is
  currently text-only, so image uploads are disabled when it's selected.
- Each API key only goes to that provider's own servers, directly from your
  machine — nothing is routed through claude.ai or any third party.
- Each provider bills separately per its own API pricing, independent of
  any claude.ai, ChatGPT, or Gemini subscription you already have.

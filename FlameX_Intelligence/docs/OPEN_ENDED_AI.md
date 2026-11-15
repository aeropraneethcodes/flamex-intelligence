# FlameIQ open-ended conversation configuration

You can enter *any* typed question; suggested prompts are examples only.

## Option 1 — Offline source search (default, no setup)

Retrieves relevant cited NASA passages and computed FLEX statistics using TF-IDF and deterministic tools. It accepts arbitrary wording but does not generate unrestricted conversational replies. Unknown facts are marked unknown.

## Option 2 — OpenAI hosted language model

Run `python -m pip install -r requirements-optional-ai.txt`. Set `OPENAI_API_KEY` using an environment variable on your laptop or under Streamlit Community Cloud's Secrets. Never upload a key to GitHub or paste it into the public app. Optional: `FLAMEX_MODEL=gpt-4o-mini`. Choose **OpenAI · API key** in FlameIQ. Hosted API may have usage costs. For deployment, the `openai` dependency must be included in the root `requirements.txt`.

## Option 3 — Ollama local language model (no API key)

Install Ollama from https://ollama.com/download, and run `ollama pull llama3.2:3b` in Windows Terminal. Run Streamlit on the **same computer** as Ollama. Choose **Ollama · local model** in FlameIQ. Local language models require sufficient device resources and may be slower. Streamlit Community Cloud cannot connect to a visitor's local Ollama instance.

## Answer scopes

- **Research evidence**: source-constrained conversations with explicit NASA references, original FLEX records and computed statistics. Missing raw studies or unsafe operational verdicts are refused. Model replies that add unsupported numeric tokens are withheld.
- **General Q&A**: optional conversational mode for non-research questions. Responses carry the disclaimer **GENERAL DISCUSSION — NOT NASA-VERIFIED**.

## Data security

When enabling a hosted model, chat messages and a compact selected evidence pack are sent to the configured external provider. Avoid sharing personal, confidential, or regulated information. Default offline mode makes no external model calls.

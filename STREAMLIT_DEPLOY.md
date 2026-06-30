# Streamlit Community Cloud Deployment

Use these settings when creating the app at https://share.streamlit.io:

- Repository: this GitHub repository
- Branch: your deploy branch, usually `main`
- Main file path: `app.py`
- Python version: `3.12`

Community Cloud installs Python dependencies from `requirements.txt` and Linux packages from
`packages.txt`.

This app can run without a local Ollama server in Streamlit Cloud. When Ollama is unavailable, it
uses a lightweight heuristic extractor so uploaded complaints still produce a draft. To disable that
fallback in another environment, set:

```bash
ALLOW_HEURISTIC_FALLBACK=false
```

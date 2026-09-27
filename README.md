# Atlas Resume Parser

Atlas is a Streamlit application that extracts text from PDF, DOCX, and TXT resumes and converts
it into validated, structured candidate data with LangChain, OpenAI, and Pydantic.

## Features

- Local text extraction for PDF, DOCX, and UTF-8 TXT files
- Nested structured output for contact data, skills, experience, education, projects, and more
- OpenAI schema-constrained output validated as nested Pydantic models
- Explicit anti-fabrication and prompt-injection rules
- Human-readable review view plus downloadable JSON and extracted text
- Curated model presets plus support for any compatible custom OpenAI model ID
- Input-size, file-size, and PDF page limits with clear errors
- Secure server-side API-key configuration or session-only manual keys

## Run locally

Python 3.10+ is recommended.

```bash
cd resume-parser
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
cp .env.example .env
# Add OPENAI_API_KEY to .env, configure Streamlit secrets, or paste a key into the sidebar.
streamlit run app.py
```

### API key configuration

Atlas checks for a key in this order:

1. `OPENAI_API_KEY` in the process environment or local `.env`
2. `OPENAI_API_KEY` in `.streamlit/secrets.toml` or Streamlit Community Cloud secrets
3. A key entered manually in the sidebar for the current session

When a server-side key exists, the UI reports that it is available without putting its value in
an input field or sending it to the browser. The user can choose that key or provide their own.
Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` for local Streamlit secrets;
the real secrets file is ignored by Git.

The model selector includes tested presets and an always-available custom model field. Editing the
custom field activates that model automatically; choosing a preset switches back to the selected
preset. Custom models must be available to the chosen API key and support OpenAI JSON Schema
structured output.

## Architecture

```text
PDF / DOCX / TXT
       │
       ▼
local text extractor
       │
       ▼
 guarded LangChain prompt ─► OpenAI structured output ─► Pydantic validation
                                                │
                                                ▼
                                   review UI + JSON download
```

## Test and lint

```bash
pytest
ruff check .
```

## Limitations

- Scanned/image-only PDFs need OCR before upload.
- Complex visual layouts may not preserve perfect reading order during text extraction.
- The language model structures extracted facts but may still make mistakes. Review the JSON
  before importing it into another system.
- Resume text is sent to OpenAI for parsing. Only process documents you are authorized to use.

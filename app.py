"""Streamlit interface for Atlas Resume Parser."""

from __future__ import annotations

import logging
import os
from html import escape
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from langchain_core.exceptions import OutputParserException
from openai import (
    APIConnectionError,
    APITimeoutError,
    AuthenticationError,
    BadRequestError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitError,
)

from resume_parser import (
    MODEL_PRESETS,
    ExtractionError,
    build_chain,
    configured_api_key,
    configured_model,
    extract_resume_text,
    parse_resume,
    resolve_model,
)

load_dotenv(dotenv_path=Path(__file__).with_name(".env"))
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(page_title="Atlas — Resume Parser", page_icon="◫", layout="wide")

st.markdown(
    """
    <style>
    :root { color-scheme: light; }
    html, body { font-family: Inter, ui-sans-serif, system-ui, sans-serif; }
    .stApp, [data-testid="stAppViewContainer"] { background: #f4f1ea; color: #17201d; }
    [data-testid="stHeader"] {
        height: 3.75rem;
        background: rgba(244, 241, 234, .94);
        border-bottom: 1px solid rgba(23, 32, 29, .08);
        backdrop-filter: blur(12px);
    }
    [data-testid="stDecoration"] { background: #b6533b; height: 2px; }
    .block-container {
        max-width: 1160px;
        padding-top: 6.2rem !important;
        padding-bottom: 5rem;
    }
    [data-testid="stSidebar"] { background: #16221e; border-right: 1px solid #293832; }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p { color: #f7f4ec !important; }
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {
        color: #bdc7c1 !important;
    }
    [data-testid="stSidebar"] hr { border-color: #35443e; }
    [data-testid="stSidebar"] input,
    [data-testid="stSidebar"] [data-baseweb="select"] > div {
        background: #f8f6f0 !important;
        color: #17201d !important;
        border-color: #5d6964 !important;
    }
    [data-testid="stSidebar"] input { -webkit-text-fill-color: #17201d !important; }
    [data-testid="stSidebar"] svg { fill: currentColor; }
    .key-status { display: flex; gap: .65rem; align-items: flex-start; margin: .25rem 0 .8rem;
                  padding: .72rem .78rem; border: 1px solid #3d5048; border-radius: 10px;
                  background: #21312b; }
    .key-status-dot { flex: 0 0 auto; width: .5rem; height: .5rem; margin-top: .35rem;
                      border-radius: 50%; background: #6fbd91; box-shadow: 0 0 0 3px #29483a; }
    .key-status-title { color: #f7f4ec; font-size: .82rem; font-weight: 750; }
    .key-status-copy { color: #aebbb4; font-size: .72rem; margin-top: .12rem; line-height: 1.4; }
    .key-missing .key-status-dot { background: #d19a69; box-shadow: 0 0 0 3px #4b3828; }
    [data-testid="stSidebar"] [data-testid="stRadio"] label p { color: #e6ebe8 !important; }
    [data-baseweb="popover"], [data-baseweb="menu"] {
        background: #fffdf8 !important;
        color: #17201d !important;
    }
    [role="option"] { color: #17201d !important; background: #fffdf8 !important; }
    [role="option"]:hover { background: #ece8de !important; }
    .brand-row { display: flex; align-items: center; justify-content: space-between; gap: 1rem; }
    .kicker { color: #a44833; font-size: .75rem; font-weight: 800; letter-spacing: .17em; }
    .privacy-pill {
        display: inline-flex; align-items: center; gap: .45rem; border: 1px solid #cec8bb;
        border-radius: 999px; padding: .38rem .7rem; background: rgba(255,255,255,.45);
        color: #4e5b55; font-size: .76rem; font-weight: 650;
    }
    .privacy-dot { width: .45rem; height: .45rem; border-radius: 50%; background: #4c866a; }
    .hero { color: #17201d; font-family: Georgia, 'Times New Roman', serif;
            font-size: clamp(3.2rem, 7vw, 6rem); line-height: .92; letter-spacing: -.052em;
            margin: 1.1rem 0 1.25rem; max-width: 920px; }
    .lede { color: #56605b; font-size: 1.1rem; line-height: 1.7; max-width: 710px; }
    .process-row { display: flex; flex-wrap: wrap; gap: .65rem; margin: 1.7rem 0 .3rem; }
    .process-step { color: #3f4a45; background: #ebe6da; border-radius: 999px;
                    padding: .48rem .78rem; font-size: .78rem; font-weight: 700; }
    .process-step b { color: #a44833; margin-right: .25rem; }
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(255, 253, 248, .72);
        border-color: #d8d1c3 !important;
        border-radius: 18px !important;
        box-shadow: 0 14px 36px rgba(41, 47, 43, .055);
    }
    [data-testid="stFileUploaderDropzone"] {
        background: #fffdf8 !important;
        border: 1.5px dashed #afa897 !important;
        border-radius: 13px !important;
        min-height: 150px;
    }
    [data-testid="stFileUploaderDropzone"] * { color: #25302c !important; }
    [data-testid="stFileUploaderDropzone"] button {
        background: #ece6da !important; border: 1px solid #c9c1b1 !important;
    }
    .feature-card { background: #1d2a25; color: #f7f4ec; border-radius: 18px;
                    padding: 1.5rem 1.55rem; }
    .feature-card h3 { color: #f7f4ec; margin: 0 0 .45rem; font-size: 1.12rem; }
    .feature-card > p { color: #c7d0cb; line-height: 1.55; margin: 0 0 1.15rem; }
    .feature-item { display: flex; gap: .75rem; padding: .68rem 0;
                    border-top: 1px solid #35443e; color: #edf0ed; font-size: .9rem; }
    .feature-num { color: #df8a71; font-weight: 800; }
    .truth-note { background: #e7eee9; border: 1px solid #c5d7cc; color: #264537;
                  border-radius: 12px; padding: .8rem 1rem; margin-top: 1rem;
                  font-size: .85rem; line-height: 1.45; }
    .pre-expander-gap { height: 1.25rem; }
    .metric { background: #fffdf8; border: 1px solid #d8d1c3; border-radius: 14px;
              padding: 1rem 1.1rem; min-height: 98px; color: #17201d;
              box-shadow: 0 8px 24px rgba(41, 47, 43, .04); }
    .metric-label { color: #6b726e; font-size: .7rem; font-weight: 750;
                    text-transform: uppercase; letter-spacing: .12em; }
    .metric-value { color: #17201d; font-family: Georgia, serif; font-size: 1.5rem;
                    line-height: 1.2; margin-top: .4rem; }
    .contact-card { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: .8rem;
                    background: #fffdf8; border: 1px solid #d8d1c3; border-radius: 14px;
                    padding: 1rem 1.1rem; color: #17201d; }
    .contact-item { min-width: 0; }
    .contact-label { color: #727873; font-size: .68rem; text-transform: uppercase;
                     letter-spacing: .1em; font-weight: 750; }
    .contact-value { color: #17201d; margin-top: .18rem; overflow-wrap: anywhere; }
    .section-card { background: #fffdf8; border: 1px solid #d8d1c3; border-radius: 14px;
                    padding: 1.2rem 1.35rem; margin-bottom: .8rem; color: #17201d; }
    .section-card li { color: #343d39; margin-bottom: .28rem; }
    .role { color: #17201d; font-size: 1.05rem; font-weight: 750; }
    .muted { color: #68706c; }
    [data-testid="stAlert"] { color: #17201d !important; border-radius: 12px; }
    [data-testid="stAlert"] * { color: inherit !important; }
    [data-baseweb="tab-list"] { gap: .45rem; }
    [data-baseweb="tab"] { color: #5f6864 !important; font-weight: 650; }
    [aria-selected="true"][data-baseweb="tab"] { color: #9f422e !important; }
    [data-testid="stExpander"] { background: rgba(255,253,248,.58); border-color: #d8d1c3; }
    div.stButton > button[kind="primary"] {
        background: #b6533b !important; border: 1px solid #b6533b !important;
        color: #fff !important; min-height: 3.15rem; border-radius: 10px;
        font-weight: 750; box-shadow: 0 8px 20px rgba(182, 83, 59, .18);
    }
    div.stButton > button[kind="primary"]:hover {
        background: #98422f !important; border-color: #98422f !important;
    }
    [data-testid="stDownloadButton"] button {
        background: #fffdf8 !important; color: #26312d !important;
        border-color: #c9c2b4 !important; min-height: 2.85rem;
    }
    code { color: #17201d; }
    @media (max-width: 700px) {
        .block-container { padding-top: 5.2rem !important; padding-left: 1rem;
                           padding-right: 1rem; }
        .brand-row { align-items: flex-start; flex-direction: column; }
        .hero { font-size: clamp(2.7rem, 15vw, 4.2rem); }
        .contact-card { grid-template-columns: 1fr; }
    }
    </style>
    <div class="brand-row">
      <div class="kicker">ATLAS / STRUCTURED RESUME INTELLIGENCE</div>
      <div class="privacy-pill"><span class="privacy-dot"></span>Session-only processing</div>
    </div>
    <div class="hero">From résumé to<br>reliable data.</div>
    <div class="lede">Upload a PDF, DOCX, or text résumé. Atlas extracts the document locally,
    then turns it into clean, reviewable candidate data with a strict schema.</div>
    <div class="process-row">
      <div class="process-step"><b>01</b> Upload</div>
      <div class="process-step"><b>02</b> Extract</div>
      <div class="process-step"><b>03</b> Structure</div>
      <div class="process-step"><b>04</b> Review & export</div>
    </div>
    """,
    unsafe_allow_html=True,
)

MAX_RUNS_PER_SESSION = 15


def streamlit_secrets() -> dict[str, object]:
    """Read optional Streamlit secrets without failing when no secrets file exists."""
    try:
        return dict(st.secrets)
    except (FileNotFoundError, RuntimeError):
        return {}


def activate_preset_model() -> None:
    """Make the dropdown selection authoritative after the user changes it."""
    st.session_state.active_model_source = "preset"


def activate_custom_model() -> None:
    """Make a non-empty custom ID authoritative as soon as the user edits it."""
    custom_value = st.session_state.get("custom_model_id", "").strip()
    if custom_value:
        st.session_state.active_model_source = "custom"
        st.session_state.model_preset = None
    else:
        st.session_state.active_model_source = "preset"
        st.session_state.model_preset = MODEL_PRESETS[0]


def friendly_error(error: Exception) -> str:
    """Return a useful message without exposing provider request details."""
    if isinstance(error, AuthenticationError):
        return "OpenAI rejected the API key. Check it and try again."
    if isinstance(error, (PermissionDeniedError, NotFoundError)):
        return "That model is unavailable to this API key. Choose another model."
    if isinstance(error, RateLimitError):
        return "The OpenAI account reached a rate, usage, or billing limit."
    if isinstance(error, BadRequestError):
        return "The model rejected the document. Try a shorter resume or another model."
    if isinstance(error, (APITimeoutError, APIConnectionError)):
        return "The model connection timed out. Please retry in a moment."
    if isinstance(error, OutputParserException):
        return "The model returned invalid structured data. Parse the resume again."
    return "The resume could not be parsed. Check the app logs and try again."


def safe(value: str | None, fallback: str = "Not provided") -> str:
    """Escape model output before inserting it into an HTML card."""
    return escape(value.strip()) if value and value.strip() else fallback


if "parsed_resume" not in st.session_state:
    st.session_state.parsed_resume = None
if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""
if "runs" not in st.session_state:
    st.session_state.runs = 0

with st.sidebar:
    st.header("Atlas settings")
    st.caption("Configure the model, then upload a résumé in the workspace.")
    secrets = streamlit_secrets()
    server_key = configured_api_key(os.environ, secrets)

    if server_key:
        st.markdown(
            f'<div class="key-status"><span class="key-status-dot"></span><div>'
            f'<div class="key-status-title">Configured API key is ready</div>'
            f'<div class="key-status-copy">Loaded from {server_key.source}. The key is not sent '
            f'to the browser.</div></div></div>',
            unsafe_allow_html=True,
        )
        key_choice = st.radio(
            "API key source",
            ["Use configured key", "Use my own key"],
            help="A manually entered key is held only in this Streamlit session.",
        )
    else:
        st.markdown(
            '<div class="key-status key-missing"><span class="key-status-dot"></span><div>'
            '<div class="key-status-title">No configured API key</div>'
            '<div class="key-status-copy">Enter a key below for this session.</div>'
            '</div></div>',
            unsafe_allow_html=True,
        )
        key_choice = "Use my own key"

    if key_choice == "Use my own key":
        manual_api_key = st.text_input(
            "Your OpenAI API key",
            type="password",
            placeholder="sk-…",
            help="Used in memory for this session and never written by the app.",
        )
        api_key = manual_api_key.strip()
    else:
        api_key = server_key.value if server_key else ""

    st.divider()
    st.markdown("**Model**")
    default_model = configured_model(os.environ, secrets)
    configured_is_preset = default_model in MODEL_PRESETS
    if "model_preset" not in st.session_state:
        st.session_state.model_preset = default_model if configured_is_preset else None
    if "custom_model_id" not in st.session_state:
        st.session_state.custom_model_id = "" if configured_is_preset else default_model
    if "active_model_source" not in st.session_state:
        st.session_state.active_model_source = "preset" if configured_is_preset else "custom"

    model_selection = st.selectbox(
        "Model preset",
        MODEL_PRESETS,
        key="model_preset",
        on_change=activate_preset_model,
        placeholder="Choose a preset to make it active",
        help="Changing this selection immediately makes the selected preset active.",
    )
    custom_model = st.text_input(
        "Custom model ID",
        key="custom_model_id",
        placeholder="Example: gpt-4.1-mini-2025-04-14",
        max_chars=120,
        on_change=activate_custom_model,
        help=(
            "Type or edit any compatible model ID to activate it. Changing the preset dropdown "
            "switches back to the selected preset."
        ),
    )
    try:
        model = resolve_model(
            model_selection,
            custom_model,
            st.session_state.active_model_source,
        )
        model_error = None
        source_label = "custom" if st.session_state.active_model_source == "custom" else "preset"
        st.caption(f"Active model ({source_label}): `{model}`")
    except ValueError as error:
        model = MODEL_PRESETS[0]
        model_error = error
        st.caption("Enter a valid custom model ID before parsing.")

    st.divider()
    st.markdown("**Privacy boundary**")
    st.caption(
        "Document text is extracted in this app, then sent to OpenAI for structuring. "
        "Avoid uploading resumes unless you have permission to process them."
    )
    st.caption(f"Session limit: {MAX_RUNS_PER_SESSION} parses.")

st.divider()
left, right = st.columns([1.12, 0.88], gap="large")

with left, st.container(border=True):
    st.markdown("### Upload a résumé")
    st.caption("Select one document to extract and structure.")
    uploaded_file = st.file_uploader(
        "PDF, DOCX, or UTF-8 TXT",
        type=["pdf", "docx", "txt"],
        help="Maximum 8 MB. Scanned PDFs need OCR before upload.",
    )
    if uploaded_file:
        st.caption(f"✓ {uploaded_file.name} · {uploaded_file.size / 1024:.0f} KB")

    parse_clicked = st.button(
        "Parse résumé  →",
        type="primary",
        use_container_width=True,
        disabled=st.session_state.runs >= MAX_RUNS_PER_SESSION,
    )

with right:
    st.markdown(
        """
        <div class="feature-card">
          <h3>One document. Nine structured sections.</h3>
          <p>A review-ready profile that stays faithful to the source résumé.</p>
          <div class="feature-item"><span class="feature-num">01</span>
          Contact & professional summary</div>
          <div class="feature-item"><span class="feature-num">02</span>
          Skills & work experience</div>
          <div class="feature-item"><span class="feature-num">03</span>
          Education & certifications</div>
          <div class="feature-item"><span class="feature-num">04</span>
          Projects, languages & parsing notes</div>
          <div class="truth-note"><strong>No gap-filling.</strong> Missing information remains empty
          or null, and ambiguous content is flagged for review.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

if parse_clicked:
    if uploaded_file is None:
        st.error("Upload a PDF, DOCX, or TXT resume first.")
    else:
        try:
            with st.status("Reading the résumé…", expanded=True) as status:
                resume_text = extract_resume_text(uploaded_file.name, uploaded_file.getvalue())
                st.session_state.resume_text = resume_text
                st.write(f"Extracted {len(resume_text):,} readable characters")
                st.write("Normalizing experience, education, and skills")
                if model_error:
                    raise model_error
                chain = build_chain(api_key, model)
                st.session_state.parsed_resume = parse_resume(chain, resume_text)
                st.session_state.runs += 1
                status.update(label="Résumé parsed", state="complete", expanded=False)
        except ExtractionError as error:
            st.error(str(error))
        except OutputParserException as error:
            logger.warning("The model returned malformed structured output: %s", error)
            st.error(friendly_error(error))
        except ValueError as error:
            st.error(str(error))
        except Exception as error:
            logger.exception("Resume parsing failed")
            st.error(friendly_error(error))

if st.session_state.parsed_resume:
    resume = st.session_state.parsed_resume
    st.divider()
    st.markdown("## Candidate profile")

    name_col, skills_col, roles_col = st.columns(3)
    with name_col:
        st.markdown(
            f'<div class="metric"><div class="metric-label">Candidate</div>'
            f'<div class="metric-value">{safe(resume.contact.full_name)}</div></div>',
            unsafe_allow_html=True,
        )
    with skills_col:
        st.markdown(
            f'<div class="metric"><div class="metric-label">Skills found</div>'
            f'<div class="metric-value">{len(resume.skills)}</div></div>',
            unsafe_allow_html=True,
        )
    with roles_col:
        st.markdown(
            f'<div class="metric"><div class="metric-label">Roles found</div>'
            f'<div class="metric-value">{len(resume.work_experience)}</div></div>',
            unsafe_allow_html=True,
        )

    overview, raw_data = st.tabs(["Review", "Structured JSON"])
    with overview:
        st.markdown("### Contact")
        contact = resume.contact
        st.markdown(
            f'<div class="contact-card">'
            f'<div class="contact-item"><div class="contact-label">Email</div>'
            f'<div class="contact-value">{safe(contact.email)}</div></div>'
            f'<div class="contact-item"><div class="contact-label">Phone</div>'
            f'<div class="contact-value">{safe(contact.phone)}</div></div>'
            f'<div class="contact-item"><div class="contact-label">Location</div>'
            f'<div class="contact-value">{safe(contact.location)}</div></div>'
            f'<div class="contact-item"><div class="contact-label">LinkedIn</div>'
            f'<div class="contact-value">{safe(contact.linkedin_url)}</div></div></div>',
            unsafe_allow_html=True,
        )

        if resume.professional_summary:
            st.markdown("### Summary")
            st.write(resume.professional_summary)

        st.markdown("### Skills")
        st.write(" · ".join(resume.skills) if resume.skills else "No explicit skills found.")

        st.markdown("### Experience")
        if not resume.work_experience:
            st.caption("No work experience found.")
        for role in resume.work_experience:
            dates = " — ".join(value for value in [role.start_date, role.end_date] if value)
            highlights = "".join(f"<li>{escape(item)}</li>" for item in role.highlights)
            st.markdown(
                f'<div class="section-card"><div class="role">{safe(role.title)}</div>'
                f'<div class="muted">{safe(role.company)} · {safe(role.location, "")}</div>'
                f'<div class="muted">{safe(dates, "Dates not provided")}</div>'
                f'<ul>{highlights}</ul></div>',
                unsafe_allow_html=True,
            )

        st.markdown("### Education")
        if not resume.education:
            st.caption("No education found.")
        for item in resume.education:
            degree = " in ".join(value for value in [item.degree, item.field_of_study] if value)
            st.markdown(
                f'<div class="section-card"><div class="role">{safe(degree)}</div>'
                f'<div class="muted">{safe(item.institution)} · '
                f'{safe(item.graduation_date, "Date not provided")}</div></div>',
                unsafe_allow_html=True,
            )

        if resume.parsing_notes:
            with st.expander("Parsing notes"):
                for note in resume.parsing_notes:
                    st.write(f"• {note}")

    with raw_data:
        json_data = resume.model_dump_json(indent=2)
        st.code(json_data, language="json")

    download_col, source_col = st.columns(2)
    with download_col:
        st.download_button(
            "Download JSON",
            data=resume.model_dump_json(indent=2),
            file_name="parsed-resume.json",
            mime="application/json",
            use_container_width=True,
        )
    with source_col:
        st.download_button(
            "Download extracted text",
            data=st.session_state.resume_text,
            file_name="extracted-resume.txt",
            mime="text/plain",
            use_container_width=True,
        )

st.markdown('<div class="pre-expander-gap"></div>', unsafe_allow_html=True)

with st.expander("How parsing works"):
    st.markdown(
        "PDF, DOCX, and TXT content is extracted locally. LangChain sends the readable text "
        "through a guarded prompt. OpenAI's structured-output mode constrains the response to a "
        "nested Pydantic resume schema before anything is displayed."
    )

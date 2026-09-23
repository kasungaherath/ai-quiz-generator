import base64
from pathlib import Path

import streamlit as st

from utils.pdf_reader import extract_text_from_pdf
from utils.quiz_generator import generate_quiz
from utils.quiz_utils import calculate_score


BASE_DIR = Path(__file__).resolve().parent
LOGO_PATH = BASE_DIR / "assets" / "quizora_logo.png"

st.set_page_config(
    page_title="Quizora AI",
    layout="wide",
    initial_sidebar_state="collapsed"
)


def image_to_data_uri(path):
    if not path.exists():
        return None

    encoded = base64.b64encode(
        path.read_bytes()
    ).decode("utf-8")

    return f"data:image/png;base64,{encoded}"


def reset_quiz_state():
    removable = {
        "quiz",
        "quiz_submitted",
        "results",
        "score",
        "quiz_config"
    }

    for key in list(st.session_state.keys()):
        if key.startswith("question_") or key in removable:
            del st.session_state[key]


logo_uri = image_to_data_uri(LOGO_PATH)


st.markdown(
    """
    <style>

    @keyframes gradientMove {
        0% {
            background-position: 0% 50%;
        }

        50% {
            background-position: 100% 50%;
        }

        100% {
            background-position: 0% 50%;
        }
    }

    @keyframes glowPulse {
        0% {
            opacity: 0.20;
            transform: translateX(-50%) scale(0.96);
        }

        50% {
            opacity: 0.45;
            transform: translateX(-50%) scale(1.04);
        }

        100% {
            opacity: 0.20;
            transform: translateX(-50%) scale(0.96);
        }
    }

    @keyframes buttonGlow {
        0% {
            box-shadow:
                0 12px 30px rgba(99, 102, 241, 0.12),
                0 0 0 rgba(56, 189, 248, 0);
        }

        50% {
            box-shadow:
                0 15px 38px rgba(124, 58, 237, 0.24),
                0 0 25px rgba(56, 189, 248, 0.12);
        }

        100% {
            box-shadow:
                0 12px 30px rgba(99, 102, 241, 0.12),
                0 0 0 rgba(56, 189, 248, 0);
        }
    }

    html {
        scroll-behavior: smooth;
    }

    .stApp {
        background:
            radial-gradient(
                circle at 8% 0%,
                rgba(124, 58, 237, 0.09),
                transparent 27%
            ),
            radial-gradient(
                circle at 95% 10%,
                rgba(14, 165, 233, 0.06),
                transparent 25%
            ),
            radial-gradient(
                circle at 45% 100%,
                rgba(20, 184, 166, 0.035),
                transparent 30%
            ),
            #080a0f;
    }

    .block-container {
        max-width: 1120px;
        padding-top: 1.3rem;
        padding-bottom: 4rem;
    }

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    header[data-testid="stHeader"] {
        background: transparent;
    }

    h1 {
        font-weight: 800 !important;
        letter-spacing: -0.05em !important;
        line-height: 1.08 !important;
    }

    h2 {
        font-weight: 760 !important;
        letter-spacing: -0.035em !important;
    }

    h3 {
        font-weight: 700 !important;
        letter-spacing: -0.02em !important;
    }

    .quizora-brand {
        display: flex;
        align-items: center;
        gap: 13px;
        margin-bottom: 1.15rem;
    }

    .quizora-brand-logo {
        width: 44px;
        height: 44px;
        object-fit: cover;
        border-radius: 11px;
        flex-shrink: 0;
    }

    .quizora-brand-name {
        color: #f8fafc;
        font-size: 1.7rem;
        font-weight: 800;
        letter-spacing: -0.04em;
        line-height: 1.05;
    }

    .quizora-brand-tagline {
        color: #747c8a;
        font-size: 0.84rem;
        margin-top: 5px;
        line-height: 1.2;
    }

    .quizora-divider {
        width: 100%;
        height: 1px;
        background: rgba(255, 255, 255, 0.07);
        margin-bottom: 3.4rem;
    }

    .hero-wrap {
        position: relative;
        isolation: isolate;
        max-width: 900px;
        margin: 0 auto 4rem auto;
    }

    .hero-wrap::before {
        content: "";
        position: absolute;
        width: 650px;
        height: 260px;
        top: -100px;
        left: 50%;

        background:
            radial-gradient(
                circle,
                rgba(124, 58, 237, 0.23),
                rgba(59, 130, 246, 0.11),
                rgba(45, 212, 191, 0.045),
                transparent 70%
            );

        filter: blur(60px);
        pointer-events: none;
        z-index: -1;

        animation: glowPulse 7s ease-in-out infinite;
    }

    .hero-title {
        max-width: 850px;
        margin-bottom: 1.3rem;

        font-size: clamp(2.8rem, 5vw, 4.4rem);
        font-weight: 800;
        letter-spacing: -0.058em;
        line-height: 1.04;

        background:
            linear-gradient(
                90deg,
                #ffffff,
                #ddd6fe,
                #a78bfa,
                #818cf8,
                #38bdf8,
                #5eead4,
                #ffffff
            );

        background-size: 300% 300%;

        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;

        background-clip: text;
        color: transparent;

        animation: gradientMove 8s ease infinite;
    }

    .hero-copy {
        max-width: 780px;
        color: #a1a8b5;
        font-size: 1.06rem;
        line-height: 1.8;
        margin-bottom: 1.25rem;
    }

    .hero-meta {
        color: #69717f;
        font-size: 0.86rem;
        font-weight: 500;
    }

    .workspace-badge,
    .analytics-badge,
    .results-badge {
        display: inline-block;

        padding: 0.42rem 0.78rem;
        margin-bottom: 0.8rem;

        border-radius: 999px;

        background:
            linear-gradient(
                90deg,
                rgba(124, 58, 237, 0.18),
                rgba(14, 165, 233, 0.12)
            );

        border:
            1px solid rgba(129, 140, 248, 0.16);

        color: #c7d2fe;

        font-size: 0.7rem;
        font-weight: 700;

        letter-spacing: 0.12em;
        text-transform: uppercase;
    }

    .workspace-title {
        color: #f8fafc;

        font-size: 2.75rem;
        font-weight: 800;

        letter-spacing: -0.05em;
        line-height: 1.06;

        margin-bottom: 0.55rem;
    }

    .workspace-copy {
        max-width: 750px;

        color: #8f97a6;

        font-size: 1rem;
        line-height: 1.75;

        margin-bottom: 1.7rem;
    }

    .builder-header {
        position: relative;
        z-index: 1;
        margin-bottom: 1.35rem;
    }

    .builder-step {
        display: inline-flex;
        align-items: center;

        padding: 0.4rem 0.72rem;

        margin-bottom: 0.8rem;

        border-radius: 999px;

        color: #c7d2fe;

        background:
            rgba(99, 102, 241, 0.08);

        border:
            1px solid rgba(129, 140, 248, 0.16);

        font-size: 0.69rem;
        font-weight: 700;

        letter-spacing: 0.11em;
        text-transform: uppercase;
    }

    .builder-heading {
        color: #f8fafc;

        font-size: 1.65rem;
        font-weight: 760;

        letter-spacing: -0.035em;
        line-height: 1.08;

        margin-bottom: 0.4rem;
    }

    .builder-description {
        max-width: 700px;

        color: #828b9a;

        font-size: 0.94rem;
        line-height: 1.65;
    }

    .builder-divider {
        height: 1px;

        margin: 1.8rem 0;

        background:
            linear-gradient(
                90deg,
                rgba(255, 255, 255, 0.08),
                rgba(129, 140, 248, 0.10),
                rgba(255, 255, 255, 0.04)
            );
    }

    .configuration-grid {
        display: grid;

        grid-template-columns:
            repeat(3, minmax(0, 1fr));

        gap: 1rem;

        margin-top: 1.1rem;
        margin-bottom: 1.2rem;
    }

    .configuration-card {
        padding: 1rem;

        border-radius: 15px;

        background:
            linear-gradient(
                180deg,
                rgba(255, 255, 255, 0.028),
                rgba(255, 255, 255, 0.012)
            );

        border:
            1px solid rgba(255, 255, 255, 0.065);
    }

    .configuration-label {
        color: #747d8d;

        font-size: 0.68rem;
        font-weight: 700;

        letter-spacing: 0.1em;
        text-transform: uppercase;

        margin-bottom: 0.45rem;
    }

    .configuration-value {
        color: #f1f5f9;
        font-size: 1rem;
        font-weight: 650;
    }

    .input-status {
        display: flex;

        justify-content: space-between;
        align-items: center;

        gap: 1rem;

        margin-top: 0.8rem;

        padding: 0.7rem 0.85rem;

        border-radius: 11px;

        background:
            rgba(255, 255, 255, 0.02);

        border:
            1px solid rgba(255, 255, 255, 0.055);

        color: #818998;

        font-size: 0.79rem;
    }

    .quiz-ready-panel {
        margin-top: 1rem;

        padding: 1rem 1.1rem;

        display: flex;
        align-items: center;
        justify-content: space-between;

        gap: 1rem;

        border-radius: 15px;

        background:
            linear-gradient(
                90deg,
                rgba(34, 197, 94, 0.08),
                rgba(99, 102, 241, 0.07)
            );

        border:
            1px solid rgba(74, 222, 128, 0.14);
    }

    .quiz-ready-title {
        color: #f8fafc;

        font-size: 0.95rem;
        font-weight: 700;

        margin-bottom: 0.2rem;
    }

    .quiz-ready-text {
        color: #818a99;

        font-size: 0.8rem;
    }

    .go-to-quiz-button {
        display: inline-flex;

        align-items: center;
        justify-content: center;

        min-width: 140px;

        padding: 0.72rem 1.15rem;

        border-radius: 11px;

        text-decoration: none !important;

        color: #ffffff !important;

        font-size: 0.86rem;
        font-weight: 700;

        background:
            linear-gradient(
                100deg,
                #7c3aed,
                #6366f1,
                #0ea5e9
            );

        background-size: 200% 200%;

        animation: gradientMove 7s ease infinite;

        box-shadow:
            0 10px 28px rgba(99, 102, 241, 0.18);

        transition:
            transform 0.15s ease,
            box-shadow 0.15s ease;
    }

    .go-to-quiz-button:hover {
        transform: translateY(-1px);

        box-shadow:
            0 14px 34px rgba(99, 102, 241, 0.28);

        color: #ffffff !important;

        text-decoration: none !important;
    }

    .quiz-anchor {
        scroll-margin-top: 80px;
    }

    .sub-label {
        color: #8b8ff8;

        font-size: 0.7rem;
        font-weight: 700;

        letter-spacing: 0.12em;
        text-transform: uppercase;

        margin-bottom: 0.4rem;
    }

    .sub-title {
        color: #f1f5f9;

        font-size: 1.25rem;
        font-weight: 720;

        letter-spacing: -0.025em;

        margin-bottom: 0.3rem;
    }

    .sub-copy {
        color: #828b9b;

        line-height: 1.65;

        margin-bottom: 1.1rem;
    }

    .analytics-board,
    .results-board {
        position: relative;
        overflow: hidden;

        padding: 1.5rem;

        margin-bottom: 1.4rem;

        border-radius: 22px;

        background:
            linear-gradient(
                145deg,
                rgba(18, 21, 31, 0.95),
                rgba(9, 12, 18, 0.96)
            );

        border:
            1px solid rgba(255, 255, 255, 0.075);

        box-shadow:
            0 25px 70px rgba(0, 0, 0, 0.24);
    }

    .analytics-board::before,
    .results-board::before {
        content: "";

        position: absolute;

        width: 320px;
        height: 320px;

        top: -180px;
        right: -90px;

        border-radius: 50%;

        background:
            radial-gradient(
                circle,
                rgba(99, 102, 241, 0.18),
                transparent 70%
            );

        pointer-events: none;
    }

    .analytics-top,
    .results-top {
        position: relative;

        z-index: 1;

        display: flex;

        justify-content: space-between;
        align-items: flex-start;

        gap: 1.2rem;

        flex-wrap: wrap;

        margin-bottom: 1.35rem;
    }

    .analytics-title,
    .results-title {
        color: #f8fafc;

        font-size: 2.45rem;
        font-weight: 800;

        letter-spacing: -0.05em;
        line-height: 1.05;

        margin-bottom: 0.45rem;
    }

    .analytics-subtitle,
    .results-subtitle {
        color: #8f97a6;

        font-size: 0.97rem;
        line-height: 1.65;

        max-width: 690px;
    }

    .analytics-chip-row,
    .results-chip-row {
        display: flex;

        flex-wrap: wrap;

        gap: 0.55rem;
    }

    .analytics-chip,
    .results-chip {
        padding: 0.48rem 0.75rem;

        border-radius: 999px;

        background:
            rgba(255, 255, 255, 0.025);

        border:
            1px solid rgba(255, 255, 255, 0.07);

        color: #a1a8b5;

        font-size: 0.77rem;
        font-weight: 500;
    }

    .analytics-grid,
    .results-grid {
        position: relative;

        z-index: 1;

        display: grid;

        grid-template-columns:
            repeat(4, minmax(0, 1fr));

        gap: 0.9rem;
    }

    .analytics-card,
    .results-card {
        padding: 1.15rem;

        min-height: 138px;

        border-radius: 17px;

        background:
            linear-gradient(
                180deg,
                rgba(255, 255, 255, 0.035),
                rgba(255, 255, 255, 0.013)
            );

        border:
            1px solid rgba(255, 255, 255, 0.07);
    }

    .analytics-label,
    .results-label {
        color: #808999;

        font-size: 0.7rem;
        font-weight: 700;

        text-transform: uppercase;
        letter-spacing: 0.1em;

        margin-bottom: 0.8rem;
    }

    .analytics-value,
    .results-value {
        color: #f8fafc;

        font-size: 2.2rem;
        font-weight: 760;

        letter-spacing: -0.045em;

        line-height: 1.05;

        margin-bottom: 0.45rem;
    }

    .analytics-value-small {
        font-size: 1.5rem;
    }

    .analytics-gradient-value,
    .results-gradient-value {
        background:
            linear-gradient(
                90deg,
                #c4b5fd,
                #818cf8,
                #38bdf8,
                #5eead4
            );

        background-size: 200% 200%;

        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;

        background-clip: text;
        color: transparent;

        animation:
            gradientMove 7s ease infinite;
    }

    .analytics-note,
    .results-note {
        color: #6f7888;

        font-size: 0.82rem;

        line-height: 1.4;
    }

    .analytics-progress-top,
    .results-progress-top {
        display: flex;

        justify-content: space-between;

        color: #808999;

        font-size: 0.82rem;

        margin-top: 1.2rem;
        margin-bottom: 0.55rem;
    }

    .results-status {
        position: relative;

        z-index: 1;

        margin-bottom: 1rem;

        padding: 1rem 1.1rem;

        border-radius: 15px;

        font-size: 0.92rem;
        font-weight: 600;

        line-height: 1.5;
    }

    .results-status.good {
        color: #dcfce7;

        background:
            linear-gradient(
                90deg,
                rgba(34, 197, 94, 0.17),
                rgba(16, 185, 129, 0.08)
            );

        border:
            1px solid rgba(34, 197, 94, 0.20);
    }

    .results-status.medium {
        color: #dbeafe;

        background:
            linear-gradient(
                90deg,
                rgba(59, 130, 246, 0.17),
                rgba(14, 165, 233, 0.08)
            );

        border:
            1px solid rgba(59, 130, 246, 0.20);
    }

    .results-status.low {
        color: #fef3c7;

        background:
            linear-gradient(
                90deg,
                rgba(245, 158, 11, 0.18),
                rgba(234, 179, 8, 0.08)
            );

        border:
            1px solid rgba(245, 158, 11, 0.20);
    }

    [data-testid="stVerticalBlockBorderWrapper"] {
        position: relative;

        background:
            linear-gradient(
                180deg,
                rgba(18, 21, 30, 0.88),
                rgba(10, 13, 19, 0.94)
            );

        border:
            1px solid rgba(255, 255, 255, 0.075)
            !important;

        border-radius: 20px !important;

        box-shadow:
            0 22px 65px rgba(0, 0, 0, 0.22);
    }

    textarea {
        min-height: 250px !important;

        background:
            linear-gradient(
                180deg,
                #0c0f16,
                #090c12
            ) !important;

        border-radius: 14px !important;

        border-color:
            rgba(255, 255, 255, 0.09)
            !important;

        line-height: 1.65 !important;
    }

    textarea:focus {
        border-color:
            rgba(124, 101, 255, 0.68)
            !important;

        box-shadow:
            0 0 0 1px rgba(124, 101, 255, 0.20),
            0 0 30px rgba(124, 58, 237, 0.07)
            !important;
    }

    [data-baseweb="select"] > div {
        min-height: 50px;

        background: #0b0e14;

        border-radius: 11px;
    }

    [data-testid="stFileUploaderDropzone"] {
        min-height: 150px;

        background:
            linear-gradient(
                180deg,
                #0c0f16,
                #090c12
            );

        border:
            1px dashed rgba(129, 140, 248, 0.22);

        border-radius: 15px;
    }

    .stRadio [role="radiogroup"] {
        gap: 0.65rem;
    }

    .stRadio [role="radiogroup"] label {
        padding: 0.55rem 0.85rem;

        background:
            rgba(255, 255, 255, 0.025);

        border:
            1px solid rgba(255, 255, 255, 0.07);

        border-radius: 12px;
    }

    .stRadio [role="radiogroup"] label:hover {
        background:
            rgba(124, 58, 237, 0.06);

        border-color:
            rgba(124, 58, 237, 0.30);
    }

    .stButton > button {
        min-height: 50px;

        border-radius: 12px;

        font-weight: 650;

        transition:
            transform 0.15s ease,
            box-shadow 0.15s ease;
    }

    .stButton > button[kind="primary"] {
        border: none;

        color: white;

        background:
            linear-gradient(
                100deg,
                #7c3aed,
                #6366f1,
                #0ea5e9
            );

        background-size: 200% 200%;

        animation:
            gradientMove 7s ease infinite,
            buttonGlow 4s ease-in-out infinite;
    }

    .stButton > button:hover {
        transform: translateY(-1px);
    }

    [data-testid="stProgress"] > div > div {
        border-radius: 999px;
    }

    hr {
        border-color:
            rgba(255, 255, 255, 0.07);
    }

    @media (prefers-reduced-motion: reduce) {

        .hero-title,
        .hero-wrap::before,
        .analytics-gradient-value,
        .results-gradient-value,
        .stButton > button[kind="primary"],
        .go-to-quiz-button {
            animation: none !important;
        }
    }

    @media (max-width: 900px) {

        .analytics-grid,
        .results-grid {
            grid-template-columns:
                repeat(2, minmax(0, 1fr));
        }
    }

    @media (max-width: 700px) {

        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }

        .quizora-brand-logo {
            width: 39px;
            height: 39px;
        }

        .quizora-brand-name {
            font-size: 1.45rem;
        }

        .quizora-brand-tagline {
            font-size: 0.76rem;
        }

        .quizora-divider {
            margin-bottom: 2.5rem;
        }

        .hero-title {
            font-size: 2.65rem;
        }

        .hero-wrap {
            margin-bottom: 3rem;
        }

        .hero-wrap::before {
            width: 330px;
        }

        .workspace-title,
        .analytics-title,
        .results-title {
            font-size: 2rem;
        }

        .configuration-grid {
            grid-template-columns: 1fr;
        }

        .quiz-ready-panel {
            flex-direction: column;
            align-items: stretch;
        }

        .go-to-quiz-button {
            width: 100%;
        }
    }

    @media (max-width: 560px) {

        .analytics-grid,
        .results-grid {
            grid-template-columns: 1fr;
        }
    }

    </style>
    """,
    unsafe_allow_html=True
)


try:

    api_key = st.secrets["GEMINI_API_KEY"]

except KeyError:

    st.error(
        "Gemini API key was not found. "
        "Add GEMINI_API_KEY to .streamlit/secrets.toml."
    )

    st.stop()


if logo_uri:

    brand_html = (
        '<div class="quizora-brand">'
        f'<img src="{logo_uri}" class="quizora-brand-logo">'
        '<div>'
        '<div class="quizora-brand-name">Quizora AI</div>'
        '<div class="quizora-brand-tagline">'
        'AI-powered study quiz generator'
        '</div>'
        '</div>'
        '</div>'
        '<div class="quizora-divider"></div>'
    )

else:

    brand_html = (
        '<div class="quizora-brand">'
        '<div>'
        '<div class="quizora-brand-name">Quizora AI</div>'
        '<div class="quizora-brand-tagline">'
        'AI-powered study quiz generator'
        '</div>'
        '</div>'
        '</div>'
        '<div class="quizora-divider"></div>'
    )


st.markdown(
    brand_html,
    unsafe_allow_html=True
)


st.markdown(
    (
        '<div class="hero-wrap">'
        '<div class="hero-title">'
        'Turn your study material into smarter quizzes.'
        '</div>'
        '<div class="hero-copy">'
        'Upload a PDF or paste your notes to generate focused '
        'AI-powered quizzes. Customize the difficulty and question '
        'format, test your knowledge, and receive instant scoring '
        'with a complete answer review.'
        '</div>'
        '<div class="hero-meta">'
        'PDF and text input &nbsp;&nbsp;|&nbsp;&nbsp; '
        'Multiple quiz formats &nbsp;&nbsp;|&nbsp;&nbsp; '
        'Instant scoring'
        '</div>'
        '</div>'
    ),
    unsafe_allow_html=True
)


st.markdown(
    '<div class="workspace-badge">Quiz workspace</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="workspace-title">Create a quiz</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="workspace-copy">'
    'Add your study material and configure the quiz '
    'before generating questions.'
    '</div>',
    unsafe_allow_html=True
)


with st.container(
    border=True
):

    st.markdown(
        '<div class="builder-header">'
        '<div class="builder-step">Step 01 · Source</div>'
        '<div class="builder-heading">Add study material</div>'
        '<div class="builder-description">'
        'Paste your notes or upload a PDF to use as '
        'the source for your quiz.'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )


    source_mode = st.radio(
        "Source",
        [
            "Paste text",
            "Upload PDF"
        ],
        horizontal=True,
        label_visibility="collapsed"
    )


    study_text = ""
    source_name = ""


    if source_mode == "Paste text":

        study_text = st.text_area(
            "Study material",
            height=260,
            placeholder=(
                "Paste lecture notes, textbook content, "
                "revision material, or other study text..."
            )
        )

        source_name = "Pasted text"


    else:

        uploaded_file = st.file_uploader(
            "Upload PDF",
            type=["pdf"],
            help="Text-based PDFs work best."
        )


        if uploaded_file is not None:

            try:

                with st.spinner(
                    "Reading document..."
                ):

                    study_text = extract_text_from_pdf(
                        uploaded_file
                    )


                source_name = uploaded_file.name


                if study_text:

                    st.success(
                        "Document ready."
                    )


                    with st.expander(
                        "Preview extracted text"
                    ):

                        st.write(
                            study_text[:4000]
                        )


                else:

                    st.warning(
                        "No readable text was found."
                    )


            except Exception as error:

                st.error(
                    "The PDF could not be processed."
                )


                with st.expander(
                    "Technical details"
                ):

                    st.exception(
                        error
                    )


    if study_text.strip():

        word_count = len(
            study_text.split()
        )


        st.markdown(
            (
                '<div class="input-status">'
                f'<span>{source_name}</span>'
                f'<span>{word_count:,} words</span>'
                '</div>'
            ),
            unsafe_allow_html=True
        )


    st.markdown(
        '<div class="builder-divider"></div>',
        unsafe_allow_html=True
    )


    st.markdown(
        '<div class="builder-header">'
        '<div class="builder-step">'
        'Step 02 · Configuration'
        '</div>'
        '<div class="builder-heading">'
        'Customize your quiz'
        '</div>'
        '<div class="builder-description">'
        'Control the question format, difficulty, '
        'and assessment length.'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )


    settings_col1, settings_col2, settings_col3 = (
        st.columns(
            3,
            gap="medium"
        )
    )


    with settings_col1:

        question_type = st.selectbox(
            "Question type",
            [
                "Multiple Choice",
                "True/False",
                "Mixed"
            ]
        )


    with settings_col2:

        difficulty = st.selectbox(
            "Difficulty",
            [
                "Easy",
                "Medium",
                "Hard"
            ]
        )


    with settings_col3:

        num_questions = st.selectbox(
            "Number of questions",
            [
                5,
                10,
                15,
                20
            ],
            index=1
        )


    st.markdown(
        (
            '<div class="configuration-grid">'

            '<div class="configuration-card">'
            '<div class="configuration-label">'
            'Format'
            '</div>'
            f'<div class="configuration-value">'
            f'{question_type}'
            '</div>'
            '</div>'

            '<div class="configuration-card">'
            '<div class="configuration-label">'
            'Difficulty'
            '</div>'
            f'<div class="configuration-value">'
            f'{difficulty}'
            '</div>'
            '</div>'

            '<div class="configuration-card">'
            '<div class="configuration-label">'
            'Quiz Length'
            '</div>'
            f'<div class="configuration-value">'
            f'{num_questions} questions'
            '</div>'
            '</div>'

            '</div>'
        ),
        unsafe_allow_html=True
    )


    MAX_CHARACTERS = 30000

    prepared_text = study_text[
        :MAX_CHARACTERS
    ]


    if len(study_text) > MAX_CHARACTERS:

        st.info(
            "The first 30,000 characters will be used."
        )


    st.write("")


    generate_button = st.button(
        "Generate quiz",
        type="primary",
        use_container_width=True
    )


if generate_button:

    if not prepared_text.strip():

        st.warning(
            "Add study material before generating a quiz."
        )


    else:

        try:

            reset_quiz_state()


            with st.spinner(
                "Generating questions..."
            ):

                quiz = generate_quiz(
                    api_key=api_key,
                    study_text=prepared_text,
                    num_questions=num_questions,
                    question_type=question_type,
                    difficulty=difficulty
                )


            st.session_state.quiz = quiz


            st.session_state.quiz_config = {
                "question_type": question_type,
                "difficulty": difficulty,
                "num_questions": len(quiz)
            }


            st.markdown(
                (
                    '<div class="quiz-ready-panel">'

                    '<div>'

                    '<div class="quiz-ready-title">'
                    'Quiz generated successfully'
                    '</div>'

                    '<div class="quiz-ready-text">'
                    f'{len(quiz)} questions are ready to answer.'
                    '</div>'

                    '</div>'

                    '<a class="go-to-quiz-button" '
                    'href="#quiz-dashboard">'
                    'Go to quiz'
                    '</a>'

                    '</div>'
                ),
                unsafe_allow_html=True
            )


        except Exception as error:

            st.error(
                "Quiz generation failed. "
                "Please wait a moment and try again."
            )


            with st.expander(
                "Technical details"
            ):

                st.exception(
                    error
                )


if (
    "quiz" in st.session_state
    and not st.session_state.get(
        "quiz_submitted",
        False
    )
):

    quiz = st.session_state.quiz


    quiz_config = st.session_state.get(
        "quiz_config",
        {}
    )


    answered_count = sum(
        1
        for index in range(
            len(quiz)
        )
        if st.session_state.get(
            f"question_{index}"
        ) is not None
    )


    remaining_count = (
        len(quiz)
        - answered_count
    )


    completion_percent = (
        int(
            (
                answered_count
                / len(quiz)
            )
            * 100
        )
        if len(quiz) > 0
        else 0
    )


    st.markdown(
        '<div id="quiz-dashboard" '
        'class="quiz-anchor"></div>',
        unsafe_allow_html=True
    )


    st.write("")
    st.write("")


    analytics_html = (
        '<div class="analytics-board">'

        '<div class="analytics-top">'

        '<div>'

        '<div class="analytics-badge">'
        'Active Quiz'
        '</div>'

        '<div class="analytics-title">'
        'Quiz Dashboard'
        '</div>'

        '<div class="analytics-subtitle">'
        'Track your progress and complete each question '
        'before submitting your assessment.'
        '</div>'

        '</div>'

        '<div class="analytics-chip-row">'

        '<span class="analytics-chip">'
        'Live progress'
        '</span>'

        '<span class="analytics-chip">'
        'Instant scoring'
        '</span>'

        '<span class="analytics-chip">'
        'Answer review'
        '</span>'

        '</div>'

        '</div>'

        '<div class="analytics-grid">'

        '<div class="analytics-card">'
        '<div class="analytics-label">'
        'Questions'
        '</div>'
        f'<div class="analytics-value">'
        f'{len(quiz)}'
        '</div>'
        '<div class="analytics-note">'
        'Total assessment items'
        '</div>'
        '</div>'

        '<div class="analytics-card">'
        '<div class="analytics-label">'
        'Difficulty'
        '</div>'
        '<div class="analytics-value '
        'analytics-gradient-value">'
        f'{quiz_config.get("difficulty", difficulty)}'
        '</div>'
        '<div class="analytics-note">'
        'Challenge level'
        '</div>'
        '</div>'

        '<div class="analytics-card">'
        '<div class="analytics-label">'
        'Format'
        '</div>'
        '<div class="analytics-value '
        'analytics-value-small">'
        f'{quiz_config.get("question_type", question_type)}'
        '</div>'
        '<div class="analytics-note">'
        'Question structure'
        '</div>'
        '</div>'

        '<div class="analytics-card">'
        '<div class="analytics-label">'
        'Completion'
        '</div>'
        f'<div class="analytics-value">'
        f'{completion_percent}%'
        '</div>'
        '<div class="analytics-note">'
        f'{answered_count} answered · '
        f'{remaining_count} remaining'
        '</div>'
        '</div>'

        '</div>'

        '<div class="analytics-progress-top">'
        '<span>Quiz progress</span>'
        f'<span>{answered_count} / {len(quiz)}</span>'
        '</div>'

        '</div>'
    )


    st.markdown(
        analytics_html,
        unsafe_allow_html=True
    )


    st.progress(
        answered_count / len(quiz)
    )


    st.write("")


    user_answers = {}


    for index, question in enumerate(
        quiz
    ):

        with st.container(
            border=True
        ):

            st.caption(
                f"QUESTION {index + 1} OF {len(quiz)}"
            )


            st.markdown(
                f"### {question['question']}"
            )


            selected_answer = st.radio(
                "Choose an answer",
                question["options"],
                key=f"question_{index}",
                index=None,
                label_visibility="collapsed"
            )


            user_answers[
                index
            ] = selected_answer


    submit_button = st.button(
        "Submit quiz",
        type="primary",
        use_container_width=True
    )


    if submit_button:

        unanswered = [
            index + 1
            for index, answer
            in user_answers.items()
            if answer is None
        ]


        if unanswered:

            st.warning(
                "Answer all questions before submitting."
            )


            st.caption(
                "Unanswered questions: "
                + ", ".join(
                    map(
                        str,
                        unanswered
                    )
                )
            )


        else:

            score, results = calculate_score(
                quiz,
                user_answers
            )


            st.session_state.score = score

            st.session_state.results = results

            st.session_state.quiz_submitted = True


            st.rerun()


if st.session_state.get(
    "quiz_submitted",
    False
):

    score = st.session_state.score

    results = st.session_state.results

    quiz = st.session_state.quiz


    total = len(
        quiz
    )

    correct = score

    incorrect = total - score


    percentage = (
        score
        / total
    ) * 100


    if percentage >= 80:

        status_class = "good"

        performance_label = "Excellent"

        status_text = (
            "Strong performance. "
            "You demonstrated a very good "
            "understanding of this material."
        )


    elif percentage >= 60:

        status_class = "medium"

        performance_label = "Good"

        status_text = (
            "Good progress. Review the missed questions "
            "and strengthen the weaker areas."
        )


    else:

        status_class = "low"

        performance_label = "Needs Review"

        status_text = (
            "More revision is recommended. "
            "Review the answers below before trying again."
        )


    st.write("")
    st.write("")


    results_html = (
        '<div class="results-board">'

        '<div class="results-top">'

        '<div>'

        '<div class="results-badge">'
        'Performance'
        '</div>'

        '<div class="results-title">'
        'Results Dashboard'
        '</div>'

        '<div class="results-subtitle">'
        'Review your score, accuracy, '
        'and answer performance.'
        '</div>'

        '</div>'

        '<div class="results-chip-row">'

        f'<span class="results-chip">'
        f'{performance_label}'
        '</span>'

        '<span class="results-chip">'
        'Instant scoring'
        '</span>'

        '<span class="results-chip">'
        'Answer review'
        '</span>'

        '</div>'

        '</div>'

        f'<div class="results-status {status_class}">'
        f'{status_text}'
        '</div>'

        '<div class="results-grid">'

        '<div class="results-card">'
        '<div class="results-label">'
        'Score'
        '</div>'
        f'<div class="results-value">'
        f'{score}/{total}'
        '</div>'
        '<div class="results-note">'
        'Final quiz score'
        '</div>'
        '</div>'

        '<div class="results-card">'
        '<div class="results-label">'
        'Accuracy'
        '</div>'
        '<div class="results-value '
        'results-gradient-value">'
        f'{percentage:.0f}%'
        '</div>'
        '<div class="results-note">'
        'Overall answer accuracy'
        '</div>'
        '</div>'

        '<div class="results-card">'
        '<div class="results-label">'
        'Correct'
        '</div>'
        f'<div class="results-value">'
        f'{correct}'
        '</div>'
        '<div class="results-note">'
        'Correct responses'
        '</div>'
        '</div>'

        '<div class="results-card">'
        '<div class="results-label">'
        'Incorrect'
        '</div>'
        f'<div class="results-value">'
        f'{incorrect}'
        '</div>'
        '<div class="results-note">'
        'Questions to review'
        '</div>'
        '</div>'

        '</div>'

        '<div class="results-progress-top">'
        '<span>Overall performance</span>'
        f'<span>{percentage:.0f}%</span>'
        '</div>'

        '</div>'
    )


    st.markdown(
        results_html,
        unsafe_allow_html=True
    )


    st.progress(
        percentage / 100
    )


    st.write("")
    st.write("")


    st.markdown(
        '<div class="sub-label">'
        'Review'
        '</div>',
        unsafe_allow_html=True
    )


    st.markdown(
        '<div class="sub-title">'
        'Answer review'
        '</div>',
        unsafe_allow_html=True
    )


    st.markdown(
        '<div class="sub-copy">'
        'Review each response and compare it '
        'with the correct answer.'
        '</div>',
        unsafe_allow_html=True
    )


    for index, result in enumerate(
        results
    ):

        status = (
            "Correct"
            if result["is_correct"]
            else "Needs review"
        )


        with st.expander(
            f"{index + 1}. "
            f"{result['question']} "
            f"- {status}"
        ):

            if result["is_correct"]:

                st.success(
                    "Your answer was correct."
                )


                st.write(
                    "**Answer:** "
                    f"{result['correct_answer']}"
                )


            else:

                st.error(
                    "Your answer was incorrect."
                )


                st.write(
                    "**Your answer:** "
                    f"{result['user_answer']}"
                )


                st.write(
                    "**Correct answer:** "
                    f"{result['correct_answer']}"
                )


    st.write("")


    if st.button(
        "Create another quiz",
        type="primary",
        use_container_width=True
    ):

        reset_quiz_state()

        st.rerun()


st.write("")
st.write("")
st.divider()


st.caption(
    "Quizora AI | AI-powered study quiz generator"
)
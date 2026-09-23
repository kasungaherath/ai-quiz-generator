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
            opacity: 0.22;
            transform: translateX(-50%) scale(0.95);
        }
        50% {
            opacity: 0.48;
            transform: translateX(-50%) scale(1.05);
        }
        100% {
            opacity: 0.22;
            transform: translateX(-50%) scale(0.95);
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

        background-size: 150% 150%;
        animation: gradientMove 20s ease infinite;
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

    .workspace-badge {
        display: inline-block;
        padding: 0.42rem 0.8rem;
        margin-bottom: 0.9rem;

        border-radius: 999px;

        background:
            linear-gradient(
                90deg,
                rgba(124, 58, 237, 0.16),
                rgba(14, 165, 233, 0.10)
            );

        border:
            1px solid rgba(129, 140, 248, 0.16);

        color: #b8b9ff;
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

    .feature-row {
        display: flex;
        flex-wrap: wrap;
        gap: 0.65rem;
        margin-bottom: 1.5rem;
    }

    .feature-pill {
        padding: 0.48rem 0.8rem;
        border-radius: 999px;

        background:
            rgba(255, 255, 255, 0.025);

        border:
            1px solid rgba(255, 255, 255, 0.07);

        color: #989fad;
        font-size: 0.8rem;
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

    [data-testid="stVerticalBlockBorderWrapper"] {
        position: relative;

        background:
            linear-gradient(
                180deg,
                rgba(18, 21, 30, 0.88),
                rgba(11, 14, 20, 0.92)
            );

        border:
            1px solid rgba(255, 255, 255, 0.075)
            !important;

        border-radius: 20px !important;

        box-shadow:
            0 22px 65px rgba(0, 0, 0, 0.22);
    }

    textarea {
        min-height: 280px !important;

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

    [data-testid="stMetric"] {
        padding: 1rem 1.1rem;

        background:
            linear-gradient(
                180deg,
                rgba(255, 255, 255, 0.032),
                rgba(255, 255, 255, 0.015)
            );

        border:
            1px solid rgba(255, 255, 255, 0.07);

        border-radius: 14px;
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
        border-color: rgba(255, 255, 255, 0.07);
    }

    @media (prefers-reduced-motion: reduce) {
        .stApp,
        .hero-title,
        .hero-wrap::before,
        .stButton > button[kind="primary"] {
            animation: none !important;
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

        .workspace-title {
            font-size: 2.2rem;
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
    (
        '<div class="workspace-copy">'
        'Transform your study material into a focused assessment. '
        'Choose your content source, customize the experience, '
        'and generate questions designed around your material.'
        '</div>'
    ),
    unsafe_allow_html=True
)

st.markdown(
    (
        '<div class="feature-row">'
        '<span class="feature-pill">Text and PDF input</span>'
        '<span class="feature-pill">MCQ and True/False</span>'
        '<span class="feature-pill">Difficulty control</span>'
        '<span class="feature-pill">Instant evaluation</span>'
        '</div>'
    ),
    unsafe_allow_html=True
)


with st.container(border=True):

    st.markdown(
        '<div class="sub-label">Source</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sub-title">Add study material</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        (
            '<div class="sub-copy">'
            'Paste your notes directly or upload a text-based PDF.'
            '</div>'
        ),
        unsafe_allow_html=True
    )


    source_mode = st.radio(
        "Choose an input method",
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
            height=280,
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
            help="Text-based PDF documents work best."
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
                        "Document processed successfully."
                    )

                    with st.expander(
                        "Preview extracted text"
                    ):
                        st.write(
                            study_text[:4000]
                        )


                else:

                    st.warning(
                        "No readable text was found in this PDF."
                    )


            except Exception as error:

                st.error(
                    "The PDF could not be processed."
                )

                with st.expander(
                    "Technical details"
                ):
                    st.exception(error)


    if study_text.strip():

        word_count = len(
            study_text.split()
        )

        st.caption(
            f"{source_name} | {word_count:,} words"
        )


    st.divider()


    st.markdown(
        '<div class="sub-label">Configuration</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sub-title">Customize your quiz</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        (
            '<div class="sub-copy">'
            'Choose the question format, difficulty, and quiz length.'
            '</div>'
        ),
        unsafe_allow_html=True
    )


    col1, col2, col3 = st.columns(3)


    with col1:
        question_type = st.selectbox(
            "Question type",
            [
                "Multiple Choice",
                "True/False",
                "Mixed"
            ]
        )


    with col2:
        difficulty = st.selectbox(
            "Difficulty",
            [
                "Easy",
                "Medium",
                "Hard"
            ]
        )


    with col3:
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


    MAX_CHARACTERS = 30000

    prepared_text = study_text[
        :MAX_CHARACTERS
    ]


    if len(study_text) > MAX_CHARACTERS:

        st.info(
            "This document is large. "
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


            st.success(
                "Quiz generated successfully."
            )


        except Exception as error:

            st.error(
                "Quiz generation failed. "
                "Please wait a moment and try again."
            )

            with st.expander(
                "Technical details"
            ):
                st.exception(error)


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


    st.write("")
    st.write("")


    st.markdown(
        '<div class="workspace-badge">Active quiz</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="workspace-title">Test what you know</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        (
            '<div class="workspace-copy">'
            'Answer each question and submit when you are ready. '
            'Your score and answer review will appear immediately.'
            '</div>'
        ),
        unsafe_allow_html=True
    )


    info1, info2, info3 = st.columns(3)


    with info1:
        st.metric(
            "Questions",
            len(quiz)
        )


    with info2:
        st.metric(
            "Difficulty",
            quiz_config.get(
                "difficulty",
                difficulty
            )
        )


    with info3:
        st.metric(
            "Format",
            quiz_config.get(
                "question_type",
                question_type
            )
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


    answered_count = sum(
        answer is not None
        for answer in user_answers.values()
    )


    completion = (
        answered_count
        / len(quiz)
    )


    st.write("")

    st.caption(
        f"{answered_count} of "
        f"{len(quiz)} questions answered"
    )

    st.progress(
        completion
    )


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

    total = len(quiz)

    percentage = (
        score / total
    ) * 100


    st.write("")
    st.write("")


    st.markdown(
        '<div class="workspace-badge">Performance</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="workspace-title">Quiz results</div>',
        unsafe_allow_html=True
    )


    if percentage >= 80:

        st.success(
            "Strong performance. "
            "You demonstrated a good understanding "
            "of this material."
        )


    elif percentage >= 60:

        st.info(
            "Good progress. Review the questions "
            "you missed and try another quiz."
        )


    else:

        st.warning(
            "More revision is recommended. "
            "Review the answers below before trying again."
        )


    result1, result2, result3 = st.columns(3)


    with result1:
        st.metric(
            "Score",
            f"{score}/{total}"
        )


    with result2:
        st.metric(
            "Accuracy",
            f"{percentage:.0f}%"
        )


    with result3:
        st.metric(
            "Incorrect",
            total - score
        )


    st.progress(
        percentage / 100
    )


    st.write("")
    st.write("")


    st.markdown(
        '<div class="sub-title">Answer review</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        (
            '<div class="sub-copy">'
            'Review incorrect responses and reinforce '
            'the correct information.'
            '</div>'
        ),
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
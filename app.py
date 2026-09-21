import streamlit as st

from utils.pdf_reader import extract_text_from_pdf
from utils.quiz_generator import generate_quiz
from utils.quiz_utils import calculate_score


# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Quizora AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# CUSTOM CSS
# =========================================================
st.markdown(
    """
    <style>

    .stApp {
        background:
            radial-gradient(
                circle at top left,
                rgba(99, 102, 241, 0.12),
                transparent 32%
            ),
            radial-gradient(
                circle at top right,
                rgba(16, 185, 129, 0.08),
                transparent 28%
            ),
            #0d1117;
    }

    .block-container {
        max-width: 1150px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    [data-testid="stSidebar"] {
        background: #111827;
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }

    [data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.035);
        border: 1px solid rgba(255, 255, 255, 0.07);
        padding: 1rem;
        border-radius: 16px;
    }

    .stButton > button {
        border-radius: 12px;
        min-height: 48px;
        font-weight: 650;
        transition:
            transform 0.15s ease,
            box-shadow 0.15s ease;
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.20);
    }

    textarea {
        border-radius: 14px !important;
    }

    [data-baseweb="select"] > div {
        border-radius: 12px;
    }

    .section-label {
        font-size: 0.78rem;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: #818cf8;
        font-weight: 700;
        margin-bottom: 0.4rem;
    }

    .section-title {
        font-size: 1.6rem;
        font-weight: 750;
        margin-bottom: 0.3rem;
    }

    .section-description {
        color: #9ca3af;
        margin-bottom: 1.4rem;
    }

    .footer {
        text-align: center;
        color: #6b7280;
        font-size: 0.82rem;
        padding-top: 2rem;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# RESET FUNCTION
# =========================================================
def reset_quiz_state():

    keys_to_remove = [
        key
        for key in st.session_state.keys()
        if key.startswith("question_")
    ]

    keys_to_remove += [
        "quiz",
        "quiz_submitted",
        "results",
        "score"
    ]

    for key in keys_to_remove:
        if key in st.session_state:
            del st.session_state[key]


# =========================================================
# API KEY
# =========================================================
try:
    api_key = st.secrets["GEMINI_API_KEY"]

except KeyError:

    st.error(
        "Gemini API key was not found. "
        "Add GEMINI_API_KEY to .streamlit/secrets.toml"
    )

    st.stop()


# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:

    st.markdown("## 🧠 Quizora AI")

    st.caption(
        "Learn smarter with AI"
    )

    st.divider()

    st.markdown("### Quiz Configuration")

    question_type = st.selectbox(
        "Question Type",
        [
            "Multiple Choice",
            "True/False",
            "Mixed"
        ]
    )

    difficulty = st.selectbox(
        "Difficulty",
        [
            "Easy",
            "Medium",
            "Hard"
        ]
    )

    num_questions = st.slider(
        "Number of Questions",
        min_value=5,
        max_value=20,
        value=10
    )

    st.divider()

    st.markdown("### Current Setup")

    st.caption(
        f"Type: {question_type}"
    )

    st.caption(
        f"Difficulty: {difficulty}"
    )

    st.caption(
        f"Questions: {num_questions}"
    )

    st.divider()

    if "quiz" in st.session_state:

        if st.button(
            "Start New Quiz",
            use_container_width=True
        ):

            reset_quiz_state()

            st.rerun()


# =========================================================
# APP HEADER
# =========================================================
st.markdown(
    """
    <h1 style="
        font-size: 3.2rem;
        font-weight: 800;
        margin-bottom: 0;
    ">
        🧠 Quizora AI
    </h1>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <h3 style="
        margin-top: 0.3rem;
        font-weight: 500;
        color: #a5b4fc;
    ">
        AI-Powered Quiz Generator for Smarter Learning
    </h3>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <p style="
        font-size: 1.08rem;
        line-height: 1.8;
        max-width: 900px;
        color: #9ca3af;
        margin-top: 1rem;
        margin-bottom: 1.8rem;
    ">
        Transform your study materials into interactive quizzes in seconds.
        Paste your notes or upload a PDF, choose your preferred difficulty
        and question format, and let AI generate a personalized quiz.
        Test your knowledge, receive instant scoring, and review your answers
        to improve your understanding.
    </p>
    """,
    unsafe_allow_html=True
)

feature1, feature2, feature3 = st.columns(3)

with feature1:

    st.markdown("### 📄 Upload")

    st.caption(
        "Use your own PDF documents or paste study notes."
    )

with feature2:

    st.markdown("### ✨ Generate")

    st.caption(
        "Create AI-powered MCQ and True/False questions."
    )

with feature3:

    st.markdown("### 📊 Learn")

    st.caption(
        "Get instant scores and review your answers."
    )


st.divider()


# =========================================================
# STUDY MATERIAL
# =========================================================
st.markdown(
    """
    <div class="section-label">
        Step 01
    </div>

    <div class="section-title">
        Add your study material
    </div>

    <div class="section-description">
        Paste your notes directly or upload a PDF document.
    </div>
    """,
    unsafe_allow_html=True
)


source_tab1, source_tab2 = st.tabs(
    [
        "Paste Text",
        "Upload PDF"
    ]
)


study_text = ""


# =========================================================
# TEXT INPUT
# =========================================================
with source_tab1:

    typed_text = st.text_area(
        "Study Material",
        height=280,
        placeholder=(
            "Paste your lecture notes, revision material, "
            "or textbook content here..."
        )
    )


# =========================================================
# PDF INPUT
# =========================================================
with source_tab2:

    uploaded_file = st.file_uploader(
        "Upload PDF",
        type=["pdf"],
        help="Upload a text-based PDF document."
    )

    pdf_text = ""

    if uploaded_file is not None:

        try:

            with st.spinner(
                "Reading your PDF..."
            ):

                pdf_text = extract_text_from_pdf(
                    uploaded_file
                )

            if pdf_text:

                st.success(
                    "PDF processed successfully."
                )

                with st.expander(
                    "Preview extracted content"
                ):

                    st.write(
                        pdf_text[:5000]
                    )

            else:

                st.warning(
                    "No readable text was found "
                    "inside this PDF."
                )

        except Exception as error:

            st.error(
                "The PDF could not be processed."
            )

            with st.expander(
                "Technical details"
            ):

                st.exception(error)


# =========================================================
# CHOOSE ACTIVE INPUT
# =========================================================
if typed_text.strip():

    study_text = typed_text

elif pdf_text.strip():

    study_text = pdf_text


# =========================================================
# GENERATE QUIZ SECTION
# =========================================================
st.write("")

st.markdown(
    """
    <div class="section-label">
        Step 02
    </div>

    <div class="section-title">
        Generate your quiz
    </div>

    <div class="section-description">
        Configure the quiz using the sidebar,
        then generate questions from your material.
    </div>
    """,
    unsafe_allow_html=True
)


generate_button = st.button(
    "✨ Generate AI Quiz",
    type="primary",
    use_container_width=True
)


# =========================================================
# GENERATE QUIZ
# =========================================================
if generate_button:

    if not study_text.strip():

        st.warning(
            "Please add study material "
            "before generating a quiz."
        )

    else:

        try:

            reset_quiz_state()

            with st.spinner(
                "Building your quiz..."
            ):

                quiz = generate_quiz(
                    api_key=api_key,
                    study_text=study_text,
                    num_questions=num_questions,
                    question_type=question_type,
                    difficulty=difficulty
                )

                st.session_state.quiz = quiz

            st.success(
                "Your quiz is ready."
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


# =========================================================
# QUIZ
# =========================================================
if "quiz" in st.session_state:

    quiz = st.session_state.quiz

    st.write("")

    st.markdown(
        """
        <div class="section-label">
            Step 03
        </div>

        <div class="section-title">
            Complete your quiz
        </div>

        <div class="section-description">
            Answer every question and submit
            when you are ready.
        </div>
        """,
        unsafe_allow_html=True
    )


    info_col1, info_col2, info_col3 = st.columns(3)

    with info_col1:

        st.metric(
            "Questions",
            len(quiz)
        )

    with info_col2:

        st.metric(
            "Difficulty",
            difficulty
        )

    with info_col3:

        st.metric(
            "Format",
            question_type
        )


    st.write("")

    user_answers = {}


    # =====================================================
    # QUESTIONS
    # =====================================================
    for index, question in enumerate(quiz):

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
                "Select an answer",
                question["options"],
                key=f"question_{index}",
                index=None,
                label_visibility="collapsed"
            )

            user_answers[index] = (
                selected_answer
            )


    # =====================================================
    # PROGRESS
    # =====================================================
    answered_count = sum(
        answer is not None
        for answer in user_answers.values()
    )

    progress_value = (
        answered_count / len(quiz)
    )

    st.write("")

    st.caption(
        f"{answered_count} of {len(quiz)} questions answered"
    )

    st.progress(
        progress_value
    )


    # =====================================================
    # SUBMIT QUIZ
    # =====================================================
    submit_button = st.button(
        "✅ Submit Quiz",
        type="primary",
        use_container_width=True
    )


    if submit_button:

        unanswered = [
            index + 1
            for index, answer in user_answers.items()
            if answer is None
        ]

        if unanswered:

            st.warning(
                "Complete all questions before submitting."
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

            st.session_state.quiz_submitted = True
            st.session_state.results = results
            st.session_state.score = score

            st.rerun()


# =========================================================
# RESULTS
# =========================================================
if (
    "quiz_submitted" in st.session_state
    and st.session_state.quiz_submitted
):

    st.write("")

    st.markdown(
        """
        <div class="section-label">
            Performance
        </div>

        <div class="section-title">
            Your quiz results
        </div>

        <div class="section-description">
            Review your score and check
            every answer below.
        </div>
        """,
        unsafe_allow_html=True
    )


    score = st.session_state.score
    results = st.session_state.results

    total = len(
        st.session_state.quiz
    )

    percentage = (
        score / total
    ) * 100


    # =====================================================
    # SCORE CARDS
    # =====================================================
    result_col1, result_col2, result_col3 = st.columns(3)

    with result_col1:

        st.metric(
            "Score",
            f"{score}/{total}"
        )

    with result_col2:

        st.metric(
            "Accuracy",
            f"{percentage:.1f}%"
        )

    with result_col3:

        incorrect = total - score

        st.metric(
            "Incorrect",
            incorrect
        )


    st.write("")

    st.progress(
        percentage / 100
    )


    if percentage >= 80:

        st.success(
            "Excellent performance. "
            "You have a strong understanding "
            "of this material."
        )

    elif percentage >= 60:

        st.info(
            "Good performance. "
            "Review the missed questions "
            "and try again."
        )

    else:

        st.warning(
            "More revision would help. "
            "Review the answers below "
            "and generate another quiz."
        )


    # =====================================================
    # ANSWER REVIEW
    # =====================================================
    st.write("")

    st.markdown(
        "## 🔍 Answer Review"
    )


    for index, result in enumerate(results):

        with st.container(
            border=True
        ):

            st.caption(
                f"QUESTION {index + 1}"
            )

            st.markdown(
                f"### {result['question']}"
            )


            if result["is_correct"]:

                st.success(
                    "Correct"
                )

                st.write(
                    f"**Answer:** "
                    f"{result['correct_answer']}"
                )

            else:

                st.error(
                    "Incorrect"
                )

                st.write(
                    f"**Your answer:** "
                    f"{result['user_answer']}"
                )

                st.write(
                    f"**Correct answer:** "
                    f"{result['correct_answer']}"
                )


    st.write("")


    if st.button(
        "🔄 Create Another Quiz",
        use_container_width=True
    ):

        reset_quiz_state()

        st.rerun()


# =========================================================
# FOOTER
# =========================================================
st.markdown(
    """
    <div class="footer">
        Quizora AI · Built with Python,
        Streamlit and Generative AI
    </div>
    """,
    unsafe_allow_html=True
)
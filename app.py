import streamlit as st

from utils.pdf_reader import extract_text_from_pdf
from utils.quiz_generator import generate_quiz
from utils.quiz_utils import calculate_score


# --------------------------------------------------
# Page Configuration
# --------------------------------------------------
st.set_page_config(
    page_title="AI Quiz Generator",
    page_icon="🧠",
    layout="centered"
)


# --------------------------------------------------
# Custom Styling
# --------------------------------------------------
st.markdown(
    """
    <style>
    .block-container {
        max-width: 900px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    h1 {
        text-align: center;
    }

    .subtitle {
        text-align: center;
        color: #777;
        font-size: 1.05rem;
        margin-bottom: 2rem;
    }

    .section-title {
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }

    .result-box {
        padding: 1rem;
        border-radius: 10px;
        margin-top: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# --------------------------------------------------
# Header
# --------------------------------------------------
st.title("🧠 AI Quiz Generator")

st.markdown(
    """
    <p class="subtitle">
        Upload study materials or paste your notes,
        then generate an AI-powered quiz instantly.
    </p>
    """,
    unsafe_allow_html=True
)


# --------------------------------------------------
# Gemini API Key
# --------------------------------------------------
try:
    api_key = st.secrets["GEMINI_API_KEY"]

except KeyError:
    st.error(
        "Gemini API key was not found. "
        "Please add GEMINI_API_KEY to "
        ".streamlit/secrets.toml"
    )

    st.stop()


# --------------------------------------------------
# Study Material Section
# --------------------------------------------------
st.divider()

st.subheader("📚 Study Material")

study_text = ""

input_method = st.radio(
    "Choose study material source:",
    [
        "Enter Text",
        "Upload PDF"
    ],
    horizontal=True
)


# --------------------------------------------------
# Text Input
# --------------------------------------------------
if input_method == "Enter Text":

    study_text = st.text_area(
        "Enter your study material:",
        height=300,
        placeholder=(
            "Paste your lecture notes, "
            "study material, or textbook content here..."
        )
    )


# --------------------------------------------------
# PDF Upload
# --------------------------------------------------
else:

    uploaded_file = st.file_uploader(
        "Upload a PDF document",
        type=["pdf"]
    )

    if uploaded_file is not None:

        try:

            with st.spinner(
                "Extracting text from PDF..."
            ):

                study_text = extract_text_from_pdf(
                    uploaded_file
                )

            if study_text:

                st.success(
                    "PDF text extracted successfully!"
                )

                with st.expander(
                    "Preview extracted text"
                ):

                    st.write(
                        study_text[:5000]
                    )

            else:

                st.warning(
                    "No readable text was found "
                    "inside this PDF."
                )

        except Exception as error:

            st.error(
                "There was a problem reading the PDF."
            )

            with st.expander(
                "Technical details"
            ):

                st.exception(error)


# --------------------------------------------------
# Quiz Settings Section
# --------------------------------------------------
st.divider()

st.subheader("⚙️ Quiz Settings")


col1, col2 = st.columns(2)


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


num_questions = st.slider(
    "Number of questions",
    min_value=5,
    max_value=20,
    value=10
)


# --------------------------------------------------
# Generate Quiz Button
# --------------------------------------------------
generate_button = st.button(
    "✨ Generate Quiz",
    type="primary",
    use_container_width=True
)


# --------------------------------------------------
# Generate Quiz
# --------------------------------------------------
if generate_button:

    if not study_text.strip():

        st.warning(
            "Please enter study material "
            "or upload a PDF first."
        )

    else:

        try:

            with st.spinner(
                "Generating your quiz..."
            ):

                quiz = generate_quiz(
                    api_key=api_key,
                    study_text=study_text,
                    num_questions=num_questions,
                    question_type=question_type,
                    difficulty=difficulty
                )

                st.session_state.quiz = quiz

                # Remove previous selected answers
                keys_to_delete = []

                for key in st.session_state:

                    if key.startswith(
                        "question_"
                    ):
                        keys_to_delete.append(key)

                for key in keys_to_delete:
                    del st.session_state[key]


                # Remove previous results
                for key in [
                    "quiz_submitted",
                    "results",
                    "score"
                ]:

                    if key in st.session_state:
                        del st.session_state[key]


            st.success(
                "Quiz generated successfully!"
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


# --------------------------------------------------
# Display Quiz
# --------------------------------------------------
if "quiz" in st.session_state:

    quiz = st.session_state.quiz

    st.divider()

    st.subheader("📝 Quiz")

    st.caption(
        f"Total Questions: {len(quiz)}"
    )

    user_answers = {}


    for index, question in enumerate(quiz):

        st.markdown(
            f"### Question {index + 1}"
        )

        st.write(
            question["question"]
        )

        selected_answer = st.radio(
            "Choose your answer:",
            question["options"],
            key=f"question_{index}",
            index=None
        )

        user_answers[index] = selected_answer

        st.divider()


    # --------------------------------------------------
    # Submit Quiz
    # --------------------------------------------------
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
                "Please answer all questions "
                "before submitting the quiz."
            )

            st.write(
                "Unanswered questions:",
                unanswered
            )

        else:

            score, results = calculate_score(
                quiz,
                user_answers
            )

            st.session_state.quiz_submitted = True
            st.session_state.results = results
            st.session_state.score = score


# --------------------------------------------------
# Quiz Results
# --------------------------------------------------
if (
    "quiz_submitted" in st.session_state
    and st.session_state.quiz_submitted
):

    st.divider()

    st.subheader("🏆 Quiz Results")


    score = st.session_state.score

    results = st.session_state.results

    total = len(
        st.session_state.quiz
    )

    percentage = (
        score / total
    ) * 100


    # --------------------------------------------------
    # Result Metrics
    # --------------------------------------------------
    col1, col2 = st.columns(2)


    with col1:

        st.metric(
            "Score",
            f"{score}/{total}"
        )


    with col2:

        st.metric(
            "Percentage",
            f"{percentage:.1f}%"
        )


    # --------------------------------------------------
    # Progress Bar
    # --------------------------------------------------
    st.progress(
        percentage / 100
    )


    # --------------------------------------------------
    # Result Message
    # --------------------------------------------------
    if percentage >= 80:

        st.success(
            "🎉 Excellent work!"
        )

    elif percentage >= 60:

        st.info(
            "👍 Good job! Keep practicing."
        )

    else:

        st.warning(
            "📚 Keep studying and try again."
        )


    # --------------------------------------------------
    # Answer Review
    # --------------------------------------------------
    st.divider()

    st.subheader(
        "🔍 Answer Review"
    )


    for index, result in enumerate(results):

        st.markdown(
            f"### Question {index + 1}"
        )

        st.write(
            result["question"]
        )


        if result["is_correct"]:

            st.success(
                "Correct answer: "
                f"{result['correct_answer']}"
            )

        else:

            st.error(
                "Your answer: "
                f"{result['user_answer']}"
            )

            st.info(
                "Correct answer: "
                f"{result['correct_answer']}"
            )


        st.divider()


# --------------------------------------------------
# Create New Quiz
# --------------------------------------------------
if "quiz" in st.session_state:

    if st.button(
        "🔄 Create New Quiz",
        use_container_width=True
    ):

        st.session_state.clear()

        st.rerun()
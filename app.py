import streamlit as st

from utils.pdf_reader import extract_text_from_pdf
from utils.quiz_generator import generate_quiz
from utils.quiz_utils import calculate_score

# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title="AI Quiz Generator",
    page_icon="🧠",
    layout="centered"
)


# -----------------------------
# App Title
# -----------------------------
st.title("🧠 AI Quiz Generator")

st.write(
    "Generate quizzes from study notes or uploaded PDF documents."
)


# -----------------------------
# API Key
# -----------------------------
api_key = st.secrets["GEMINI_API_KEY"]


# -----------------------------
# Study Material Input
# -----------------------------
study_text = ""

input_method = st.radio(
    "Choose study material source:",
    ["Enter Text", "Upload PDF"]
)


# -----------------------------
# Text Input
# -----------------------------
if input_method == "Enter Text":

    study_text = st.text_area(
        "Enter your study material:",
        height=300,
        placeholder="Paste your notes here..."
    )


# -----------------------------
# PDF Upload
# -----------------------------
else:

    uploaded_file = st.file_uploader(
        "Upload a PDF",
        type=["pdf"]
    )

    if uploaded_file is not None:

        try:

            with st.spinner("Extracting text from PDF..."):

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
                    "No readable text was found in this PDF."
                )

        except Exception as error:

            st.error(
                "There was a problem reading the PDF."
            )

            st.exception(error)


# -----------------------------
# Quiz Settings
# -----------------------------
st.subheader("Quiz Settings")

question_type = st.selectbox(
    "Question type",
    [
        "Multiple Choice",
        "True/False",
        "Mixed"
    ]
)

num_questions = st.slider(
    "Number of questions",
    min_value=5,
    max_value=20,
    value=10
)

difficulty = st.selectbox(
    "Difficulty",
    [
        "Easy",
        "Medium",
        "Hard"
    ]
)


# -----------------------------
# Generate Quiz Button
# -----------------------------
generate_button = st.button(
    "Generate Quiz",
    type="primary"
)


# -----------------------------
# Generate Quiz
# -----------------------------
if generate_button:

    if not study_text.strip():

        st.warning(
            "Please provide study material first."
        )

    else:

        try:

            with st.spinner(
                "Generating quiz..."
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
                "Quiz generated successfully!"
            )

        except Exception as error:

            st.error(
                "Quiz generation failed."
            )

            st.exception(error)


# -----------------------------
# Display Quiz 
# -----------------------------

if "quiz" in st.session_state:

    st.subheader("Quiz")

    user_answers = {}

    for index, question in enumerate(st.session_state.quiz):

        st.write(f"### Question {index + 1}")
        st.write(question["question"])

        selected_answer = st.radio(
            "Choose your answer:",
            question["options"],
            key=f"question_{index}",
            index=None
        )

        user_answers[index] = selected_answer

    st.session_state.user_answers = user_answers

    submit_button = st.button(
        "Submit Quiz",
        type="primary"
    )

    if submit_button:

        unanswered = [
            index + 1
            for index, answer in user_answers.items()
            if answer is None
        ]

        if unanswered:
            st.warning(
                "Please answer all questions before submitting."
            )

        else:
            score, results = calculate_score(
                st.session_state.quiz,
                user_answers
            )

            total = len(st.session_state.quiz)
            percentage = (score / total) * 100

            st.subheader("Quiz Results")

            st.metric(
                "Score",
                f"{score}/{total}"
            )

            st.progress(percentage / 100)

            st.write(
                f"**Percentage: {percentage:.1f}%**"
            )

            st.subheader("Answer Review")

            for index, result in enumerate(results):

                st.write(
                    f"### Question {index + 1}"
                )

                st.write(result["question"])

                if result["is_correct"]:

                    st.success(
                        f"Correct: {result['correct_answer']}"
                    )

                else:

                    st.error(
                        f"Your answer: {result['user_answer']}"
                    )

                    st.info(
                        f"Correct answer: {result['correct_answer']}"
                    )
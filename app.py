import streamlit as st

st.set_page_config(
    page_title="AI Quiz Generator",
    page_icon="🧠",
    layout="centered"
)

st.title("🧠 AI Quiz Generator")

st.write("Generate quizzes from study notes and PDF documents.")

input_method = st.radio(
    "Choose study material source:",
    ["Enter Text", "Upload PDF"]
)
if input_method == "Enter Text":
    study_text = st.text_area(
        "Enter your study material:",
        height=300,
        placeholder="Paste your notes here..."
    )

else:
    uploaded_file = st.file_uploader(
        "Upload a PDF",
        type=["pdf"]
    )
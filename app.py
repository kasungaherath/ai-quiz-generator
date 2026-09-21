import streamlit as st
from utils.pdf_reader import extract_text_from_pdf

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

    if uploaded_file is not None:
        with st.spinner("Extracting text from PDF..."):
            study_text = extract_text_from_pdf(uploaded_file)

        if study_text:
            st.success("PDF text extracted successfully!")

            with st.expander("Preview extracted text"):
                st.write(study_text[:5000])

        else:
            st.warning("No readable text was found in this PDF.")
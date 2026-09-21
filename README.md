# 🧠 Quizora AI

Quizora AI is an AI-powered quiz generator that transforms study notes and PDF documents into interactive quizzes.

Users can paste study material or upload a PDF, choose the quiz type, difficulty level, and number of questions, then generate a personalized quiz using Generative AI.

The application automatically evaluates answers, calculates the score and percentage, and provides an answer review.

---

## ✨ Features

- Upload PDF study materials
- Paste study notes manually
- Generate AI-powered quiz questions
- Multiple-choice questions
- True/False questions
- Mixed quiz mode
- Easy, Medium, and Hard difficulty levels
- Adjustable number of questions
- Automatic scoring
- Percentage calculation
- Quiz progress tracking
- Answer review
- Retry handling for temporary AI API errors
- Create a new quiz
- Modern Streamlit interface

---

## 🛠️ Technologies Used

- Python
- Streamlit
- Google Gemini API
- PyPDF
- Generative AI / LLM
- Git
- GitHub

---

## 📁 Project Structure

```text
ai-quiz-generator/
│
├── app.py
├── README.md
├── requirements.txt
├── .gitignore
│
├── utils/
│   ├── __init__.py
│   ├── pdf_reader.py
│   ├── quiz_generator.py
│   └── quiz_utils.py
│
└── .streamlit/
    └── secrets.toml
```

> `.streamlit/secrets.toml` contains your API key and should not be uploaded to GitHub.

---

## ⚙️ Installation

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/ai-quiz-generator.git
```

Move into the project folder:

```bash
cd ai-quiz-generator
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

Install the required packages:

```bash
pip install -r requirements.txt
```

---

## 🔑 Gemini API Setup

Create a Gemini API key using Google AI Studio.

Create the following file:

```text
.streamlit/secrets.toml
```

Add your API key:

```toml
GEMINI_API_KEY = "your-api-key-here"
```

Make sure `.gitignore` contains:

```text
.streamlit/secrets.toml
```

---

## ▶️ Run the Application

```bash
python -m streamlit run app.py
```

---

## 🧩 How It Works

1. Paste study notes or upload a PDF.
2. PyPDF extracts text from the PDF.
3. Select question type, difficulty, and number of questions.
4. The study material is sent to the Gemini API.
5. Gemini generates quiz questions.
6. Streamlit displays the quiz.
7. Submit your answers.
8. The app calculates the score and percentage.
9. Review correct and incorrect answers.

---

## 🚀 Future Improvements

- OCR support for scanned PDFs
- Timed quizzes
- Quiz history
- User accounts
- Performance analytics
- Export quiz results
- Support for DOCX and TXT files
- AI-generated answer explanations

---

## 📸 Screenshots

Screenshots will be added after final testing and deployment.

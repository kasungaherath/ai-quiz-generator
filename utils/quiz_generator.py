import json
from google import genai


def generate_quiz(
    api_key,
    study_text,
    num_questions,
    question_type,
    difficulty
):
    client = genai.Client(api_key=api_key)

    prompt = f"""
You are an educational quiz generator.

Generate {num_questions} {difficulty.lower()} difficulty quiz questions.

Question type:
{question_type}

Use ONLY the study material below.

Requirements:
- Multiple-choice questions must have exactly 4 options.
- True/False questions must have exactly 2 options: True and False.
- Each question must have exactly one correct answer.
- Do not create duplicate questions.
- Return valid JSON only.
- Do not include Markdown code fences.
- Do not include explanations outside the JSON.

Return this structure:

[
  {{
    "question": "Question text",
    "type": "mcq",
    "options": [
      "Option 1",
      "Option 2",
      "Option 3",
      "Option 4"
    ],
    "answer": "Correct option"
  }}
]

Study material:

{study_text}
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    result = response.text.strip()

    # Remove Markdown code fences if the model adds them
    if result.startswith("```json"):
        result = result[7:]

    if result.startswith("```"):
        result = result[3:]

    if result.endswith("```"):
        result = result[:-3]

    result = result.strip()

    return json.loads(result)
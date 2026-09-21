import json
import time
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

Generate exactly {num_questions} {difficulty.lower()} difficulty quiz questions.

Question type:
{question_type}

Use ONLY the study material provided below.

Requirements:

1. Questions must be based only on the study material.
2. Do not use outside knowledge.
3. Multiple-choice questions must have exactly 4 options.
4. True/False questions must have exactly 2 options:
   True and False.
5. Each question must have exactly one correct answer.
6. Do not create duplicate questions.
7. The value in "answer" must exactly match one item in "options".
8. Return valid JSON only.
9. Do not include Markdown code fences.
10. Do not include explanations outside the JSON.

Return data in this format:

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

For True/False questions use this format:

[
    {{
        "question": "Question text",
        "type": "true_false",
        "options": [
            "True",
            "False"
        ],
        "answer": "True"
    }}
]

Study material:

{study_text}
"""

    max_retries = 3

    for attempt in range(max_retries):

        try:
            response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=prompt
            )

            if not response.text:
                raise ValueError(
                    "Gemini returned an empty response."
                )

            result = response.text.strip()

            # Remove Markdown fences if Gemini adds them
            if result.startswith("```json"):
                result = result[7:]

            elif result.startswith("```"):
                result = result[3:]

            if result.endswith("```"):
                result = result[:-3]

            result = result.strip()

            quiz = json.loads(result)

            # Basic validation
            if not isinstance(quiz, list):
                raise ValueError(
                    "The generated quiz is not a valid list."
                )

            if len(quiz) == 0:
                raise ValueError(
                    "The generated quiz contains no questions."
                )

            valid_questions = []

            for question in quiz:

                if not isinstance(question, dict):
                    continue

                if "question" not in question:
                    continue

                if "options" not in question:
                    continue

                if "answer" not in question:
                    continue

                if not isinstance(
                    question["options"],
                    list
                ):
                    continue

                if (
                    question["answer"]
                    not in question["options"]
                ):
                    continue

                valid_questions.append(question)

            if len(valid_questions) == 0:
                raise ValueError(
                    "Gemini did not return any valid quiz questions."
                )

            return valid_questions

        except Exception as error:

            error_message = str(error).lower()

            temporary_error = (
                "503" in error_message
                or "unavailable" in error_message
                or "high demand" in error_message
                or "429" in error_message
                or "resource_exhausted" in error_message
                or "rate limit" in error_message
            )

            if (
                temporary_error
                and attempt < max_retries - 1
            ):
                time.sleep(2)
                continue

            raise error
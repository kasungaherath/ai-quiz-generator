import json
import time
from google import genai


def clean_json_response(text):
    text = text.strip()

    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]

    if text.endswith("```"):
        text = text[:-3]

    return text.strip()


def validate_question(question, question_type):
    if not isinstance(question, dict):
        return False

    if "question" not in question:
        return False

    if "options" not in question:
        return False

    if "answer" not in question:
        return False

    options = question["options"]
    answer = question["answer"]

    if not isinstance(options, list):
        return False

    if answer not in options:
        return False

    if question_type == "Multiple Choice":

        if len(options) != 4:
            return False

        normalized = [
            str(option).strip().lower()
            for option in options
        ]

        if normalized == ["true", "false"]:
            return False

        question["type"] = "mcq"

        return True

    if question_type == "True/False":

        normalized = {
            str(option).strip().lower()
            for option in options
        }

        if normalized != {"true", "false"}:
            return False

        if len(options) != 2:
            return False

        question["type"] = "true_false"

        return True

    if question_type == "Mixed":

        if len(options) == 4:
            question["type"] = "mcq"
            return True

        normalized = {
            str(option).strip().lower()
            for option in options
        }

        if (
            len(options) == 2
            and normalized == {"true", "false"}
        ):
            question["type"] = "true_false"
            return True

    return False


def generate_quiz(
    api_key,
    study_text,
    num_questions,
    question_type,
    difficulty
):
    client = genai.Client(
        api_key=api_key
    )

    if question_type == "Multiple Choice":

        type_rules = """
IMPORTANT QUESTION TYPE RULES:

You MUST generate ONLY multiple-choice questions.

Every question MUST:
- Have exactly 4 answer options.
- Have exactly one correct answer.
- Use type "mcq".
- NEVER use True/False questions.
- NEVER use only True and False as the options.
"""

    elif question_type == "True/False":

        type_rules = """
IMPORTANT QUESTION TYPE RULES:

You MUST generate ONLY True/False questions.

Every question MUST:
- Have exactly 2 options.
- The options MUST be "True" and "False".
- Use type "true_false".
- Have exactly one correct answer.
- NEVER generate multiple-choice questions.
"""

    else:

        type_rules = """
IMPORTANT QUESTION TYPE RULES:

Generate a mixture of multiple-choice and True/False questions.

For multiple-choice:
- Use type "mcq".
- Use exactly 4 options.

For True/False:
- Use type "true_false".
- Use exactly 2 options: "True" and "False".
"""

    prompt = f"""
You are an educational quiz generator.

Generate EXACTLY {num_questions} quiz questions.

Difficulty:
{difficulty}

Selected question type:
{question_type}

{type_rules}

Use ONLY the study material provided below.

General requirements:

- Do not use outside knowledge.
- Do not repeat questions.
- Each question must have exactly one correct answer.
- The value of "answer" must exactly match one option.
- Return valid JSON only.
- Do not include Markdown.
- Do not include explanations.
- Do not include text before or after the JSON.

Return this JSON structure:

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

    max_retries = 4

    last_error = None

    for attempt in range(max_retries):

        try:
            response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=prompt
            )

            if not response.text:
                raise ValueError(
                    "The AI returned an empty response."
                )

            cleaned_response = clean_json_response(
                response.text
            )

            quiz = json.loads(
                cleaned_response
            )

            if not isinstance(quiz, list):
                raise ValueError(
                    "Quiz response must be a list."
                )

            valid_questions = []

            for question in quiz:

                if validate_question(
                    question,
                    question_type
                ):
                    valid_questions.append(
                        question
                    )

            if len(valid_questions) != num_questions:

                raise ValueError(
                    f"Expected {num_questions} valid "
                    f"{question_type} questions, but received "
                    f"{len(valid_questions)}."
                )

            return valid_questions

        except Exception as error:

            last_error = error

            error_text = str(
                error
            ).lower()

            temporary_error = (
                "503" in error_text
                or "unavailable" in error_text
                or "high demand" in error_text
                or "429" in error_text
                or "rate limit" in error_text
                or "resource_exhausted" in error_text
            )

            if attempt < max_retries - 1:

                if temporary_error:
                    time.sleep(3)
                else:
                    time.sleep(1)

                continue

            raise last_error
def calculate_score(quiz, user_answers):
    score = 0
    results = []

    for index, question in enumerate(quiz):
        user_answer = user_answers.get(index)
        correct_answer = question["answer"]

        is_correct = user_answer == correct_answer

        if is_correct:
            score += 1

        results.append(
            {
                "question": question["question"],
                "user_answer": user_answer,
                "correct_answer": correct_answer,
                "is_correct": is_correct
            }
        )

    return score, results
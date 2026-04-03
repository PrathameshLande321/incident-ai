class Grader:
    def grade(self, task, action_history):
        expected = task["solution"]

        if not expected:
            return 0.0

        correct = 0

        # count correct actions in correct order
        for i in range(min(len(action_history), len(expected))):
            if action_history[i] == expected[i]:
                correct += 1
            else:
                break  # stop at first wrong step

        # base score (progress)
        score = correct / len(expected)

        # penalty for extra unnecessary steps
        extra_steps = max(0, len(action_history) - len(expected))
        penalty = 0.1 * extra_steps

        final_score = max(0.0, score - penalty)

        return round(final_score, 2)
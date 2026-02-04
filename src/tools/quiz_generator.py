"""
Quiz Generator - Generate and evaluate quizzes based on lesson content
"""

from typing import List, Dict, Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from ..config import settings
from ..rag.vector_store import LessonVectorStore
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class QuizGenerator:
    """Generate quizzes from lesson content using RAG + LLM"""

    def __init__(self, vector_store: LessonVectorStore):
        self.vector_store = vector_store
        self.llm = ChatOpenAI(
            model=settings.model_name,
            temperature=0.3,  # Lower temperature for more consistent quiz generation
            openai_api_key=settings.openai_api_key,
        )

    def generate_quiz(
        self, lesson_id: int, lesson_title: str, num_questions: int = 5
    ) -> List[Dict[str, str]]:
        """
        Generate quiz questions based on lesson content

        Args:
            lesson_id: ID of the lesson
            lesson_title: Title of the lesson
            num_questions: Number of questions to generate

        Returns:
            List of question dictionaries with 'question', 'type', 'correct_answer', 'options'
        """
        logger.info(f"Generating {num_questions} quiz questions for lesson {lesson_id}")

        # Retrieve relevant lesson content
        lesson_content = self._get_lesson_content(lesson_id, lesson_title)

        # Generate questions using LLM
        quiz_prompt = f"""Based on this English grammar lesson about "{lesson_title}", generate {num_questions} quiz questions.

LESSON CONTENT:
{lesson_content}

Generate {num_questions} questions with the following format for EACH question:
1. Multiple choice questions (4 options, A-D)
2. Include the correct answer
3. Mix difficulty levels (easy, medium, hard)

Return your response in this EXACT format for each question:

Q1: [Question text]
A) [Option A]
B) [Option B]
C) [Option C]
D) [Option D]
Correct: [A/B/C/D]

Q2: [Question text]
...

Make questions practical and test understanding of grammar rules, usage, and examples from the lesson."""

        messages = [
            SystemMessage(
                content="You are an expert English grammar teacher creating quiz questions."
            ),
            HumanMessage(content=quiz_prompt),
        ]

        response = self.llm.invoke(messages)
        questions = self._parse_quiz_response(response.content)

        logger.info(f"Generated {len(questions)} quiz questions")
        return questions

    def _get_lesson_content(self, lesson_id: int, lesson_title: str) -> str:
        """Retrieve lesson content using RAG"""
        # Get comprehensive content for the lesson
        chunks = self.vector_store.retrieve_relevant_chunks(
            query=f"Complete overview of {lesson_title}", k=5, lesson_id=lesson_id
        )

        # Combine chunks
        content = "\n\n".join([chunk.page_content for chunk in chunks])
        return content

    def _parse_quiz_response(self, response_text: str) -> List[Dict[str, str]]:
        """Parse LLM response into structured quiz questions"""
        questions = []
        current_question = None
        current_options = []

        lines = response_text.strip().split("\n")

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # New question
            if line.startswith("Q") and ":" in line:
                # Save previous question
                if current_question and current_options:
                    questions.append(
                        {
                            "question": current_question,
                            "options": current_options.copy(),
                            "correct_answer": current_correct,
                            "type": "multiple_choice",
                        }
                    )

                # Start new question
                current_question = line.split(":", 1)[1].strip()
                current_options = []
                current_correct = None

            # Options
            elif line.startswith(("A)", "B)", "C)", "D)")):
                option_text = line[2:].strip()
                current_options.append({"label": line[0], "text": option_text})

            # Correct answer
            elif line.startswith("Correct:"):
                current_correct = line.split(":")[1].strip()

        # Add last question
        if current_question and current_options:
            questions.append(
                {
                    "question": current_question,
                    "options": current_options,
                    "correct_answer": current_correct,
                    "type": "multiple_choice",
                }
            )

        return questions


def evaluate_quiz(
    questions: List[Dict[str, str]], user_answers: List[str]
) -> Dict[str, any]:
    """
    Evaluate user's quiz answers

    Args:
        questions: List of quiz questions with correct answers
        user_answers: List of user's answers (e.g., ['A', 'B', 'C', 'D', 'A'])

    Returns:
        Dict with score, percentage, passed status, and detailed results
    """
    if len(questions) != len(user_answers):
        logger.error(
            f"Mismatch: {len(questions)} questions but {len(user_answers)} answers"
        )
        raise ValueError("Number of answers doesn't match number of questions")

    correct_count = 0
    results = []

    for i, (question, user_answer) in enumerate(zip(questions, user_answers), 1):
        correct_answer = question["correct_answer"]
        is_correct = user_answer.upper() == correct_answer.upper()

        if is_correct:
            correct_count += 1

        results.append(
            {
                "question_number": i,
                "question": question["question"],
                "user_answer": user_answer,
                "correct_answer": correct_answer,
                "is_correct": is_correct,
            }
        )

    score = correct_count / len(questions)
    passed = score >= settings.passing_score

    logger.info(
        f"Quiz evaluation: {correct_count}/{len(questions)} correct ({score:.1%}), Passed: {passed}"
    )

    return {
        "total_questions": len(questions),
        "correct_answers": correct_count,
        "score": score,
        "percentage": score * 100,
        "passed": passed,
        "results": results,
    }

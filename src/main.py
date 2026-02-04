"""
LangGraph-based Main Entry Point
Interactive CLI using LangGraph state machine
"""

from .workflow import TeachingGraph
from .rag.setup import setup_rag_system
from .rag.loader import LessonLoader
from .database.progress import get_or_create_user, get_current_lesson_id
from .utils.logger import setup_logger

logger = setup_logger(__name__)


class LangGraphTeacherCLI:
    """LangGraph-based CLI for English Teacher"""

    def __init__(self):
        logger.info("Initializing LangGraph Teaching System...")
        self.vector_store = setup_rag_system()
        self.graph = TeachingGraph(self.vector_store)
        self.loader = LessonLoader()
        self.lesson_metadata = self.loader.get_lesson_metadata()
        self.user_id = None
        self.current_state = None

    def run(self):
        """Main CLI loop"""
        print("\n" + "=" * 80)
        print("🎓 Welcome to English Teacher AI (LangGraph Edition)!")
        print("=" * 80 + "\n")

        # Get user ID
        self.user_id = input("Enter your name or ID: ").strip()
        if not self.user_id:
            self.user_id = "default_user"

        print(f"\nHello, {self.user_id}! Let's start learning with LangGraph.\n")

        # Initialize user
        user = get_or_create_user(self.user_id)

        # Main loop
        while True:
            # Get current lesson
            lesson_id = get_current_lesson_id(self.user_id)
            if lesson_id not in self.lesson_metadata:
                print(f"\n🎉 Congratulations! You've completed all lessons!\n")
                break

            lesson_info = self.lesson_metadata[lesson_id]

            # Show lesson info and introduce lesson (teacher teaches first)
            if not self.current_state or self.current_state.get("phase") == "completed":
                print("\n" + "=" * 80)
                print(f"📚 LESSON {lesson_id}: {lesson_info['title']}")
                print("=" * 80 + "\n")

                # Teacher introduces and teaches the lesson first
                self.introduce_lesson(lesson_id, lesson_info["title"])

                print(
                    "\nCommands: 'quiz' (take quiz) | 'summary' (lesson summary) | 'quit' (exit)"
                )
                print("-" * 80 + "\n")

            # Get user input
            user_input = input("You: ").strip()

            if not user_input:
                continue

            # Handle commands
            if user_input.lower() == "quit":
                print("\n👋 Goodbye! Keep practicing!\n")
                break

            elif user_input.lower() == "quiz":
                self.handle_quiz(lesson_id, lesson_info["title"])
                continue

            elif user_input.lower() == "summary":
                self.show_summary(lesson_id, lesson_info["title"])
                continue

            # Initialize or update state
            if not self.current_state:
                self.current_state = {
                    "user_id": self.user_id,
                    "current_lesson_id": lesson_id,
                    "lesson_title": lesson_info["title"],
                    "messages": [],
                    "user_input": user_input,
                    "phase": "teaching",
                    "next_action": "continue",
                }
            else:
                self.current_state["user_input"] = user_input
                self.current_state["next_action"] = "continue"

            # Run through graph
            logger.info(f"[CLI] Running graph with input: {user_input[:50]}...")
            result = self.graph.run(self.current_state)

            # Update state
            self.current_state = result

            # Show response
            if result.get("teacher_response"):
                print(f"\nTeacher: {result['teacher_response']}\n")

            # Handle errors
            if result.get("error"):
                print(f"\n❌ Error: {result['error']}\n")

    def handle_quiz(self, lesson_id: int, lesson_title: str):
        """Handle quiz workflow using LangGraph"""
        print("\n" + "=" * 80)
        print("📝 QUIZ TIME")
        print("=" * 80 + "\n")

        # Initialize quiz state
        quiz_state = {
            "user_id": self.user_id,
            "current_lesson_id": lesson_id,
            "lesson_title": lesson_title,
            "messages": (
                self.current_state.get("messages", []) if self.current_state else []
            ),
            "user_input": "Start quiz",
            "phase": "quiz",
            "next_action": "quiz",
            "quiz_answers": None,
        }

        # Generate quiz (run through graph)
        logger.info("[CLI] Generating quiz via graph...")
        result = self.graph.run(quiz_state)

        if not result.get("quiz_questions"):
            print("❌ Failed to generate quiz. Please try again.\n")
            return

        questions = result["quiz_questions"]

        # Ask questions
        user_answers = []
        for i, q in enumerate(questions, 1):
            print(f"\nQuestion {i}/{len(questions)}:")
            print(f"{q['question']}\n")

            for opt in q["options"]:
                print(f"  {opt['label']}) {opt['text']}")

            while True:
                answer = input("\nYour answer (A/B/C/D): ").strip().upper()
                if answer in ["A", "B", "C", "D"]:
                    user_answers.append(answer)
                    break
                print("Please enter A, B, C, or D")

        # Evaluate through graph
        print("\n" + "=" * 80)
        print("📊 EVALUATING...")
        print("=" * 80 + "\n")

        result["quiz_answers"] = user_answers
        result = self.graph.run(result)

        # Show results
        score = result.get("quiz_score", 0)
        passed = result.get("quiz_passed", False)

        if passed:
            print(f"🎉 Congratulations! You passed with {score*100:.0f}%!")
            print("You're ready for the next lesson!\n")
        else:
            print(f"📚 You scored {score*100:.0f}%. Keep practicing!")
            print(f"You need {70}% to pass. Review the material and try again.\n")

        # Update current state
        self.current_state = result

    def introduce_lesson(self, lesson_id: int, lesson_title: str):
        """Teacher introduces and teaches the lesson content proactively"""
        print("\n👨‍🏫 Teacher: Hello! Let me introduce today's lesson...\n")

        # Initialize state for introduction
        intro_state = {
            "user_id": self.user_id,
            "current_lesson_id": lesson_id,
            "lesson_title": lesson_title,
            "messages": [],
            "user_input": f"Please introduce and teach the main concepts of {lesson_title}. Give a comprehensive explanation with examples.",
            "phase": "teaching",
            "next_action": "continue",
        }

        # Run through graph to get introduction
        result = self.graph.run(intro_state)

        # Show teacher's introduction
        if result.get("teacher_response"):
            print(f"Teacher: {result['teacher_response']}\n")

        # Update state
        self.current_state = result

    def show_summary(self, lesson_id: int, lesson_title: str):
        """Show lesson summary"""
        chunks = self.vector_store.retrieve_relevant_chunks(
            query=f"Key points and summary of {lesson_title}", k=3, lesson_id=lesson_id
        )

        print("\n" + "=" * 80)
        print("📋 LESSON SUMMARY")
        print("=" * 80 + "\n")

        for i, chunk in enumerate(chunks, 1):
            print(f"{i}. {chunk.page_content[:200]}...\n")


def main():
    """Main entry point"""
    try:
        cli = LangGraphTeacherCLI()
        cli.run()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye! Keep practicing!\n")
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        print(f"\n❌ An error occurred: {e}\n")


if __name__ == "__main__":
    main()

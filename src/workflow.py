"""
LangGraph Workflow - Teaching State Machine
"""

from typing import Literal
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from .state import TeachingState
from .config import settings
from .rag.vector_store import LessonVectorStore
from .tools.quiz_generator import QuizGenerator, evaluate_quiz
from .database.progress import (
    get_or_create_user,
    update_progress,
    get_current_lesson_id,
)
from .utils.logger import setup_logger

logger = setup_logger(__name__)


class TeachingGraph:
    """LangGraph-based teaching workflow"""

    def __init__(self, vector_store: LessonVectorStore):
        self.vector_store = vector_store
        self.quiz_generator = QuizGenerator(vector_store)
        self.llm = ChatOpenAI(
            model=settings.model_name,
            temperature=settings.temperature,
            openai_api_key=settings.openai_api_key,
            max_tokens=settings.max_openai_tokens,
        )

        # Build the graph
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(TeachingState)

        # Add nodes
        workflow.add_node("retrieve_content", self.retrieve_content_node)
        workflow.add_node("generate_response", self.generate_response_node)
        workflow.add_node("generate_quiz", self.generate_quiz_node)
        workflow.add_node("evaluate_quiz", self.evaluate_quiz_node)
        workflow.add_node("update_progress", self.update_progress_node)

        # Set entry point
        workflow.set_entry_point("retrieve_content")

        # Add edges
        workflow.add_edge("retrieve_content", "generate_response")
        workflow.add_conditional_edges(
            "generate_response",
            self.route_after_response,
            {"continue": END, "quiz": "generate_quiz", "exit": END},
        )
        workflow.add_edge("generate_quiz", "evaluate_quiz")
        workflow.add_edge("evaluate_quiz", "update_progress")
        workflow.add_conditional_edges(
            "update_progress",
            self.route_after_progress,
            {"next_lesson": END, "retry": END, "continue": END},
        )

        return workflow.compile()

    # ========== NODE FUNCTIONS ==========

    def retrieve_content_node(self, state: TeachingState) -> TeachingState:
        """Node: Retrieve relevant lesson content using RAG"""
        logger.info(f"[NODE: retrieve_content] Query: {state['user_input'][:50]}...")

        try:
            chunks = self.vector_store.retrieve_relevant_chunks(
                query=state["user_input"],
                k=settings.retrieval_k,
                lesson_id=state.get("current_lesson_id"),
            )

            content = "\n\n".join(
                [
                    f"[Section {i+1}]: {chunk.page_content}"
                    for i, chunk in enumerate(chunks)
                ]
            )

            state["retrieved_content"] = content
            logger.info(f"[NODE: retrieve_content] Retrieved {len(chunks)} chunks")

        except Exception as e:
            logger.error(f"[NODE: retrieve_content] Error: {e}")
            state["error"] = str(e)
            state["retrieved_content"] = ""

        return state

    def generate_response_node(self, state: TeachingState) -> TeachingState:
        """Node: Generate teacher response using LLM"""
        logger.info("[NODE: generate_response] Generating teaching response...")
        print(f"\n{'='*60}")
        print(f"🤖 LANGGRAPH GENERATING RESPONSE")
        print(f"{'='*60}")
        print(f"User Input: {state['user_input'][:100]}...")
        print(f"Lesson: {state['lesson_title']}")

        try:
            # Check if request is from UI (for markdown formatting)
            is_ui_request = state.get("source") == "ui"

            markdown_instruction = (
                """

FORMATTING (IMPORTANT):
- Use markdown formatting in your responses
- Use **bold** for key concepts and important terms
- Use *italics* for emphasis
- Use bullet points (- ) for lists
- Use numbered lists (1. 2. 3.) for steps
- Use > for quotes or examples
- Use `code` for technical terms
- Use ### for section headers if needed
- Keep paragraphs separated with blank lines"""
                if is_ui_request
                else ""
            )

            system_prompt = f"""You are an expert English grammar teacher teaching "{state['lesson_title']}".

TEACHING GUIDELINES:
- Be conversational, friendly, and encouraging like a real teacher
- Use the provided lesson content to teach accurately
- When introducing a lesson, explain the main concepts clearly with examples
- Break down complex topics into easy-to-understand parts
- Provide real-world examples to illustrate grammar concepts
- Keep responses engaging and informative (2-4 paragraphs)
- Ask if the student has questions after explaining concepts{markdown_instruction}

LESSON CONTENT:
{state['retrieved_content']}"""

            messages = [SystemMessage(content=system_prompt)]

            # Add conversation history
            for msg in state.get("messages", [])[-6:]:
                # Handle both dict and LangChain message objects
                if isinstance(msg, dict):
                    if msg["role"] == "user":
                        messages.append(HumanMessage(content=msg["content"]))
                    else:
                        messages.append(AIMessage(content=msg["content"]))
                elif hasattr(msg, "type"):
                    messages.append(msg)

            # Add current input
            messages.append(HumanMessage(content=state["user_input"]))

            print(f"📤 Calling OpenAI LLM...")
            # Generate response
            response = self.llm.invoke(messages)
            state["teacher_response"] = response.content
            state["llm_response"] = response  # Store raw response for voice streaming

            print(f"✅ RESPONSE GENERATED FROM LANGGRAPH:")
            print(f"{'-'*60}")
            print(f"{response.content}")
            print(f"{'-'*60}\n")

            # Update messages
            state["messages"].append({"role": "user", "content": state["user_input"]})
            state["messages"].append({"role": "assistant", "content": response.content})

            logger.info("[NODE: generate_response] Response generated")

        except Exception as e:
            logger.error(f"[NODE: generate_response] Error: {e}")
            state["error"] = str(e)
            state["teacher_response"] = (
                "I apologize, I encountered an error. Please try again."
            )

        return state

    def generate_quiz_node(self, state: TeachingState) -> TeachingState:
        """Node: Generate quiz questions"""
        logger.info("[NODE: generate_quiz] Generating quiz...")

        try:
            questions = self.quiz_generator.generate_quiz(
                lesson_id=state["current_lesson_id"],
                lesson_title=state["lesson_title"],
                num_questions=5,
            )

            state["quiz_questions"] = questions
            state["phase"] = "quiz"
            logger.info(f"[NODE: generate_quiz] Generated {len(questions)} questions")

        except Exception as e:
            logger.error(f"[NODE: generate_quiz] Error: {e}")
            state["error"] = str(e)
            state["quiz_questions"] = []
            state["quiz_score"] = 0.0
            state["quiz_passed"] = False

        return state

    def evaluate_quiz_node(self, state: TeachingState) -> TeachingState:
        """Node: Evaluate quiz answers"""
        logger.info("[NODE: evaluate_quiz] Evaluating answers...")

        try:
            if not state.get("quiz_answers"):
                logger.warning("[NODE: evaluate_quiz] No answers provided")
                state["error"] = "No quiz answers provided"
                return state

            results = evaluate_quiz(
                questions=state["quiz_questions"], user_answers=state["quiz_answers"]
            )

            state["quiz_score"] = results["score"]
            state["quiz_passed"] = results["passed"]
            state["phase"] = "evaluation"

            logger.info(
                f"[NODE: evaluate_quiz] Score: {results['score']:.1%}, Passed: {results['passed']}"
            )

        except Exception as e:
            logger.error(f"[NODE: evaluate_quiz] Error: {e}")
            state["error"] = str(e)
            state["quiz_score"] = 0.0
            state["quiz_passed"] = False

        return state

    def update_progress_node(self, state: TeachingState) -> TeachingState:
        """Node: Update user progress in database"""
        logger.info("[NODE: update_progress] Updating progress...")

        try:
            # Use defaults if quiz failed to generate
            quiz_score = state.get("quiz_score", 0.0)
            quiz_passed = state.get("quiz_passed", False)

            update_progress(
                user_id=state["user_id"],
                lesson_id=state["current_lesson_id"],
                score=quiz_score,
                passed=quiz_passed,
            )

            # Get next lesson
            next_lesson_id = get_current_lesson_id(state["user_id"])

            if quiz_passed:
                state["next_action"] = (
                    "next_lesson"
                    if next_lesson_id > state["current_lesson_id"]
                    else "continue"
                )
                state["phase"] = "completed"
            else:
                state["next_action"] = "retry"
                state["phase"] = "teaching"

            logger.info(f"[NODE: update_progress] Next action: {state['next_action']}")

        except Exception as e:
            logger.error(f"[NODE: update_progress] Error: {e}")
            state["error"] = str(e)

        return state

    # ========== ROUTING FUNCTIONS ==========

    def route_after_response(
        self, state: TeachingState
    ) -> Literal["continue", "quiz", "exit"]:
        """Route after generating response"""
        next_action = state.get("next_action", "continue")

        if next_action == "quiz":
            return "quiz"
        elif next_action == "exit":
            return "exit"
        else:
            return "continue"

    def route_after_progress(
        self, state: TeachingState
    ) -> Literal["next_lesson", "retry", "continue"]:
        """Route after updating progress"""
        return state.get("next_action", "continue")

    # ========== EXECUTION ==========

    def run(self, state: TeachingState) -> TeachingState:
        """Execute the graph with initial state (synchronous)"""
        logger.info("[GRAPH] Starting teaching workflow")
        result = self.graph.invoke(state)
        logger.info(f"[GRAPH] Workflow completed, phase: {result.get('phase')}")
        return result

    async def astream(self, state: TeachingState):
        """Execute the graph with streaming (async)"""
        logger.info("[GRAPH] Starting teaching workflow (streaming)")
        async for event in self.graph.astream(state):
            yield event
        logger.info("[GRAPH] Workflow streaming completed")

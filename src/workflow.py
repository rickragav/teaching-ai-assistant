"""
LangGraph Workflow - Teaching State Machine
"""

from typing import Literal
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI, AzureChatOpenAI
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
        if settings.use_azure_openai:
            self.llm = AzureChatOpenAI(
                azure_deployment=settings.azure_openai_deployment,
                azure_endpoint=settings.azure_openai_endpoint,
                api_key=settings.azure_openai_api_key,
                api_version=settings.azure_openai_api_version,
                temperature=settings.temperature,
                max_tokens=settings.max_openai_tokens,
            )
        else:
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
        workflow.add_node("greeting", self.greeting_node)
        workflow.add_node("retrieve_content", self.retrieve_content_node)
        workflow.add_node("generate_response", self.generate_response_node)
        workflow.add_node("generate_quiz", self.generate_quiz_node)
        workflow.add_node("evaluate_quiz", self.evaluate_quiz_node)
        workflow.add_node("update_progress", self.update_progress_node)

        # Set entry point based on whether it's a greeting request
        workflow.set_entry_point("greeting")

        # Add conditional edge from greeting node
        workflow.add_conditional_edges(
            "greeting",
            self.route_after_greeting,
            {"greet": END, "continue": "retrieve_content"},
        )

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

    def greeting_node(self, state: TeachingState) -> TeachingState:
        """Node: Generate greeting based on conversation history"""
        logger.info("[NODE: greeting] Checking if greeting is needed...")

        # Check if this is a greeting request (empty or "__greeting__" input)
        user_input = state.get("user_input", "").strip()
        is_greeting_request = user_input == "" or user_input == "__greeting__"

        if not is_greeting_request:
            logger.info(
                "[NODE: greeting] Not a greeting request, continuing to normal flow"
            )
            state["is_greeting"] = False
            return state

        # This is a greeting request
        state["is_greeting"] = True
        conversation_history = state.get("messages", [])
        has_history = len(conversation_history) > 0

        try:
            if has_history:
                # Returning user - greet based on history
                logger.info("[NODE: greeting] Generating greeting for returning user")
                system_prompt = f"""You are a friendly English grammar teacher for the lesson "{state['lesson_title']}".

The student is returning to continue their learning. Look at their conversation history and:
- Welcome them back warmly
- Briefly reference what you discussed before
- Ask if they want to continue or have questions
- Keep it conversational and encouraging (2-3 sentences)

Conversation History:
{self._format_history_for_prompt(conversation_history[-6:])}
"""
                prompt = (
                    "Generate a warm welcome back message for the returning student."
                )
            else:
                # New user - fresh greeting
                logger.info("[NODE: greeting] Generating greeting for new user")
                system_prompt = f"""You are a friendly English grammar teacher teaching "{state['lesson_title']}".

This is a new student starting this lesson. Greet them warmly and:
- Welcome them to the lesson
- Briefly introduce what they'll learn
- Encourage them and express enthusiasm
- Ask if they're ready to begin
- Keep it warm and inviting (2-3 sentences)
"""
                prompt = "Generate a welcoming introduction for the new student."

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=prompt),
            ]

            response = self.llm.invoke(messages)
            state["teacher_response"] = response.content

            logger.info(
                f"[NODE: greeting] Greeting generated: {response.content[:100]}..."
            )

        except Exception as e:
            logger.error(f"[NODE: greeting] Error: {e}")
            # Fallback greeting
            state["teacher_response"] = (
                f"Hello! Welcome to {state['lesson_title']}. "
                "I'm excited to help you improve your English skills today. Shall we begin?"
            )

        return state

    def _format_history_for_prompt(self, messages: list) -> str:
        """Format conversation history for prompt"""
        formatted = []
        for msg in messages:
            if isinstance(msg, dict):
                role = "Student" if msg["role"] == "user" else "Teacher"
                formatted.append(f"{role}: {msg['content']}")
        return "\n".join(formatted)

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
            system_prompt = f"""You are an expert English grammar teacher teaching "{state['lesson_title']}".

TEACHING GUIDELINES:
- Be conversational, friendly, and encouraging like a real teacher
- Use the provided lesson content to teach accurately
- When introducing a lesson, explain the main concepts clearly with examples
- Break down complex topics into easy-to-understand parts
- Provide real-world examples to illustrate grammar concepts
- Keep responses engaging and informative (2-4 paragraphs)
- Ask if the student has questions after explaining concepts

QUIZ AND PROGRESSION:
- When the student indicates they understand the lesson (e.g., "I'm clear", "I got it", "understood"), offer to test their knowledge with a quiz
- Say something like: "Great! Since you've understood the concepts, would you like to take a short quiz to test your knowledge? It will help reinforce what you've learned."
- If the student agrees to a quiz, end your response with the phrase: [QUIZ_READY]

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
            response_text = response.content

            # Check if teacher is ready to offer quiz
            quiz_ready = "[QUIZ_READY]" in response_text
            if quiz_ready:
                # Remove the marker from the response
                response_text = response_text.replace("[QUIZ_READY]", "").strip()
                state["next_action"] = "quiz"
                logger.info(
                    "[NODE: generate_response] Quiz marker detected, will route to quiz"
                )

            state["teacher_response"] = response_text
            state["llm_response"] = response  # Store raw response for voice streaming

            print(f"✅ RESPONSE GENERATED FROM LANGGRAPH:")
            print(f"{'-'*60}")
            print(f"{response_text}")
            print(f"{'-'*60}\n")

            # Update messages
            state["messages"].append({"role": "user", "content": state["user_input"]})
            state["messages"].append({"role": "assistant", "content": response_text})

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

    def route_after_greeting(
        self, state: TeachingState
    ) -> Literal["greet", "continue"]:
        """Route after greeting node"""
        is_greeting = state.get("is_greeting", False)
        route = "greet" if is_greeting else "continue"
        logger.info(
            f"[ROUTER: greeting] is_greeting={is_greeting} -> routing to '{route}'"
        )
        return route

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

from collections.abc import Coroutine
from typing import Any, AsyncIterable
from livekit.agents.llm.chat_context import ChatContext, ChatMessage
from livekit.agents.llm.llm import ChatChunk
from livekit.agents.llm.tool_context import Tool
from livekit.agents.types import FlushSentinel
from livekit.agents.voice import Agent
from abc import ABC

from livekit.agents.voice.agent import ModelSettings
from livekit.rtc.audio_frame import AudioFrame


class BaseAgent(Agent, ABC):

    def __init__(self, instructions, langgraph=None, *args, **kwargs):
        super().__init__(instructions=instructions, *args, **kwargs)
        self.langgraph = langgraph  # Store the LangGraph instance

    async def llm_node(
        self, chat_ctx: ChatContext, tools: list[Tool], model_settings: ModelSettings
    ) -> (
        AsyncIterable[ChatChunk | str | FlushSentinel]
        | Coroutine[Any, Any, AsyncIterable[ChatChunk | str | FlushSentinel]]
        | Coroutine[Any, Any, str]
        | Coroutine[Any, Any, ChatChunk]
        | Coroutine[Any, Any, None]
    ):
        print("BaseAgent llm_node called")

        # Get the last user message from chat context items
        user_message = ""
        for item in chat_ctx.items:
            if isinstance(item, ChatMessage) and item.role == "user":
                user_message = item.text_content

        # Call LangGraph if available
        if self.langgraph:

            async def stream_from_langgraph():
                # Initialize state with required fields
                state = {
                    "user_id": "console",
                    "current_lesson_id": 1,
                    "lesson_title": "Lesson 1: The Power in Relationships",
                    "messages": [],
                    "user_input": user_message,
                }

                # Stream from LangGraph
                async for event in self.langgraph.astream(state):
                    # LangGraph events are like: {"node_name": {...state...}}
                    # We need to look inside each node's output for teacher_response
                    for node_name, node_output in event.items():
                        if (
                            isinstance(node_output, dict)
                            and "teacher_response" in node_output
                        ):
                            response_text = node_output["teacher_response"]
                            print(
                                f"🎯 Streaming response from LangGraph: {response_text[:100]}..."
                            )
                            # Stream word by word
                            words = response_text.split()
                            for word in words:
                                yield word + " "

            return stream_from_langgraph()
        else:
            # Fallback: Simple test response
            async def stream_response():
                response_text = "Hello! This is a sample response rakesh."
                words = response_text.split()
                for word in words:
                    yield word + " "

            return stream_response()

    async def tts_node(
        self, text: AsyncIterable[str], model_settings: ModelSettings
    ) -> (
        AsyncIterable[AudioFrame]
        | Coroutine[Any, Any, AsyncIterable[AudioFrame]]
        | Coroutine[Any, Any, None]
    ):
        """Clean up ** from text and log before/after with transcription logging."""
        before_chunks = []
        after_chunks = []

        async def process_stream():
            async for chunk in text:
                # Return immediately if chunk is empty
                if not chunk:
                    continue

                before_chunks.append(chunk)

                # Replace inline instead of doing a separate pass
                processed = chunk.replace("**", "'")
                after_chunks.append(processed)

                yield processed  # stream processed chunks immediately

        gen = process_stream()

        async def logging_wrapper():
            async for processed in gen:
                yield processed
            # Log the before/after processing comparison
            print(f"Transcription LLM Before Processed: {''.join(before_chunks)}")
            print(f"Transcription LLM After Processed: {''.join(after_chunks)}")

        return super().tts_node(logging_wrapper(), model_settings)

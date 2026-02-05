"""
Text-to-Speech utility using Deepgram API
"""

import httpx
import re
from typing import AsyncGenerator
from src.config import settings
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class DeepgramTTS:
    """Deepgram Text-to-Speech service"""

    def __init__(self):
        self.api_key = settings.deepgram_api_key
        self.base_url = "https://api.deepgram.com/v1/speak"
        self.model = settings.deepgram_model
        self.encoding = settings.deepgram_encoding
        self.sample_rate = settings.deepgram_sample_rate
        self.max_characters = 2000  # Deepgram TTS character limit per request

    def split_text_into_chunks(self, text: str) -> list[str]:
        """
        Split text into chunks that fit within Deepgram's character limit.
        Splits at sentence boundaries to maintain natural speech flow.

        Args:
            text: Text to split

        Returns:
            List of text chunks, each under max_characters
        """
        if len(text) <= self.max_characters:
            return [text]

        chunks = []
        # Split into sentences (. ! ? followed by space or end of string)
        sentences = re.split(r"(?<=[.!?])\s+", text)

        current_chunk = ""
        for sentence in sentences:
            # If single sentence exceeds limit, split at word boundaries
            if len(sentence) > self.max_characters:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = ""

                # Split long sentence into words
                words = sentence.split()
                for word in words:
                    if len(current_chunk) + len(word) + 1 <= self.max_characters:
                        current_chunk += word + " "
                    else:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                        current_chunk = word + " "
            else:
                # Add sentence to current chunk if it fits
                if len(current_chunk) + len(sentence) + 1 <= self.max_characters:
                    current_chunk += sentence + " "
                else:
                    # Current chunk is full, save it and start new chunk
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = sentence + " "

        # Add remaining chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        return chunks

    async def synthesize_chunk(self, text: str) -> bytes:
        """
        Synthesize a single text chunk to audio.

        Args:
            text: Text to synthesize (must be under max_characters)

        Returns:
            Audio data as bytes
        """
        url = f"{self.base_url}?model={self.model}&encoding={self.encoding}&sample_rate={self.sample_rate}"

        headers = {
            "Authorization": f"Token {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {"text": text}

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.content

    async def text_to_speech_stream(self, text: str) -> AsyncGenerator[bytes, None]:
        """
        Convert text to speech and stream audio data.
        Automatically splits long text into chunks and synthesizes each part.

        Args:
            text: Text to convert to speech (any length)

        Yields:
            Audio data chunks
        """
        if not self.api_key:
            logger.error("DEEPGRAM_API_KEY not configured")
            raise ValueError("Deepgram API key not configured")

        # Split text into manageable chunks
        text_chunks = self.split_text_into_chunks(text)

        if len(text_chunks) > 1:
            logger.info(f"Splitting text into {len(text_chunks)} chunks for TTS")

        try:
            for i, chunk in enumerate(text_chunks, 1):
                logger.info(
                    f"Synthesizing chunk {i}/{len(text_chunks)}: {chunk[:50]}..."
                )

                # Synthesize this chunk
                audio_data = await self.synthesize_chunk(chunk)

                # Yield audio data in smaller pieces for streaming
                chunk_size = 4096
                for j in range(0, len(audio_data), chunk_size):
                    yield audio_data[j : j + chunk_size]

        except httpx.HTTPStatusError as e:
            # Read response content first for streaming responses
            error_detail = ""
            try:
                error_detail = await e.response.aread()
                error_detail = error_detail.decode("utf-8")
            except:
                error_detail = "Unable to read error response"

            logger.error(
                f"Deepgram API error: {e.response.status_code} - {error_detail}"
            )
            raise
        except Exception as e:
            logger.error(f"TTS streaming error: {str(e)}")
            raise


# Global TTS instance
tts_service = DeepgramTTS()

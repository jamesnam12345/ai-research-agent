"""
Claude API utilities for LLM interactions.
Provides standardized interface to Anthropic's Claude models.
"""

from anthropic import Anthropic
import logging
import sys
import os
from typing import Optional

# Add parent directory to path to import config
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from config.settings import settings

logger = logging.getLogger(__name__)


class ClaudeClient:
    """
    Wrapper for Claude API with standardized configuration.
    Provides synchronous text generation using Claude models.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Claude client.

        Args:
            api_key: Anthropic API key (defaults to settings)
        """
        self.api_key = api_key or settings.ANTHROPIC_API_KEY
        self.client = Anthropic(api_key=self.api_key)

    def generate(
        self,
        system_prompt: str,
        user_message: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        model: Optional[str] = None
    ) -> str:
        """
        Generate text using Claude API.

        Args:
            system_prompt: System instructions for Claude
            user_message: User message/prompt
            temperature: Sampling temperature (defaults to settings)
            max_tokens: Max tokens to generate (defaults to settings)
            model: Model to use (defaults to settings)

        Returns:
            Generated text response

        Raises:
            Exception: If API call fails
        """
        temperature = temperature if temperature is not None else settings.CLAUDE_TEMPERATURE
        max_tokens = max_tokens or settings.CLAUDE_MAX_TOKENS
        model = model or settings.CLAUDE_MODEL

        try:
            logger.info(f"Calling Claude API (model={model}, temp={temperature})")

            response = self.client.messages.create(
                model=model,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}],
                temperature=temperature,
                max_tokens=max_tokens
            )

            # Extract text from response
            text = response.content[0].text
            logger.info(f"Claude API call successful ({len(text)} chars)")

            return text

        except Exception as e:
            logger.error(f"Claude API call failed: {str(e)}")
            raise Exception(f"Claude API error: {str(e)}")

    def generate_with_retries(
        self,
        system_prompt: str,
        user_message: str,
        max_retries: int = 3,
        **kwargs
    ) -> str:
        """
        Generate text with automatic retries on failure.

        Args:
            system_prompt: System instructions
            user_message: User message
            max_retries: Maximum number of retry attempts
            **kwargs: Additional arguments passed to generate()

        Returns:
            Generated text response

        Raises:
            Exception: If all retries fail
        """
        last_error = None

        for attempt in range(max_retries):
            try:
                return self.generate(system_prompt, user_message, **kwargs)
            except Exception as e:
                last_error = e
                logger.warning(f"Attempt {attempt + 1}/{max_retries} failed: {str(e)}")

                if attempt < max_retries - 1:
                    logger.info("Retrying...")
                    continue
                else:
                    logger.error(f"All {max_retries} attempts failed")
                    raise last_error

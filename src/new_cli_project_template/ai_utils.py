"""AI processing utilities and helper functions."""

from __future__ import annotations

import sys
from collections.abc import Generator
from pathlib import Path

from par_ai_core.llm_config import LlmConfig, llm_run_manager
from par_ai_core.llm_providers import (
    LlmProvider,
    provider_default_models,
    provider_light_models,
)
from par_ai_core.output_utils import DisplayOutputFormat, display_formatted_output
from par_ai_core.pricing_lookup import PricingDisplay
from par_ai_core.provider_cb_info import get_parai_callback
from rich.console import Console
from rich.panel import Panel
from rich.pretty import Pretty

from .config import AppConfig
from .logging_config import get_logger

logger = get_logger(__name__)


def get_model_name(ai_provider: LlmProvider, model: str | None, light_model: bool) -> str:
    """Get the appropriate model name for the provider.

    Args:
        ai_provider: The AI provider to use
        model: Specific model name (if provided)
        light_model: Whether to use a light/fast model

    Returns:
        The model name to use
    """
    if model:
        return model

    if light_model:
        return provider_light_models[ai_provider]

    return provider_default_models[ai_provider]


def create_llm_config(config: AppConfig) -> LlmConfig:
    """Create LLM configuration from app config.

    Args:
        config: Application configuration

    Returns:
        Configured LlmConfig instance
    """
    model_name = get_model_name(config["ai_provider"], config["model"], config["light_model"])

    logger.debug(f"Creating LLM config for {config['ai_provider'].value} with model {model_name}")

    return LlmConfig(
        provider=config["ai_provider"],
        model_name=model_name,
        temperature=config["temperature"],
        base_url=config["ai_base_url"],
    )


def process_ai_request(
    llm_config: LlmConfig,
    prompt: str,
    system_prompt: str = "You are a helpful assistant.",
    debug: bool = False,
    pricing: PricingDisplay = PricingDisplay.NONE,
) -> str:
    """Process AI request and return response.

    Args:
        llm_config: LLM configuration
        prompt: User prompt
        system_prompt: System prompt
        debug: Enable debug output
        pricing: Pricing display option

    Returns:
        AI response content
    """
    console = Console(stderr=True)

    chat_history = [
        ("system", system_prompt),
        ("user", prompt),
    ]

    if debug:
        console.print(Panel.fit(Pretty(chat_history), title="[bold]AI Prompt", border_style="bold"))

    logger.debug(f"Processing AI request with model: {llm_config.model_name}")

    try:
        with get_parai_callback(show_end=debug, show_pricing=pricing):
            chat_model = llm_config.build_chat_model()
            result = chat_model.invoke(chat_history, config=llm_run_manager.get_runnable_config(chat_model.name))

            if debug:
                console.print(Panel.fit(Pretty(result), title="[bold]AI Response", border_style="bold"))

            logger.debug("AI request processed successfully")
            # Handle content that might be string or list
            if isinstance(result.content, str):
                return result.content
            return str(result.content)

    except Exception as e:
        logger.error(f"AI request failed: {e}")
        raise


def stream_ai_response(
    llm_config: LlmConfig,
    prompt: str,
    system_prompt: str = "You are a helpful assistant.",
    debug: bool = False,
) -> Generator[str, None, None]:
    """Stream AI response for real-time output.

    Args:
        llm_config: LLM configuration
        prompt: User prompt
        system_prompt: System prompt
        debug: Enable debug output

    Yields:
        Response chunks as they arrive
    """
    console = Console(stderr=True)

    chat_history = [
        ("system", system_prompt),
        ("user", prompt),
    ]

    if debug:
        console.print(Panel.fit(Pretty(chat_history), title="[bold]AI Prompt", border_style="bold"))

    logger.debug(f"Starting streaming AI request with model: {llm_config.model_name}")

    try:
        chat_model = llm_config.build_chat_model()

        for chunk in chat_model.stream(chat_history, config=llm_run_manager.get_runnable_config(chat_model.name)):
            if chunk.content:
                # Handle content that might be string or list
                if isinstance(chunk.content, str):
                    yield chunk.content
                else:
                    yield str(chunk.content)

    except Exception as e:
        logger.error(f"Streaming AI request failed: {e}")
        raise


def read_prompt_from_input(
    prompt: str | None = None,
    input_file: Path | None = None,
    stdin: bool = False,
) -> str:
    """Read prompt from various input sources.

    Args:
        prompt: Direct prompt string
        input_file: Path to file containing prompt
        stdin: Read from standard input

    Returns:
        The prompt content

    Raises:
        ValueError: If no valid input source provided
    """
    if prompt:
        logger.debug("Using direct prompt")
        return prompt

    if input_file and input_file.exists():
        logger.debug(f"Reading prompt from file: {input_file}")
        return input_file.read_text(encoding="utf-8").strip()

    if stdin or (not prompt and not input_file):
        logger.debug("Reading prompt from stdin")
        if sys.stdin.isatty():
            console = Console(stderr=True)
            console.print("[yellow]Enter your prompt (press Ctrl+D to finish):[/yellow]")

        content = sys.stdin.read().strip()
        if not content:
            raise ValueError("No input provided")
        return content

    if input_file and not input_file.exists():
        raise ValueError(f"Input file does not exist: {input_file}")

    raise ValueError("No valid input source provided")


def display_response(
    content: str,
    display_format: DisplayOutputFormat = DisplayOutputFormat.MD,
    console: Console | None = None,
) -> None:
    """Display AI response in the specified format.

    Args:
        content: Response content to display
        display_format: Output format
        console: Console instance (uses default if None)
    """
    if console is None:
        console = Console()

    display_formatted_output(content, display_format, console=console)


# TODO: Add your custom AI processing functions here
# Examples:


def summarize_text(text: str, llm_config: LlmConfig) -> str:
    """Summarize the given text.

    Args:
        text: Text to summarize
        llm_config: LLM configuration

    Returns:
        Summary of the text
    """
    system_prompt = "You are an expert at summarizing text. Provide a concise summary of the main points."
    prompt = f"Please summarize the following text:\n\n{text}"

    return process_ai_request(llm_config, prompt, system_prompt)


def translate_text(text: str, target_language: str, llm_config: LlmConfig) -> str:
    """Translate text to the target language.

    Args:
        text: Text to translate
        target_language: Target language for translation
        llm_config: LLM configuration

    Returns:
        Translated text
    """
    system_prompt = f"You are an expert translator. Translate the given text to {target_language}."
    prompt = f"Please translate the following text:\n\n{text}"

    return process_ai_request(llm_config, prompt, system_prompt)


def analyze_code(code: str, llm_config: LlmConfig) -> str:
    """Analyze code and provide insights.

    Args:
        code: Code to analyze
        llm_config: LLM configuration

    Returns:
        Code analysis and suggestions
    """
    system_prompt = (
        "You are a code review expert. Analyze the code and provide insights, suggestions, and potential improvements."
    )
    prompt = f"Please analyze the following code:\n\n```\n{code}\n```"

    return process_ai_request(llm_config, prompt, system_prompt)

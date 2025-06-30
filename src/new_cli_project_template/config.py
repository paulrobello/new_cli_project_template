"""Configuration management for the application."""

from __future__ import annotations

import os
import tomllib
from pathlib import Path
from typing import TypedDict

from par_ai_core.llm_providers import LlmProvider, provider_env_key_names
from pydantic import BaseModel, Field
from rich.console import Console

from . import __application_binary__


class AppConfig(TypedDict):
    """Application configuration type."""

    ai_provider: LlmProvider
    model: str | None
    light_model: bool
    ai_base_url: str | None
    temperature: float
    debug: bool


class ConfigFile(BaseModel):
    """Configuration file structure."""

    ai_provider: LlmProvider = LlmProvider.OPENAI
    model: str | None = None
    light_model: bool = False
    ai_base_url: str | None = None
    temperature: float = Field(default=0.5, ge=0.0, le=2.0)
    debug: bool = False


def get_config_file_path() -> Path:
    """Get the path to the configuration file."""
    # Check for config file in current directory first, then home directory
    local_config = Path("config.toml")
    if local_config.exists():
        return local_config

    home_config = Path.home() / f".{__application_binary__}.toml"
    return home_config


def load_config_file() -> ConfigFile:
    """Load configuration from file if it exists."""
    config_path = get_config_file_path()

    if not config_path.exists():
        return ConfigFile()

    try:
        with open(config_path, "rb") as f:
            config_data = tomllib.load(f)
        return ConfigFile(**config_data)
    except Exception as e:
        console = Console(stderr=True)
        console.print(f"[yellow]Warning: Failed to load config file {config_path}: {e}[/yellow]")
        console.print("[yellow]Using default configuration.[/yellow]")
        return ConfigFile()


def validate_environment(ai_provider: LlmProvider) -> None:
    """Validate required environment variables are set."""
    console = Console(stderr=True)

    # Providers that don't require API keys
    no_key_providers = {LlmProvider.OLLAMA, LlmProvider.LLAMACPP, LlmProvider.BEDROCK}

    if ai_provider in no_key_providers:
        return

    key_name = provider_env_key_names[ai_provider]
    if not os.environ.get(key_name):
        console.print(f"[bold red]Missing {key_name} environment variable for {ai_provider.value}[/bold red]")
        console.print("[yellow]Please set the required API key in your environment.[/yellow]")
        console.print(f"[yellow]You can add it to your .env file or ~/.{__application_binary__}.env[/yellow]")
        raise ValueError(f"Missing required environment variable: {key_name}")


def create_example_config() -> None:
    """Create an example configuration file."""
    config_path = Path("config.toml")

    if config_path.exists():
        console = Console(stderr=True)
        console.print(f"[yellow]Config file {config_path} already exists.[/yellow]")
        return

    example_config = """# Example configuration file for new_cli_project_template
# Copy this to config.toml and adjust as needed

# AI Provider configuration
ai_provider = "OpenAI"  # Options: OpenAI, Anthropic, Google, Groq, XAI, Mistral, Bedrock, Ollama, LlamaCpp
model = ""  # Leave empty to use default model for provider
light_model = false  # Use lighter/faster model variant
ai_base_url = ""  # Custom base URL for OpenAI-compatible providers
temperature = 0.5  # Response creativity (0.0-2.0)
debug = false  # Enable debug output

# TODO: Add your custom configuration options here
# Examples:
# max_tokens = 1000
# system_prompt = "You are a helpful assistant."
# output_format = "markdown"
"""

    with open(config_path, "w", encoding="utf-8") as f:
        f.write(example_config)

    console = Console(stderr=True)
    console.print(f"[green]Created example config file: {config_path}[/green]")
    console.print("[yellow]Please edit it with your preferred settings.[/yellow]")


def merge_config(
    file_config: ConfigFile,
    cli_ai_provider: LlmProvider | None = None,
    cli_model: str | None = None,
    cli_light_model: bool | None = None,
    cli_ai_base_url: str | None = None,
    cli_temperature: float | None = None,
    cli_debug: bool | None = None,
) -> AppConfig:
    """Merge configuration from file and CLI arguments."""
    # CLI arguments override file configuration
    return AppConfig(
        ai_provider=cli_ai_provider or file_config.ai_provider,
        model=cli_model or file_config.model,
        light_model=cli_light_model if cli_light_model is not None else file_config.light_model,
        ai_base_url=cli_ai_base_url or file_config.ai_base_url,
        temperature=cli_temperature if cli_temperature is not None else file_config.temperature,
        debug=cli_debug if cli_debug is not None else file_config.debug,
    )

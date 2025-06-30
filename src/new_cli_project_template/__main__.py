"""Main application with improved CLI structure and features."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from dotenv import load_dotenv
from par_ai_core.llm_providers import LlmProvider
from par_ai_core.output_utils import DisplayOutputFormat
from par_ai_core.pricing_lookup import PricingDisplay
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text

from . import __application_binary__, __application_title__, __version__
from .ai_utils import (
    analyze_code,
    create_llm_config,
    display_response,
    process_ai_request,
    read_prompt_from_input,
    stream_ai_response,
    summarize_text,
    translate_text,
)
from .config import (
    create_example_config,
    load_config_file,
    merge_config,
    validate_environment,
)
from .logging_config import get_logger, setup_logging

# Create the main Typer app with rich help
app = typer.Typer(
    name=__application_binary__,
    help=f"{__application_title__} - A starter template for AI-powered CLI applications",
    rich_markup_mode="rich",
    add_completion=False,
)
console = Console(stderr=True)
logger = get_logger(__name__)

# Load environment variables
load_dotenv()
load_dotenv(Path(f"~/.{__application_binary__}.env").expanduser())


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        console.print(f"[bold blue]{__application_title__}[/bold blue] version [bold green]{__version__}[/bold green]")
        raise typer.Exit()


def display_configuration(
    ai_provider: LlmProvider,
    model: str,
    light_model: bool,
    ai_base_url: str | None,
    temperature: float,
    debug: bool,
    pricing: PricingDisplay,
    display_format: DisplayOutputFormat,
) -> None:
    """Display current configuration in a formatted panel."""
    console.print(
        Panel.fit(
            Text.assemble(
                ("AI Provider: ", "cyan"),
                (f"{ai_provider.value}", "green"),
                "\n",
                ("Model: ", "cyan"),
                (f"{model}", "green"),
                "\n",
                ("Light Model: ", "cyan"),
                (f"{light_model}", "green"),
                "\n",
                ("Base URL: ", "cyan"),
                (f"{ai_base_url or 'default'}", "green"),
                "\n",
                ("Temperature: ", "cyan"),
                (f"{temperature}", "green"),
                "\n",
                ("Debug: ", "cyan"),
                (f"{debug}", "green"),
                "\n",
                ("Pricing: ", "cyan"),
                (f"{pricing.value}", "green"),
                "\n",
                ("Display Format: ", "cyan"),
                (f"{display_format.value}", "green"),
            ),
            title="[bold]Configuration",
            border_style="bold",
        )
    )


@app.command("process")
def process_command(
    prompt: Annotated[
        str | None,
        typer.Option(
            "--prompt",
            "-p",
            help="Prompt to send to AI (use quotes for multi-word prompts)",
        ),
    ] = None,
    input_file: Annotated[
        Path | None,
        typer.Option(
            "--input-file",
            "-i",
            help="Read prompt from file",
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
        ),
    ] = None,
    system_prompt: Annotated[
        str,
        typer.Option(
            "--system-prompt",
            "-s",
            help="System prompt to use",
        ),
    ] = "You are a helpful assistant.",
    ai_provider: Annotated[
        LlmProvider | None,
        typer.Option("--ai-provider", "-a", help="AI provider to use"),
    ] = None,
    model: Annotated[
        str | None,
        typer.Option(
            "--model",
            "-m",
            help="AI model to use (overrides config file)",
        ),
    ] = None,
    light_model: Annotated[
        bool | None,
        typer.Option(
            "--light-model",
            "-l",
            help="Use a lighter/faster model variant",
        ),
    ] = None,
    ai_base_url: Annotated[
        str | None,
        typer.Option(
            "--ai-base-url",
            "-b",
            help="Override the base URL for the AI provider",
        ),
    ] = None,
    temperature: Annotated[
        float | None,
        typer.Option(
            "--temperature",
            "-t",
            help="Temperature for response creativity (0.0-2.0)",
            min=0.0,
            max=2.0,
        ),
    ] = None,
    pricing: Annotated[
        PricingDisplay,
        typer.Option("--pricing", help="Show pricing information"),
    ] = PricingDisplay.NONE,
    display_format: Annotated[
        DisplayOutputFormat,
        typer.Option(
            "--output",
            "-o",
            help="Output format (md, json, csv)",
        ),
    ] = DisplayOutputFormat.MD,
    stream: Annotated[
        bool,
        typer.Option(
            "--stream",
            help="Stream response in real-time",
        ),
    ] = False,
    debug: Annotated[
        bool,
        typer.Option(
            "--debug",
            help="Enable debug mode with verbose output",
        ),
    ] = False,
    version: Annotated[
        bool | None,
        typer.Option("--version", "-v", callback=version_callback, is_eager=True),
    ] = None,
) -> None:
    """Process a prompt with AI and display the response.

    Examples:
        # Simple prompt
        new_cli_project_template process -p "Hello, world!"

        # From file
        new_cli_project_template process -i prompt.txt

        # From stdin
        echo "Hello!" | new_cli_project_template process

        # With custom system prompt
        new_project_template process -p "Explain AI" -s "You are a teacher"

        # Stream response
        new_project_template process -p "Write a story" --stream
    """
    try:
        # Setup logging
        setup_logging(debug=debug)
        logger.debug("Starting process command")

        # Load and merge configuration
        file_config = load_config_file()
        config = merge_config(
            file_config,
            cli_ai_provider=ai_provider,
            cli_model=model,
            cli_light_model=light_model,
            cli_ai_base_url=ai_base_url,
            cli_temperature=temperature,
            cli_debug=debug,
        )

        # Validate environment
        validate_environment(config["ai_provider"])

        # Create LLM configuration
        llm_config = create_llm_config(config)

        # Display configuration if debug mode
        if debug:
            from .ai_utils import get_model_name

            model_name = get_model_name(config["ai_provider"], config["model"], config["light_model"])
            display_configuration(
                config["ai_provider"],
                model_name,
                config["light_model"],
                config["ai_base_url"],
                config["temperature"],
                config["debug"],
                pricing,
                display_format,
            )

        # Read prompt from input
        stdin_mode = prompt is None and input_file is None
        prompt_text = read_prompt_from_input(
            prompt=prompt,
            input_file=input_file,
            stdin=stdin_mode,
        )

        logger.debug(f"Processing prompt of length: {len(prompt_text)}")

        # Process AI request
        if stream:
            # Stream response
            console.print("[dim]Streaming response...[/dim]")
            response_parts = []
            try:
                for chunk in stream_ai_response(llm_config, prompt_text, system_prompt, debug):
                    console.print(chunk, end="")
                    response_parts.append(chunk)
                console.print()  # New line at end
            except KeyboardInterrupt:
                console.print("\n[yellow]Response interrupted by user[/yellow]")
                raise typer.Exit(0)
        else:
            # Regular response
            response = process_ai_request(llm_config, prompt_text, system_prompt, debug, pricing)
            display_response(response, display_format, console)

        logger.debug("Process command completed successfully")

    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        raise typer.Exit(0)
    except Exception as e:
        logger.error(f"Process command failed: {e}")
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        if debug:
            console.print_exception()
        raise typer.Exit(code=1)


@app.command("chat")
def chat_command(
    system_prompt: Annotated[
        str,
        typer.Option(
            "--system-prompt",
            "-s",
            help="System prompt for the chat session",
        ),
    ] = "You are a helpful assistant.",
    ai_provider: Annotated[
        LlmProvider | None,
        typer.Option("--ai-provider", "-a", help="AI provider to use"),
    ] = None,
    model: Annotated[
        str | None,
        typer.Option("--model", "-m", help="AI model to use"),
    ] = None,
    debug: Annotated[
        bool,
        typer.Option("--debug", help="Enable debug mode"),
    ] = False,
) -> None:
    """Start an interactive chat session with the AI.

    Examples:
        # Basic chat
        new_project_template chat

        # Custom system prompt
        new_project_template chat -s "You are a coding assistant"

        # Specific model
        new_project_template chat -m gpt-4
    """
    try:
        setup_logging(debug=debug)
        console.print("[bold blue]Starting interactive chat session[/bold blue]")
        console.print("[dim]Type 'quit', 'exit', or press Ctrl+C to end the session[/dim]\n")

        # Load configuration
        file_config = load_config_file()
        config = merge_config(
            file_config,
            cli_ai_provider=ai_provider,
            cli_model=model,
            cli_debug=debug,
        )

        validate_environment(config["ai_provider"])
        llm_config = create_llm_config(config)

        # Chat loop
        while True:
            try:
                user_input = Prompt.ask("[bold green]You[/bold green]").strip()

                if user_input.lower() in {"quit", "exit", "q"}:
                    console.print("[yellow]Goodbye![/yellow]")
                    break

                if not user_input:
                    continue

                console.print("[bold blue]AI:[/bold blue] ", end="")
                for chunk in stream_ai_response(llm_config, user_input, system_prompt, debug):
                    console.print(chunk, end="")
                console.print("\n")

            except (EOFError, KeyboardInterrupt):
                console.print("\n[yellow]Goodbye![/yellow]")
                break

    except Exception as e:
        logger.error(f"Chat command failed: {e}")
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise typer.Exit(code=1)


@app.command("config")
def config_command(
    create: Annotated[
        bool,
        typer.Option("--create", help="Create an example configuration file"),
    ] = False,
    show: Annotated[
        bool,
        typer.Option("--show", help="Show current configuration"),
    ] = False,
) -> None:
    """Manage application configuration.

    Examples:
        # Create example config file
        new_project_template config --create

        # Show current configuration
        new_project_template config --show
    """
    if create:
        create_example_config()
        return

    if show:
        from .config import get_config_file_path

        config_file = load_config_file()
        config_path = get_config_file_path()

        console.print(
            Panel.fit(
                Text.assemble(
                    ("Config File: ", "cyan"),
                    (f"{config_path}", "green" if config_path.exists() else "red"),
                    "\n",
                    ("AI Provider: ", "cyan"),
                    (f"{config_file.ai_provider.value}", "green"),
                    "\n",
                    ("Model: ", "cyan"),
                    (f"{config_file.model or 'default'}", "green"),
                    "\n",
                    ("Light Model: ", "cyan"),
                    (f"{config_file.light_model}", "green"),
                    "\n",
                    ("Temperature: ", "cyan"),
                    (f"{config_file.temperature}", "green"),
                    "\n",
                    ("Debug: ", "cyan"),
                    (f"{config_file.debug}", "green"),
                ),
                title="[bold]Current Configuration",
                border_style="bold",
            )
        )
        return

    # Default: show help
    console.print("[yellow]Use --create to create example config or --show to display current config[/yellow]")


# TODO: Add your custom commands here
# Examples:


@app.command("summarize")
def summarize_command(
    input_file: Annotated[
        Path,
        typer.Argument(help="File to summarize"),
    ],
    output_file: Annotated[
        Path | None,
        typer.Option("--output", "-o", help="Output file (default: stdout)"),
    ] = None,
) -> None:
    """Summarize text from a file.

    Example:
        new_project_template summarize document.txt -o summary.txt
    """
    try:
        setup_logging()

        if not input_file.exists():
            console.print(f"[red]File not found: {input_file}[/red]")
            raise typer.Exit(1)

        text = input_file.read_text(encoding="utf-8")
        file_config = load_config_file()
        config = merge_config(file_config)
        validate_environment(config["ai_provider"])
        llm_config = create_llm_config(config)

        summary = summarize_text(text, llm_config)

        if output_file:
            output_file.write_text(summary, encoding="utf-8")
            console.print(f"[green]Summary saved to: {output_file}[/green]")
        else:
            display_response(summary, DisplayOutputFormat.MD, console)

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise typer.Exit(code=1)


@app.command("translate")
def translate_command(
    text: Annotated[str, typer.Argument(help="Text to translate")],
    language: Annotated[str, typer.Argument(help="Target language")],
) -> None:
    """Translate text to another language.

    Example:
        new_project_template translate "Hello world" Spanish
    """
    try:
        setup_logging()

        file_config = load_config_file()
        config = merge_config(file_config)
        validate_environment(config["ai_provider"])
        llm_config = create_llm_config(config)

        translation = translate_text(text, language, llm_config)
        display_response(translation, DisplayOutputFormat.MD, console)

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise typer.Exit(code=1)


@app.command("analyze-code")
def analyze_code_command(
    input_file: Annotated[
        Path,
        typer.Argument(help="Code file to analyze"),
    ],
) -> None:
    """Analyze code and provide insights.

    Example:
        new_project_template analyze-code script.py
    """
    try:
        setup_logging()

        if not input_file.exists():
            console.print(f"[red]File not found: {input_file}[/red]")
            raise typer.Exit(1)

        code = input_file.read_text(encoding="utf-8")
        file_config = load_config_file()
        config = merge_config(file_config)
        validate_environment(config["ai_provider"])
        llm_config = create_llm_config(config)

        analysis = analyze_code(code, llm_config)
        display_response(analysis, DisplayOutputFormat.MD, console)

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()

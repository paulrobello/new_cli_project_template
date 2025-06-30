# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a comprehensive Python project template built with modern tooling that provides a robust foundation for AI-powered CLI applications. The project features a multi-command CLI interface, configuration management, logging, and comprehensive AI integration through PAR AI Core. It demonstrates best practices for Python development including proper error handling, type safety, and modular architecture.

## Development Commands

### Core Development Workflow
- `make checkall` - Format code, run linter, and type check (run after any code changes)
- `uv run new_cli_project_template --help` - Show all available commands
- `uv run new_cli_project_template process -p "Your prompt"` - Process a single prompt
- `uv run new_cli_project_template chat` - Start interactive chat session
- `uv run new_cli_project_template config --create` - Create example config file

### Package Management
- `uv sync` - Sync dependencies (equivalent to pip install)
- `uv add <package>` - Add new dependencies
- `uv remove <package>` - Remove dependencies
- `make depsupdate` - Update all dependencies
- `make setup` - Initial setup (uv lock + sync)

### Individual Tools
- `make format` - Format code with ruff
- `make lint` - Run ruff linter with fixes
- `make typecheck` - Run pyright type checker
- `uv run pyright` - Type checking
- `uv run ruff check src/new_cli_project_template --fix` - Lint with fixes

### Configuration Management
- `config.toml` - Local project configuration (created with `config --create`)
- `~/.new_cli_project_template.toml` - Global user configuration
- `.env` and `~/.new_cli_project_template.env` - Environment variables
- Configuration precedence: CLI args > config file > environment > defaults

### Testing and Quality
- `make profile` - Profile with scalene
- `make profile2` - Profile with pyinstrument
- `make pre-commit` - Run pre-commit hooks

## Project Architecture

### Core Structure
- **src/new_cli_project_template/**: Main package directory
  - `__init__.py`: Package metadata, version, and application constants
  - `__main__.py`: Multi-command CLI application with improved structure
  - `config.py`: Configuration management with TOML support
  - `logging_config.py`: Logging setup with Rich integration
  - `ai_utils.py`: AI processing utilities and example functions
- **Entry point**: `new_cli_project_template.__main__:app` (Typer CLI with multiple commands)

### AI Integration
- Built on PAR AI Core library for multi-provider AI support
- Supports: OpenAI, Anthropic, Google, Groq, XAI, Mistral, Bedrock, Ollama, LlamaCpp
- Multiple input methods: direct prompt, file input, or stdin
- Streaming and non-streaming response modes
- Environment variables for API keys (see .env.example for complete list)
- LLM configuration with model selection, temperature control, and pricing display
- Example AI functions: summarize, translate, analyze code

### Key Dependencies
- `typer` - CLI framework with rich annotations
- `par-ai-core` - Multi-provider AI integration
- `rich` - Terminal output formatting
- `python-dotenv` - Environment variable loading
- `tomli-w` - TOML configuration file support
- `pydantic` - Data validation for configuration

### CLI Commands
- **process**: Process a single prompt with various input options
- **chat**: Interactive chat session with streaming responses
- **config**: Manage configuration files (create examples, show current)
- **summarize**: Summarize text from files
- **translate**: Translate text to different languages
- **analyze-code**: Analyze code files and provide insights

### Configuration
- **ruff**: Line length 120, Google-style docstrings, modern Python (3.11+)
- **pyright**: Basic type checking mode, Python 3.12 target
- **Environment**: Loads from `.env` and `~/.new_cli_project_template.env`
- **Config files**: TOML format with validation and layered configuration

### Development Standards
- Python 3.11+ required
- Type annotations mandatory
- Google-style docstrings
- Uses `uv` for package management
- Follows src/ layout pattern
- UTF-8 encoding for all file operations
- Comprehensive error handling with user-friendly messages
- Logging with Rich integration
- Modular architecture with separation of concerns

### Template Customization Points
- Add custom commands in `__main__.py` (marked with TODO comments)
- Extend configuration options in `config.py`
- Add custom AI functions in `ai_utils.py`
- Modify logging configuration in `logging_config.py`
- Update environment variables in `.env.example`
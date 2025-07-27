# New CLI Project Template

## Description
A comprehensive Python project template for building AI-powered CLI applications. This template provides a robust foundation with multi-command CLI interface, configuration management, logging, and extensive AI integration through PAR AI Core.

**Note**: This is a template repository designed to be used with [bootstrap_project](https://github.com/paulrobello/bootstrap_project) for quickly creating new Python projects. When used with bootstrap_project, all references to "new_cli_project_template" will be automatically replaced with your chosen project name.

## Features

- **Multi-Command CLI**: Process prompts, interactive chat, configuration management, and example AI tools
- **Multiple AI Providers**: OpenAI, Anthropic, Google, Groq, XAI, Mistral, Bedrock, Ollama, LlamaCpp
- **Flexible Input**: Direct prompts, file input, or stdin
- **Configuration Management**: YAML files with layered configuration system
- **Rich Terminal UI**: Beautiful output with Rich library integration
- **Streaming Responses**: Real-time AI output with proper error handling
- **Type Safety**: Full type annotations throughout
- **Modern Tooling**: Built with uv, ruff, pyright, and Python 3.11+

## Technology Stack
- **Python 3.11+** - Modern Python with latest features
- **[PAR AI Core](https://github.com/paulrobello/par_ai_core)** - Multi-provider AI integration
- **Typer** - Modern CLI framework with Rich integration
- **Rich** - Beautiful terminal output and formatting
- **PyYAML** - YAML configuration file support
- **Pydantic** - Data validation and configuration
- **uv** - Fast Python package management


## Using as a Template

The recommended way to use this template is with [bootstrap_project](https://github.com/paulrobello/bootstrap_project):

```bash
# Install bootstrap_project
uv tool install bootstrap_project

# Create a new project from this template
bsp --project-name my_awesome_project

# Create with additional packages
bsp --project-name my_ai_app --packages par-ai-core
```

This will:
- Create a new project with your chosen name
- Replace all instances of `new_cli_project_template` with your project name
- Set up git repository
- Install dependencies
- Be ready for development!

## Prerequisites

- Python 3.11 or higher (3.11, 3.12, 3.13 supported)
- An API key for at least one AI provider (see [API Keys](#api-keys) section)
- [uv](https://docs.astral.sh/uv/) for package management (recommended) or pip

## Quick Start

### 1. Installation

#### From PyPI (when published)
```shell
uv tool install new_cli_project_template
```

#### From Source
```shell
# Clone the repository
git clone https://github.com/paulrobello/new_cli_project_template.git
cd new_cli_project_template

# Install dependencies
uv sync

# Run the application
uv run new_cli_project_template --help
```

### 2. Setup Configuration

```shell
# Create example configuration file
uv run new_cli_project_template config --create

# Copy example environment file
cp .env.example .env

# Edit .env with your API keys
# At minimum, set one AI provider key (e.g., OPENAI_API_KEY)
```

### 3. Basic Usage

```shell
# Simple prompt processing
uv run new_cli_project_template process -p "Hello, world!"

# Start interactive chat
uv run new_cli_project_template chat

# View all available commands
uv run new_cli_project_template --help
```

## Commands

### Core Commands

#### `process` - Process a single prompt
```shell
# Simple prompt
new_cli_project_template process -p "Explain quantum computing"

# From file
new_cli_project_template process -i prompt.txt

# From stdin
echo "Hello AI!" | new_cli_project_template process

# With custom system prompt
new_cli_project_template process -p "Write a poem" -s "You are Shakespeare"

# Stream response in real-time
new_cli_project_template process -p "Tell me a story" --stream

# Specify AI provider and model
new_cli_project_template process -p "Hello" -a Anthropic -m claude-3-sonnet

# Debug mode with detailed output
new_cli_project_template process -p "Test" --debug
```

#### `chat` - Interactive chat session
```shell
# Basic chat
new_cli_project_template chat

# Chat with custom system prompt
new_cli_project_template chat -s "You are a coding assistant"

# Chat with specific model
new_cli_project_template chat -m gpt-4

# Debug chat session
new_cli_project_template chat --debug
```

#### `config` - Configuration management
```shell
# Create example configuration file
new_cli_project_template config --create

# Show current configuration
new_cli_project_template config --show
```

### Example AI Tools

#### `summarize` - Summarize text files
```shell
# Summarize to stdout
new_cli_project_template summarize document.txt

# Save summary to file
new_cli_project_template summarize document.txt -o summary.txt
```

#### `translate` - Translate text
```shell
# Translate text
new_cli_project_template translate "Hello world" Spanish
new_cli_project_template translate "Bonjour le monde" English
```

#### `analyze-code` - Code analysis
```shell
# Analyze Python file
new_cli_project_template analyze-code script.py

# Analyze any code file
new_cli_project_template analyze-code main.js
```

## Configuration

### Configuration Files

The application supports layered configuration:

1. **CLI arguments** (highest priority)
2. **Configuration files** (`config.yaml` or `~/.new_cli_project_template.yaml`)
3. **Environment variables** (`.env` or `~/.new_cli_project_template.env`)
4. **Defaults** (lowest priority)

#### Create Configuration File
```shell
# Creates config.yaml in current directory
new_cli_project_template config --create
```

Example `config.yaml`:
```yaml
# AI Provider Configuration
ai_provider: "OpenAI"  # Options: OpenAI, Anthropic, Google, Groq, XAI, Mistral, Bedrock, Ollama, LlamaCpp
model: ""  # Leave empty for default model for provider
light_model: false  # Use lighter/faster model variants when available
ai_base_url: ""  # Custom base URL for OpenAI-compatible API endpoints
temperature: 0.7  # Response creativity level (0.0 = deterministic, 2.0 = very creative)
debug: false  # Enable debug output and detailed logging

# Advanced Configuration Examples (uncomment and modify as needed):
# max_tokens: 4000  # Maximum tokens in response
# system_prompt: "You are a helpful assistant specialized in Python programming."
# timeout: 30  # Request timeout in seconds
# retry_attempts: 3  # Number of retry attempts for failed requests
# 
# Custom endpoints for different providers:
# custom_endpoints:
#   - name: "local_ollama"
#     url: "http://localhost:11434"
#   - name: "custom_openai"
#     url: "https://api.your-domain.com/v1"
```

### YAML Configuration Reference

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `ai_provider` | string | "OpenAI" | AI provider to use (see supported providers above) |
| `model` | string | "" | Specific model name (leave empty for provider default) |
| `light_model` | boolean | false | Use faster/cheaper model variants when available |
| `ai_base_url` | string | "" | Custom API endpoint URL for OpenAI-compatible providers |
| `temperature` | float | 0.5 | Creativity level (0.0-2.0, where 0.0 is deterministic) |
| `debug` | boolean | false | Enable detailed debug output and logging |

### Global vs Local Configuration

- **Local**: `config.yaml` in your current directory (project-specific)
- **Global**: `~/.new_cli_project_template.yaml` in your home directory (user-wide defaults)
- **Priority**: Local config overrides global config, CLI args override both

### Environment Variables

Copy `.env.example` to `.env` and configure:

```shell
# Required: At least one AI provider API key
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
GROQ_API_KEY=your_groq_api_key_here
# ... (see .env.example for complete list)
```

### API Keys

Get API keys from these providers:

- **OpenAI**: [platform.openai.com](https://platform.openai.com/account/api-keys)
- **Anthropic**: [console.anthropic.com](https://console.anthropic.com/)
- **Google**: [console.cloud.google.com](https://console.cloud.google.com)
- **Groq**: [console.groq.com](https://console.groq.com/)
- **XAI**: [x.ai/api](https://x.ai/api)
- **Mistral**: [console.mistral.ai](https://console.mistral.ai/)
- **OpenRouter**: [openrouter.ai](https://openrouter.ai/)
- **GitHub Models**: [github.com/marketplace/models](https://github.com/marketplace/models) (free)

**Local Models** (no API key required):
- **Ollama**: Install from [ollama.ai](https://ollama.ai)
- **LlamaCpp**: For local GGUF model files

**AWS Bedrock**: Configure AWS credentials via `AWS_PROFILE` or `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY`


## Development

### Setup Development Environment

```shell
# Clone repository
git clone https://github.com/paulrobello/new_cli_project_template.git
cd new_cli_project_template

# Install dependencies
uv sync

# Run tests and linting
make checkall

# Run the application
uv run new_cli_project_template --help
```

### Common Development Tasks

```shell
# Format, lint, and type check
make checkall

# Individual tools
make format      # Format with ruff
make lint        # Lint with ruff
make typecheck   # Type check with pyright

# Update dependencies
uv sync -U

# Build package
uv build
```

### Adding Custom Commands

The template is designed for easy extension:

1. **Add new commands** in `src/new_cli_project_template/__main__.py`
2. **Add AI utilities** in `src/new_cli_project_template/ai_utils.py`
3. **Extend configuration** in `src/new_cli_project_template/config.py`
4. **Update help text** and examples

Look for `# TODO` comments for specific extension points.

## Examples

### Real-World Usage Examples

```shell
# Content creation workflow
echo "Write a blog post about Python async programming" | \
  new_cli_project_template process -s "You are a technical writer" > blog_post.md

# Code review assistant
new_cli_project_template analyze-code my_script.py

# Document translation
new_cli_project_template translate "$(cat document.txt)" French > document_fr.txt

# Interactive AI assistant
new_cli_project_template chat -s "You are a helpful coding assistant"

# Batch processing with different models
for file in *.txt; do
  new_cli_project_template summarize "$file" -o "summary_${file}"
done
```

### Integration Examples

```shell
# Use with other tools
git log --oneline -10 | \
  new_cli_project_template process -p "Summarize these git commits"

# Process clipboard content (macOS)
pbpaste | new_cli_project_template process -p "Fix grammar and spelling"

# Combine with jq for structured output
new_cli_project_template process -p "List 5 Python tips" -o json | jq '.'
```
## What's New

### Version 0.1.0
- **Multi-Command CLI**: Comprehensive command structure with `process`, `chat`, `config`, and example tools
- **YAML Configuration**: Modern YAML-based configuration system with layered settings
- **Rich Terminal UI**: Beautiful output with syntax highlighting and formatting
- **Streaming Responses**: Real-time AI output for better user experience
- **Multiple Input Methods**: Direct prompts, file input, and stdin support
- **Type Safety**: Full type annotations and validation throughout
- **Modular Architecture**: Clean separation of concerns with extensible design
- **Example AI Tools**: Summarization, translation, and code analysis examples
- **Comprehensive Documentation**: Detailed usage examples and development guide
- **Modern Tooling**: Built with uv, ruff, pyright, and Python 3.11+
- **Quality Assurance**: Pre-commit hooks, automated formatting, and type checking
- **Template Ready**: Designed for easy customization and extension

## Template Customization

When creating a new project from this template, you'll want to customize it for your specific needs:

### Key Customization Points

1. **Commands** (`__main__.py`): Add your own CLI commands
2. **AI Functions** (`ai_utils.py`): Implement domain-specific AI tools
3. **Configuration** (`config.py`): Extend configuration options
4. **Dependencies** (`pyproject.toml`): Add project-specific packages

### Files Automatically Updated

When using bootstrap_project, these files are automatically updated with your project name:
- `pyproject.toml` - Project metadata and dependencies
- `README.md` - Documentation
- `CLAUDE.md` - Development instructions
- `src/new_cli_project_template/*.py` - All Python source files
- `.env` - Environment configuration
- `Makefile` - Build commands
- `.github-disabled/workflows/*.yml` - CI/CD workflows

## Contributing

Contributions are welcome! This template is designed to be a starting point for AI-powered CLI applications.

### How to Contribute

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run `make checkall` to ensure code quality
5. Submit a pull request

### Areas for Contribution

- Additional AI tool examples
- Support for more AI providers
- Enhanced configuration options
- Better error handling and user experience
- Documentation improvements
- Performance optimizations

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

Paul Robello - probello@gmail.com

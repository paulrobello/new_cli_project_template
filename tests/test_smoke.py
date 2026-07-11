"""Smoke tests for the new_cli_project_template package."""

from new_cli_project_template import __application_title__, __version__


def test_version_is_defined() -> None:
    """The package exposes a non-empty version string."""
    assert isinstance(__version__, str)
    assert __version__


def test_application_title_is_defined() -> None:
    """The package exposes a non-empty application title."""
    assert isinstance(__application_title__, str)
    assert __application_title__


def test_cli_app_builds() -> None:
    """The Typer application is importable and has registered commands."""
    from new_cli_project_template.__main__ import app

    assert app.registered_commands

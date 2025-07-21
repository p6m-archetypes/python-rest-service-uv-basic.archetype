#!/usr/bin/env python3
"""
Development Environment Setup Script

This script helps set up the development environment for {{ PrefixName }}{{ SuffixName }}
using uv for dependency management.
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], description: str) -> bool:
    """
    Run a command and return True if successful.
    
    Args:
        cmd: Command to run as list of strings
        description: Description of what the command does
        
    Returns:
        True if command succeeded, False otherwise
    """
    print(f"📦 {description}...")
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False
    except FileNotFoundError:
        print(f"❌ Command not found: {cmd[0]}")
        return False


def check_uv_installed() -> bool:
    """Check if uv is installed."""
    try:
        subprocess.run(["uv", "--version"], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def install_uv() -> bool:
    """Install uv if not present."""
    print("🔧 Installing uv...")
    try:
        # Try installing via pip first
        subprocess.run([sys.executable, "-m", "pip", "install", "uv"], check=True)
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install uv via pip")
        print("🔧 Please install uv manually: https://github.com/astral-sh/uv")
        return False


def main() -> None:
    """Main setup function."""
    print("🚀 Setting up {{ PrefixName }}{{ SuffixName }} development environment")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not Path("pyproject.toml").exists():
        print("❌ pyproject.toml not found. Please run this script from the project root.")
        sys.exit(1)
    
    # Check if uv is installed
    if not check_uv_installed():
        if not install_uv():
            sys.exit(1)
    
    success = True
    
    # Lock dependencies
    success &= run_command(
        ["uv", "lock"],
        "Locking dependencies with uv"
    )
    
    # Install development dependencies
    success &= run_command(
        ["uv", "sync", "--dev"],
        "Installing development dependencies"
    )
    
    # Install pre-commit hooks
    success &= run_command(
        ["uv", "run", "pre-commit", "install"],
        "Installing pre-commit hooks"
    )
    
    # Run initial code quality checks
    success &= run_command(
        ["uv", "run", "ruff", "check", "."],
        "Running Ruff linter"
    )
    
    success &= run_command(
        ["uv", "run", "ruff", "format", "--check", "."],
        "Checking code formatting"
    )
    
    # Run type checking
    success &= run_command(
        ["uv", "run", "mypy", "."],
        "Running MyPy type checking"
    )
    
    print("=" * 60)
    if success:
        print("🎉 Development environment setup completed successfully!")
        print("\n📚 Next steps:")
        print("  • Run tests: uv run pytest")
        print("  • Start development server: uv run python -m {{ org_name }}.{{ solution_name }}.{{ prefix_name }}.{{ suffix_name }}.server.main")
        print("  • View docs: http://localhost:8000/docs")
        print("  • Run linting: uv run ruff check .")
        print("  • Run formatting: uv run ruff format .")
        print("  • Run type checking: uv run mypy .")
    else:
        print("❌ Setup completed with some errors. Please check the output above.")
        sys.exit(1)


if __name__ == "__main__":
    main() 
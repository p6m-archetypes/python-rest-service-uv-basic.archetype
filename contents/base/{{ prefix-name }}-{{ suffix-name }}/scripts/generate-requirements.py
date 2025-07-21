#!/usr/bin/env python3
"""
Requirements.txt Generator

This script generates requirements.txt files from pyproject.toml
for environments that don't support pyproject.toml directly.
"""

import subprocess
import sys
from pathlib import Path


def generate_requirements() -> None:
    """Generate requirements.txt files using uv."""
    
    print("📦 Generating requirements.txt files...")
    
    # Check if we're in the right directory
    if not Path("pyproject.toml").exists():
        print("❌ pyproject.toml not found. Please run this script from the project root.")
        sys.exit(1)
    
    try:
        # Generate main requirements.txt (production dependencies)
        print("📝 Generating requirements.txt (production)...")
        with open("requirements.txt", "w") as f:
            result = subprocess.run(
                ["uv", "pip", "compile", "pyproject.toml"],
                capture_output=True,
                text=True,
                check=True
            )
            f.write(result.stdout)
        print("✅ requirements.txt generated")
        
        # Generate dev requirements.txt (development dependencies)
        print("📝 Generating requirements-dev.txt (development)...")
        with open("requirements-dev.txt", "w") as f:
            result = subprocess.run(
                ["uv", "pip", "compile", "pyproject.toml", "--extra", "dev"],
                capture_output=True,
                text=True,
                check=True
            )
            f.write(result.stdout)
        print("✅ requirements-dev.txt generated")
        
        # Generate test requirements.txt (test dependencies)
        print("📝 Generating requirements-test.txt (testing)...")
        with open("requirements-test.txt", "w") as f:
            result = subprocess.run(
                ["uv", "pip", "compile", "pyproject.toml", "--extra", "test"],
                capture_output=True,
                text=True,
                check=True
            )
            f.write(result.stdout)
        print("✅ requirements-test.txt generated")
        
        # Generate lint requirements.txt (linting dependencies)
        print("📝 Generating requirements-lint.txt (linting)...")
        with open("requirements-lint.txt", "w") as f:
            result = subprocess.run(
                ["uv", "pip", "compile", "pyproject.toml", "--extra", "lint"],
                capture_output=True,
                text=True,
                check=True
            )
            f.write(result.stdout)
        print("✅ requirements-lint.txt generated")
        
        print("🎉 All requirements.txt files generated successfully!")
        print("\n📚 Generated files:")
        print("  • requirements.txt - Production dependencies")
        print("  • requirements-dev.txt - Development dependencies")
        print("  • requirements-test.txt - Testing dependencies")
        print("  • requirements-lint.txt - Linting dependencies")
        print("\n🔧 Usage:")
        print("  pip install -r requirements.txt")
        print("  pip install -r requirements-dev.txt  # For development")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to generate requirements.txt: {e}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        sys.exit(1)
    except FileNotFoundError:
        print("❌ uv command not found. Please install uv first:")
        print("  pip install uv")
        sys.exit(1)


if __name__ == "__main__":
    generate_requirements() 
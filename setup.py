# setup.py
"""Setup script and packaging configuration for Nexomate MVP."""

from setuptools import setup, find_packages
from pathlib import Path

# Load long description from README if available
readme_path = Path(__file__).resolve().parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

setup(
    name="nexomate",
    version="1.0.0",
    description="Autonomous, self-hosted lead sourcing, verification, scoring, and outreach engine.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Nexomate Team",
    author_email="hello@nexomate.local",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=[
        "streamlit>=1.30.0",
        "pandas>=2.0.0",
        "openpyxl>=3.1.0",
        "SQLAlchemy>=2.0.0",
        "beautifulsoup4>=4.12.0",
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
        "ollama>=0.1.6",
    ],
    entry_points={
        "console_scripts": [
            "nexomate=main:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Topic :: Communications :: Email",
        "Topic :: Office/Business",
    ],
)

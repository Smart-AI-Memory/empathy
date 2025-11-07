"""
Setup script for Empathy Framework
"""

from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Core dependencies - minimal required for framework to function
CORE_REQUIRES = [
    "pydantic>=2.0.0,<3.0.0",
    "typing-extensions>=4.0.0,<5.0.0",
    "python-dotenv>=1.0.0,<2.0.0",
]

# Optional LLM provider integrations
ANTHROPIC_REQUIRES = ["anthropic>=0.8.0,<1.0.0"]
OPENAI_REQUIRES = ["openai>=1.6.0,<2.0.0"]

# LangChain ecosystem for agents/workflows
AGENTS_REQUIRES = [
    "langchain>=0.1.0,<0.3.0",
    "langchain-core>=0.1.0,<0.3.0",
    "langgraph>=0.1.0,<0.2.0",
]

# Backend API server (optional)
BACKEND_REQUIRES = [
    "fastapi>=0.100.0,<1.0.0",
    "uvicorn>=0.20.0,<1.0.0",
]

# LSP server for editor integration (optional)
LSP_REQUIRES = [
    "pygls>=1.0.0,<2.0.0",
    "lsprotocol>=2023.0.0,<2024.0.0",
]

# Documentation generation (optional)
DOCS_REQUIRES = [
    "python-docx>=0.8.11,<1.0.0",
]

# YAML support (optional)
YAML_REQUIRES = ["pyyaml>=6.0,<7.0"]

# Windows compatibility
WINDOWS_REQUIRES = [
    "colorama>=0.4.6,<1.0.0",  # ANSI color support for Windows CMD
]

# Development dependencies
DEV_REQUIRES = [
    "pytest>=7.0,<9.0",
    "pytest-asyncio>=0.21,<1.0",
    "pytest-cov>=4.0,<5.0",
    "black>=23.0,<25.0",
    "mypy>=1.0,<2.0",
    "ruff>=0.1,<1.0",
    "coverage>=7.0,<8.0",
]

setup(
    name="empathy-framework",
    version="1.5.0",
    author="Patrick Roebuck",
    author_email="patrick.roebuck@smartaimemory.com",
    description="A five-level maturity model for AI-human collaboration with anticipatory empathy",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Deep-Study-AI/Empathy",
    packages=find_packages(
        include=[
            "coach_wizards",
            "coach_wizards.*",
            "empathy_os",
            "empathy_os.*",
            "wizards",
            "wizards.*",
            "agents",
            "agents.*",
            "empathy_software_plugin",
            "empathy_software_plugin.*",
            "empathy_healthcare_plugin",
            "empathy_healthcare_plugin.*",
            "empathy_llm_toolkit",
            "empathy_llm_toolkit.*",
        ]
    ),
    package_dir={"empathy_os": "src/empathy_os"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    python_requires=">=3.10",  # Dropped 3.9 (EOL May 2025)
    install_requires=CORE_REQUIRES,
    extras_require={
        # LLM providers (user chooses which they need)
        "anthropic": ANTHROPIC_REQUIRES,
        "openai": OPENAI_REQUIRES,
        "llm": ANTHROPIC_REQUIRES + OPENAI_REQUIRES,  # Both providers
        # Optional features
        "agents": AGENTS_REQUIRES,
        "backend": BACKEND_REQUIRES,
        "lsp": LSP_REQUIRES,
        "docs": DOCS_REQUIRES,
        "yaml": YAML_REQUIRES,
        "windows": WINDOWS_REQUIRES,
        # Development
        "dev": DEV_REQUIRES,
        # Complete installation (everything)
        "all": (
            ANTHROPIC_REQUIRES
            + OPENAI_REQUIRES
            + AGENTS_REQUIRES
            + BACKEND_REQUIRES
            + LSP_REQUIRES
            + DOCS_REQUIRES
            + YAML_REQUIRES
            + WINDOWS_REQUIRES
        ),
    },
    entry_points={
        "console_scripts": [
            "empathy-framework=empathy_os.cli:main",
            "empathy-scan=empathy_software_plugin.cli:scan_command",  # Converted from bin/
        ],
    },
    keywords="ai collaboration empathy anticipatory-ai systems-thinking",
    project_urls={
        "Documentation": "https://github.com/Deep-Study-AI/Empathy/docs",
        "Source": "https://github.com/Deep-Study-AI/Empathy",
        "Tracker": "https://github.com/Deep-Study-AI/Empathy/issues",
    },
)

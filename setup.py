"""
Setup script for Empathy Framework
"""

from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="empathy-framework",
    version="1.0.0-beta",
    author="Patrick Roebuck",
    author_email="patrick.roebuck@deepstudyai.com",
    description="A five-level maturity model for AI-human collaboration with anticipatory empathy",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Deep-Study-AI/Empathy",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.9",
    install_requires=[
        # Core dependencies (minimal)
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-asyncio>=0.21",
            "black>=23.0",
            "mypy>=1.0",
            "ruff>=0.1",
        ],
        "examples": [
            "langgraph>=0.1",
            "langchain-core>=0.1",
        ],
        "yaml": [
            "pyyaml>=6.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "empathy-framework=empathy_os.cli:main",
        ],
    },
    keywords="ai collaboration empathy anticipatory-ai systems-thinking",
    project_urls={
        "Documentation": "https://github.com/Deep-Study-AI/Empathy/docs",
        "Source": "https://github.com/Deep-Study-AI/Empathy",
        "Tracker": "https://github.com/Deep-Study-AI/Empathy/issues",
    },
)

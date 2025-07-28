"""Setup configuration for SP404MK2 Sample Agent."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="sp404mk2-sample-agent",
    version="0.1.0",
    author="SP404MK2 Agent Team",
    description="AI-powered sample collection and curation for SP404MK2",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ciscoittech/sp404mk2-sample-agent",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Sound/Audio",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.11",
    install_requires=[
        "typer>=0.9.0",
        "rich>=13.0.0",
        "pydantic>=2.0.0",
        "pydantic-ai>=0.0.1",
        "aiohttp>=3.9.0",
        "python-dotenv>=1.0.0",
        "yt-dlp>=2024.1.0",
        "librosa>=0.10.0",
        "numpy>=1.24.0",
        "scipy>=1.10.0",
        "soundfile>=0.12.0",
        "pydub>=0.25.0",
        "jinja2>=3.1.0",
        "openrouter>=0.1.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "sp404agent=src.cli:app",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.yml", "*.yaml"],
    },
)
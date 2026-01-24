# setup.py
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="infinity_portal",
    version="1.0.0",
    author="infinity_portal",
    description="Build your autonomous hedge fund in minutes with AI agents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/infinity_portal/Infinity_Portal",
    packages=find_packages(exclude=["tests*", "experimental*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial :: Investment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=8.0.0",
            "pytest-asyncio>=0.23.0",
            "pytest-cov>=4.1.0",
            "black>=24.0.0",
            "flake8>=7.0.0",
            "mypy>=1.8.0",
        ],
        "backtesting": [
            "vectorbt>=0.26.0",
            "ta-lib>=0.4.0",
        ],
        "brokers": [
            "pyetrade>=1.3.0",
            "td-ameritrade-python-api>=0.3.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "autohedge=autohedge.cli:main",
        ],
    },
)
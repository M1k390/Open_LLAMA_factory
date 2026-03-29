"""Setup script for OpenLlama."""

from setuptools import setup, find_packages

setup(
    name="open_llama",
    version="1.0.0",
    description="Autonomous AI coding agent using local llama.cpp server",
    author="OpenLlama Team",
    packages=find_packages(),
    install_requires=[
        "requests>=2.28.0",
        "tinydb>=4.7.0",
    ],
    entry_points={
        "console_scripts": [
            "open_llama=open_llama.main:main",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)

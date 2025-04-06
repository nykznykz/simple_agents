from setuptools import setup, find_packages

setup(
    name="simple_agents",
    version="0.1.0",
    packages=find_packages(include=['simple_agents', 'simple_agents.*']),
    install_requires=[
        "ollama",
        "duckduckgo-search",
        "gradio",
    ],
    python_requires=">=3.9",
) 
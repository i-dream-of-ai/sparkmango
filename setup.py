from setuptools import setup, find_packages

setup(
    name="mcp-server",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "web3>=6.11.1",
        "pydantic>=1.8.0",
        "click>=8.0.0",
        "openai>=1.0.0"
    ],
    entry_points={
        "console_scripts": [
            "mcp-server=mcp_server.cli:cli",
        ],
    },
    author="Arjun Bhuptani",
    author_email="arjunbhuptani@gmail.com",
    description="Convert Solidity bytecode to MCP server",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/arjunbhuptani/solidity-mcp-server",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
) 
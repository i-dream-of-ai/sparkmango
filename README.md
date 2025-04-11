# SparkMango

![SparkMango Logo](brand/logomark.png)

A Model Context Protocol (MCP) server that converts Solidity bytecode into a functional server implementation.

## Overview

SparkMango provides a bridge between Solidity smart contracts and Python-based server applications. It automatically generates server implementations from Solidity contracts, making it easier to interact with blockchain contracts through a RESTful API.

## Features

- Convert Solidity contracts to Python implementations
- Automatic server generation
- State management for contract variables
- RESTful API endpoints
- Event handling
- Comprehensive testing framework

## Installation

```bash
pip install mcp-server
```

## Usage

1. Generate a server from a Solidity contract:

```bash
mcp-server generate --contract path/to/contract.json --output output_directory
```

2. Start the server:

```bash
mcp-server start --port 8000
```

## Development

### Setup

1. Clone the repository:
```bash
git clone https://github.com/ArjunBhuptani/sparkmango.git
cd sparkmango
```

2. Install dependencies:
```bash
pip install -r requirements.txt
pip install -r requirements-test.txt
```

### Testing

Run the test suite:
```bash
python -m pytest
```

## Documentation

For detailed documentation, please refer to the [docs](docs/) directory.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Project Status

For current project status and upcoming features, see [PROJECT_STATUS.md](PROJECT_STATUS.md). 
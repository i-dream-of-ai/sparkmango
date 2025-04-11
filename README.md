# MCP Server Generator

A tool to generate Model Context Protocol (MCP) servers from Solidity contract ABIs.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
pip install -r requirements-test.txt
```

2. Set up environment variables:
```bash
# Required for OpenAI API access
export OPENAI_API_KEY=your_api_key_here

# Required for Ethereum node access
export ETH_NODE_URL=your_ethereum_node_url_here
```

## Usage

Generate an MCP server from a contract ABI:
```bash
python -m mcp_server.cli generate path/to/abi.json output_dir ContractName
```

Clear the method implementation cache:
```bash
python -m mcp_server.cli clear-cache output_dir/cache
```

## Testing

Run the test suite:
```bash
pytest tests/
```

The test suite requires:
1. An OpenAI API key
2. An Ethereum node URL (e.g., from Infura or Alchemy)
3. The UniToken.json ABI file in the contracts directory

## Development

The project structure:
```
mcp_server/
├── abi_analyzer.py    # ABI analysis tools
├── llm_generator.py   # LLM-based method generation
├── method_cache.py    # Method implementation caching
├── mcp_generator.py   # MCP server generation
└── cli.py            # Command-line interface

tests/
├── test_uni_token.py # Uni token contract tests
└── ...

contracts/
└── UniToken.json     # Uni token contract ABI
```

## License

MIT 
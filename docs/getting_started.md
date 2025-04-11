# Getting Started with SparkMango

## Installation

```bash
pip install mcp-server
```

## Basic Usage

### 1. Generate a Server from a Solidity Contract

```python
from mcp_server import MCPGenerator

# Initialize the generator
generator = MCPGenerator()

# Generate server implementation
generator.generate(
    contract_path="path/to/contract.json",
    output_dir="output_directory",
    contract_name="MyContract"
)
```

### 2. Start the Server

```python
from mcp_server import start_server

# Start the server on port 8000
start_server(port=8000)
```

## Working with Contract State

```python
from mcp_server.state import State

# Initialize state
state = State()

# Set a value
state.set("my_key", "my_value")

# Get a value
value = state.get("my_key")

# Delete a value
state.delete("my_key")
```

## Handling Contract Methods

### Reading Methods (view/pure)

```python
# The generated server automatically creates endpoints for view/pure methods
# Example: GET /contract/balanceOf?address=0x123...
response = requests.get("http://localhost:8000/contract/balanceOf?address=0x123...")
balance = response.json()["result"]
```

### Writing Methods

```python
# The generated server automatically creates endpoints for state-changing methods
# Example: POST /contract/transfer
response = requests.post(
    "http://localhost:8000/contract/transfer",
    json={
        "to": "0x123...",
        "amount": 100
    }
)
transaction_hash = response.json()["transaction_hash"]
```

## Event Handling

```python
from mcp_server import EventHandler

# Initialize event handler
handler = EventHandler()

# Subscribe to events
@handler.on("Transfer")
def handle_transfer(event):
    print(f"Transfer: {event['from']} -> {event['to']} ({event['value']})")

# Start listening
handler.start()
```

## Configuration

SparkMango can be configured using environment variables:

```bash
# Ethereum node URL
export ETH_NODE_URL="https://mainnet.infura.io/v3/your-api-key"

# Server configuration
export MCP_SERVER_PORT=8000
export MCP_SERVER_HOST="0.0.0.0"
```

## Next Steps

- Learn about [Core Concepts](core_concepts.md)
- Explore the [API Reference](api_reference.md)
- Check out [Examples](examples/README.md)
- Dive into [Advanced Topics](advanced_topics.md) 
# ERC20 Token Example

This example demonstrates how to use SparkMango with an ERC20 token contract.

## Contract Source

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract ERC20Token {
    string public name;
    string public symbol;
    uint8 public decimals;
    uint256 public totalSupply;
    
    mapping(address => uint256) public balanceOf;
    mapping(address => mapping(address => uint256)) public allowance;
    
    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);
    
    constructor(
        string memory _name,
        string memory _symbol,
        uint8 _decimals,
        uint256 _initialSupply
    ) {
        name = _name;
        symbol = _symbol;
        decimals = _decimals;
        totalSupply = _initialSupply;
        balanceOf[msg.sender] = _initialSupply;
    }
    
    function transfer(address to, uint256 value) external returns (bool) {
        require(balanceOf[msg.sender] >= value, "Insufficient balance");
        balanceOf[msg.sender] -= value;
        balanceOf[to] += value;
        emit Transfer(msg.sender, to, value);
        return true;
    }
    
    function approve(address spender, uint256 value) external returns (bool) {
        allowance[msg.sender][spender] = value;
        emit Approval(msg.sender, spender, value);
        return true;
    }
    
    function transferFrom(address from, address to, uint256 value) external returns (bool) {
        require(balanceOf[from] >= value, "Insufficient balance");
        require(allowance[from][msg.sender] >= value, "Insufficient allowance");
        balanceOf[from] -= value;
        balanceOf[to] += value;
        allowance[from][msg.sender] -= value;
        emit Transfer(from, to, value);
        return true;
    }
}
```

## Generated Server Usage

```python
from mcp_server import MCPGenerator, start_server
from mcp_server.state import State
import requests

# Generate server implementation
generator = MCPGenerator()
generator.generate(
    contract_path="erc20_token.json",
    output_dir="erc20_server",
    contract_name="ERC20Token"
)

# Start the server
start_server(port=8000)

# Initialize state
state = State()

# Set initial balances
state.set("balanceOf:0x123...", 1000)
state.set("balanceOf:0x456...", 0)

# Make API calls
# Get balance
response = requests.get(
    "http://localhost:8000/contract/balanceOf",
    params={"address": "0x123..."}
)
balance = response.json()["result"]
print(f"Balance: {balance}")

# Transfer tokens
response = requests.post(
    "http://localhost:8000/contract/transfer",
    json={
        "to": "0x456...",
        "value": 100
    }
)
tx_hash = response.json()["transaction_hash"]
print(f"Transfer transaction: {tx_hash}")

# Listen for Transfer events
@state.on("Transfer")
def handle_transfer(event):
    print(f"Transfer: {event['from']} -> {event['to']} ({event['value']})")
```

## Testing

```python
import pytest
from mcp_server import MCPGenerator
from mcp_server.state import State

def test_erc20_transfer():
    # Initialize
    state = State()
    generator = MCPGenerator()
    
    # Set initial state
    state.set("balanceOf:0x123...", 1000)
    state.set("balanceOf:0x456...", 0)
    
    # Generate and start server
    generator.generate("erc20_token.json", "test_server", "ERC20Token")
    start_server(port=8001)
    
    # Test transfer
    response = requests.post(
        "http://localhost:8001/contract/transfer",
        json={
            "to": "0x456...",
            "value": 100
        }
    )
    assert response.status_code == 200
    
    # Verify balances
    response = requests.get(
        "http://localhost:8001/contract/balanceOf",
        params={"address": "0x123..."}
    )
    assert response.json()["result"] == 900
    
    response = requests.get(
        "http://localhost:8001/contract/balanceOf",
        params={"address": "0x456..."}
    )
    assert response.json()["result"] == 100
```

## Requirements

```txt
mcp-server>=0.1.0
web3>=6.0.0
requests>=2.25.0
pytest>=7.0.0
```

## Next Steps

1. Deploy the contract to a testnet
2. Configure the server with your contract address
3. Implement additional token functionality
4. Add more test cases 
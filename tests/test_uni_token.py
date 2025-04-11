import pytest
import os
import json
import asyncio
from pathlib import Path
import requests
import time
from web3 import Web3
from mcp_server.abi_analyzer import ABIAnalyzer
from mcp_server.mcp_generator import MCPGenerator

# Uni token contract address on Ethereum mainnet
UNI_TOKEN_ADDRESS = "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984"

def pytest_configure(config):
    """Configure pytest with environment variables."""
    # Check for required environment variables
    required_vars = ['OPENAI_API_KEY', 'ETH_NODE_URL']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        pytest.exit(f"Missing required environment variables: {', '.join(missing_vars)}")

@pytest.fixture
def uni_abi():
    """Load the Uni token ABI."""
    abi_path = Path(__file__).parent.parent / "contracts" / "UniToken.json"
    if not abi_path.exists():
        pytest.skip("UniToken.json not found")
    with open(abi_path) as f:
        return json.load(f)

@pytest.fixture
def web3():
    """Create a Web3 instance."""
    node_url = os.getenv('ETH_NODE_URL')
    if not node_url:
        pytest.skip("ETH_NODE_URL not set")
    return Web3(Web3.HTTPProvider(node_url))

@pytest.fixture
def mcp_server(uni_abi, tmp_path, web3):
    """Generate and start an MCP server for the Uni token."""
    # Create generator
    generator = MCPGenerator(
        analysis=ABIAnalyzer(uni_abi).analyze(),
        output_dir=tmp_path,
        contract_name="UniToken",
        openai_api_key=os.getenv('OPENAI_API_KEY')
    )
    
    # Generate server
    asyncio.run(generator.generate())
    
    # Start server in a separate process
    import subprocess
    server_process = subprocess.Popen(
        ["python", str(tmp_path / "server.py")],
        env={
            "CONTRACT_ADDRESS": UNI_TOKEN_ADDRESS,
            "ETH_NODE_URL": os.getenv('ETH_NODE_URL'),
            "PYTHONPATH": str(tmp_path),
            **os.environ
        }
    )
    
    # Wait for server to start
    max_wait = 10
    for _ in range(max_wait):
        try:
            response = requests.get(f"http://localhost:8000/docs")
            if response.status_code == 200:
                break
        except requests.exceptions.ConnectionError:
            time.sleep(1)
    else:
        server_process.terminate()
        pytest.fail("Server failed to start")
    
    yield f"http://localhost:8000"
    
    # Cleanup
    server_process.terminate()
    server_process.wait()

@pytest.mark.asyncio
async def test_balance_of(mcp_server, web3, uni_abi):
    """Test the balanceOf function."""
    # Test address (Uniswap deployer)
    test_address = web3.to_checksum_address("0x47173B170C64d16393a52e6C480b3Ad8c302ba1e")
    
    # First verify the address has a balance using Web3 directly
    contract = web3.eth.contract(
        address=UNI_TOKEN_ADDRESS,
        abi=uni_abi['abi']
    )
    direct_balance = contract.functions.balanceOf(test_address).call()
    assert direct_balance > 0, "Test address has no UNI balance"
    
    # Make request to MCP server
    response = requests.post(
        f"{mcp_server}/mcp",
        json={
            "method": "balanceOf",
            "params": {
                "account": test_address
            },
            "context": {
                "test": True
            }
        }
    )
    
    # Check response
    assert response.status_code == 200, f"Server returned {response.status_code}: {response.text}"
    result = response.json()
    
    # Check result structure
    assert "result" in result, "Response missing 'result' field"
    assert "context" in result, "Response missing 'context' field"
    assert result["context"]["test"] is True, "Context not preserved"
    
    # Check balance matches direct Web3 call
    mcp_balance = int(result["result"])
    assert mcp_balance == direct_balance, f"MCP balance {mcp_balance} != direct balance {direct_balance}"
    
    # Print balance for verification
    print(f"Uni token balance for {test_address}: {mcp_balance}") 
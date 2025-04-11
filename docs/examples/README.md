# Examples

This directory contains practical examples of using SparkMango with different types of contracts.

## Available Examples

1. [ERC20 Token](erc20_token.md)
   - Basic token functionality
   - Transfer and balance operations
   - Event handling

2. [Simple Storage](simple_storage.md)
   - Basic state management
   - CRUD operations
   - Event emission

3. [Multi-Signature Wallet](multi_sig_wallet.md)
   - Complex state management
   - Multiple signers
   - Transaction approval flow

## Running Examples

Each example includes:
- Contract source code
- Generated server code
- Usage examples
- Test cases

To run an example:

```bash
# Navigate to the example directory
cd docs/examples/erc20_token

# Install dependencies
pip install -r requirements.txt

# Run the example
python example.py
```

## Contributing Examples

We welcome new examples! To contribute:

1. Create a new directory for your example
2. Include:
   - Contract source code
   - Usage instructions
   - Test cases
   - Requirements file
3. Update this README
4. Submit a pull request 
# Core Concepts

## Model Context Protocol (MCP)

The Model Context Protocol is a framework that enables the conversion of Solidity smart contracts into functional server implementations. It provides:

1. **State Management**: Handling contract state variables
2. **Method Execution**: Processing contract method calls
3. **Event Handling**: Managing contract events
4. **API Generation**: Creating RESTful endpoints

## State Management

### State Class

The `State` class is the core component for managing contract state:

```python
class State:
    def __init__(self):
        self.storage = {}
        self.web3 = Web3()
    
    def get(self, key: str) -> Any:
        """Retrieve a value from storage."""
        return self.storage.get(key)
    
    def set(self, key: str, value: Any) -> None:
        """Store a value in storage."""
        self.storage[key] = value
    
    def delete(self, key: str) -> None:
        """Remove a value from storage."""
        if key in self.storage:
            del self.storage[key]
```

### State Persistence

State can be persisted using various backends:
- In-memory (default)
- File-based
- Database-backed
- Blockchain-backed

## Method Handling

### Method Types

1. **View Methods**
   - Read-only operations
   - No state modification
   - Example: `balanceOf(address)`

2. **Pure Methods**
   - No state access
   - No state modification
   - Example: `calculateHash(bytes)`

3. **State-Changing Methods**
   - Modify contract state
   - Require transaction
   - Example: `transfer(address,uint256)`

### Method Execution Flow

1. Request received at API endpoint
2. Parameters validated
3. Method executed
4. Result returned/transaction sent
5. State updated (if applicable)

## Event System

### Event Types

1. **Standard Events**
   - Emitted by contract
   - Stored in event logs
   - Example: `Transfer(address,address,uint256)`

2. **Custom Events**
   - User-defined events
   - Custom processing logic

### Event Handling

```python
class EventHandler:
    def __init__(self):
        self.listeners = {}
    
    def on(self, event_name: str):
        def decorator(func):
            self.listeners[event_name] = func
            return func
        return decorator
    
    def emit(self, event_name: str, data: dict):
        if event_name in self.listeners:
            self.listeners[event_name](data)
```

## API Generation

### Endpoint Structure

1. **Base URL**: `/contract`
2. **Method Path**: `/{method_name}`
3. **Parameters**: Query params or JSON body

### Response Format

```json
{
    "success": true,
    "result": "value",
    "transaction_hash": "0x...",  // For state-changing methods
    "error": null
}
```

## Security Considerations

1. **Input Validation**
   - Type checking
   - Range validation
   - Format verification

2. **Access Control**
   - Method permissions
   - Role-based access
   - Ownership checks

3. **Gas Optimization**
   - State access patterns
   - Batch operations
   - Caching strategies 
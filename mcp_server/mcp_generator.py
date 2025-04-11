from typing import Dict, List
from pathlib import Path
import os
import json
from .abi_analyzer import FunctionDefinition, FunctionParameter, FunctionType
from .llm_generator import LLMMethodGenerator
import logging
import sys
import importlib.util
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional

class MCPGenerator:
    def __init__(self, analysis: Dict, output_dir: Path, contract_name: str, openai_api_key: str):
        """Initialize the MCP generator with ABI analysis results."""
        self.analysis = analysis
        self.output_dir = output_dir
        self.contract_name = contract_name
        self.llm_generator = LLMMethodGenerator(
            cache_dir=str(output_dir / 'cache'),
            openai_api_key=openai_api_key
        )
        
    async def generate(self):
        """Generate the MCP server implementation."""
        # Create output directory structure
        self._create_directory_structure()
        
        # Generate state variables first since server.py depends on it
        self._generate_state_variables()
        
        # Generate main server file
        self._generate_server_file()
        
        # Generate method implementations
        await self._generate_methods()
        
        # Generate documentation
        self._generate_documentation()
        
    def _create_directory_structure(self):
        """Create the necessary directory structure for the MCP server."""
        directories = [
            self.output_dir,
            self.output_dir / 'methods',
            self.output_dir / 'state',
            self.output_dir / 'tests',
            self.output_dir / 'docs',
            self.output_dir / 'cache'
        ]
        
        for directory in directories:
            directory.mkdir(exist_ok=True)
            
        # Create empty __init__.py files in each directory
        for directory in directories:
            init_file = directory / '__init__.py'
            if not init_file.exists():
                init_file.touch()
                
        # Create root __init__.py
        root_init = self.output_dir / '__init__.py'
        if not root_init.exists():
            root_init.touch()
            
    def _generate_server_file(self):
        """Generate the main MCP server file."""
        template = '''from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import json
import logging
import sys
import importlib.util
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))
logger.debug("Added %s to Python path", current_dir)

try:
    from methods import *
    logger.debug("Successfully imported methods")
except ImportError as e:
    logger.error("Failed to import methods: %s", e)
    raise

try:
    from state import State
    logger.debug("Successfully imported State")
except ImportError as e:
    logger.error("Failed to import State: %s", e)
    raise

app = FastAPI(
    title="{contract_name} MCP Server",
    description="Model Context Protocol server for {contract_name} smart contract",
    version="1.0.0"
)

class MCPRequest(BaseModel):
    """Base model for MCP requests."""
    method: str
    params: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None

class MCPResponse(BaseModel):
    """Base model for MCP responses."""
    result: Any
    context: Optional[Dict[str, Any]] = None

# Initialize contract state
try:
    state = State()
    logger.debug("Successfully initialized State")
except Exception as e:
    logger.error("Failed to initialize State: %s", e)
    raise

def load_method(method_name: str):
    """Dynamically load a method implementation."""
    logger.debug("Loading method %s", method_name)
    method_path = Path(__file__).parent / 'methods' / f'{{method_name}}.py'

    if not method_path.exists():
        logger.error("Method file not found: %s", method_path)
        raise HTTPException(status_code=404, detail=f"Method {{method_name}} not found")

    try:
        spec = importlib.util.spec_from_file_location(method_name, str(method_path))
        module = importlib.util.module_from_spec(spec)
        sys.modules[method_name] = module
        spec.loader.exec_module(module)
        method = getattr(module, method_name)
        logger.debug("Successfully loaded method %s", method_name)
        return method
    except Exception as e:
        logger.error("Failed to load method %s: %s", method_name, e)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/mcp", response_model=MCPResponse)
async def process_mcp_request(request: MCPRequest):
    """
    Process an MCP request for the {contract_name} contract.

    This endpoint accepts requests in the Model Context Protocol format and
    routes them to the appropriate contract method implementation.
    """
    logger.debug("Processing MCP request: %s", request.method)
    try:
        # Load and execute the method
        method = load_method(request.method)
        result = await method(state, **request.params)
        logger.debug("Method %s executed successfully", request.method)

        return MCPResponse(
            result=result,
            context=request.context
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error processing MCP request: %s", e)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == '__main__':
    import uvicorn
    logger.info("Starting MCP server")
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''.format(contract_name=self.contract_name)

        # Write the server file
        server_path = self.output_dir / 'server.py'
        with open(server_path, 'w') as f:
            f.write(template)
            
    async def _generate_methods(self):
        """Generate MCP implementations for each function."""
        for function in self.analysis['functions']:
            await self._generate_method_file(function)
            
    async def _generate_method_file(self, function: FunctionDefinition):
        """Generate an MCP implementation for a single function."""
        # Generate implementation using LLM
        implementation = await self.llm_generator.generate_method(function, self.analysis['abi'])
        
        # Save the implementation
        with open(self.output_dir / 'methods' / f'{function.name}.py', 'w') as f:
            f.write(implementation)
            
    def _generate_state_variables(self):
        """Generate state variable implementations."""
        template = '''from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import os
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class State(BaseModel):
    """State variables for the MCP contract."""
    # Contract state
    contract_address: str
    abi: List[Dict[str, Any]]
    account: str
    
    # Contract variables
    {state_vars}
    
    def __init__(self, **data):
        """Initialize state variables."""
        logger.debug("Initializing State with data: %s", data)
        
        # Set contract state from environment
        contract_address = os.getenv("CONTRACT_ADDRESS")
        logger.debug("Got contract_address from env: %s", contract_address)
        data["contract_address"] = contract_address
        
        abi = {abi}
        logger.debug("Setting ABI: %s", abi)
        data["abi"] = abi
        
        account = os.getenv("ACCOUNT_ADDRESS", "0x0000000000000000000000000000000000000000")
        logger.debug("Got account from env: %s", account)
        data["account"] = account
        
        # Initialize contract variables with defaults
        {init_vars}
        
        logger.debug("Calling super().__init__ with data: %s", data)
        super().__init__(**data)
        logger.debug("State initialization complete")
'''
        
        state_vars = []
        init_vars = []
        
        for var in self.analysis['state_variables']:
            type_hint = self._get_python_type(var['type'])
            state_vars.append(f"{var['name']}: Optional[{type_hint}] = Field(default=None)")
            init_vars.append(f"data['{var['name']}'] = None")
            
        state_vars_str = '\n    '.join(state_vars)
        init_vars_str = '\n        '.join(init_vars)
        
        # Convert JavaScript-style booleans to Python-style
        abi_str = str(self.analysis['abi']).replace('false', 'False').replace('true', 'True')
        
        with open(self.output_dir / 'state' / '__init__.py', 'w') as f:
            f.write(template.format(
                state_vars=state_vars_str,
                init_vars=init_vars_str,
                abi=abi_str
            ))
    
    def _get_python_type(self, solidity_type: str) -> str:
        """Convert Solidity type to Python type hint."""
        type_mapping = {
            'uint256': 'int',
            'uint8': 'int',
            'bool': 'bool',
            'address': 'str',
            'string': 'str',
            'bytes32': 'bytes'
        }
        return type_mapping.get(solidity_type, 'Any')
    
    def _generate_documentation(self):
        """Generate documentation for the MCP server."""
        template = f'''# {self.contract_name} Model Context Protocol Server

This document describes the Model Context Protocol (MCP) server implementation of the {self.contract_name} contract.

## API Overview

The MCP server provides a RESTful API that follows the Model Context Protocol specification. All endpoints accept and return JSON data.

### Base URL

```
http://localhost:8000
```

### Endpoints

#### POST /mcp

Process an MCP request for the {self.contract_name} contract.

**Request Body:**
```json
{{
    "method": "string",
    "params": {{
        // Method-specific parameters
    }},
    "context": {{
        // Optional context data
    }}
}}
```

**Response:**
```json
{{
    "result": {{
        // Method-specific result
    }},
    "context": {{
        // Optional context data
    }}
}}
```

## Available Methods

{self._generate_function_docs()}

## Events

{self._generate_event_docs()}

## State Variables

{self._generate_state_var_docs()}

## Integration Guide

### Using with AI Agents

To integrate this MCP server with an AI agent:

1. Start the server:
   ```bash
   python {self.contract_name.lower()}_server.py
   ```

2. Make requests to the server using the MCP format:
   ```python
   import requests
   
   response = requests.post(
       "http://localhost:8000/mcp",
       json={{
           "method": "balanceOf",
           "params": {{
               "account": "0x1234..."
           }},
           "context": {{
               "agent_id": "agent-1"
           }}
       }}
   )
   ```

3. Process the response:
   ```python
   result = response.json()["result"]
   context = response.json()["context"]
   ```

### Error Handling

The server returns appropriate HTTP status codes and error messages:

- 200: Success
- 404: Method not found
- 500: Server error

Error responses include a detail message explaining the error.
'''
        
        with open(self.output_dir / 'docs' / 'README.md', 'w') as f:
            f.write(template)
            
    def _generate_function_docs(self) -> str:
        """Generate function documentation."""
        docs = []
        for function in self.analysis['functions']:
            params = [f"{p.name}: {p.type}" for p in function.inputs]
            returns = [f"{p.type}" for p in function.outputs]
            
            docs.append(f"### {function.name}")
            docs.append(f"\nFunction Type: {function.state_mutability.value}")
            if params:
                docs.append("\nParameters:")
                for param in params:
                    docs.append(f"- {param}")
            if returns:
                docs.append("\nReturns:")
                for ret in returns:
                    docs.append(f"- {ret}")
            docs.append("\n")
            
        return '\n'.join(docs)
    
    def _generate_event_docs(self) -> str:
        """Generate event documentation."""
        docs = []
        for event in self.analysis['events']:
            params = [f"{p['name']}: {p['type']} (indexed: {p['indexed']})" 
                     for p in event['inputs']]
            
            docs.append(f"### {event['name']}")
            if params:
                docs.append("\nParameters:")
                for param in params:
                    docs.append(f"- {param}")
            docs.append("\n")
            
        return '\n'.join(docs)
    
    def _generate_state_var_docs(self) -> str:
        """Generate state variable documentation."""
        docs = []
        for var in self.analysis['state_variables']:
            docs.append(f"### {var['name']}")
            docs.append(f"Type: {var['type']}\n")
            
        return '\n'.join(docs) 
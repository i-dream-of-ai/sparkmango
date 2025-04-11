import json
import logging
from typing import Dict, Optional
from pathlib import Path
import openai
import asyncio
from .method_cache import MethodCache, MethodValidator, LLMMeter
from .abi_analyzer import FunctionDefinition
import web3

class LLMMethodGenerator:
    def __init__(self, cache_dir: str, openai_api_key: str):
        self.cache = MethodCache(Path(cache_dir))
        self.validator = MethodValidator()
        self.meter = LLMMeter()
        self.logger = logging.getLogger(__name__)
        
        # Initialize OpenAI client
        openai.api_key = openai_api_key
        
    async def generate_method(self, function: FunctionDefinition, contract_abi: Dict) -> str:
        """
        Generate a method implementation, using cache if available.
        """
        # Check cache first
        cached = self.cache.get_cached_implementation(function)
        if cached:
            return cached
            
        # Generate implementation using LLM
        implementation = await self._generate_with_llm(function, contract_abi)
        
        # Validate implementation
        is_valid, error = self.validator.validate_implementation(function, implementation)
        if not is_valid:
            raise ValueError(f"Invalid implementation generated: {error}")
            
        # Cache the implementation
        self.cache.cache_implementation(function, implementation)
        
        return implementation
        
    async def _generate_with_llm(self, function: FunctionDefinition, contract_abi: Dict) -> str:
        """
        Generate method implementation using OpenAI's API.
        """
        prompt = self._create_prompt(function, contract_abi)
        
        max_retries = 3
        retry_delay = 5  # Initial delay in seconds
        
        for attempt in range(max_retries):
            try:
                response = await openai.ChatCompletion.acreate(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": self._get_system_prompt()},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1  # Low temperature for more deterministic output
                )
                
                # Record usage
                self.meter.record_usage(response.usage.total_tokens)
                
                implementation = response.choices[0].message.content
                
                # Extract just the function implementation
                # The LLM might include markdown or other formatting
                if "```python" in implementation:
                    implementation = implementation.split("```python")[1].split("```")[0]
                elif "```" in implementation:
                    implementation = implementation.split("```")[1].split("```")[0]
                    
                return implementation.strip()
                
            except openai.error.RateLimitError as e:
                if attempt == max_retries - 1:
                    raise  # Re-raise on last attempt
                    
                # Extract wait time from error message if available
                import re
                wait_time = retry_delay
                match = re.search(r"Please try again in (\d+\.\d+)s", str(e))
                if match:
                    wait_time = float(match.group(1))
                    
                self.logger.warning(f"Rate limit hit, waiting {wait_time}s before retry {attempt + 1}/{max_retries}")
                await asyncio.sleep(wait_time)
                retry_delay *= 2  # Exponential backoff
                
            except Exception as e:
                self.logger.error(f"LLM generation failed: {str(e)}")
                raise
            
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the LLM."""
        return """You are a smart contract developer specializing in Web3.py implementations.
Your task is to generate Python implementations of Solidity functions that follow the Model Context Protocol (MCP).

You will be given a template and asked to fill in specific parts of it. Your response should ONLY include the filled-in template, with no additional text or explanations.

The template will contain placeholders marked with <placeholder> that you need to replace with the appropriate values:
1. <function_name> - Replace with the actual function name from the Solidity contract
2. <params> - Replace with the function parameters, comma-separated (e.g., "owner, spender" for approve function)
3. <str(e)> - Leave as is, this is for error handling

IMPORTANT:
- For view functions, the template returns {"result": result}
- For state-changing functions, the template returns {"type": "transaction_to_sign", "transaction": tx}
- DO NOT modify the template structure, only replace the placeholders
- Keep all dictionary keys and values exactly as shown in the template
- Preserve all whitespace and indentation

Your response should be a complete, valid Python function that can be used directly."""
        
    def _create_prompt(self, function: FunctionDefinition, contract_abi: Dict) -> str:
        """Create the prompt for the LLM."""
        # Create parameter string
        params = ["state: State"]
        for param in function.inputs:
            params.append(f"{param.name}: {param.type}")
        param_str = ", ".join(params)
        
        # Create return type annotation
        return_type = "Dict"  # All functions return Dict
        
        # Create template based on function type
        if function.state_mutability.value == "view":
            template = f"""async def {function.name}({param_str}) -> {return_type}:
    try:
        contract = web3.eth.contract(address=state.contract_address, abi=state.abi)
        result = await contract.functions.<function_name>(<params>).call()
        return {{"result": result}}
    except Exception as e:
        raise ValueError(f"Failed to execute {function.name}: <str(e)>")"""
        else:
            template = f"""async def {function.name}({param_str}) -> {return_type}:
    try:
        contract = web3.eth.contract(address=state.contract_address, abi=state.abi)
        tx = await contract.functions.<function_name>(<params>).build_transaction({{
            "from": state.account,
            "gas": await contract.functions.<function_name>(<params>).estimate_gas()
        }})
        return {{
            "type": "transaction_to_sign",
            "transaction": tx
        }}
    except Exception as e:
        raise ValueError(f"Failed to build {function.name} transaction: <str(e)>")"""
        
        # Create the prompt
        return f"""Fill in the following template for the {function.name} function:

Template:
{template}

Function details:
- Name: {function.name}
- State mutability: {function.state_mutability.value}
- Inputs: {[f"{p.name}: {p.type}" for p in function.inputs]}
- Outputs: {[f"{p.name}: {p.type}" for p in function.outputs]}

Contract ABI: {json.dumps(contract_abi)}

Replace the placeholders in the template with the appropriate values. Your response should be a complete, valid Python function.""" 
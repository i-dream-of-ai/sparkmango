import json
import hashlib
from pathlib import Path
from typing import Dict, Optional, Tuple
import logging
from .abi_analyzer import FunctionDefinition

class MethodCache:
    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(exist_ok=True)
        self.logger = logging.getLogger(__name__)
        
    def _get_cache_key(self, function: FunctionDefinition) -> str:
        """Generate a unique cache key for a function."""
        # Create a deterministic string representation of the function
        func_str = json.dumps({
            'name': function.name,
            'inputs': [(p.name, p.type) for p in function.inputs],
            'outputs': [(p.name, p.type) for p in function.outputs],
            'state_mutability': function.state_mutability.value
        }, sort_keys=True)
        
        return hashlib.sha256(func_str.encode()).hexdigest()
        
    def get_cached_implementation(self, function: FunctionDefinition) -> Optional[str]:
        """Get cached implementation if it exists."""
        cache_key = self._get_cache_key(function)
        cache_file = self.cache_dir / f"{cache_key}.py"
        
        if cache_file.exists():
            self.logger.info(f"Cache hit for function {function.name}")
            return cache_file.read_text()
            
        self.logger.info(f"Cache miss for function {function.name}")
        return None
        
    def cache_implementation(self, function: FunctionDefinition, implementation: str):
        """Cache a generated implementation."""
        cache_key = self._get_cache_key(function)
        cache_file = self.cache_dir / f"{cache_key}.py"
        
        cache_file.write_text(implementation)
        self.logger.info(f"Cached implementation for function {function.name}")
        
class MethodValidator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def validate_implementation(self, function: FunctionDefinition, implementation: str) -> Tuple[bool, str]:
        """
        Validate a generated implementation.
        Returns (is_valid, error_message)
        """
        # Base required components for all functions
        required_components = [
            "async def",
            "web3.eth.contract",
            "try:",
            "except Exception as e:"
        ]
        
        # Add function-specific components
        if function.state_mutability.value != "view":
            required_components.append("build_transaction")
        else:
            required_components.append("call()")
        
        # Check for required components
        for component in required_components:
            if component not in implementation:
                return False, f"Missing required component: {component}"
                
        # Check function signature
        expected_signature = f"async def {function.name}(state: State"
        if not implementation.startswith(expected_signature):
            return False, "Invalid function signature"
            
        # Check parameter names match
        for param in function.inputs:
            if f"{param.name}:" not in implementation:
                return False, f"Missing parameter: {param.name}"
                
        # Check return type
        if function.state_mutability.value == "view":
            if "return {" not in implementation:
                return False, "View function must return a dictionary"
        else:
            # Check for either single or double quoted version
            if '"type": "transaction_to_sign"' not in implementation and "'type': 'transaction_to_sign'" not in implementation:
                return False, "State-changing function must return transaction_to_sign"
                
        return True, ""
        
class LLMMeter:
    def __init__(self):
        self.total_tokens = 0
        self.total_requests = 0
        self.logger = logging.getLogger(__name__)
        
    def record_usage(self, tokens: int):
        """Record LLM usage."""
        self.total_tokens += tokens
        self.total_requests += 1
        self.logger.info(f"LLM Usage: {tokens} tokens (Total: {self.total_tokens} tokens, {self.total_requests} requests)")
        
    def get_usage_stats(self) -> Dict:
        """Get usage statistics."""
        return {
            "total_tokens": self.total_tokens,
            "total_requests": self.total_requests,
            "average_tokens_per_request": self.total_tokens / self.total_requests if self.total_requests > 0 else 0
        } 
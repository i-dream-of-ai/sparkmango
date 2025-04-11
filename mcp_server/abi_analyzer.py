from typing import Dict, List, Optional, Union
import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

class FunctionType(Enum):
    VIEW = "view"
    PURE = "pure"
    NONPAYABLE = "nonpayable"
    PAYABLE = "payable"

@dataclass
class FunctionParameter:
    name: str
    type: str
    components: Optional[List['FunctionParameter']] = None

@dataclass
class FunctionDefinition:
    name: str
    inputs: List[FunctionParameter]
    outputs: List[FunctionParameter]
    state_mutability: FunctionType
    is_constructor: bool = False

class ABIAnalyzer:
    def __init__(self, abi_input: Union[str, Dict]):
        """Initialize the ABI analyzer with either a path to an ABI file or a dictionary."""
        if isinstance(abi_input, (str, Path)):
            with open(abi_input, 'r') as f:
                data = json.load(f)
                self.abi = data.get('abi', data)
        else:
            self.abi = abi_input.get('abi', abi_input)
            
    def analyze(self) -> Dict:
        """Analyze the ABI and return a structured representation."""
        analysis = {
            'abi': self.abi,
            'functions': self._get_functions(),
            'events': self._get_events(),
            'state_variables': self._get_state_variables(),
            'constructor': self._get_constructor()
        }
        return analysis
    
    def _get_functions(self) -> List[FunctionDefinition]:
        """Extract all functions from the ABI."""
        functions = []
        for item in self.abi:
            if item['type'] == 'function':
                func = FunctionDefinition(
                    name=item['name'],
                    inputs=[self._parse_parameter(p) for p in item.get('inputs', [])],
                    outputs=[self._parse_parameter(p) for p in item.get('outputs', [])],
                    state_mutability=FunctionType(item.get('stateMutability', 'nonpayable'))
                )
                functions.append(func)
        return functions
    
    def _get_events(self) -> List[Dict]:
        """Extract all events from the ABI."""
        return [item for item in self.abi if item['type'] == 'event']
    
    def _get_state_variables(self) -> List[Dict]:
        """Extract state variables from view functions."""
        state_vars = []
        for item in self.abi:
            if (item['type'] == 'function' and 
                item.get('stateMutability') == 'view' and 
                len(item.get('inputs', [])) == 0):
                state_vars.append({
                    'name': item['name'],
                    'type': item['outputs'][0]['type'] if item.get('outputs') else 'unknown'
                })
        return state_vars
    
    def _get_constructor(self) -> Optional[Dict]:
        """Extract the constructor from the ABI."""
        for item in self.abi:
            if item['type'] == 'constructor':
                return item
        return None
    
    def _parse_parameter(self, param: Dict) -> FunctionParameter:
        """Parse a parameter definition."""
        components = None
        if 'components' in param:
            components = [self._parse_parameter(c) for c in param['components']]
            
        return FunctionParameter(
            name=param.get('name', ''),
            type=param['type'],
            components=components
        ) 
from typing import Dict, Any
from web3 import Web3

class State:
    def __init__(self):
        self.storage: Dict[str, Any] = {}
        self.web3 = Web3()
        
    def get(self, key: str) -> Any:
        return self.storage.get(key)
        
    def set(self, key: str, value: Any) -> None:
        self.storage[key] = value
        
    def delete(self, key: str) -> None:
        if key in self.storage:
            del self.storage[key]
            
    def clear(self) -> None:
        self.storage.clear()
        
    def __getitem__(self, key: str) -> Any:
        return self.get(key)
        
    def __setitem__(self, key: str, value: Any) -> None:
        self.set(key, value)
        
    def __delitem__(self, key: str) -> None:
        self.delete(key)
        
    def __contains__(self, key: str) -> bool:
        return key in self.storage

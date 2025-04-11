from mcp_server.state import State

def test_state_basic_operations():
    state = State()
    
    # Test set and get
    state.set("test_key", "test_value")
    assert state.get("test_key") == "test_value"
    
    # Test dictionary interface
    state["key2"] = "value2"
    assert state["key2"] == "value2"
    
    # Test contains
    assert "test_key" in state
    assert "nonexistent" not in state
    
    # Test delete
    del state["test_key"]
    assert "test_key" not in state
    
    # Test clear
    state.clear()
    assert len(state.storage) == 0 
from typing import Dict, Any, Optional, List
import json
from datetime import datetime

class MCPContextManager:
    def __init__(self):
        self._context: Dict[str, Any] = {
            "conversation_history": [],
            "system_state": {},
            "active_tools": set(),
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat()
            }
        }
        
    def add_conversation_turn(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Add a conversation turn to the context"""
        turn = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        self._context["conversation_history"].append(turn)
        self._update_timestamp()
    
    def update_system_state(self, key: str, value: Any) -> None:
        """Update system state with new information"""
        self._context["system_state"][key] = value
        self._update_timestamp()
    
    def register_tool(self, tool_name: str) -> None:
        """Register an active tool in the context"""
        self._context["active_tools"].add(tool_name)
        self._update_timestamp()
    
    def unregister_tool(self, tool_name: str) -> None:
        """Unregister a tool from the context"""
        self._context["active_tools"].discard(tool_name)
        self._update_timestamp()
    
    def get_context_window(self, window_size: int = 10) -> List[Dict[str, Any]]:
        """Get recent conversation history within window size"""
        return self._context["conversation_history"][-window_size:]
    
    def get_system_state(self) -> Dict[str, Any]:
        """Get current system state"""
        return self._context["system_state"].copy()
    
    def get_active_tools(self) -> set:
        """Get set of currently active tools"""
        return self._context["active_tools"].copy()
    
    def _update_timestamp(self) -> None:
        """Update last modified timestamp"""
        self._context["metadata"]["last_updated"] = datetime.now().isoformat()
    
    def save_context(self, filepath: str) -> None:
        """Save context to file"""
        with open(filepath, 'w') as f:
            json.dump(self._context, f, indent=2)
    
    def load_context(self, filepath: str) -> None:
        """Load context from file"""
        with open(filepath, 'r') as f:
            loaded_context = json.load(f)
            self._context.update(loaded_context)
    
    def clear_context(self) -> None:
        """Clear all context data"""
        self._context = {
            "conversation_history": [],
            "system_state": {},
            "active_tools": set(),
            "metadata": {
                "created_at": self._context["metadata"]["created_at"],
                "last_updated": datetime.now().isoformat()
            }
        } 
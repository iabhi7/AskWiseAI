from typing import Dict, List, Any, Optional
import time
import uuid

class ConversationMemory:
    """Simple in-memory storage for conversation history."""
    
    def __init__(self, max_history: int = 10, ttl: int = 3600):
        """
        Initialize conversation memory.
        
        Args:
            max_history: Maximum number of turns to remember
            ttl: Time-to-live in seconds for conversations (default: 1 hour)
        """
        self.conversations: Dict[str, Dict[str, Any]] = {}
        self.max_history = max_history
        self.ttl = ttl
    
    def create_conversation(self) -> str:
        """
        Create a new conversation.
        
        Returns:
            Conversation ID
        """
        conversation_id = str(uuid.uuid4())
        self.conversations[conversation_id] = {
            "messages": [],
            "created_at": time.time(),
            "last_updated": time.time()
        }
        return conversation_id
    
    def add_message(self, conversation_id: str, role: str, content: str, 
                   metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Add a message to the conversation history.
        
        Args:
            conversation_id: ID of the conversation
            role: Role of the message sender (user/assistant)
            content: Message content
            metadata: Optional metadata about the message
            
        Returns:
            True if successful, False otherwise
        """
        if conversation_id not in self.conversations:
            return False
        
        # Update the conversation
        conversation = self.conversations[conversation_id]
        conversation["messages"].append({
            "role": role,
            "content": content,
            "timestamp": time.time(),
            "metadata": metadata or {}
        })
        
        # Trim history if needed
        if len(conversation["messages"]) > self.max_history:
            conversation["messages"] = conversation["messages"][-self.max_history:]
        
        conversation["last_updated"] = time.time()
        return True
    
    def get_messages(self, conversation_id: str) -> List[Dict[str, Any]]:
        """
        Get all messages for a conversation.
        
        Args:
            conversation_id: ID of the conversation
            
        Returns:
            List of messages
        """
        if conversation_id not in self.conversations:
            return []
        
        return self.conversations[conversation_id]["messages"]
    
    def get_conversation_context(self, conversation_id: str, 
                               max_turns: Optional[int] = None) -> str:
        """
        Get a formatted context string from conversation history.
        
        Args:
            conversation_id: ID of the conversation
            max_turns: Maximum number of turns to include
            
        Returns:
            Formatted conversation context
        """
        messages = self.get_messages(conversation_id)
        
        if not messages:
            return ""
        
        # Limit to max_turns if specified
        if max_turns and len(messages) > max_turns * 2:  # Each turn is user + assistant
            messages = messages[-(max_turns * 2):]
        
        # Format the conversation context
        context = "Previous conversation:\n"
        for msg in messages:
            prefix = "User: " if msg["role"] == "user" else "Assistant: "
            context += f"{prefix}{msg['content']}\n\n"
        
        return context
    
    def clean_expired_conversations(self) -> int:
        """
        Remove expired conversations.
        
        Returns:
            Number of conversations removed
        """
        now = time.time()
        expired_ids = [
            cid for cid, data in self.conversations.items()
            if now - data["last_updated"] > self.ttl
        ]
        
        for cid in expired_ids:
            del self.conversations[cid]
        
        return len(expired_ids)

# Create a global conversation memory instance
conversation_memory = ConversationMemory() 
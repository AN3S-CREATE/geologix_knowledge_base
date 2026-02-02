"""
GeoLogix AI - Chat Manager
Handles chat history, folders, and conversation management.
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import uuid

class ChatManager:
    """Manages chat sessions, history, and folder organization."""
    
    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent.parent / "Data_Directories" / "chats"
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.folders_file = self.base_dir / "folders.json"
        self.active_sessions: Dict[str, dict] = {}
        self._load_folders()
    
    def _load_folders(self):
        """Load folder structure."""
        if self.folders_file.exists():
            with open(self.folders_file, 'r', encoding='utf-8') as f:
                self.folders = json.load(f)
        else:
            self.folders = {
                "default": {"name": "General", "created": datetime.now().isoformat()},
                "financial": {"name": "Financial Analysis", "created": datetime.now().isoformat()},
                "operations": {"name": "Operations", "created": datetime.now().isoformat()},
                "strategic": {"name": "Strategic Planning", "created": datetime.now().isoformat()},
            }
            self._save_folders()
    
    def _save_folders(self):
        """Save folder structure."""
        with open(self.folders_file, 'w', encoding='utf-8') as f:
            json.dump(self.folders, f, indent=2)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # FOLDER MANAGEMENT
    # ═══════════════════════════════════════════════════════════════════════════
    
    def create_folder(self, folder_id: str, name: str) -> dict:
        """Create a new chat folder."""
        folder_id = folder_id.lower().replace(" ", "_")
        if folder_id in self.folders:
            return {"error": f"Folder '{folder_id}' already exists"}
        
        self.folders[folder_id] = {
            "name": name,
            "created": datetime.now().isoformat()
        }
        self._save_folders()
        
        # Create folder directory
        folder_path = self.base_dir / folder_id
        folder_path.mkdir(exist_ok=True)
        
        return {"success": True, "folder_id": folder_id, "name": name}
    
    def list_folders(self) -> List[dict]:
        """List all chat folders."""
        return [
            {"id": fid, "name": data["name"], "created": data["created"]}
            for fid, data in self.folders.items()
        ]
    
    def delete_folder(self, folder_id: str) -> dict:
        """Delete a folder (moves chats to default)."""
        if folder_id == "default":
            return {"error": "Cannot delete default folder"}
        if folder_id not in self.folders:
            return {"error": f"Folder '{folder_id}' not found"}
        
        # Move all chats to default
        folder_path = self.base_dir / folder_id
        default_path = self.base_dir / "default"
        default_path.mkdir(exist_ok=True)
        
        if folder_path.exists():
            for chat_file in folder_path.glob("*.json"):
                chat_file.rename(default_path / chat_file.name)
            folder_path.rmdir()
        
        del self.folders[folder_id]
        self._save_folders()
        return {"success": True, "message": f"Folder '{folder_id}' deleted, chats moved to default"}
    
    # ═══════════════════════════════════════════════════════════════════════════
    # CHAT SESSION MANAGEMENT
    # ═══════════════════════════════════════════════════════════════════════════
    
    def create_chat(self, title: str = None, folder_id: str = "default") -> dict:
        """Create a new chat session."""
        chat_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now()
        
        chat = {
            "id": chat_id,
            "title": title or f"Chat {timestamp.strftime('%Y-%m-%d %H:%M')}",
            "folder_id": folder_id,
            "created": timestamp.isoformat(),
            "updated": timestamp.isoformat(),
            "messages": [],
            "metadata": {
                "total_tokens": 0,
                "deep_thinking_used": False,
                "web_search_used": False
            }
        }
        
        self.active_sessions[chat_id] = chat
        self._save_chat(chat)
        
        return {"chat_id": chat_id, "title": chat["title"], "folder_id": folder_id}
    
    def _save_chat(self, chat: dict):
        """Save chat to disk."""
        folder_path = self.base_dir / chat["folder_id"]
        folder_path.mkdir(exist_ok=True)
        
        chat_file = folder_path / f"{chat['id']}.json"
        with open(chat_file, 'w', encoding='utf-8') as f:
            json.dump(chat, f, indent=2, ensure_ascii=False)
    
    def load_chat(self, chat_id: str) -> Optional[dict]:
        """Load a chat session."""
        # Check active sessions first
        if chat_id in self.active_sessions:
            return self.active_sessions[chat_id]
        
        # Search in folders
        for folder_id in self.folders:
            chat_file = self.base_dir / folder_id / f"{chat_id}.json"
            if chat_file.exists():
                with open(chat_file, 'r', encoding='utf-8') as f:
                    chat = json.load(f)
                    self.active_sessions[chat_id] = chat
                    return chat
        
        return None
    
    def add_message(self, chat_id: str, role: str, content: str, 
                    thinking: str = None, metadata: dict = None) -> dict:
        """Add a message to chat history."""
        chat = self.load_chat(chat_id)
        if not chat:
            # Auto-create if not exists
            result = self.create_chat()
            chat_id = result["chat_id"]
            chat = self.active_sessions[chat_id]
        
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        
        if thinking:
            message["thinking"] = thinking
        if metadata:
            message["metadata"] = metadata
        
        chat["messages"].append(message)
        chat["updated"] = datetime.now().isoformat()
        
        # Update title from first user message if default
        if role == "user" and len(chat["messages"]) == 1:
            chat["title"] = content[:50] + ("..." if len(content) > 50 else "")
        
        self._save_chat(chat)
        return {"success": True, "message_count": len(chat["messages"])}
    
    def get_history(self, chat_id: str, limit: int = 20) -> List[dict]:
        """Get chat history for context."""
        chat = self.load_chat(chat_id)
        if not chat:
            return []
        
        return chat["messages"][-limit:]
    
    def get_context_messages(self, chat_id: str, limit: int = 10) -> List[dict]:
        """Get messages formatted for LLM context."""
        history = self.get_history(chat_id, limit)
        return [
            {"role": msg["role"], "content": msg["content"]}
            for msg in history
        ]
    
    def move_chat(self, chat_id: str, target_folder_id: str) -> dict:
        """Move a chat to a different folder."""
        if target_folder_id not in self.folders:
            return {"error": f"Folder '{target_folder_id}' not found"}
        
        chat = self.load_chat(chat_id)
        if not chat:
            return {"error": f"Chat '{chat_id}' not found"}
        
        old_folder = chat["folder_id"]
        old_path = self.base_dir / old_folder / f"{chat_id}.json"
        
        # Update chat folder
        chat["folder_id"] = target_folder_id
        chat["updated"] = datetime.now().isoformat()
        
        # Save to new location
        self._save_chat(chat)
        
        # Remove from old location
        if old_path.exists():
            old_path.unlink()
        
        return {
            "success": True, 
            "chat_id": chat_id,
            "from_folder": old_folder,
            "to_folder": target_folder_id
        }
    
    def list_chats(self, folder_id: str = None) -> List[dict]:
        """List all chats, optionally filtered by folder."""
        chats = []
        
        folders_to_check = [folder_id] if folder_id else list(self.folders.keys())
        
        for fid in folders_to_check:
            folder_path = self.base_dir / fid
            if folder_path.exists():
                for chat_file in folder_path.glob("*.json"):
                    try:
                        with open(chat_file, 'r', encoding='utf-8') as f:
                            chat = json.load(f)
                            chats.append({
                                "id": chat["id"],
                                "title": chat["title"],
                                "folder_id": chat["folder_id"],
                                "updated": chat["updated"],
                                "message_count": len(chat["messages"])
                            })
                    except:
                        pass
        
        # Sort by updated date
        chats.sort(key=lambda x: x["updated"], reverse=True)
        return chats
    
    def delete_chat(self, chat_id: str) -> dict:
        """Delete a chat session."""
        chat = self.load_chat(chat_id)
        if not chat:
            return {"error": f"Chat '{chat_id}' not found"}
        
        chat_file = self.base_dir / chat["folder_id"] / f"{chat_id}.json"
        if chat_file.exists():
            chat_file.unlink()
        
        if chat_id in self.active_sessions:
            del self.active_sessions[chat_id]
        
        return {"success": True, "deleted": chat_id}

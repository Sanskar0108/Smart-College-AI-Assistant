import os
import json
import threading
from typing import List, Dict, Optional, Any
from backend.core.config import DB_FILE_PATH, UPLOAD_DIR

class JsonDb:
    """
    Thread-safe JSON file database simulator to persist workspace metadata,
    extracted texts, and active document state.
    """
    def __init__(self):
        self.lock = threading.Lock()
        self._ensure_db_exists()

    def _ensure_db_exists(self):
        with self.lock:
            # Create directories if missing
            os.makedirs(os.path.dirname(DB_FILE_PATH), exist_ok=True)
            if not os.path.exists(DB_FILE_PATH):
                self._save_state_unlocked({
                    "documents": [],
                    "active_document_id": None,
                    "settings": self._get_default_settings()
                })

    def _get_default_settings(self) -> Dict[str, Any]:
        return {
            "user_name": "User",
            "user_about": "Active Student",
            "model": "local",
            "ollama_url": "http://localhost:11434",
            "system_prompt": "You are a helpful college AI assistant. Ground your answers in the student's study notes."
        }

    def get_settings(self) -> Dict[str, Any]:
        """
        Retrieves the global settings state. If missing, populates and returns defaults.
        """
        with self.lock:
            state = self._load_state_unlocked()
            if "settings" not in state:
                state["settings"] = self._get_default_settings()
                self._save_state_unlocked(state)
            return state["settings"]

    def update_settings(self, new_settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Updates the global settings dictionary state.
        """
        with self.lock:
            state = self._load_state_unlocked()
            current_settings = state.get("settings", self._get_default_settings())
            current_settings.update(new_settings)
            state["settings"] = current_settings
            self._save_state_unlocked(state)
            return current_settings

    def _load_state_unlocked(self) -> Dict[str, Any]:
        try:
            with open(DB_FILE_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {
                "documents": [],
                "active_document_id": None
            }

    def _save_state_unlocked(self, state: Dict[str, Any]):
        with open(DB_FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)

    def list_documents(self) -> List[Dict[str, Any]]:
        """
        Returns all document metadata items (excluding the full extracted text and chunks to keep payloads small).
        """
        with self.lock:
            state = self._load_state_unlocked()
            active_id = state.get("active_document_id")
            
            docs = []
            for doc in state.get("documents", []):
                # Copy document structure and omit extracted_text and chunks for listing
                doc_copy = doc.copy()
                doc_copy["active"] = (doc_copy["id"] == active_id)
                if "extracted_text" in doc_copy:
                    del doc_copy["extracted_text"]
                if "chunks" in doc_copy:
                    del doc_copy["chunks"]
                docs.append(doc_copy)
            return docs

    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a single document including full text extraction.
        """
        with self.lock:
            state = self._load_state_unlocked()
            active_id = state.get("active_document_id")
            for doc in state.get("documents", []):
                if doc["id"] == doc_id:
                    doc_copy = doc.copy()
                    doc_copy["active"] = (doc_copy["id"] == active_id)
                    return doc_copy
            return None

    def add_document(self, metadata: Dict[str, Any], extracted_text: str) -> Dict[str, Any]:
        """
        Adds a new document to the database state.
        """
        with self.lock:
            state = self._load_state_unlocked()
            
            # Append text context to storage record
            full_record = metadata.copy()
            full_record["extracted_text"] = extracted_text
            
            # If no active document currently, make this the active one by default
            if not state.get("active_document_id"):
                state["active_document_id"] = metadata["id"]
                full_record["active"] = True
            else:
                full_record["active"] = False

            state["documents"].append(full_record)
            self._save_state_unlocked(state)
            
            return full_record

    def update_document_status(self, doc_id: str, status: str, error: Optional[str] = None, text: Optional[str] = None, pages: Optional[int] = None, preview: Optional[str] = None, chunks: Optional[List[Dict[str, Any]]] = None):
        """
        Updates parse states, text contents, and chunks for a document.
        """
        with self.lock:
            state = self._load_state_unlocked()
            for doc in state.get("documents", []):
                if doc["id"] == doc_id:
                    doc["parse_status"] = status
                    doc["parse_error"] = error
                    if text is not None:
                        doc["extracted_text"] = text
                    if pages is not None:
                        doc["page_count"] = pages
                    if preview is not None:
                        doc["preview_snippet"] = preview
                    if chunks is not None:
                        doc["chunks"] = chunks
                    break
            self._save_state_unlocked(state)

    def delete_document(self, doc_id: str) -> Optional[str]:
        """
        Deletes metadata and the physical file from the local storage.
        """
        filename_to_delete = None
        with self.lock:
            state = self._load_state_unlocked()
            docs = state.get("documents", [])
            
            new_docs = []
            for doc in docs:
                if doc["id"] == doc_id:
                    filename_to_delete = doc["name"]
                    # Delete the physical file if it exists
                    file_path = os.path.join(UPLOAD_DIR, f"{doc_id}_{doc['name']}")
                    if os.path.exists(file_path):
                        try:
                            os.remove(file_path)
                        except OSError:
                            pass
                else:
                    new_docs.append(doc)
            
            state["documents"] = new_docs
            
            # Handle active document replacement if active document is deleted
            if state.get("active_document_id") == doc_id:
                if len(new_docs) > 0:
                    state["active_document_id"] = new_docs[0]["id"]
                else:
                    state["active_document_id"] = None
                    
            self._save_state_unlocked(state)
            
        return filename_to_delete

    def get_active_document_id(self) -> Optional[str]:
        """
        Getter for current workspace scope.
        """
        with self.lock:
            state = self._load_state_unlocked()
            return state.get("active_document_id")

    def set_active_document_id(self, doc_id: str) -> bool:
        """
        Setter to shift current workspace scope.
        """
        with self.lock:
            state = self._load_state_unlocked()
            # Verify document exists in list
            doc_ids = [d["id"] for d in state.get("documents", [])]
            if doc_id in doc_ids:
                state["active_document_id"] = doc_id
                self._save_state_unlocked(state)
                return True
            return False

# Global single instance database
db = JsonDb()

"""Persistence layer using TinyDB."""

import json
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
from tinydb import TinyDB, Query
from tinydb.table import Document


class ProgressDB:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db = TinyDB(str(db_path))
        self.progress_table = self.db.table("progress")
        self.state_table = self.db.table("state")
        self.learnings_table = self.db.table("learnings")

    def add_progress(self, story_id: str, description: str, files: list, learnings: list):
        """Add a progress entry."""
        self.progress_table.insert({
            "story_id": story_id,
            "description": description,
            "files": files,
            "learnings": learnings,
            "timestamp": datetime.now().isoformat()
        })

    def get_progress(self) -> list:
        """Get all progress entries."""
        return self.progress_table.all()

    def add_learning(self, category: str, content: str):
        """Add a reusable learning."""
        self.learnings_table.insert({
            "category": category,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })

    def get_learnings(self) -> list:
        """Get all learnings."""
        return self.learnings_table.all()

    def save_state(self, key: str, value: Any):
        """Save state value."""
        State = Query()
        existing = self.state_table.search(State.key == key)
        if existing:
            self.state_table.update({"value": value}, State.key == key)
        else:
            self.state_table.insert({"key": key, "value": value})

    def get_state(self, key: str, default: Any = None) -> Any:
        """Get state value."""
        State = Query()
        result = self.state_table.search(State.key == key)
        if result:
            return result[0]["value"]
        return default

    def mark_story_complete(self, story_id: str):
        """Mark a story as complete."""
        self.save_state(f"story_complete_{story_id}", True)

    def is_story_complete(self, story_id: str) -> bool:
        """Check if a story is complete."""
        return self.get_state(f"story_complete_{story_id}", False)

    def close(self):
        """Close the database."""
        self.db.close()


class PRDStore:
    def __init__(self, db: ProgressDB):
        self.db = db

    def save_prd(self, prd_data: Dict[str, Any]):
        """Save PRD data."""
        self.db.save_state("prd", prd_data)

    def get_prd(self) -> Optional[Dict[str, Any]]:
        """Get PRD data."""
        return self.db.get_state("prd")

    def update_story_status(self, story_id: str, passes: bool):
        """Update story status."""
        prd = self.get_prd()
        if prd:
            for story in prd.get("userStories", []):
                if story.get("id") == story_id:
                    story["passes"] = passes
                    self.save_prd(prd)
                    if passes:
                        self.db.mark_story_complete(story_id)
                    return True
        return False

    def get_next_story(self) -> Optional[Dict[str, Any]]:
        """Get the highest priority incomplete story."""
        prd = self.get_prd()
        if not prd:
            return None
        
        stories = prd.get("userStories", [])
        incomplete = [s for s in stories if not s.get("passes", False)]
        
        if not incomplete:
            return None
        
        incomplete.sort(key=lambda x: x.get("priority", 999))
        return incomplete[0]

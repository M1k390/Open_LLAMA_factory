"""Tests for store module."""

import tempfile
import json
from pathlib import Path
from store import ProgressDB, PRDStore


class TestProgressDB:
    def test_init(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_db.json"
            db = ProgressDB(db_path)
            
            assert db.db_path == db_path
            assert db.db is not None
            db.close()

    def test_add_and_get_progress(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_db.json"
            db = ProgressDB(db_path)
            
            db.add_progress("US-001", "First story", ["file1.py"], ["learning1"])
            progress = db.get_progress()
            
            assert len(progress) == 1
            assert progress[0]["story_id"] == "US-001"
            db.close()

    def test_add_and_get_learnings(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_db.json"
            db = ProgressDB(db_path)
            
            db.add_learning("pattern", "Use X for Y")
            learnings = db.get_learnings()
            
            assert len(learnings) == 1
            assert learnings[0]["category"] == "pattern"
            db.close()

    def test_save_and_get_state(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_db.json"
            db = ProgressDB(db_path)
            
            db.save_state("key1", "value1")
            value = db.get_state("key1")
            
            assert value == "value1"
            db.close()

    def test_get_state_default(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_db.json"
            db = ProgressDB(db_path)
            
            value = db.get_state("nonexistent", "default")
            
            assert value == "default"
            db.close()

    def test_mark_story_complete(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_db.json"
            db = ProgressDB(db_path)
            
            db.mark_story_complete("US-001")
            
            assert db.is_story_complete("US-001") is True
            assert db.is_story_complete("US-999") is False
            db.close()


class TestPRDStore:
    def test_save_and_get_prd(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_db.json"
            db = ProgressDB(db_path)
            store = PRDStore(db)
            
            prd_data = {
                "project": "Test",
                "userStories": [{"id": "US-001", "passes": False}]
            }
            store.save_prd(prd_data)
            
            retrieved = store.get_prd()
            assert retrieved["project"] == "Test"
            db.close()

    def test_update_story_status(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_db.json"
            db = ProgressDB(db_path)
            store = PRDStore(db)
            
            store.save_prd({
                "userStories": [
                    {"id": "US-001", "passes": False, "priority": 1},
                    {"id": "US-002", "passes": False, "priority": 2}
                ]
            })
            
            result = store.update_story_status("US-001", True)
            
            assert result is True
            prd = store.get_prd()
            assert prd["userStories"][0]["passes"] is True
            db.close()

    def test_get_next_story(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_db.json"
            db = ProgressDB(db_path)
            store = PRDStore(db)
            
            store.save_prd({
                "userStories": [
                    {"id": "US-002", "passes": False, "priority": 2},
                    {"id": "US-001", "passes": False, "priority": 1},
                    {"id": "US-003", "passes": True, "priority": 3}
                ]
            })
            
            story = store.get_next_story()
            
            assert story["id"] == "US-001"
            assert story["priority"] == 1
            db.close()

    def test_get_next_story_all_complete(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_db.json"
            db = ProgressDB(db_path)
            store = PRDStore(db)
            
            store.save_prd({
                "userStories": [
                    {"id": "US-001", "passes": True},
                    {"id": "US-002", "passes": True}
                ]
            })
            
            story = store.get_next_story()
            
            assert story is None
            db.close()

    def test_get_next_story_no_prd(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_db.json"
            db = ProgressDB(db_path)
            store = PRDStore(db)
            
            story = store.get_next_story()
            
            assert story is None
            db.close()

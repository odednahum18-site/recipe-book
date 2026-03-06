"""
Repository pattern for data access.
JSON file implementation for local dev. Swap to Firestore for production.
"""
import json
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from config import DATA_DIR


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _generate_id() -> str:
    return uuid.uuid4().hex[:12]


class JSONRepository:
    """JSON file-backed repository. Each collection is a separate JSON file."""

    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)

    def _file_path(self, collection: str) -> str:
        return os.path.join(DATA_DIR, f"{collection}.json")

    def _read_all(self, collection: str) -> List[Dict[str, Any]]:
        path = self._file_path(collection)
        if not os.path.exists(path):
            return []
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write_all(self, collection: str, data: List[Dict[str, Any]]):
        path = self._file_path(collection)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def get_all(self, collection: str) -> List[Dict[str, Any]]:
        return self._read_all(collection)

    def get_by_id(self, collection: str, item_id: str) -> Optional[Dict[str, Any]]:
        items = self._read_all(collection)
        for item in items:
            if item.get("id") == item_id:
                return item
        return None

    def get_by_field(self, collection: str, field: str, value: Any) -> Optional[Dict[str, Any]]:
        items = self._read_all(collection)
        for item in items:
            if item.get(field) == value:
                return item
        return None

    def query(self, collection: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        items = self._read_all(collection)
        if not filters:
            return items
        result = []
        for item in items:
            match = True
            for key, value in filters.items():
                if item.get(key) != value:
                    match = False
                    break
            if match:
                result.append(item)
        return result

    def create(self, collection: str, data: Dict[str, Any]) -> Dict[str, Any]:
        items = self._read_all(collection)
        if "id" not in data:
            data["id"] = _generate_id()
        data["created_at"] = _now_iso()
        data["updated_at"] = _now_iso()
        items.append(data)
        self._write_all(collection, items)
        return data

    def update(self, collection: str, item_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        items = self._read_all(collection)
        for i, item in enumerate(items):
            if item.get("id") == item_id:
                item.update(data)
                item["updated_at"] = _now_iso()
                items[i] = item
                self._write_all(collection, items)
                return item
        return None

    def delete(self, collection: str, item_id: str) -> bool:
        items = self._read_all(collection)
        new_items = [item for item in items if item.get("id") != item_id]
        if len(new_items) == len(items):
            return False
        self._write_all(collection, new_items)
        return True

    def count(self, collection: str, filters: Optional[Dict[str, Any]] = None) -> int:
        return len(self.query(collection, filters))

    def exists(self, collection: str, field: str, value: Any) -> bool:
        return self.get_by_field(collection, field, value) is not None


# Singleton
db = JSONRepository()

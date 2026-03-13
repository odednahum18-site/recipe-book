"""
Firestore implementation of the Repository pattern.
Same interface as JSONRepository for seamless swap.
"""
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from google.cloud import firestore


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _generate_id() -> str:
    return uuid.uuid4().hex[:12]


class FirestoreRepository:
    """Firestore-backed repository with the same interface as JSONRepository."""

    def __init__(self):
        self._db = firestore.Client()

    def _col(self, collection: str):
        return self._db.collection(collection)

    def get_all(self, collection: str) -> List[Dict[str, Any]]:
        docs = self._col(collection).stream()
        return [{"id": doc.id, **doc.to_dict()} for doc in docs]

    def get_by_id(self, collection: str, item_id: str) -> Optional[Dict[str, Any]]:
        doc = self._col(collection).document(item_id).get()
        if doc.exists:
            return {"id": doc.id, **doc.to_dict()}
        return None

    def get_by_field(self, collection: str, field: str, value: Any) -> Optional[Dict[str, Any]]:
        docs = self._col(collection).where(field, "==", value).limit(1).stream()
        for doc in docs:
            return {"id": doc.id, **doc.to_dict()}
        return None

    def query(self, collection: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        ref = self._col(collection)
        if filters:
            for key, value in filters.items():
                ref = ref.where(key, "==", value)
        docs = ref.stream()
        return [{"id": doc.id, **doc.to_dict()} for doc in docs]

    def create(self, collection: str, data: Dict[str, Any]) -> Dict[str, Any]:
        item_id = data.pop("id", None) or _generate_id()
        data["created_at"] = _now_iso()
        data["updated_at"] = _now_iso()
        self._col(collection).document(item_id).set(data)
        data["id"] = item_id
        return data

    def update(self, collection: str, item_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        doc_ref = self._col(collection).document(item_id)
        doc = doc_ref.get()
        if not doc.exists:
            return None
        data["updated_at"] = _now_iso()
        doc_ref.update(data)
        updated = doc.to_dict()
        updated.update(data)
        updated["id"] = item_id
        return updated

    def delete(self, collection: str, item_id: str) -> bool:
        doc_ref = self._col(collection).document(item_id)
        doc = doc_ref.get()
        if not doc.exists:
            return False
        doc_ref.delete()
        return True

    def count(self, collection: str, filters: Optional[Dict[str, Any]] = None) -> int:
        return len(self.query(collection, filters))

    def exists(self, collection: str, field: str, value: Any) -> bool:
        return self.get_by_field(collection, field, value) is not None

    def query_recipes(
        self,
        category_id: Optional[str] = None,
        tag: Optional[str] = None,
        search: Optional[str] = None,
        sort_by: str = "newest",
        offset: int = 0,
        limit: int = 12,
    ) -> tuple:
        """Query published recipes using Firestore server-side filtering.
        Returns (results, total_count)."""
        ref = self._col("recipes").where("published", "==", True)

        # Firestore supports array_contains for tags and category_ids
        if tag:
            ref = ref.where("tags", "array_contains", tag)
        if category_id:
            # Can't combine two array_contains, fall back to client-side
            if not tag:
                ref = ref.where("category_ids", "array_contains", category_id)

        # Server-side sorting (only if no search — search needs client-side)
        if not search:
            if sort_by == "stars":
                ref = ref.order_by("star_count", direction=firestore.Query.DESCENDING)
            elif sort_by == "name":
                ref = ref.order_by("name.en")
            else:
                ref = ref.order_by("created_at", direction=firestore.Query.DESCENDING)

        # Fetch all matching docs
        docs = ref.stream()
        recipes = [{"id": doc.id, **doc.to_dict()} for doc in docs]

        # Client-side filtering for cases Firestore can't handle
        if category_id and tag:
            # category_id couldn't be applied server-side when tag was also used
            recipes = [r for r in recipes if category_id in r.get("category_ids", [])]

        if search:
            search_lower = search.lower()
            recipes = [
                r for r in recipes
                if search_lower in r.get("name", {}).get("en", "").lower()
                or search_lower in r.get("name", {}).get("he", "")
            ]
            # Sort client-side since search prevented server-side sorting
            if sort_by == "stars":
                recipes.sort(key=lambda r: r.get("star_count", 0), reverse=True)
            elif sort_by == "name":
                recipes.sort(key=lambda r: r.get("name", {}).get("en", "").lower())
            else:
                recipes.sort(key=lambda r: r.get("created_at", ""), reverse=True)

        total = len(recipes)
        return recipes[offset : offset + limit], total

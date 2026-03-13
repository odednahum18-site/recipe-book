"""Pydantic models and constants for the Recipe Book API."""
from typing import Optional, List, Literal
from pydantic import BaseModel


class BilingualText(BaseModel):
    en: str
    he: str


class IngredientInput(BaseModel):
    text: BilingualText
    amount: str
    unit: Optional[dict] = None


class RecipeCreate(BaseModel):
    name: BilingualText
    recipe_of: Optional[BilingualText] = None
    category_ids: List[str]
    tags: Optional[List[str]] = []
    ingredients: List[IngredientInput]
    steps: BilingualText
    images: Optional[List[dict]] = []
    published: Optional[bool] = False
    prep_time: Optional[str] = None
    difficulty: Optional[Literal["easy", "medium", "hard"]] = None
    servings: Optional[int] = None


class RecipeUpdate(BaseModel):
    name: Optional[BilingualText] = None
    recipe_of: Optional[BilingualText] = None
    category_ids: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    ingredients: Optional[List[IngredientInput]] = None
    steps: Optional[BilingualText] = None
    images: Optional[List[dict]] = None
    published: Optional[bool] = None
    prep_time: Optional[str] = None
    difficulty: Optional[Literal["easy", "medium", "hard"]] = None
    servings: Optional[int] = None


class LoginRequest(BaseModel):
    username: str
    password: str


class StarRequest(BaseModel):
    visitor_id: str


class CategoryCreate(BaseModel):
    name: BilingualText
    icon: Optional[str] = ""
    order: Optional[int] = 0


class CategoryOrderItem(BaseModel):
    id: str
    order: int


class GoogleLoginRequest(BaseModel):
    credential: str


class InviteRequest(BaseModel):
    email: str
    display_name: Optional[str] = ""


class TranslateFieldItem(BaseModel):
    field: str
    value: str
    format: Literal["text", "html"] = "text"


class TranslateRequest(BaseModel):
    texts: List[TranslateFieldItem]
    source_lang: str
    target_lang: str


DIETARY_TAGS = [
    {"slug": "meat", "name": {"en": "Meat", "he": "\u05d1\u05e9\u05e8\u05d9"}},
    {"slug": "dairy", "name": {"en": "Dairy", "he": "\u05d7\u05dc\u05d1\u05d9"}},
    {"slug": "parve", "name": {"en": "Parve", "he": "\u05e4\u05e8\u05d5\u05d5\u05d4"}},
    {"slug": "fish", "name": {"en": "Fish", "he": "\u05d3\u05d2\u05d9\u05dd"}},
    {"slug": "chicken", "name": {"en": "Chicken", "he": "\u05e2\u05d5\u05e3"}},
]

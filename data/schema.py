from __future__ import annotations
import re
from pydantic import BaseModel, field_validator
from typing import Optional, Any
from enum import Enum

class Difficulty(str, Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"

class YarnSpec(BaseModel):
    weight: str
    amount: str
    color: str = ""

class Materials(BaseModel):
    yarn: list[YarnSpec]
    hook: str
    notions: list[str] = []

class Round(BaseModel):
    round: int
    instruction: str
    stitch_count: int = 0

    @field_validator("round", "stitch_count", mode="before")
    @classmethod
    def coerce_int(cls, v: Any) -> int:
        if isinstance(v, int):
            return v
        m = re.search(r"\d+", str(v))
        return int(m.group()) if m else 0

class Part(BaseModel):
    name: str
    make: int = 1
    rounds: list[Round]

class Pattern(BaseModel):
    id: Optional[str] = None
    title: str
    description: str
    source_url: Optional[str] = None
    author: Optional[str] = None
    difficulty: Difficulty
    materials: Materials
    gauge: str = ""
    abbreviations: dict[str, str] = {}
    parts: list[Part]
    assembly: str = ""
    tags: list[str] = []
    freeform: bool = False

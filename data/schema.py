from __future__ import annotations
from pydantic import BaseModel
from typing import Optional
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

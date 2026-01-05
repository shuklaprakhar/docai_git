from pydantic import BaseModel
from typing import List, Dict, Any, Optional


class PageClassification(BaseModel):
    page_index: int
    category: str


class OrderItem(BaseModel):
    item_code: Optional[str]
    hipc_code: Optional[str]
    price: Optional[str]
    description: Optional[str]


class Patient(BaseModel):
    name: Optional[str]
    dob: Optional[str]
    other: Dict[str, Any] = {}


class IngestResult(BaseModel):
    file: str
    pages: int
    classifications: List[PageClassification]
    extracted: Dict[str, Any]


class IngestResponse(BaseModel):
    status: str
    results: List[IngestResult]

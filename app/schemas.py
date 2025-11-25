from pydantic import BaseModel
from typing import Optional


class OperatorCreate(BaseModel):
    name: str
    active: Optional[bool] = True
    limit: Optional[int] = 5


class OperatorOut(BaseModel):
    id: int
    name: str
    active: bool
    limit: int

    class Config:
        orm_mode = True


class SourceCreate(BaseModel):
    name: str


class SourceOut(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class SourceOperatorAssign(BaseModel):
    operator_id: int
    weight: int = 1


class ContactCreate(BaseModel):
    external_id: Optional[str] = None
    e_mail: Optional[str] = None
    source_id: int
    payload: Optional[str] = None


class ContactOut(BaseModel):
    id: int
    lead_id: int
    source_id: int
    operator_id: Optional[int] = None
    status: str
    payload: Optional[str] = None

    class Config:
        orm_mode = True


class LeadOut(BaseModel):
    id: int
    external_id: Optional[str] = None
    e_mail: Optional[str] = None

    class Config:
        orm_mode = True

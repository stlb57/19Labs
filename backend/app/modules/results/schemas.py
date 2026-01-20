from pydantic import BaseModel, Field
from typing import List, Optional, Any
from uuid import UUID
from datetime import datetime

class ResultBase(BaseModel):
    parameter_slug: str
    raw_value: str
    flag: str = "normal" 

class ResultEntry(ResultBase):
    pass

class ResultBatchUpdate(BaseModel):
    accession_id: UUID
    results: List[ResultEntry]
    final_submit: bool = False # If true, moves from draft to committed

class ResultRead(ResultBase):
    id: UUID
    test_id: Optional[UUID]
    unit: Optional[str]
    is_draft: bool
    updated_at: datetime
    
    # Delta Check
    delta_flag: bool = False
    prev_value: Optional[str] = None

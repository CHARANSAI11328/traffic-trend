from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class ReportGenerateRequest(BaseModel):
    title: Optional[str] = "Executive Road Safety Brief"
    report_type: str = "executive"  # executive, geographical, severity, risk
    format: str = "pdf"             # pdf, excel, csv
    state: Optional[str] = "All"
    severity: Optional[str] = "All"
    year: Optional[int] = 0
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class ReportResponse(BaseModel):
    id: int
    title: str
    report_type: str
    format: str
    file_path: str
    generated_at: datetime
    status: str

    class Config:
        from_attributes = True

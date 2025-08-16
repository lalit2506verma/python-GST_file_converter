from typing import List, Literal, Optional
from pydantic import BaseModel

class GSTINB2CSItem(BaseModel):
    typ: str
    pos: str
    rt: float
    txval: float
    csamt: float
    sply_ty: Literal["INTRA", "INTER"]
    iamt: Optional[float] = None
    samt: Optional[float]= None
    camt: Optional[float]= None


class GSTINResponse(BaseModel):
    gstin: str
    fp: str
    version: str
    hash: str
    b2cs: List[GSTINB2CSItem]

class ProcessResponse(BaseModel):
    pivot_excel: str
    b2cs_csv: str
    gst_json: str

class InvoiceStats(BaseModel):
    initial_invoice: Optional[int]
    last_invoice: Optional[int]
    total_invoice_count: int

class SplitInvoiceResponse(BaseModel):
    invoice_records: list
    credit_note_records: list

class StatsResponse(BaseModel):
    invoice_stats: InvoiceStats
    credit_note_stats: InvoiceStats
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
import pandas as pd, tempfile
from app.services.fileio import read_file
from app.services.invoices import generate_invoice_summary

router = APIRouter(tags=["Invoices"])

@router.post("/meesho-tax_invoice/")
async def m_tax_invoice(tax_invoice: UploadFile = File(...)):
    df = read_file(tax_invoice)
    required = ["Type", "Invoice No."]
    if not all(c in df.columns for c in required):
        raise HTTPException(status_code=422, detail=f"Missing required columns: {required}")

    out_rows = []
    for key in ["INVOICE", "CREDIT NOTE"]:
        part = df[df["Type"] == key].copy()
        out_rows.append(generate_invoice_summary(part, key, col="Invoice No."))

    summary = pd.concat(out_rows, ignore_index=True)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
        summary.to_csv(tmp.name, index=False)
        return FileResponse(tmp.name, filename="invoice_summary.csv", media_type="text/csv")

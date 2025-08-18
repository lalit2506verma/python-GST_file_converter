import os, tempfile, pandas as pd
from fastapi import UploadFile
from app.core.settings import settings

def ensure_dirs() -> None:
    os.makedirs(settings.SAVE_DIR, exist_ok=True)

def read_file(upload: UploadFile) -> pd.DataFrame:
    name = (upload.filename or "").lower()
    if name.endswith(".csv"):
        return pd.read_csv(upload.file)
    elif name.endswith((".xls", ".xlsx")):
        return pd.read_excel(upload.file)
    raise ValueError(f"Unsupported file type: {name}")

def save_temp_csv(df: pd.DataFrame) -> str:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
        df.to_csv(tmp.name, index=False)
        return tmp.name

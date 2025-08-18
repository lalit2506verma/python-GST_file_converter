import re
from typing import Optional, Dict

import pandas as pd

def split_by_type(df: pd.DataFrame, type_col: str = "Type"):
    ser = df[type_col].astype(str).str.upper().str.strip()
    return df[ser == "INVOICE"].copy(), df[ser == "CREDIT NOTE"].copy()

def extract_invoice_number_stats(df: pd.DataFrame, col: str = "Invoice No.") -> Optional[Dict[str, str]]:
    if df.empty:
        return None

    def extract_suffix_number(invoice: str) -> int:
        # Extract the last number from the string (numeric suffix)
        match = re.search(r"(\d+)$", str(invoice))
        return int(match.group()) if match else -1

    df["_num"] = df[col].apply(extract_suffix_number)

    min_invoice = df.loc[df["_num"].idxmin(), col]
    max_invoice = df.loc[df["_num"].idxmax(), col]
    count = len(df)

    df.drop(columns=["_num"])

    return {
        "min_invoice": min_invoice,
        "max_invoice": max_invoice,
        "count": str(count),
    }

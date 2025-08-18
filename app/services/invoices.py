import re
from typing import Optional, Dict

import pandas as pd

DOC_TYPE_MAPPING = {
    "INVOICE": "Invoice for outward supply",
    "CREDIT NOTE": "Credit Note",
}

def split_by_type(df: pd.DataFrame, type_col: str = "Type"):
    ser = df[type_col].astype(str).str.upper().str.strip()
    return df[ser == "INVOICE"].copy(), df[ser == "CREDIT NOTE"].copy()

def extract_invoice_number_stats(df: pd.DataFrame, type: str, col: str) -> pd.DataFrame:

    if type not in DOC_TYPE_MAPPING:
        raise ValueError(f"Wrong Nature of document: {type}. Allowed: {list(DOC_TYPE_MAPPING.keys())}")

    nature_of_doc = DOC_TYPE_MAPPING[type]

    if df.empty:
        return pd.DataFrame([{
            "Nature of Document": nature_of_doc,
            "Sr. No. From": None,
            "Sr. No. To": None,
            "Total Number": 0,
            "Cancelled": 0
        }])

    def extract_suffix_number(invoice: str) -> int:
        # Extract the last number from the string (numeric suffix)
        match = re.search(r"(\d+)$", str(invoice))
        return int(match.group()) if match else -1

    df["_num"] = df[col].apply(extract_suffix_number)

    min_invoice = df.loc[df["_num"].idxmin(), col]
    max_invoice = df.loc[df["_num"].idxmax(), col]
    total_count = len(df)

    df.drop(columns=["_num"])
    cancelled_count = 0

    summary = pd.DataFrame([{
        "Nature of Document": nature_of_doc,
        "Sr. No. From": min_invoice,
        "Sr. No. To": max_invoice,
        "Total Number": total_count,
        "Cancelled": cancelled_count
    }])

    return summary

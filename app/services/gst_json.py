import json, pandas as pd
from app.core.settings import settings

B2CS_MAPPING = {
    "Rate": "rt",
    "Type": "typ",
    "Place Of Supply": "pos",
    "Taxable Value": "txval",
    "Cess Amount": "csamt",
}

def csv_to_gst_json(df: pd.DataFrame, output_path: str) -> str:
    df_json = df.copy()
    df_json["pos"] = df_json["Place Of Supply"].apply(lambda pos: str(pos).split("-")[0])
    df_json["Taxable Value"] = df_json["Taxable Value"].apply(lambda v: round(v, 2))

    gst_state = settings.GSTIN[:2]
    df_json["sply_ty"] = df_json["pos"].apply(lambda c: "INTRA" if c == gst_state else "INTER")

    df_json["iamt"] = df_json.apply(
        lambda r: round((r["Rate"] / 100) * r["Taxable Value"], 2) if r["sply_ty"] == "INTER" else 0.0,
        axis=1
    )
    df_json["camt"] = df_json.apply(
        lambda r: round(((r["Rate"] / 2) / 100) * r["Taxable Value"], 2) if r["sply_ty"] == "INTRA" else 0.0,
        axis=1
    )
    df_json["samt"] = df_json["camt"]

    df_json = df_json.rename(columns=B2CS_MAPPING)

    records = []
    for _, row in df_json.iterrows():
        rec = {k: v for k, v in row.items() if k in B2CS_MAPPING.values() or k == "sply_ty"}
        if row["sply_ty"] == "INTER":
            if row["iamt"] != 0: rec["iamt"] = row["iamt"]
        else:
            if row["camt"] != 0: rec["camt"] = row["camt"]
            if row["samt"] != 0: rec["samt"] = row["samt"]
        records.append(rec)

    payload = {
        "gstin": settings.GSTIN, "fp": settings.FP,
        "version": settings.VERSION, "hash": settings.HASH_VAL,
        "b2cs": records
    }
    with open(output_path, "w", encoding="utf-8") as jf:
        json.dump(payload, jf, indent=4)
    return output_path

import json

from config import GSTIN, FP, VERSION, HASH_VAL, B2CS_MAPPING

def csv_to_gst_json(df, output_path):

    #Copying the data
    df_json = df.copy()

    # Extracting the only state code (first two digits of the "Place of supply" column)
    df_json["pos"] = df_json["Place Of Supply"].apply(lambda pos: str(pos).split("-")[0])

    df_json["Taxable Value"] = df_json["Taxable Value"].apply(lambda val: round(val, 2))

    # Adding supply type column based on GSTIN first 2 digit
    gst_state_code = GSTIN[:2]
    df_json["sply_ty"] = df_json["pos"].apply(
        lambda code: "INTRA" if code == gst_state_code else "INTER"
    )

    # Calculate tax as according to "Place of supply"
    df_json["iamt"] = df_json.apply(
        lambda row: round((row["Rate"] / 100) * row["Taxable Value"], 2)
        if row["sply_ty"] == "INTER" else 0.0,
        axis = 1
    )

    df_json["camt"] = df_json.apply(
        lambda row: round(((row["Rate"] / 2) / 100) * row["Taxable Value"], 2)
        if row["sply_ty"] == "INTRA" else 0.0,
        axis = 1
    )

    df_json["samt"] = df_json["camt"]

    # Rename other columns according to mapping
    df_json = df_json.rename(columns=B2CS_MAPPING)

    records = []
    for _, row in df_json.iterrows():
        record = {k: v for k, v in row.items() if k in B2CS_MAPPING.values() or k == "sply_ty"}

        if row["sply_ty"] == "INTER":   # Different state -> IGST
            if row["iamt"] != 0:
                record["iamt"] = row["iamt"]
        elif row["sply_ty"] == "INTRA":  # Same state -> SGST and CGST
            if row["camt"] != 0:
                record["camt"] = row["camt"]
            if row["samt"] != 0:
                record["samt"] = row["samt"]

        records.append(record)

    gst_json = {
        "gstin": GSTIN,
        "fp": FP,
        "version": VERSION,
        "hash": HASH_VAL,
        "b2cs": records
    }

    with open(output_path, "w", encoding="utf-8") as jf:
        json.dump(gst_json, jf, indent=4)

    return output_path

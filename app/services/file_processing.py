from typing import Iterable, Dict

import pandas as pd

from app.core.config import STATES_CODES

# Read EXCEL or CSV file
def read_file(upload_file):
    filename = upload_file.filename.lower()
    if filename.endswith(".csv"):
        return pd.read_csv(upload_file.file)
    elif filename.endswith((".xls", ".xlsx")):
        return pd.read_excel(upload_file.file)
    else:
        raise ValueError(f"Unsupported file type: {filename}")

# Create PIVOT table
def make_pivot(df):
    return pd.pivot_table(
        df,
        index=['end_customer_state_new', 'gst_rate'],
        values='total_taxable_sale_value',
        aggfunc='sum',
        fill_value=0
    )

def require_columns(df: pd.DataFrame, cols: Iterable[str]):
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing Required Columns: {missing}")

def add_state_code(state_name: str) -> str:
    return STATES_CODES.get(state_name, state_name)

# Converting CSV file from PIVOT table
def final_csv_file(pivot_table) -> pd.DataFrame:
    place_of_supply = 'Place Of Supply'
    rate = 'Rate'
    taxable_value = 'Taxable Value'
    _type = 'Type'
    applicable_tax_rate = 'Applicable % of Tax Rate'
    cess_amount = 'Cess Amount'
    gst_no = 'E-Commerce GSTIN'

    df = pivot_table.reset_index().rename(columns={
        'end_customer_state_new': place_of_supply,
        'gst_rate': rate,
        'total_taxable_sale_value': taxable_value
    })

    df[place_of_supply] = df[place_of_supply].ffill().apply(add_state_code)
    df[_type] = 'OE'
    df[applicable_tax_rate] = ''
    df[cess_amount] = 0
    df[gst_no] = ''

    return df[[_type, place_of_supply, rate, applicable_tax_rate, taxable_value, cess_amount, gst_no]]


# def doc_csv_file(rec: Dict[str, str], type: str) -> pd.DataFrame:
#     if
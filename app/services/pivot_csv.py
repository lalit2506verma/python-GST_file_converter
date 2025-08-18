import pandas as pd
from app.core.settings import STATES_CODES

def make_pivot(df: pd.DataFrame) -> pd.DataFrame:
    return pd.pivot_table(
        df,
        index=['end_customer_state_new', 'gst_rate'],
        values='total_taxable_sale_value',
        aggfunc='sum',
        fill_value=0
    )

def add_state_code(state_name: str) -> str:
    return STATES_CODES.get(state_name, state_name)

def final_csv_file(pivot_table: pd.DataFrame) -> pd.DataFrame:
    place = 'Place Of Supply'; rate = 'Rate'; taxable = 'Taxable Value'
    typ = 'Type'; app_rate = 'Applicable % of Tax Rate'
    cess = 'Cess Amount'; gst_no = 'E-Commerce GSTIN'

    df = pivot_table.reset_index().rename(columns={
        'end_customer_state_new': place,
        'gst_rate': rate,
        'total_taxable_sale_value': taxable
    })

    df[place] = df[place].ffill().apply(add_state_code)
    df[typ] = 'OE'; df[app_rate] = ''; df[cess] = 0; df[gst_no] = ''
    return df[[typ, place, rate, app_rate, taxable, cess, gst_no]]

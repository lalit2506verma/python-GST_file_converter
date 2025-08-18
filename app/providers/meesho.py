import pandas as pd
from app.providers.base import SalesProvider

class MeeshoProvider(SalesProvider):
    name = "meesho"

    def normalize_sales(self, sales_df: pd.DataFrame) -> pd.DataFrame:
        # ensure required cols exist; pass-through for your current schema
        return sales_df[["end_customer_state_new","total_taxable_sale_value","gst_rate"]].copy()

    def normalize_returns(self, returns_df: pd.DataFrame) -> pd.DataFrame:
        df = returns_df[["end_customer_state_new","total_taxable_sale_value","gst_rate"]].copy()
        df["total_taxable_sale_value"] *= -1
        return df

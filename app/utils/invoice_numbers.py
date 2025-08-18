import re, pandas as pd
from typing import Optional

def extract_suffix_number(inv: str) -> int:
    if not isinstance(inv, str): return -1
    m = re.search(r"(\d+)$", inv)
    return int(m.group(1)) if m else -1

def min_max_whole(df: pd.DataFrame, col: str) -> tuple[Optional[str], Optional[str], int]:
    if df.empty: return None, None, 0
    tmp = df.copy()
    tmp["_num"] = tmp[col].apply(extract_suffix_number)
    min_inv = tmp.loc[tmp["_num"].idxmin(), col]
    max_inv = tmp.loc[tmp["_num"].idxmax(), col]
    return min_inv, max_inv, len(tmp)

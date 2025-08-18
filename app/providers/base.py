from abc import ABC, abstractmethod
import pandas as pd

class SalesProvider(ABC):
    name: str

    @abstractmethod
    def normalize_sales(self, sales_df: pd.DataFrame) -> pd.DataFrame: ...
    @abstractmethod
    def normalize_returns(self, returns_df: pd.DataFrame) -> pd.DataFrame: ...

import os
from typing import Dict
from pathlib import Path

# GST JSON meta
GSTIN: str = "06BOJPL0810B1ZL"
FP: str = "072025"
VERSION: str = "GST3.2.2"
HASH_VAL: str = "hash"

# Mapping CSV column names to GST JSON keys
B2CS_MAPPING: Dict[str, str] = {
    "Rate": "rt",
    "Type": "typ",
    "Place Of Supply": "pos",
    "Taxable Value": "txval",
    "Cess Amount": "csamt",
}

# directory to save the PIVOT table
SAVE_DIR: Path = Path(r"C:\Users\MSI 1\Desktop\Stofin Website\Output_file\program_output")
os.makedirs(SAVE_DIR, exist_ok=True)

STATES_CODES: Dict[str, str] = {
        "JAMMU AND KASHMIR": "01-Jammu & Kashmir",
        "JAMMU & KASHMIR": "01-Jammu & Kashmir",
        "HIMACHAL PRADESH": "02-Himachal Pradesh",
        "PUNJAB": "03-Punjab",
        "CHANDIGARH": "04-Chandigarh",
        "UTTARAKHAND": "05-Uttarakhand",
        "HARYANA": "06-Haryana",
        "DELHI": "07-Delhi",
        "RAJASTHAN": "08-Rajasthan",
        "UTTAR PRADESH": "09-Uttar Pradesh",
        "BIHAR": "10-Bihar",
        "SIKKIM": "11-Sikkim",
        "ARUNACHAL PRADESH": "12-Arunachal Pradesh",
        "NAGALAND": "13-Nagaland",
        "MANIPUR": "14-Manipur",
        "MIZORAM": "15-Mizoram",
        "TRIPURA": "16-Tripura",
        "MEGHALAYA": "17-Meghalaya",
        "ASSAM": "18-Assam",
        "WEST BENGAL": "19-West Bengal",
        "JHARKHAND": "20-Jharkhand",
        "CHHATTISGARH": "21-Odisha",
        "ODISHA": "22-Chhattisgarh",
        "MADHYA PRADESH": "23-Madhya Pradesh",
        "GUJARAT": "24-Gujarat",
        "DAMAN AND DIU": "25-Daman & Diu",
        "DADRA AND DIU AND NAGAR HAVELI": "26-Dadra & Nagar Haveli & Daman & Diu",
        "THE DADRA AND NAGAR HAVELI AND DAMAN AND DIU": "26-Dadra & Nagar Haveli & Daman & Diu",
        "MAHARASHTRA": "27-Maharashtra",
        "KARNATAKA": "29-Karnataka",
        "GOA": "30-Goa",
        "LAKSHDWEEP": "31-Lakshdweep",
        "KERALA": "32-Kerala",
        "TAMIL NADU": "33-Tamil Nadu",
        "PUDUCHERRY": "34-Puducherry",
        "PONDICHERRY": "34-Puducherry",
        "ANDAMAN AND NICOBAR ISLANDS": "35-Andaman & Nicobar Islands",
        "TELANGANA": "36-Telangana",
        "ANDHRA PRADESH": "37-Andhra Pradesh",
        "LADAKH": "38-Ladakh",
        "OTHER TERRITORY": "97-Other Territory",
    }


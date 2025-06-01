import os
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
import pandas as pd
import warnings
import tempfile

warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

STATES_CODES = {
        "JAMMU AND KASHMIR": "01",
        "HIMACHAL PRADESH": "02",
        "PUNJAB": "03",
        "CHANDIGARH": "04",
        "UTTARAKHAND": "05",
        "HARYANA": "06",
        "DELHI": "07",
        "RAJASTHAN": "08",
        "UTTAR PRADESH": "09",
        "BIHAR": "10",
        "SIKKIM": "11",
        "ARUNACHAL PRADESH": "12",
        "NAGALAND": "13",
        "MANIPUR": "14",
        "MIZORAM": "15",
        "TRIPURA": "16",
        "MEGHALAYA": "17",
        "ASSAM": "18",
        "WEST BENGAL": "19",
        "JHARKHAND": "20",
        "CHHATTISGARH": "21",
        "ODISHA": "22",
        "MADHYA PRADESH": "23",
        "GUJARAT": "24",
        "DAMAN AND DIU": "25",
        "DADRA AND DIU AND NAGAR HAVELI": "26",
        "MAHARASHTRA": "27",
        "KARNATAKA": "29",
        "GOA": "30",
        "LAKSHADWEEP": "31",
        "KERALA": "32",
        "TAMIL NADU": "33",
        "PUDUCHERRY": "34",
        "ANDAMAN AND NICOBAR ISLANDS": "35",
        "TELANGANA": "36",
        "ANDHRA PRADESH": "37",
        "LADAKH": "38",
        "OTHER TERRITORY": "97",
        "CENTRE JURISDICTION": "99"
    }

app = FastAPI()

@app.post("/process/")
async def process_file(
        sales_file : UploadFile = File(...),
        return_sales_file : UploadFile = File(...),
        background_tasks: BackgroundTasks = BackgroundTasks()
):

    print("FastAPI hit")
    #Defining important columns
    selected_col = [
        'end_customer_state_new',
        'total_taxable_sale_value',
        'gst_rate'
    ]

    try:
        # Validating the files format and assigning the files
        sales_df = read_file(sales_file)
        return_sales_df = read_file(return_sales_file)

        # Ensure required columns are present in the files
        if not all(col in sales_df.columns for col in selected_col) or not all(col in return_sales_df.columns for col in selected_col):
            raise HTTPException(status_code=422, detail=f"File must includes these column: {selected_col}")

        # Filtering and mark the return sales report as negative
        sales = sales_df[selected_col]
        returns = return_sales_df[selected_col]
        returns['total_taxable_sale_value'] *= -1

        # Combining data of both the files
        combined_file = pd.concat([sales, returns], ignore_index=True)

        # Creating Pivot table
        pivot_table = make_pivot(combined_file)

        #Converting PIVOT table into CSV file
        csv_sales_file = final_csv_file(pivot_table)

        # Save to temp File
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp:
            output_path = temp.name
            csv_sales_file.to_csv(output_path, index=False)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

    # Background cleanup
    background_tasks.add_task(os.remove, output_path)

    # returning the processed file
    return FileResponse(
        path = output_path,
        filename="messho_processed_csv_file.csv",
        media_type="text/csv"
    )


# Read file format and return the data frame
def read_file(report : UploadFile) -> pd.DataFrame:
    filename = report.filename.lower()

    if filename.endswith(".csv"):
        return pd.read_csv(report.file)

    elif filename.endswith(".xlx") or filename.endswith(".xlsx"):
        return pd.read_excel(report.file)

    else:
        raise HTTPException(
            status_code = 400,
            detail = f"Unsupported file type: {filename}. Only Only .csv, .xls, and .xlsx are supported."
        )

# Make pivot table of the combined dataframe
def make_pivot(file : pd.DataFrame):
    return pd.pivot_table(
        file,
        index=['end_customer_state_new', 'gst_rate'],
        values='total_taxable_sale_value',
        aggfunc='sum',
        fill_value=0,
        margins=False
    )

# Convert PIVOT TABLE to CSV file
def final_csv_file(pivot_table):

    #Required Columns
    place_of_supply = 'Place Of Supply'
    rate = 'Rate'
    taxable_value = 'Taxable Value'
    _type = 'Type'
    applicable_tax_rate = 'Applicable % of Tax Rate'
    cess_amount = 'Cess Amount'
    gst_no = 'E-Commerce GSTIN'

    #Resetting the index
    csv_sales_file = pivot_table.reset_index()

    # Rename columns
    csv_sales_file = csv_sales_file.rename(columns = {
        'end_customer_state_new': place_of_supply,
        'gst_rate': rate,
        'total_taxable_sale_value': taxable_value
    })

    #Formatting the states
    #csv_sales_file[place_of_supply] = csv_sales_file[place_of_supply].astype(str).apply(string.capwords)

    #Fill blank 'Place Of Supply' with the last non-blank value (forward fill)
    csv_sales_file[place_of_supply] = csv_sales_file[place_of_supply].ffill()

    # Applying function to add the state code
    csv_sales_file[place_of_supply] = csv_sales_file[place_of_supply].apply(add_state_code)

    # Add missing columns with default values
    csv_sales_file[_type] = 'OE'
    csv_sales_file[applicable_tax_rate] = ''
    csv_sales_file[cess_amount] = ''
    csv_sales_file[gst_no] = ''

    # Reorder columns to match the b2cs- Format.csv
    csv_sales_file = csv_sales_file[[_type, place_of_supply, rate, applicable_tax_rate, taxable_value, cess_amount, gst_no]]

    return csv_sales_file

# FUNCTION : Convert State to state code String
def add_state_code(state_name):
    print(state_name)
    code = STATES_CODES.get(state_name)
    if code:
        return f"{code}- {state_name}"

    return state_name

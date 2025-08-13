import os
import traceback

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
import pandas as pd
import warnings
import tempfile

warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

SAVE_DIR = r"C:\Users\MSI 1\Desktop\Stofin Website\Output_file\program_output"
os.makedirs(SAVE_DIR, exist_ok=True)

STATES_CODES = {
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

app = FastAPI()

@app.post("/process-file/")
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

        # Save pivot as excel to specific location
        excel_filename = os.path.join(SAVE_DIR, "pivot_output.xlsx")
        pivot_table.to_excel(excel_filename, index=True)
        print(f"Pivot table saved to: {excel_filename}")

        #Converting PIVOT table into CSV file
        csv_sales_file = final_csv_file(pivot_table)

        # Save to temp File
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp:
            output_path = temp.name
            csv_sales_file.to_csv(output_path, index=False)

    except Exception as e:
        print("Error occurred:", e)
        traceback.print_exc()  # This prints the full traceback to the terminal
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
        return code

    return state_name


import uvicorn

if __name__ == '__main__':
    uvicorn.run(app, host='localhost', port=8000)
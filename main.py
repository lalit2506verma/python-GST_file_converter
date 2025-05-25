import \
    os

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
import pandas as pd
import warnings
import tempfile

warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

app = FastAPI()


# @app.post("/process-excel")
# async def process_excel(file : UploadFile = File(...)):
#     print("Python started")
#     contents = await file.read()
#
#     # define the columns that need to be extracted and new columns name
#     selected_col = [
#         'end_customer_state_new',
#         'total_taxable_sale_value',
#         'gst_rate']
#     new_col_name = {
#         'State': 'end_customer_state_new',
#         'Taxable_value': 'total_taxable_sale_value',
#         'GST_rate': 'gst_rate',
#     }
#
#     # creating dataframe
#     sales = pd.read_excel(BytesIO(contents), usecols= selected_col)
#
#     #copying the read data of specific column to new Excel file
#     output = BytesIO
#     sales.to_excel(output, index = False)
#     output.seek(0)
#
#     return StreamingResponse(output, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', headers={
#         "Content-Disposition": f"attachment; filename=processed_{file.filename}.xlsx"
#     })


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

        # Save to tmep File
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as temp:
            output_path = temp.name
            pivot_table.to_excel(output_path)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

    # Background cleanup
    background_tasks.add_task(os.remove, output_path)

    # returning the processed file
    return FileResponse(
        path = output_path,
        filename="messho_processed_file.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
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


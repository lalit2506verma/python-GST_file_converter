from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
import pandas as pd
import tempfile
import os
import traceback

from services.file_processing import read_file, make_pivot, final_csv_file
from services.json_conversion import csv_to_gst_json
from config import SAVE_DIR

app = FastAPI()

@app.post("/process-file/")
async def process_file(
    sales_file: UploadFile = File(...),
    return_sales_file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    try:
        # Read Excel file
        sales_df = read_file(sales_file)
        return_sales_df = read_file(return_sales_file)

        # Checking required columns exists
        required_cols = ['end_customer_state_new', 'total_taxable_sale_value', 'gst_rate']

        if not all(c in sales_df.columns for c in required_cols) or not all(c in return_sales_df.columns for c in required_cols):
            raise HTTPException(status_code=422, detail=f"Missing required columns: {required_cols}")

        return_sales_df['total_taxable_sale_value'] *= -1
        combined_df = pd.concat(
            [sales_df[required_cols], return_sales_df[required_cols]],
            ignore_index=True
        )

        # Rounding off the "taxable value" to 4 decimal digit
        combined_df["total_taxable_sale_value"] = pd.to_numeric(combined_df["total_taxable_sale_value"], errors="coerce").round(4)

        # Creating PIVOT table from combined Data frame
        pivot_table = make_pivot(combined_df)

        # Saving pivot table
        excel_path = os.path.join(SAVE_DIR, "pivot_output.xlsx")
        pivot_table.to_excel(excel_path, index=True)

        # CSV file created
        csv_df = final_csv_file(pivot_table)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_csv:
            csv_path = temp_csv.name
            csv_df.to_csv(csv_path, index=False)

        json_path = os.path.join(SAVE_DIR, "gst_output.json")
        csv_to_gst_json(csv_df, json_path)

        background_tasks.add_task(os.remove, csv_path)

        return FileResponse(path=csv_path, filename="processed.csv", media_type="text/csv")

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


import uvicorn

if __name__ == '__main__':
    uvicorn.run(app, host='localhost', port=8000)
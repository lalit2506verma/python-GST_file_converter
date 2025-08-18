from fastapi import APIRouter, File, UploadFile, HTTPException, BackgroundTasks, Query
from fastapi.responses import FileResponse
import os, pandas as pd
from app.core.settings import settings
from app.services.fileio import read_file, save_temp_csv
from app.services.pivot_csv import make_pivot, final_csv_file
from app.services.gst_json import csv_to_gst_json
from app.providers.registry import get_provider

router = APIRouter(tags=["GST"])

@router.post("/process-file/")
async def process_file(
    sales_file: UploadFile = File(...),
    return_sales_file: UploadFile = File(...),
    provider: str = Query("meesho"),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    try:
        prov = get_provider(provider)
        sales_df = prov.normalize_sales(read_file(sales_file))
        returns_df = prov.normalize_returns(read_file(return_sales_file))

        combined = pd.concat([sales_df, returns_df], ignore_index=True)
        combined["total_taxable_sale_value"] = pd.to_numeric(
            combined["total_taxable_sale_value"], errors="coerce"
        ).round(4)

        pivot = make_pivot(combined)
        # save pivot workbook too
        pivot_path = os.path.join(settings.SAVE_DIR, "pivot_output.xlsx")
        pivot.to_excel(pivot_path, index=True)

        csv_df = final_csv_file(pivot)
        csv_path = save_temp_csv(csv_df)

        # JSON for GST portal
        json_path = os.path.join(settings.SAVE_DIR, "gst_output.json")
        csv_to_gst_json(csv_df, json_path)

        background_tasks.add_task(os.remove, csv_path)
        return FileResponse(csv_path, filename="processed.csv", media_type="text/csv")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Processing error") from e

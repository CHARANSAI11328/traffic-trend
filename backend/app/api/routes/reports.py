from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from backend.app.api.dependencies import get_repo
from backend.app.database.repository import DatabaseRepository
from backend.app.analytics.kpis import KPICalculator
from backend.app.reports.pdf_generator import PDFReportGenerator
from backend.app.reports.excel_exporter import ExcelExporter
from backend.app.schemas.reports import ReportGenerateRequest, ReportResponse
from backend.app.core.config import settings

router = APIRouter()

@router.get("", response_model=list[ReportResponse])
def list_reports(repo: DatabaseRepository = Depends(get_repo)):
    return repo.get_report_history()

@router.post("/generate", response_model=ReportResponse)
def generate_report(
    req: ReportGenerateRequest,
    repo: DatabaseRepository = Depends(get_repo)
):
    active_dataset = repo.get_active_dataset()
    dataset_id = active_dataset.id if active_dataset else None
    dataset_name = active_dataset.name if active_dataset else "Default System Dataset"

    # Fetch filtered data
    df = repo.get_records_df(
        dataset_id=dataset_id,
        state=req.state,
        severity=req.severity,
        year=req.year,
        start_date=req.start_date,
        end_date=req.end_date
    )

    if df.empty:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot generate report: No accident records found matching criteria"
        )

    kpis = KPICalculator.compute(df)
    filter_summary = f"State: {req.state} | Severity: {req.severity} | Year: {req.year or 'All Years'}"

    file_format = req.format.lower()
    if file_format == "pdf":
        out_path = PDFReportGenerator.generate_executive_report(
            kpis=kpis,
            df_filtered=df,
            dataset_name=dataset_name,
            filter_summary=filter_summary
        )
    elif file_format in ["excel", "xlsx"]:
        file_format = "excel"
        out_path = ExcelExporter.export_analytics_workbook(
            df_filtered=df,
            kpis=kpis,
            dataset_name=dataset_name
        )
    elif file_format == "csv":
        import time
        out_filename = f"Traffic_Trend_Filtered_{int(time.time())}.csv"
        out_path = settings.EXPORTS_DATA_DIR / out_filename
        df.to_csv(out_path, index=False)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unsupported format '{req.format}'")

    report_record = repo.save_report_history(
        title=req.title or "Executive Road Safety Brief",
        report_type=req.report_type,
        file_path=str(out_path),
        format=file_format,
        date_range_start=req.start_date,
        date_range_end=req.end_date
    )

    repo.log("INFO", f"Generated {file_format.upper()} report '{report_record.title}'", "ReportGenerator")

    return report_record

@router.get("/{report_id}/download")
def download_report(report_id: int, repo: DatabaseRepository = Depends(get_repo)):
    reports = repo.get_report_history(limit=100)
    target = next((r for r in reports if r.id == report_id), None)
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report record not found")

    file_path = Path(target.file_path)
    if not file_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report file not found on disk")

    media_type = "application/pdf" if target.format == "pdf" else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    if target.format == "csv":
        media_type = "text/csv"

    return FileResponse(
        path=str(file_path),
        media_type=media_type,
        filename=file_path.name
    )

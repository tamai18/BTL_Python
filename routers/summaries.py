from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import crud, schemas
from database import get_db

router = APIRouter(
    prefix="/summaries",
    tags=["Summaries"]
)

@router.post("/", response_model=schemas.MonthlySummaryResponse)
def create_summary(user_id: int, year: int, month: int, db: Session = Depends(get_db)):
    summary = crud.create_monthly_summary(db, user_id, year, month)
    if not summary:
        raise HTTPException(status_code=400, detail="⚠️ Không thể tạo tổng kết.")
    return summary


@router.get("/{user_id}/{year}/{month}", response_model=list[schemas.MonthlySummaryResponse])
def get_summary(user_id: int, year: int, month: int, db: Session = Depends(get_db)):
    summary = crud.get_summary_by_user_and_month(db, user_id, year, month)
    if not summary:
        raise HTTPException(status_code=404, detail="⚠️ Không có dữ liệu tổng kết cho tháng này.")
    return summary

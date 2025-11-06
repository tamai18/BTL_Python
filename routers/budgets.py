from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
import crud
from datetime import datetime


router = APIRouter(
    prefix="/budgets",
    tags=["Budgets"]
)

@router.get("/{user_id}/{month}")
def get_budgets_summary(user_id: int, month: str, db: Session = Depends(get_db)):
    # 1. Xử lý tháng/năm
    try:
        if "-" in month:
            part = month.split("-")
            if len(part) != 2: raise ValueError
            year, month_num = map(int, part)
        else:
            month_num = int(month)
            year = datetime.now().year

        if not (1 <= month_num <= 12):
            raise ValueError("Tháng không hợp lệ")

    except ValueError as e:
        return {"message": f"⚠️ Định dạng tháng không hợp lệ: {e}", "data": []}

    kq = crud.get_budget_summary_for_month(db, user_id, year, month_num)

    if isinstance(kq, dict) and "error" in kq:
        return {"message": kq["error"], "data": []}
    if isinstance(kq, dict) and "message" in kq:
        return {"message": kq["message"], "data": []}

    return {"data": kq}

@router.get("/check/{user_id}/{category_id}/{year}/{month}")
def check_budget(user_id: int, category_id: int, year: int, month: int, db: Session = Depends(get_db)):
    kq = crud.check_budget_exceeded(db, user_id, category_id, year, month)
    return kq
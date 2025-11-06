from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import crud, schemas
from database import get_db

router = APIRouter(
    prefix="/incomes",
    tags=["Incomes"]
)
# Tạo khoản thu
@router.post("/")
def create_income(income: schemas.IncomeCreate, user_id: int, db: Session = Depends(get_db)):
    kq = crud.create_income(db, user_id, income.category_name, income.amount, income.date, income.note)
    print(">>> Kết quả CRUD:", kq)
    if isinstance(kq, dict) and "error" in kq:
        raise HTTPException(status_code=404, detail=kq["error"])
    return kq

# Lấy tất cả khoản thu của 1 user
@router.get("/{user_id}")
def get_all_incomes(user_id: int, db: Session = Depends(get_db)):
    return crud.get_incomes_by_user(db, user_id)

# Lấy khoản thu theo tháng
@router.get("/{user_id}/month/{year}/{month}")
def get_income_by_month(user_id: int, year: int, month: int, db: Session = Depends(get_db)):
    return crud.get_incomes_by_month(db, user_id, year, month)

# Cập nhật khoản thu
@router.put("/{income_id}")
def update_income(income_id: int, update_data: schemas.IncomeUpdate, db: Session = Depends(get_db)):
    kq = crud.update_income(db, income_id, update_data.category_name, update_data.amount, update_data.date, update_data.note)
    if not kq:
        return {"error": "⚠️ Khoản thu không tồn tại."}
    return kq

# Xóa khoản thu
@router.delete("/{income_id}")
def delete_income(income_id: int, db: Session = Depends(get_db)):
    kq = crud.delete_income(db, income_id)
    if not kq:
        return {"error": "⚠️ Khoản thu không tồn tại."}
    return {"message": "🗑️ Xóa khoản thu thành công!"}
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import crud, schemas
from database import get_db
from auth import verify_token

router = APIRouter(
    prefix="/expense",
    tags=["Expense"]
)

# Tạo khoản chi
@router.post("/")
def create_expense(expense: schemas.ExpenseCreate, user_id: int, db: Session = Depends(get_db)):
    kq = crud.create_expense(db, user_id, expense.category_name, expense.amount, expense.date, expense.note)
    if isinstance(kq, dict) and "error" in kq:
        raise HTTPException(status_code=404, detail=kq["error"])
    return kq

# Lấy tất cả khoản chi của 1 user
@router.get("/{user_id}")
def get_all_expenses(user_id: int, db: Session = Depends(get_db)):
    return crud.get_expenses_by_user(db, user_id)

# Lấy khoản chi theo tháng
@router.get("/{user_id}/month/{year}/{month}")
def get_expense_by_month(user_id: int, year: int, month: int, db: Session = Depends(get_db)):
    return crud.get_expenses_by_month(db, user_id, year, month)

# Cập nhật khoản chi
@router.put("/{expense_id}")
def update_expense(expense_id: int, update_data: schemas.ExpenseUpdate, db: Session = Depends(get_db)):
    kq = crud.update_expense(db, expense_id, update_data.category_name, update_data.amount, update_data.date, update_data.note)
    if not kq:
        return {"error": "⚠️ Khoản chi không tồn tại."}
    return kq

# Xóa khoản chi
@router.delete("/{expense_id}")
def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    kq = crud.delete_expense(db, expense_id)
    if not kq:
        return {"error": "⚠️ Khoản chi không tồn tại."}
    return {"message": "🗑️ Xóa khoản chi thành công!"}
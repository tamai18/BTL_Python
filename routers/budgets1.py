from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
import crud, schemas
from datetime import datetime

router = APIRouter(
    prefix="/budgets1",
    tags=["Budgets1 (DL)"]
)

@router.post("/")
def create_budget(user_id: int, budget: schemas.BudgetCreate, db: Session = Depends(get_db)):
    kq = crud.create_budget(db, user_id, budget.category_id, budget.amount, budget.month)
    if isinstance(kq, dict) and "error" in kq:
        return {"message": kq["error"]}
    return {
        "message": f"✅ Ngân sách cho danh mục {kq.category_name} của tháng {kq.month} đã được tạo: {kq.amount:,.0f}₫",
        "data": {
            "budget_id": kq.budget_id,
            "category_id": kq.category_id,
            "category_name": kq.category_name,
            "amount": kq.amount
        }
    }

@router.put("/{budget_id}/")
def update_budget(budget_id: int, budget: schemas.BudgetBase, db: Session = Depends(get_db)):
    kq = crud.update_budget(db, budget_id, budget.category_id, budget.amount, budget.month)
    if not kq:
        return {"message": "⚠️ Ngân sách không tồn tại."}
    return kq


@router.delete("/{budget_id}")
def delete_budget(budget_id: int, category_id: int, db: Session = Depends(get_db)):
    kq = crud.delete_budget(db, budget_id, category_id)
    if not kq:
        return {"message": "⚠️ Ngân sách không tồn tại."}
    return {"message": f"🗑️ Ngân sách cho danh mục {kq.category_name} của tháng {kq.month} đã bị xóa."}


@router.get("/{user_id}/{month}")
def get_budgets_by_month(user_id: int, month: str, db: Session = Depends(get_db)):
    budgets = crud.get_budgets_by_user_and_month(db, user_id, month)
    if isinstance(budgets, dict) and "error" in budgets:
        return {"message": budgets["error"], "data": []}

    if not budgets:
        return {"message": "⚠️ Không có ngân sách nào trong tháng này.", "data": []}

    result = [
        {
            "budget_id": b.budget_id,
            "category_id": b.category_id,
            "category_name": b.category_name,
            "amount": b.amount,
            "month": b.month
        }
        for b in budgets
    ]
    return {"message": "✅ Lấy danh sách ngân sách thành công!", "data": result}
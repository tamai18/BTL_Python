from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import crud, schemas

router = APIRouter(
    prefix="/settings",
    tags=["Settings"]
)

@router.get("/{user_id}")
def get_setting(user_id: int, db: Session = Depends(get_db)):
    setting = crud.get_setting_by_user(db, user_id)
    if not setting:
        raise HTTPException(status_code=404, detail="⚠️ Cài đặt không tồn tại.")
    return {"message": "✅ Đã cài đặt thành công."}

@router.put("/{setting_id}")
def update_setting(setting_id: int, data: schemas.SettingsUpdate, db: Session = Depends(get_db)):
    kq = crud.update_setting(
        db,
        setting_id,
        currency=data.currency,
        saving_ratio=data.saving_ratio,
        language=data.language,
        theme=data.theme,
        chart_type=data.chart_type
    )
    if isinstance(kq, dict) and "error" in kq:
        raise HTTPException(status_code=400, detail=kq["error"])
    return {"message": "✅ Cập nhật cài đặt thành công."}

@router.delete("/{setting_id}")
def delete_setting(setting_id: int, db: Session = Depends(get_db)):
    kq = crud.delete_setting(db, setting_id)
    if not kq:
        raise HTTPException(status_code=404, detail="⚠️ Cài đặt không tồn tại.")
    return {"message": "🗑️ Đã xóa thành công cài đặt."}
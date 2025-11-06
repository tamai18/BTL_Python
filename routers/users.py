from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import crud, models, schemas
from auth import verify_token

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.post("/register", response_model=schemas.UserResponse)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    kq = crud.create_user(db, user.username, user.email, user.password, user.confirm_password)
    if isinstance(kq, dict) and "error" in kq:
        raise HTTPException(status_code=400, detail=f"⚠️ {kq['error']}")
    return kq

@router.post("/login")
def login_user(user: schemas.UserLogin, db: Session = Depends(get_db)):
    kq = crud.verify_login(db, user.email, user.password)
    if not kq:
        raise HTTPException(status_code=401, detail="🔒 Email hoặc password không đúng.")
    user_data = kq["user"]
    token = kq["access_token"]
    return {
        "message": "✅ Đăng nhập thành công!",
        "user_id": user_data.user_id,
        "username": user_data.username,
        "email": user_data.email,
        "access_token": token,
    }

@router.delete("/{user_id}")
def delete_user(user_id: int = Depends(verify_token), db: Session = Depends(get_db)):
    kq = crud.delete_user(db, user_id)
    if not kq:
        raise HTTPException(status_code=404, detail="🚫 Không tìm thấy người dùng!")
    return {"message": "🗑️ Xóa người dùng thành công!"}

@router.post("/logout", response_model=schemas.UserLogout)
def logout_user(user_id: int = Depends(verify_token), db: Session = Depends(get_db)):
    kq = crud.logout_user(db, user_id)
    if isinstance(kq, dict) and "error" in kq:
        raise HTTPException(status_code=404, detail=kq["error"])
    return {"message": kq["message"]}
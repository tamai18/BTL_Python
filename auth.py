from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta

from fastapi import status

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# schemes=["bcrypt"]: dùng thuật toán bcrypt để mã hóa mật khẩu
# deprecated="auto" đổi thuật toán băm (ví dụ từ bcrypt sang argon2) -> tự động nhận biết các mật khẩu cũ để vẫn xác minh được chúng.

# Mã hóa mật khẩu = hàm băm
def get_password_hash(password: str) -> str:
    if not isinstance(password, str):
        raise ValueError(f"Password không phải chuỗi, nhận được {type(password)}")

    encoded = password.encode("utf-8")
    # Nếu dài hơn 72 bytes, cắt và cảnh báo
    if len(encoded) > 72:
        print("⚠️ Password quá dài, cắt ngắn còn 72 bytes!")
        encoded = encoded[:72]
        password = encoded.decode("utf-8", errors="ignore")

    return pwd_context.hash(password)


# Xác minh mật khẩu nhập lại khi đăng kí
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password) #verify: hàm so sánh

# Tạo TOKEN
# Khóa bí mật và thuật toán mã hóa
SECRET_KEY = "4bc29a905c0fed7c3288e9602d9b80c2a6faedf3e43e280e91c6befd9a77d7e7"
ALGORITHM = "HS256"

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=120)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM) # Đóng gói mã hóa thành chuỗi token
    return encoded_jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")    #lấy token từ header Authorization
def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])  # Giải mã token -> lay lại dl ban đầu
        username: str = payload.get("user_id")     #Lấy giá trị của khóa sub (tên ng dung) trong dữ liệu token
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="⚠️ Token không hợp lệ hoặc đã hết hạn.")
        return username
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="⚠️ Không thể xác thực thông tin đăng nhập",
        )
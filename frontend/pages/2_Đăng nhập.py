import streamlit as st
import requests

# === Cấu hình ===
API_URL = "http://127.0.0.1:8000"  # backend FastAPI

st.set_page_config(page_title="Đăng nhập hệ thống", page_icon="🔐", layout="centered")

# === Nếu đã đăng nhập thì chuyển sang trang chính ===
if "logged_in" in st.session_state and st.session_state["logged_in"]:
    st.success(f"👋 Xin chào, {st.session_state['username']}!")
    st.page_link("app.py", label="➡️ Vào trang chính", icon="🏠")
    st.stop()

# === Giao diện chọn tab ===
tab_login, tab_register = st.tabs(["🔑 Đăng nhập", "🆕 Đăng ký"])

# ------------------------------------------------------------
# 🟢 TAB ĐĂNG NHẬP
# ------------------------------------------------------------
with tab_login:
    st.subheader("Đăng nhập hệ thống")

    email = st.text_input("📧 Email", key="login_email")
    password = st.text_input("🔒 Mật khẩu", type="password", key="login_password")

    if st.button("➡️ Đăng nhập", key="btn_login"):
        if not email or not password:
            st.warning("⚠️ Vui lòng nhập đầy đủ thông tin.")
        else:
            try:
                res = requests.post(f"{API_URL}/users/login", json={
                    "email": email,
                    "password": password
                })
                if res.status_code == 200:
                    data = res.json()
                    st.session_state["logged_in"] = True
                    st.session_state["user_id"] = data["user_id"]
                    st.session_state["username"] = data["username"]
                    st.session_state["email"] = data["email"]
                    st.session_state["access_token"] = data["access_token"]
                    st.success("✅ Đăng nhập thành công!")
                    st.switch_page("app.py")
                else:
                    detail = res.json().get("detail", "Đăng nhập thất bại.")
                    st.error(f"🚫 {detail}")
            except requests.exceptions.ConnectionError:
                st.error("❌ Không thể kết nối tới máy chủ backend.\nHãy kiểm tra xem FastAPI đã chạy chưa.")

# ------------------------------------------------------------
# 🔵 TAB ĐĂNG KÝ
# ------------------------------------------------------------
with tab_register:
    st.subheader("Tạo tài khoản mới")

    username = st.text_input("👤 Tên người dùng", key="reg_username")
    email_reg = st.text_input("📧 Email", key="reg_email")
    password_reg = st.text_input("🔑 Mật khẩu", type="password", key="reg_password")
    confirm_reg = st.text_input("🔁 Xác nhận mật khẩu", type="password", key="reg_confirm")

    if st.button("🆗 Đăng ký", key="btn_register"):
        if not username or not email_reg or not password_reg or not confirm_reg:
            st.warning("⚠️ Vui lòng nhập đầy đủ thông tin.")
        elif password_reg != confirm_reg:
            st.error("🚫 Mật khẩu xác nhận không khớp.")
        else:
            try:
                res = requests.post(f"{API_URL}/users/register", json={
                    "username": username,
                    "email": email_reg,
                    "password": password_reg,
                    "confirm_password": confirm_reg
                })
                if res.status_code == 200:
                    st.success("🎉 Đăng ký thành công! Bạn có thể đăng nhập ngay.")
                else:
                    detail = res.json().get("detail", "Đăng ký thất bại.")
                    st.error(f"🚫 {detail}")
            except requests.exceptions.ConnectionError:
                st.error("❌ Không thể kết nối tới máy chủ backend.")

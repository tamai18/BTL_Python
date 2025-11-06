import streamlit as st
import pandas as pd
import datetime
import requests
import time

from style import load_custom_css

# Gọi CSS toàn cục
load_custom_css()

# Ghi đè lại hàm st.set_page_config để luôn tải CSS
original_set_page_config = st.set_page_config

def custom_set_page_config(*args, **kwargs):
    load_custom_css()
    original_set_page_config(*args, **kwargs)

st.set_page_config = custom_set_page_config

# ===============================
# ⚙️ Cấu hình trang
# ===============================
st.set_page_config(page_title="Quản lý Thu Chi", page_icon="💵", layout="wide")
API_BASE = "http://127.0.0.1:8000"  # URL backend FastAPI

# ===============================
# 🧠 Kiểm tra trạng thái đăng nhập
# ===============================
if "access_token" not in st.session_state or not st.session_state["access_token"]:
    st.warning("🔒 Bạn cần đăng nhập để truy cập hệ thống.")
    st.page_link("pages/2_Đăng nhập.py", label="➡️ Quay lại trang đăng nhập", icon="🔑")
    st.stop()

TOKEN = st.session_state["access_token"]
USER_ID = st.session_state["user_id"]
USERNAME = st.session_state["username"]

AUTH_HEADERS = {"Authorization": f"Bearer {TOKEN}"}

# ===============================
# 🧾 Header giao diện
# ===============================
st.title("📘 Quản lý Thu - Chi cá nhân")
st.sidebar.success(f"👋 Xin chào, {USERNAME}!")

if st.sidebar.button("🚪 Đăng xuất"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.success("✅ Đã đăng xuất thành công!")
    time.sleep(4)
    st.switch_page("2_Đăng nhập.py")

# ===============================
# 🔧 HÀM GỌI API
# ===============================

def fetch_transactions():
    """Lấy danh sách thu & chi từ backend"""
    try:
        res_income = requests.get(f"{API_BASE}/incomes/{USER_ID}", headers=AUTH_HEADERS)
        res_expense = requests.get(f"{API_BASE}/expense/{USER_ID}", headers=AUTH_HEADERS)

        income = res_income.json() if res_income.status_code == 200 else []
        expense = res_expense.json() if res_expense.status_code == 200 else []

        for i in income:
            i["type"] = "Thu nhập"
        for e in expense:
            e["type"] = "Chi tiêu"

        return income + expense

    except Exception as e:
        st.error(f"❌ Lỗi khi tải dữ liệu: {e}")
        time.sleep(6)
        return []


def add_transaction(type_, category, amount, note, date_):
    """Thêm giao dịch mới"""
    try:
        endpoint = "incomes" if type_ == "Thu nhập" else "expense"
        url = f"{API_BASE}/{endpoint}/?user_id={USER_ID}"
        payload = {
            "category_name": category,
            "amount": amount,
            "note": note,
            "date": str(date_)
        }
        res = requests.post(url, json=payload, headers=AUTH_HEADERS)
        if res.status_code == 200:
            st.success("✅ Giao dịch đã được thêm thành công!")
            time.sleep(4)
        else:
            st.error(f"❌ Lỗi khi thêm: {res.text}")
            time.sleep(6)
    except Exception as e:
        st.error(f"⚠️ Lỗi kết nối: {e}")
        time.sleep(6)


def update_transaction(id_, type_, category, amount, note, date_):
    """Cập nhật giao dịch"""
    try:
        endpoint = "incomes" if type_ == "Thu nhập" else "expense"
        url = f"{API_BASE}/{endpoint}/{id_}"
        payload = {
            "category_name": category,  # ✅ Thêm dòng này
            "amount": amount,
            "note": note,
            "date": str(date_)
        }
        res = requests.put(url, json=payload, headers=AUTH_HEADERS)
        if res.status_code == 200:
            st.success("✅ Đã cập nhật giao dịch!")
            time.sleep(5)
        else:
            try:
                detail = res.json().get("detail", res.text)
            except:
                detail = res.text
            st.error(f"❌ Lỗi cập nhật: {detail}")
            time.sleep(6)
    except Exception as e:
        st.error(f"⚠️ Lỗi kết nối: {e}")
        time.sleep(6)


def delete_transaction(id_, type_):
    """Xóa giao dịch"""
    try:
        endpoint = "incomes" if type_ == "Thu nhập" else "expense"
        url = f"{API_BASE}/{endpoint}/{id_}"
        res = requests.delete(url, headers=AUTH_HEADERS)
        if res.status_code == 200:
            st.success("🗑️ Đã xóa giao dịch!")
            time.sleep(5)
        else:
            st.error(f"❌ Không thể xóa: {res.text}")
            time.sleep(6)
    except Exception as e:
        st.error(f"⚠️ Lỗi khi xóa: {e}")
        time.sleep(6)

# ===============================
# 🧭 Giao diện chính
# ===============================
if "mode" not in st.session_state:
    st.session_state["mode"] = "Thu nhập"
if "edit_id" not in st.session_state:
    st.session_state["edit_id"] = None

st.sidebar.header("🔧 Chức năng")
menu = st.sidebar.radio("Chọn thao tác:", ["Thêm giao dịch", "Danh sách giao dịch"])

data = pd.DataFrame(fetch_transactions())
if not data.empty:
    data["date"] = pd.to_datetime(data["date"], errors="coerce")

# ===============================
# ➕ THÊM GIAO DỊCH
# ===============================
if menu == "Thêm giao dịch":
    st.subheader("💰 Loại giao dịch")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🟢 Thu nhập"):
            st.session_state["mode"] = "Thu nhập"
    with col2:
        if st.button("🔴 Chi tiêu"):
            st.session_state["mode"] = "Chi tiêu"

    st.markdown(f"### ➕ Nhập khoản **{st.session_state['mode']}**")

    with st.form("add_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            date_ = st.date_input("📅 Ngày", datetime.date.today())
            note = st.text_input("🗒️ Ghi chú")
        with c2:
            amount = st.number_input("💵 Số tiền", min_value=0.0)
            if st.session_state["mode"] == "Thu nhập":
                category = st.selectbox("📂 Danh mục", ["Lương", "Thưởng", "Bán hàng", "Khác"])
            else:
                category = st.selectbox("📂 Danh mục", ["Ăn uống", "Hóa đơn", "Quần áo", "Mỹ phẩm"])

        submit = st.form_submit_button("💾 Lưu giao dịch")

        if submit:
            if amount == 0.0:
                st.warning("⚠️ Vui lòng nhập số tiền hợp lệ!")
                time.sleep(4)
            else:
                add_transaction(st.session_state["mode"], category, amount, note, date_)
                st.rerun()

# ===============================
# 📋 DANH SÁCH GIAO DỊCH
# ===============================
elif menu == "Danh sách giao dịch":
    st.header("📋 Danh sách Thu - Chi")

    if not data.empty:
        with st.expander("🔍 Bộ lọc nâng cao", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                category_filter = st.text_input("📂 Tìm theo danh mục", "")
                note_filter = st.text_input("🗒️ Tìm theo ghi chú", "")
            with col2:
                today = datetime.date.today()
                first_day = today.replace(day=1)
                last_day = (first_day + datetime.timedelta(days=31)).replace(day=1) - datetime.timedelta(days=1)
                start_date = st.date_input("📅 Từ ngày", value=first_day)
                end_date = st.date_input("📅 Đến ngày", value=last_day)

            filtered_data = data.copy()
            filtered_data["date"] = pd.to_datetime(filtered_data["date"], errors="coerce").dt.date

            if start_date > end_date:
                st.error("⚠️ Ngày bắt đầu phải trước hoặc bằng ngày kết thúc!")
                time.sleep(4)
                filtered_data = pd.DataFrame()
            else:
                filtered_data = filtered_data[
                    (filtered_data["date"] >= start_date) & (filtered_data["date"] <= end_date)
                ]

        if category_filter.strip():
            filtered_data = filtered_data[
                filtered_data["category_name"].str.contains(category_filter, case=False, na=False)
            ]
        if note_filter.strip():
            filtered_data = filtered_data[
                filtered_data["note"].str.contains(note_filter, case=False, na=False)
            ]

        if filtered_data.empty:
            st.warning("❌ Không tìm thấy giao dịch nào phù hợp!")
            time.sleep(5)
        else:
            total_income = filtered_data.query("type == 'Thu nhập'")["amount"].sum()
            total_expense = filtered_data.query("type == 'Chi tiêu'")["amount"].sum()
            balance = total_income - total_expense

            st.markdown(f"""
            💵 **Tổng thu:** `{total_income:,.0f} đ`  
            💸 **Tổng chi:** `{total_expense:,.0f} đ`  
            📊 **Số dư:** `{balance:,.0f} đ`
            """)
            st.markdown("---")

            for i, (_, row) in enumerate(filtered_data.iterrows()):
                color = "🟢" if row["type"] == "Thu nhập" else "🔴"
                cols = st.columns([1.2, 1.5, 2, 2, 2, 1, 1])
                cols[0].write(f"{color} {row['type']}")
                cols[1].write(row.get("category_name", ""))
                cols[2].write(f"{row['amount']:,.0f} đ")
                cols[3].write(row.get("note", ""))
                cols[4].write(pd.to_datetime(row["date"]).strftime("%d/%m/%Y"))

                if cols[5].button("✏️", key=f"edit_{i}_{row['type']}"):
                    edit_type = row["type"]

                    # Lấy ID một cách an toàn dựa trên loại
                    if edit_type == "Thu nhập":
                        edit_id = row.get("income_id")
                    else:
                        edit_id = row.get("expense_id")

                    # Fallback (dự phòng) nếu backend chỉ dùng cột "id" chung
                    if pd.isna(edit_id):
                        edit_id = row.get("id")

                    st.session_state["edit_id"] = edit_id
                    st.session_state["edit_type"] = edit_type
                    st.session_state["edit_row"] = row
                    st.rerun()

                if cols[6].button("❌", key=f"delete_{i}_{row['type']}"):
                    delete_transaction(
                        row.get("id") or row.get("income_id") or row.get("expense_id"),
                        row["type"]
                    )
                    st.rerun()

        # ====== FORM SỬA ======
        if st.session_state.get("edit_id"):
            edit_id = st.session_state["edit_id"]
            row = st.session_state["edit_row"]
            st.markdown("---")
            st.subheader("✏️ Sửa giao dịch")

            with st.form(f"edit_form_{edit_id}"):
                new_date = st.date_input("📅 Ngày", pd.to_datetime(row["date"]).date())
                new_note = st.text_input("🗒️ Ghi chú", row.get("note", ""))
                new_amount = st.number_input("💵 Số tiền", value=float(row["amount"]), min_value=0.0)
                new_category = st.text_input("📂 Danh mục", row.get("category_name", ""))
                save = st.form_submit_button("💾 Lưu thay đổi")

            if save:
                update_transaction(edit_id, row["type"], new_category, new_amount, new_note, new_date)
                st.session_state["edit_id"] = None
                st.rerun()

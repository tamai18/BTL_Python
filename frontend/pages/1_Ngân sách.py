import time
import streamlit as st
import pandas as pd
import datetime
import requests

API_URL = "http://127.0.0.1:8000"  # 🔧 URL backend của bạn

st.set_page_config(page_title="Quản lý ngân sách", page_icon="💰", layout="wide")
st.title("📊 Quản lý Ngân sách Chi tiêu")

# ====== KIỂM TRA ĐĂNG NHẬP ======
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.warning("🔒 Bạn cần đăng nhập để truy cập hệ thống.")
    st.page_link("pages/2_Login.py", label="➡️ Đăng nhập ngay", icon="🔑")
    st.stop()

user_id = st.session_state["user_id"]
st.sidebar.success(f"👋 Xin chào, {st.session_state['username']}!")
if st.sidebar.button("🚪 Đăng xuất"):
    st.session_state.clear()
    st.switch_page("pages/2_Login.py")

# ====== HÀM GỌI API ======
def get_budgets(user_id, month):
    r = requests.get(f"{API_URL}/budgets1/{user_id}/{month}")
    return r.json()

def add_budget(user_id, month, category, amount):
    data = {
        "category_id": category,
        "month": month,
        "amount": amount
    }
    r = requests.post(f"{API_URL}/budgets1/?user_id={user_id}", json=data)
    return r.json()

def update_budget(budget_id, month, category, amount):
    data = {
        "category_id": category,
        "month": month,
        "amount": amount
    }
    r = requests.put(f"{API_URL}/budgets1/{budget_id}/", json=data)
    return r.json()

def delete_budget(budget_id, category_id):
    r = requests.delete(f"{API_URL}/budgets1/{budget_id}?category_id={category_id}")
    return r.json()

# ====== GIAO DIỆN ======
st.sidebar.header("🔧 Chức năng")
menu = st.sidebar.radio("Chọn thao tác:", ["Thêm ngân sách", "Danh sách ngân sách"])

# ====== THÊM NGÂN SÁCH ======
if menu == "Thêm ngân sách":
    st.subheader("📝 Thêm ngân sách mới")

    with st.form("add_budget_form", clear_on_submit=True):
        today = datetime.date.today()
        years = list(range(2023, 2031))
        months = list(range(1, 13))

        c1, c2 = st.columns(2)
        with c1:
            selected_year = st.selectbox("📆 Năm", years, index=years.index(today.year))
            selected_month = st.selectbox("🗓️ Tháng", months, index=today.month - 1)
            month = f"{selected_year}-{selected_month:02d}"
        with c2:
            category_map = {
                "Ăn uống": 1,
                "Hóa đơn": 2,
                "Quần áo": 3,
                "Mỹ phẩm": 4,
                "Giải trí": 5,
                "Khác": 6
            }
            category_name = st.selectbox("📂 Danh mục", list(category_map.keys()))
            category_id = category_map[category_name]
            amount = st.number_input("💵 Ngân sách (VND)", min_value=0.0, step=100000.0)

        submitted = st.form_submit_button("💾 Lưu ngân sách")
        if submitted:
            res = add_budget(user_id, month, category_id, amount)
            st.success(res["message"])
            time.sleep(5)
            st.rerun()

# ====== DANH SÁCH NGÂN SÁCH ======
elif menu == "Danh sách ngân sách":
    st.header("📋 Danh sách ngân sách")

    today = datetime.date.today()
    current_month = f"{today.year}-{today.month:02d}"
    budgets_data = get_budgets(user_id, current_month)

    if not budgets_data["data"]:
        st.info("⚠️ Chưa có ngân sách nào cho tháng này.")
    else:
        budgets_df = pd.DataFrame(budgets_data["data"])
        for i, row in enumerate(budgets_df.itertuples(), start=1):
            cols = st.columns([2, 2, 2, 1, 1])
            cols[0].write(f"📅 **{row.month}**")
            cols[1].write(f"📂 **{row.category_name}**")
            cols[2].write(f"💰 {row.amount:,.0f} đ")

            # Dùng khóa unique thật sự (id + index)
            if cols[3].button("✏️ Sửa", key=f"edit_{row.budget_id}_{i}"):
                st.session_state["edit_budget"] = row._asdict()
                st.rerun()

            if cols[4].button("🗑️ Xóa", key=f"delete_{row.budget_id}_{i}"):
                st.session_state["delete_budget"] = row._asdict()
                st.rerun()

# ====== SỬA ======
if "edit_budget" in st.session_state:
    st.subheader("✏️ Sửa ngân sách")
    row = st.session_state["edit_budget"]

    with st.form("edit_budget_form"):
        years = list(range(2023, 2031))
        months = list(range(1, 13))
        current_year, current_month = map(int, row["month"].split("-"))

        c1, c2, c3 = st.columns(3)
        with c1:
            selected_year = st.selectbox("📆 Năm", years, index=years.index(current_year))
            selected_month = st.selectbox("🗓️ Tháng", months, index=current_month - 1)
            month = f"{selected_year}-{selected_month:02d}"
        with c2:
            category_id = row["category_id"]
        with c3:
            amount = st.number_input("💵 Ngân sách (VND)", value=float(row["amount"]), min_value=0.0, step=100000.0)

        save = st.form_submit_button("💾 Lưu thay đổi")
        if save:
            res = update_budget(row["budget_id"], month, category_id, amount)
            st.success(res["message"])
            del st.session_state["edit_budget"]
            st.rerun()

# ====== XÓA ======
if "delete_budget" in st.session_state:
    row = st.session_state["delete_budget"]
    st.warning(f"⚠️ Xóa ngân sách danh mục **{row['category_id']}** của tháng {row['month']}?")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("✅ Xác nhận xóa"):
            res = delete_budget(row["budget_id"], row["category_id"])
            st.success(res["message"])
            del st.session_state["delete_budget"]
            st.rerun()
    with c2:
        if st.button("❌ Hủy"):
            del st.session_state["delete_budget"]
            st.info("Đã hủy thao tác xóa.")
            st.rerun()

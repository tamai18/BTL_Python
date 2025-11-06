import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import requests
from streamlit_option_menu import option_menu
from frontend.style import load_custom_css

load_custom_css()
# Cấu hình
st.set_page_config(layout="wide")
# địa chỉ API backend
BACKEND_URL = "http://127.0.0.1:8000"

# --- KIỂM TRA ĐĂNG NHẬP ---
if 'access_token' not in st.session_state or not st.session_state['access_token']:
    st.error("Bạn phải đăng nhập để xem trang này.")
    st.warning("Vui lòng quay lại 'homepage' để đăng nhập.")
    st.stop()

# Lấy thông tin xác thực
TOKEN = st.session_state['access_token']
USER_ID = st.session_state['user_id']
AUTH_HEADERS = {'Authorization': f'Bearer {TOKEN}'}


# --- HÀM GỌI API ---
@st.cache_data(ttl=300)
def fetch_data(endpoint: str) -> pd.DataFrame:
    """Hàm chung để gọi API và trả về DataFrame."""
    full_url = f"{BACKEND_URL}{endpoint}"
    try:
        response = requests.get(full_url, headers=AUTH_HEADERS)
        if response.status_code == 200:
            data = response.json()
            return pd.DataFrame(data)
        elif response.status_code == 401:
            st.error("Xác thực thất bại. Vui lòng đăng nhập lại.")
            st.session_state['access_token'] = None
            st.rerun()
        elif response.status_code == 404:
            st.info(f"Không tìm thấy dữ liệu tại: {endpoint}")
        else:
            st.error(f"Lỗi {response.status_code} khi gọi API:{response.json().get('detail')}")
    except requests.exceptions.RequestException as e:
        st.error(f"Lỗi kết nối đến backend:{e}")
    return pd.DataFrame()


# --- Menu chính ---
selected = option_menu(
    menu_title=None,
    options=["Thu nhập", "Chi tiêu"],
    icons=["cash-coin", "currency-dollar", "graph-up-arrow"],  # Icons đẹp hơn
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {"padding": "5px", "background-color": "#D5E7F2", "border-radius": "10px"},
        "icon": {"color": "#007bff", "font-size": "20px"},
        "nav-link": {
            "font-size": "18px",
            "color": "#333",
            "text-align": "center",
            "margin": "5px",
            "--hover-color": "#d4eaf7",  # Nền khi hover
            "border-radius": "8px",
        },
        "nav-link-selected": {
            "background-color": "#007bff",  # Màu xanh dương
            "color": "white",
            "font-weight": "bold",
            "border-radius": "8px",
        },
    },
)

# Lấy dữ liệu thu nhập từ API
income_data_raw = fetch_data(f"/incomes/{USER_ID}")
if not income_data_raw.empty:
    income_data = income_data_raw.rename(columns={
        "date": "Ngày",
        "category_name": "Nguồn thu",
        "amount": "Thu nhập (VND)"
    })
    income_data["Ngày"] = pd.to_datetime(income_data["Ngày"])
else:
    income_data = pd.DataFrame({
        "Ngày": pd.Series(dtype='datetime64[ns]'),
        "Nguồn thu": pd.Series(dtype='object'),
        "Thu nhập (VND)": pd.Series(dtype='float')
    })
    st.info("Chưa có dữ liệu thu nhập.")

# Lấy dữ liệu chi tiêu từ API
expense_data_raw = fetch_data(f"/expense/{USER_ID}")
if not expense_data_raw.empty:
    expense_data = expense_data_raw.rename(columns={
        "date": "Ngày",
        "category_name": "Danh mục",
        "amount": "Chi tiêu (VND)"
    })
    expense_data["Ngày"] = pd.to_datetime(expense_data["Ngày"])
else:
    expense_data = pd.DataFrame({
        "Ngày": pd.Series(dtype='datetime64[ns]'),
        "Danh mục": pd.Series(dtype='object'),
        "Chi tiêu (VND)": pd.Series(dtype='float')
    })
    st.info("Chưa có dữ liệu chi tiêu.")


# --- Các hàm tính toán (Giữ nguyên) ---
def thu_nhap_theo_thang(df, nam):
    # Lọc các bản ghi rỗng (nếu có)
    df = df.dropna(subset=["Ngày"])
    df = df[df["Ngày"].dt.year == nam]
    if df.empty:
        return pd.DataFrame({"Tháng": [f"Tháng {i}" for i in range(1, 13)], "Thu nhập (VND)": [0] * 12})

    df["Tháng"] = df["Ngày"].dt.month
    monthly = df.groupby("Tháng")["Thu nhập (VND)"].sum().reset_index()

    # Tạo khung 12 tháng
    full_months = pd.DataFrame({"Tháng": range(1, 13)})
    monthly_full = full_months.merge(monthly, on="Tháng", how="left").fillna(0)
    monthly_full["Thu nhập (VND)"] = monthly_full["Thu nhập (VND)"].astype(int)
    monthly_full["Tháng"] = monthly_full["Tháng"].apply(lambda x: f"Tháng {x}")

    return monthly_full


def chi_tieu_theo_thang(df, nam):
    # Lọc các bản ghi rỗng (nếu có)
    df = df.dropna(subset=["Ngày"])
    df = df[df["Ngày"].dt.year == nam]
    if df.empty:
        return pd.DataFrame({"Tháng": [f"Tháng {i}" for i in range(1, 13)], "Chi tiêu (VND)": [0] * 12})

    df["Tháng"] = df["Ngày"].dt.month
    monthly = df.groupby("Tháng")["Chi tiêu (VND)"].sum().reset_index()

    # Tạo khung 12 tháng
    full_months = pd.DataFrame({"Tháng": range(1, 13)})
    monthly_full = full_months.merge(monthly, on="Tháng", how="left").fillna(0)
    monthly_full["Chi tiêu (VND)"] = monthly_full["Chi tiêu (VND)"].astype(int)
    monthly_full["Tháng"] = monthly_full["Tháng"].apply(lambda x: f"Tháng {x}")

    return monthly_full


# --- CHỌN NĂM ---
current_year = datetime.now().year
# Tạo danh sách các năm
year_list = list(range(current_year - 2, current_year + 3))

nam_chon = st.selectbox(
    "Chọn năm để xem báo cáo:",
    options=year_list,
    index=year_list.index(current_year)  # Mặc định chọn năm nay
)
st.divider()

# --- Logic vẽ biểu đồ ---
if selected == "Thu nhập":

    monthly_income = thu_nhap_theo_thang(income_data, nam_chon)
    max_value = monthly_income["Thu nhập (VND)"].max()

    fig = px.bar(
        monthly_income,
        x="Tháng",
        y="Thu nhập (VND)",
        title=f"Tổng thu nhập từng tháng trong năm {nam_chon}",
        text="Thu nhập (VND)"
    )
    fig.update_xaxes(type="category")
    fig.update_traces(texttemplate='%{text:,.0f}', textposition="outside")  # Sửa định dạng số
    fig.update_yaxes(range=[0, max_value * 1.15 if max_value > 0 else 100000])  # Tránh lỗi nếu max_value=0
    fig.update_layout(xaxis_title="Tháng", yaxis_title="Thu nhập (VND)", uniformtext_minsize=8, uniformtext_mode='hide')
    st.plotly_chart(fig, use_container_width=True)

elif selected == "Chi tiêu":
    monthly_expense = chi_tieu_theo_thang(expense_data, nam_chon)
    max_value = monthly_expense["Chi tiêu (VND)"].max()
    fig = px.bar(
        monthly_expense,
        x="Tháng",
        y="Chi tiêu (VND)",
        title=f"Tổng chi tiêu theo từng tháng trong năm {nam_chon}",
        text="Chi tiêu (VND)"
    )
    fig.update_xaxes(type="category")
    fig.update_traces(texttemplate='%{text:,.0f}', textposition="outside")  # Sửa định dạng số
    fig.update_yaxes(range=[0, max_value * 1.1 if max_value > 0 else 100000])  # Tránh lỗi nếu max_value=0
    fig.update_layout(xaxis_title="Tháng", yaxis_title="Chi tiêu (VND)", uniformtext_minsize=8, uniformtext_mode='hide')
    st.plotly_chart(fig, use_container_width=True)
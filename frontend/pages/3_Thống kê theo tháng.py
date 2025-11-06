import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import streamlit as st
from streamlit_option_menu import option_menu
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
import requests
from frontend.style import load_custom_css

load_custom_css()
# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(
    layout="wide",
    page_title="Tổng quan tháng",
    initial_sidebar_state="expanded"  # Sidebar luôn mở
)


# --- 3. KIỂM TRA ĐĂNG NHẬP VÀ API (Giữ nguyên) ---

# if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
#     st.warning("🔒 Bạn cần đăng nhập để truy cập hệ thống.")
#     st.page_link("pages/2_Đăng nhập.py", label="➡️ Đăng nhập ngay", icon="🔑")
#     st.stop()
#
# user_id = st.session_state["user_id"]
# st.sidebar.success(f"👋 Xin chào, {st.session_state['username']}!")
# if st.sidebar.button("🚪 Đăng xuất"):
#     st.session_state.clear()
#     st.switch_page("pages/2_Đăng nhập.py")

BACKEND_URL = "http://127.0.0.1:8000"

if 'access_token' not in st.session_state or not st.session_state['access_token']:
     st.error("Bạn phải đăng nhập để xem trang này.")
     st.warning("Vui lòng quay lại 'homepage' để đăng nhập.")
     st.stop()

TOKEN = st.session_state['access_token']
USER_ID = st.session_state['user_id']
AUTH_HEADERS = {'Authorization': f'Bearer {TOKEN}'}


@st.cache_data(ttl=300)
def fetch_data(endpoint: str) -> pd.DataFrame:
    full_url = f"{BACKEND_URL}{endpoint}"
    try:
        response = requests.get(full_url, headers=AUTH_HEADERS)
        if response.status_code == 200:
            return pd.DataFrame(response.json())
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


@st.cache_data(ttl=300)
def fetch_budget_data(endpoint: str) -> pd.DataFrame:
    full_url = f"{BACKEND_URL}{endpoint}"
    try:
        response = requests.get(full_url, headers=AUTH_HEADERS)
        if response.status_code == 200:
            return pd.DataFrame(response.json().get("data", []))
        elif response.status_code == 401:
            st.error("Xác thực thất bại. Vui lòng đăng nhập lại.")
            st.session_state['access_token'] = None
            st.rerun()
        elif response.status_code == 404:
            st.info(f"Không tìm thấy dữ liệu tại: {endpoint}")
        else:
            st.error(f"Lỗi {response.status_code} khi gọi API: {response.json().get('detail')}")
    except requests.exceptions.RequestException as e:
        st.error(f"Lỗi kết nối đến backend: {e}")
    return pd.DataFrame()


# --- 4. TẢI DỮ LIỆU (Giữ nguyên) ---
# ... (Giữ nguyên 4 khối code tải income_data_raw, expense_data_raw và xử lý ngày) ...
# du lieu thu nhap
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
# Phần này định nghĩa expense_data (đừng xóa)
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
# Ngày hiện tại
today = datetime.now().date()
current_year = today.year
current_month = today.month
this_week_start = today - timedelta(days=today.weekday())
this_month_start = today.replace(day=1)

# --- 5. MENU CHÍNH (SỬA STYLE) ---
selected = option_menu(
    menu_title=None,
    options=["Danh mục thu nhập", "Danh mục chi tiêu", "Phần trăm ngân sách"],
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

# --- 6. HIỂN THỊ CÁC TAB (SỬA LẠI HTML) ---
if selected == "Danh mục thu nhập":
    month_income = income_data[income_data["Ngày"].dt.date >= this_month_start]
    total_month = income_data.loc[income_data["Ngày"].dt.date >= this_month_start, "Thu nhập (VND)"].sum()

    # SỬA LẠI: Dùng class CSS mới 'metric-income'
    st.markdown(f"""
        <div class='metric-box metric-income' style='width:50%;margin:0 auto 30px auto;'>
            <h4>💰 Tổng thu nhập tháng {today.month}</h4>
            <h2>{total_month:,.0f} VND</h2>
        </div>
    """, unsafe_allow_html=True)

    fig = px.pie(
        month_income,
        names="Nguồn thu",
        values="Thu nhập (VND)",
        title="Tỷ trọng thu nhập theo nguồn",
        color_discrete_sequence=px.colors.qualitative.Set2,
        hole=0.4
    )
    fig.update_traces(textinfo="percent+label", textfont_size=16)
    st.plotly_chart(fig, use_container_width=True)

# --- SỬA LẠI TAB NÀY ---
elif selected == "Danh mục chi tiêu":
    total_today = expense_data.loc[expense_data["Ngày"].dt.date == today, "Chi tiêu (VND)"].sum()
    total_week = expense_data.loc[expense_data["Ngày"].dt.date >= this_week_start, "Chi tiêu (VND)"].sum()
    total_month = expense_data.loc[expense_data["Ngày"].dt.date >= this_month_start, "Chi tiêu (VND)"].sum()

    st.subheader("Tổng chi tiêu")
    col1, col2, col3 = st.columns(3)

    # SỬA LẠI: Dùng class CSS, bỏ style gõ tay
    col1.markdown(
        f"""
        <div class='metric-box metric-today'>
            <h4>Hôm nay</h4>
            <h2>{total_today:,.0f} VND</h2>
        </div>
        """,
        unsafe_allow_html=True
    )
    col2.markdown(
        f"""
        <div class='metric-box metric-week'>
            <h4>Tuần này</h4>
            <h2>{total_week:,.0f} VND</h2>
        </div>
        """,
        unsafe_allow_html=True
    )
    col3.markdown(
        f"""
        <div class='metric-box metric-month'>
            <h4>Tháng này</h4>
            <h2>{total_month:,.0f} VND</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Biểu đồ (giữ nguyên)
    month_expense = expense_data[expense_data["Ngày"].dt.date >= this_month_start]
    category_summary = month_expense.groupby("Danh mục")["Chi tiêu (VND)"].sum().reset_index()

    fig = px.pie(
        month_expense,
        names="Danh mục",
        values="Chi tiêu (VND)",
        title="Tỷ trọng chi tiêu theo danh mục",
        color_discrete_sequence=px.colors.qualitative.Pastel,
        hole=0.4
    )
    fig.update_traces(textinfo="percent+label", textfont_size=14)
    st.plotly_chart(fig, use_container_width=True)

# --- TAB NGÂN SÁCH (Giữ nguyên) ---
elif selected == "Phần trăm ngân sách":
    st.subheader("Chọn kỳ xem ngân sách")

    # 1. BỘ LỌC NĂM VÀ THÁNG
    default_year = datetime.now().year
    default_month = datetime.now().month

    col_filter_1, col_filter_2 = st.columns(2)
    with col_filter_1:
        year_list = list(range(default_year - 1, default_year + 2))
        selected_year = st.selectbox(
            "Chọn năm",
            options=year_list,
            index=year_list.index(default_year)
        )
    with col_filter_2:
        month_list = list(range(1, 13))
        selected_month = st.selectbox(
            "Chọn tháng",
            options=month_list,
            index=default_month - 1
        )

    month_str_api = f"{selected_year}-{selected_month:02d}"
    st.info(f"Đang tải tóm tắt ngân sách cho tháng: {month_str_api}...")

    # 2. TẢI DỮ LIỆU TÓM TẮT
    summary_df = fetch_budget_data(f"/budgets/{USER_ID}/{month_str_api}")
    if summary_df.empty:
        st.warning(f"Chưa có ngân sách nào được đặt cho tháng {month_str_api}.")
        st.stop()

    # 3. BỘ LỌC DANH MỤC
    st.subheader("Chọn danh mục để xem chi tiết")
    if 'category_name' not in summary_df.columns:
        st.error("Lỗi: API trả về không có cột 'category_name'.")
        st.stop()

    category_list = summary_df['category_name'].unique().tolist()
    options_list = ["Tất cả danh mục"] + category_list
    selected_category = st.selectbox(
        "Lọc theo danh mục",
        options=options_list
    )
    st.divider()

    # 4. LOGIC HIỂN THỊ
    # TRƯỜNG HỢP 1: NẾU CHỌN "TẤT CẢ DANH MỤC"
    if selected_category == "Tất cả danh mục":
        display_df = summary_df

        # A. Hiển thị TỔNG QUAN
        st.subheader(f"Tổng quan Ngân sách tháng {month_str_api}")
        if 'budget' not in display_df.columns or 'expense' not in display_df.columns:
            st.error("Lỗi: Dữ liệu API trả về không chứa cột 'budget' hoặc 'expense'.")
            st.stop()

        total_budget_all = display_df["budget"].sum()
        total_expense_all = display_df["expense"].sum()
        total_remaining_all = total_budget_all - total_expense_all

        c1, c2, c3 = st.columns(3)
        c1.metric("Tổng ngân sách", f"{total_budget_all:,.0f} VND")
        c2.metric("Tổng đã chi", f"{total_expense_all:,.0f} VND")
        if total_remaining_all >= 0:
            c3.metric("Tổng còn lại", f"{total_remaining_all:,.0f} VND")
        else:
            c3.metric("Tổng bội chi", f"{total_remaining_all:,.0f} VND", delta_color="inverse")
        st.divider()

        # B. Hiển thị CHI TIẾT
        st.subheader("Chi tiết theo Danh mục")
        if display_df.empty:
            st.info("Không có dữ liệu chi tiết cho lựa chọn này.")
        else:
            display_df['percent_used'] = (display_df['expense'] / display_df['budget'].replace(0, 1e-9)) * 100
            display_df = display_df.sort_values(by="percent_used", ascending=False)

            for index, row in display_df.iterrows():
                st.markdown(f"#### {row['category_name']}")
                budget_amount = row['budget']
                expense_amount = row['expense']
                status_message = row.get('trang_thai', f"{row['percent_used']:.1f}% đã dùng")
                percent_used = row['percent_used']
                percent_for_bar = min(percent_used / 100.0, 1.0)
                st.progress(percent_for_bar, text=status_message)

                col1, col2, col3 = st.columns(3)
                col1.metric("Ngân sách", f"{budget_amount:,.0f} VND")
                col2.metric("Đã chi", f"{expense_amount:,.0f} VND")
                remaining = budget_amount - expense_amount
                if remaining < 0:
                    col3.metric("Bội chi", f"{remaining:,.0f} VND", delta_color="inverse")
                else:
                    col3.metric("Còn lại", f"{remaining:,.0f} VND")
                st.divider()

    # TRƯỜNG HỢP 2: NẾU CHỌN MỘT DANH MỤC CỤ THỂ
    else:
        display_df = summary_df[summary_df['category_name'] == selected_category]

        if display_df.empty:
            st.error("Lỗi: Không tìm thấy dữ liệu cho danh mục đã chọn.")
            st.stop()

        row = display_df.iloc[0]
        st.subheader(f"Ngân sách {row['category_name']} tháng {month_str_api}")

        budget_amount = row['budget']
        expense_amount = row['expense']
        percent_used = (expense_amount / budget_amount) * 100 if budget_amount > 0 else 0
        status_message = row.get('trang_thai', f"{percent_used:.1f}% đã dùng")
        percent_for_bar = min(percent_used / 100.0, 1.0)

        st.progress(percent_for_bar, text=status_message)
        col1, col2, col3 = st.columns(3)
        col1.metric("Ngân sách", f"{budget_amount:,.0f} VND")
        col2.metric("Đã chi", f"{expense_amount:,.0f} VND")
        remaining = budget_amount - expense_amount
        if remaining < 0:
            col3.metric("Bội chi", f"{remaining:,.0f} VND", delta_color="inverse")
        else:
            col3.metric("Còn lại", f"{remaining:,.0f} VND")
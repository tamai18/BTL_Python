# Tên file: style.py
import streamlit as st


def load_custom_css():
    """
    Hàm này chứa tất cả CSS tùy chỉnh và chèn vào trang.
    """
    css = """
    <style>
    /* Nền chung của trang */
    body {
        background-color: #f0f2f5; 
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #b5ead7; /* <-- MÀU NỀN XANH DƯƠNG */
        border-right: 1px solid #ddd;
        box-shadow: 2px 0px 5px rgba(0,0,0,0.05); /* Thêm bóng đổ nhẹ */
    }
    /* Target tên các trang (link) trong sidebar */
    [data-testid="stSidebar"] ul a {
        color: #ffffff !important; /* <-- MÀU CHỮ TRẮNG */
        padding: 10px 16px;
        border-radius: 8px;
        margin-bottom: 5px;
        transition: background-color 0.3s ease, color 0.3s ease;
    }

    /* Khi hover (di chuột) qua link */
    [data-testid="stSidebar"] ul a:hover {
        background-color: #5dade2 !important; /* <-- Màu nền xanh nhạt hơn khi hover */
        color: #ffffff !important;
    }

    /* Nền khối nội dung chính */
    .main .block-container {
        background-color: #ffffff;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }

    /* Tiêu đề */
    h1, h2, h3, h4 {
        color: #333;
        font-weight: 600;
    }

    /* .metric-box, .metric-income, ... */
    .metric-box {
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        text-align: center;
        margin-bottom: 15px;
        transition: transform 0.2s ease;
    }
    .metric-box:hover {
        transform: translateY(-5px); 
    }
    .metric-box h4 { margin-bottom: 5px; color: #555; font-size: 1.1rem; }
    .metric-box h2 { font-size: 2.1em; font-weight: 700; margin-top: 0; }

    .metric-income { background-color: #fff0f1; } 
    .metric-income h2 { color: #e63946; } 
    .metric-today { background-color: #e0f7fa; } 
    .metric-today h2 { color: #007bb6; } 
    .metric-week { background-color: #e8f5e9; }
    .metric-week h2 { color: #2e7d32; } 
    .metric-month { background-color: #fff3e0; }
    .metric-month h2 { color: #f57c00; } 
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
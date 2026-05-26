import streamlit as st
from mock_data import (
    customers, brokers, stocks,
    activities, KPI_TARGETS, DEMO_DATE
)

# Xóa page_icon, để mặc định
st.set_page_config(
    page_title="SSI BrokerHub",
    page_icon="assets/logo.png",
    layout="wide"
)

# Khởi tạo session_state
if "initialized" not in st.session_state:
    st.session_state.customers          = [c.copy() for c in customers]
    st.session_state.brokers            = [b.copy() for b in brokers]
    st.session_state.stocks             = [s.copy() for s in stocks]
    st.session_state.activities         = [a.copy() for a in activities]
    st.session_state.kpi_targets        = KPI_TARGETS
    st.session_state.demo_date          = DEMO_DATE
    st.session_state.current_broker_id  = 1  
    st.session_state.initialized        = True

# Layout trang chủ tối giản
col1, col2 = st.columns([1, 15]) 

with col1:
    st.image("assets/logo.png", width=70) 

with col2:
    st.markdown("<h1 style='margin-bottom: 0px; padding-bottom: 0px;'>Hệ thống Quản lý Môi giới</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #6B7280; font-size: 1.1rem;'>Nền tảng quản trị chỉ tiêu và đánh giá hiệu suất nội bộ — SSI BrokerHub</p>", unsafe_allow_html=True)

st.divider()
st.markdown("Vui lòng lựa chọn các phân hệ nghiệp vụ tại thanh điều hướng bên trái.")
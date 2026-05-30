import streamlit as st
from data.mock_data import (
    customers, brokers, stocks,
    activities, KPI_TARGETS, DEMO_DATE, FEE_RATES
)

st.set_page_config(
    page_title="SSI BrokerHub",
    page_icon="assets/logo.png",
    layout="wide"
)

# Khởi tạo session_state & Hàm dùng chung
if "initialized" not in st.session_state:
    st.session_state.customers          = [c.copy() for c in customers]
    st.session_state.brokers            = [b.copy() for b in brokers]
    st.session_state.stocks             = [s.copy() for s in stocks]
    st.session_state.activities         = [a.copy() for a in activities]
    st.session_state.kpi_targets        = KPI_TARGETS
    st.session_state.demo_date          = DEMO_DATE
    st.session_state.fee_rates          = FEE_RATES
    st.session_state.logged_in          = False
    st.session_state.current_broker_id  = None  
    st.session_state.initialized        = True

def render_badge(profit_margin):
    if profit_margin > 5.0:
        return '<span style="background-color: #10B98120; color: #10B981; padding: 4px 8px; border-radius: 4px; font-size: 0.85rem; font-weight: 600; border: 1px solid #10B98150;">Lãi tốt (>5%)</span>'
    elif profit_margin >= 0.0:
        return '<span style="background-color: #F59E0B20; color: #F59E0B; padding: 4px 8px; border-radius: 4px; font-size: 0.85rem; font-weight: 600; border: 1px solid #F59E0B50;">Hòa vốn / Lãi nhẹ</span>'
    else:
        return '<span style="background-color: #ED1C2420; color: #ED1C24; padding: 4px 8px; border-radius: 4px; font-size: 0.85rem; font-weight: 600; border: 1px solid #ED1C2450;">Gồng lỗ</span>'

if "render_badge" not in st.session_state:
    st.session_state.render_badge = render_badge

# ==========================================
# MODULE 0: MÀN HÌNH CHỌN BROKER (LOG IN)
# ==========================================
if not st.session_state.logged_in:
    col_space1, col_login, col_space3 = st.columns([1, 1.5, 1])
    
    with col_login:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        with st.container(border=True):
            st.image("assets/logo.png", width=80)
            st.markdown("<h2 style='color: #ED1C24; margin-bottom: 0px;'>Đăng nhập Hệ thống</h2>", unsafe_allow_html=True)
            st.caption("Xác thực danh tính môi giới qua SSI Smart OTP")
            
            broker_dict = {b["id"]: b["name"] for b in st.session_state.brokers}
            selected_id = st.selectbox("Chọn nhân sự:", options=list(broker_dict.keys()), format_func=lambda x: broker_dict[x])
            
            # Thêm trường giả lập Smart OTP
            otp_code = st.text_input("Mã xác thực Smart OTP (6 số):", type="password", max_chars=6, placeholder="Nhập mã OTP từ thiết bị...")
            
            if st.button("Đăng nhập", type="primary", use_container_width=True):
                # Kiểm tra phải nhập đúng 6 số thì mới cho qua
                if len(otp_code) == 6 and otp_code.isdigit():
                    st.session_state.current_broker_id = selected_id
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("Lỗi xác thực: Vui lòng nhập đúng định dạng 6 chữ số Smart OTP.")
                
    st.stop()

# ==========================================
# GIAO DIỆN CHÍNH
# ==========================================
col1, col2 = st.columns([1, 15]) 

with col1:
    st.image("assets/logo.png", width=70) 

with col2:
    st.markdown("<h1 style='margin-bottom: 0px; padding-bottom: 0px;'>Hệ thống Quản lý Môi giới</h1>", unsafe_allow_html=True)
    current_broker_name = next(b["name"] for b in st.session_state.brokers if b["id"] == st.session_state.current_broker_id)
    st.markdown(f"<p style='color: #6B7280; font-size: 1.1rem;'>Xin chào, <b>{current_broker_name}</b>! Nền tảng quản trị chỉ tiêu nội bộ — SSI BrokerHub</p>", unsafe_allow_html=True)

st.divider()
st.markdown("Vui lòng lựa chọn các phân hệ nghiệp vụ tại thanh điều hướng bên trái.")

with st.sidebar:
    st.markdown("---")
    if st.button("Đăng xuất", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()
import streamlit as st
import base64
from data.mock_data import (
    customers, brokers, stocks,
    activities, KPI_TARGETS, DEMO_DATE, FEE_RATES
)

st.set_page_config(
    page_title="Cổng An Ninh | SSI BrokerHub",
    page_icon="assets/logo.png",
    layout="wide"
)

# Ẩn nút Deploy và thanh toolbar
st.markdown("""
    <style>
        .stDeployButton {display: none !important;}
        [data-testid="stToolbar"] {display: none !important;}
        [data-testid="stHeader"] {background: transparent !important;}
        [data-testid="collapsedControl"] {display: none;}
        [data-testid="stSidebar"] {display: none;}
    </style>
""", unsafe_allow_html=True)

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

# ==========================================
# MODULE 0: CỔNG XÁC THỰC (AUTHENTICATION GATEWAY)
# ==========================================
if not st.session_state.logged_in:
    def get_base64_of_bin_file(bin_file):
        try:
            with open(bin_file, 'rb') as f:
                data = f.read()
            return base64.b64encode(data).decode()
        except Exception:
            return None

    img_base64 = get_base64_of_bin_file("assets/hoiso_ssi.jpg")
    
    if img_base64:
        bg_css = f"""
        <style>
        .stApp {{
            background-image: linear-gradient(to bottom right, rgba(17, 24, 39, 0.85), rgba(237, 28, 36, 0.4)), url("data:image/jpeg;base64,{img_base64}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        </style>
        """
    else:
        bg_css = "<style>.stApp { background: #111827; }</style>"
    st.markdown(bg_css, unsafe_allow_html=True)
    
    st.markdown("""
        <style>
        label {color: #FFFFFF !important; font-weight: 500;}
        [data-testid="stForm"] {
            background: rgba(0, 0, 0, 0.6) !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5);
        }
        h1, h3, p { color: #FFFFFF !important; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    col_left, col_space, col_right = st.columns([1.2, 0.2, 1])
    
    with col_left:
        st.markdown("<div style='padding-left: 10%; padding-top: 20px;'>", unsafe_allow_html=True)
        st.image("assets/logo.png", width=140)
        st.markdown("<h1 style='font-family: sans-serif; font-weight: 900; font-size: 3.5rem; line-height: 1.2; text-shadow: 2px 2px 8px rgba(0,0,0,0.9); margin-top: 20px;'>CỔNG THÔNG TIN NỘI BỘ SSI</h1>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 1.3rem; font-weight: 400; text-shadow: 1px 1px 4px rgba(0,0,0,0.9);'>Hệ thống Không gian Điều hành & Công cụ Môi giới</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col_right:
        st.markdown("<h3 style='margin-bottom: 15px; font-weight: bold; text-shadow: 1px 1px 4px rgba(0,0,0,0.5);'>ĐĂNG NHẬP HỆ THỐNG</h3>", unsafe_allow_html=True)
        with st.form("login_form", clear_on_submit=False):
            broker_dict = {b["id"]: b["name"] for b in st.session_state.brokers}
            selected_id = st.selectbox("Định danh Cán bộ (Broker):", options=list(broker_dict.keys()), format_func=lambda x: broker_dict[x])
            st.markdown("<br>", unsafe_allow_html=True) 
            otp_code = st.text_input("Mã xác thực Smart OTP (6 số):", type="password", max_chars=6, placeholder="Nhập mã OTP từ thiết bị...")
            st.markdown("<br>", unsafe_allow_html=True)
            submit_login = st.form_submit_button("XÁC THỰC VÀ TRUY CẬP", type="primary", use_container_width=True)
            
            if submit_login:
                if len(otp_code) == 6 and otp_code.isdigit():
                    st.session_state.current_broker_id = selected_id
                    st.session_state.logged_in = True
                    
                    # Lệnh thần thánh: Chuyển hướng thẳng vào trang Điều Hành
                    st.switch_page("pages/1_Tong_Quan.py")
                else:
                    st.error("Lỗi: Mã Smart OTP không hợp lệ. Vui lòng nhập 6 chữ số.")
    st.stop()
else:
    # Nếu đã đăng nhập mà lỡ F5 trang web thì tự động nhảy thẳng vào trang 1
    st.switch_page("pages/1_Tong_Quan.py")

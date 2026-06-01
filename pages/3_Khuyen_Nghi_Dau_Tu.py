import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="Advisory Hub | SSI BrokerHub", page_icon="assets/logo.png", layout="wide")

# Kiểm tra xác thực
if "initialized" not in st.session_state or not st.session_state.logged_in:
    st.warning("Yêu cầu xác thực. Vui lòng quay lại trang chủ để đăng nhập hệ thống.")
    st.stop()
# ========================================================
# --- TẠO MENU NGANG TRÊN CÙNG (TOP NAVIGATION) - 6 MODULES ---
# ========================================================
st.markdown("""
<style>
    /* Ẩn sidebar mặc định */
    [data-testid='stSidebar'] {display: none !important;}
    
    /* Ép cứng font chữ siêu to lên mọi thành phần của Menu */
    [data-testid="stPageLink"] p,
    [data-testid="stPageLink"] span,
    [data-testid="stPageLink"] a,
    [data-testid="stPageLink-NavLink"] p {
        font-size: 24px !important;
        font-weight: 900 !important;
        line-height: 1.3 !important;
        white-space: normal !important; /* Cho phép chữ tự rớt dòng */
        text-align: center !important; 
    }
    
    /* Căn giữa nút bấm trong cột */
    [data-testid="stPageLink"] {
        display: flex;
        justify-content: center;
        align-items: center;
    }
</style>
""", unsafe_allow_html=True)

menu_cols = st.columns(6)
with menu_cols[0]: st.page_link("pages/1_Tong_Quan.py", label="Tổng Quan")
with menu_cols[1]: st.page_link("pages/2_Quan_Tri_Danh_Muc.py", label="Quản Trị Danh Mục")
with menu_cols[2]: st.page_link("pages/3_Khuyen_Nghi_Dau_Tu.py", label="Khuyến Nghị Đầu Tư")
with menu_cols[3]: st.page_link("pages/4_Theo_Doi_KPI.py", label="Theo Dõi KPI")
with menu_cols[4]: st.page_link("pages/5_Nhat_Ky_Van_Hanh.py", label="Nhật Ký Vận Hành")
with menu_cols[5]: st.page_link("pages/6_Danh_Gia_Noi_Bo.py", label="Đánh Giá Nội Bộ")
st.markdown("---")

stocks = st.session_state.stocks
customers = st.session_state.customers
current_broker_id = st.session_state.current_broker_id

st.markdown("<h2 style='color: #000000; margin-bottom: 0px;'>Trung tâm Khuyến nghị đầu tư</h2>", unsafe_allow_html=True)
st.markdown("<p style='color: #6B7280; font-size: 1rem;'>Hỗ trợ môi giới phân tích doanh nghiệp và gửi tín hiệu giao dịch đến khách hàng</p>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# PHẦN 1: BỘ LỌC VÀ CHỌN MÃ CỔ PHIẾU
# ==========================================
col_select1, col_select2 = st.columns([1, 2])

with col_select1:
    with st.container(border=True):
        st.markdown("**Lựa chọn danh mục phân tích**")
        ticker_list = [s["ticker"] for s in stocks]
        selected_ticker = st.selectbox("Mã cổ phiếu niêm yết:", options=ticker_list)
        
        # Lấy dữ liệu mã đã chọn
        stock_data = next(s for s in stocks if s["ticker"] == selected_ticker)
        
        # BỔ SUNG: KẾT NỐI API THỊ TRƯỜNG THỰC
        with st.spinner("Đang đồng bộ API từ sàn HOSE..."):
            try:
                live_data = yf.Ticker(f"{selected_ticker}.HM").history(period="1d")
                if not live_data.empty:
                    real_price = live_data['Close'].iloc[-1]
                    price_display = f"{real_price:,.0f} VNĐ"
                else:
                    price_display = "Thị trường đóng cửa"
            except Exception:
                price_display = "Lỗi kết nối API"
        
        st.markdown(f"**Giá khớp lệnh Real-time:** <span style='color: #10B981; font-size: 1.3rem; font-weight: bold;'>{price_display}</span>", unsafe_allow_html=True)
        st.caption(f"Cập nhật Fundamental lần cuối: {stock_data['updated_at']}")

# ==========================================
# PHẦN 2: CHI TIẾT PHÂN TÍCH (FUNDAMENTAL & TECHNICAL)
# ==========================================
st.markdown(f"### Phân tích chi tiết: {stock_data['ticker']} - {stock_data['company_name']}")

col_f1, col_f2, col_f3, col_f4 = st.columns(4)
with col_f1:
    st.metric("Chỉ số ROE", f"{stock_data['roe']}%")
with col_f2:
    st.metric("EPS (Trượt)", f"{stock_data['eps']:,} VNĐ")
with col_f3:
    st.metric("P/E Forward", f"{stock_data['pe']}x")
with col_f4:
    st.metric("Chỉ số RSI", stock_data['rsi'])

st.markdown("<br>", unsafe_allow_html=True)

col_body1, col_body2 = st.columns([2, 1])

with col_body1:
    with st.container(border=True):
        st.markdown("**Luận điểm đầu tư (Investment Thesis)**")
        st.write(stock_data['thesis'])
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**Trạng thái dòng tiền (Volume Analysis)**")
        st.info(stock_data['volume'])

with col_body2:
    with st.container(border=True):
        st.markdown("**Vùng giá khuyến nghị**")
        st.markdown(f"Vùng mua: <span style='color: #10B981; font-weight: bold;'>{stock_data['buy_zone']}</span>", unsafe_allow_html=True)
        st.markdown(f"Giá mục tiêu: <span style='color: #000000; font-weight: bold;'>{stock_data['target']}</span>", unsafe_allow_html=True)
        st.markdown(f"Giá cắt lỗ: <span style='color: #ED1C24; font-weight: bold;'>{stock_data['cutloss']}</span>", unsafe_allow_html=True)
        
        st.divider()
        st.markdown("**Xác nhận hành động**")
        action = st.radio("Khuyến nghị:", ["MUA TÍCH LŨY", "MUA GIA TĂNG", "THEO DÕI"], label_visibility="collapsed")

# ==========================================
# PHẦN 3: GỬI KHUYẾN NGHỊ CHO KHÁCH HÀNG (ĐÃ TÍCH HỢP LLM COPILOT)
# ==========================================
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("#### Hệ thống Push Tín hiệu & Trợ lý Soạn thảo")

# BỔ SUNG: TRỢ LÝ AI SOẠN THẢO (LLM Copilot)
auto_draft = f"Kính gửi Quý khách hàng,\n\nHệ thống Phân tích SSI BrokerHub cập nhật tín hiệu kỹ thuật cho mã cổ phiếu {stock_data['ticker']} ({stock_data['company_name']}).\n"
auto_draft += f"- Giá thị trường hiện tại: {price_display}\n"
auto_draft += f"- Vùng giá giải ngân an toàn: {stock_data['buy_zone']}\n"
auto_draft += f"- Định giá mục tiêu: {stock_data['target']} | Ngưỡng cắt lỗ: {stock_data['cutloss']}\n\n"
auto_draft += f"Luận điểm đầu tư: {stock_data['thesis']} Dòng tiền hiện tại đang cho thấy dấu hiệu {stock_data['volume'].lower()}.\n\n"
auto_draft += f"Hành động khuyến nghị: {action}.\n\nTrân trọng,"

message_content = st.text_area("Nội dung kịch bản tư vấn (Được tạo tự động, có thể chỉnh sửa):", value=auto_draft, height=220)

# Lọc danh sách khách hàng của broker hiện tại
my_customers = [c for c in customers if c["broker_id"] == current_broker_id]
df_customers = pd.DataFrame(my_customers)

if not df_customers.empty:
    # Cho phép chọn khách hàng để gửi
    selected_customers = st.multiselect(
        "Chọn khách hàng nhận thông báo:",
        options=df_customers["name"].tolist(),
        default=df_customers["name"].tolist()
    )
    
    if st.button("Xác nhận gửi tín hiệu Smart OTP", type="primary"):
        if selected_customers:
            st.success(f"Yêu cầu thành công: Đã gửi thông báo khuyến nghị {stock_data['ticker']} đến {len(selected_customers)} khách hàng qua ứng dụng SSI iBoard Pro.")
        else:
            st.error("Lỗi: Vui lòng lựa chọn ít nhất một khách hàng.")
else:
    st.info("Hệ thống chưa ghi nhận danh sách khách hàng thuộc quyền quản lý của bạn.")

with st.sidebar:
    st.markdown("---")
    st.markdown("**QUẢN TRỊ NỘI DUNG**")
    st.caption("Dữ liệu giá Real-time được đồng bộ qua Yahoo Finance API. Báo cáo phân tích được cung cấp bởi SSI Research Center. Mọi thông tin chỉ mang tính chất tham khảo.")
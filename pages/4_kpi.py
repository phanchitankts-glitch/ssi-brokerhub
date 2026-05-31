import streamlit as st
import pandas as pd

st.set_page_config(page_title="KPI Cá Nhân | SSI BrokerHub", page_icon="assets/logo.png", layout="wide")

# Kiểm tra xác thực hệ thống
if "initialized" not in st.session_state or not st.session_state.logged_in:
    st.warning("Yêu cầu xác thực. Vui lòng quay lại trang chủ để đăng nhập hệ thống.")
    st.stop()

# Đọc dữ liệu dùng chung từ AppContext
current_broker_id = st.session_state.current_broker_id
brokers = st.session_state.brokers
customers = st.session_state.customers

# Lấy thông tin chi tiết của môi giới hiện tại
current_broker = next(b for b in brokers if b["id"] == current_broker_id)
my_customers = [c for c in customers if c["broker_id"] == current_broker_id]

# ==========================================================
# HEADER ĐỒNG BỘ HOÀN TOÀN THEO PHONG CÁCH CỦA TẤN
# ==========================================================
st.markdown("<h2 style='color: #000000; margin-bottom: 0px;'>KPI Scorecard cá nhân</h2>", unsafe_allow_html=True)
st.markdown("<p style='color: #6B7280; font-size: 1rem;'>Theo dõi tiến độ chỉ tiêu thử việc và xếp hạng thi đua nội bộ phòng</p>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# CHỈ TIÊU BẮT BUỘC THEO ĐỀ BÀI THỬ VIỆC TẠI SSI
t_cust = 20          # 20 khách hàng
t_active = 10        # 10 tài khoản active
t_fee = 6000000      # 6,000,000 VNĐ phí môi giới/tháng

# Tính toán số liệu thực tế dựa trên liên kết dữ liệu chung
my_total_cust = len(my_customers)
my_active_cust = len([c for c in my_customers if c["status"] == "active"])
my_fee_m1 = current_broker["fee"]["month1"]
my_fee_m2 = current_broker["fee"]["month2"]
my_fee_m3 = current_broker["fee"]["month3"]

# Tính tỷ lệ phần trăm hoàn thành chỉ tiêu
pct_cust = (my_total_cust / t_cust) * 100
pct_active = (my_active_cust / t_active) * 100
pct_fee = (my_fee_m3 / t_fee) * 100

# ==========================================================
# PHẦN 1: BẢNG CHỈ SỐ HIỆU SUẤT CHI TIẾT (KPI SCORECARD)
# ==========================================================
st.markdown("### I. Bảng chỉ số hiệu suất chi tiết")

col_body1, col_body2 = st.columns([2, 1])

with col_body1:
    with st.container(border=True):
        st.markdown("**Tiến độ & Tỷ lệ hoàn thành mục tiêu thử việc**")
        
        kpi_data = {
            "Chỉ tiêu quản lý": ["Tổng số khách hàng thu hút", "Tài khoản duy trì giao dịch (Active)", "Doanh số phí (Tháng hiện tại)"],
            "Mục tiêu yêu cầu": [f"{t_cust} KH", f"{t_active} TK", f"{t_fee:,.0f} VNĐ"],
            "Thực tế hiện có": [f"{my_total_cust} KH", f"{my_active_cust} TK", f"{my_fee_m3:,.0f} VNĐ"],
            "Còn thiếu": [f"{max(0, t_cust - my_total_cust)} KH", f"{max(0, t_active - my_active_cust)} TK", f"{max(0, t_fee - my_fee_m3):,.0f} VNĐ"],
            "Tỷ lệ hoàn thành": [f"{pct_cust:.1f}%", f"{pct_active:.1f}%", f"{pct_fee:.1f}%"]
        }
        st.dataframe(pd.DataFrame(kpi_data), use_container_width=True, hide_index=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**Lịch sử doanh số phí môi giới qua 3 tháng thử việc**")
        
        fee_history = {
            "Kỳ đánh giá": ["Tháng thử việc 1", "Tháng thử việc 2", "Tháng thử việc 3 (Hiện tại)"],
            "Doanh số phí thu về (VNĐ)": [f"{my_fee_m1:,.0f}", f"{my_fee_m2:,.0f}", f"{my_fee_m3:,.0f}"],
            "Chuẩn yêu cầu": [f"{t_fee:,.0f}", f"{t_fee:,.0f}", f"{t_fee:,.0f}"],
            "Kết quả đánh giá": ["Đạt tiêu chuẩn", "Đạt tiêu chuẩn", "Đang thẩm định"]
        }
        st.dataframe(pd.DataFrame(fee_history), use_container_width=True, hide_index=True)

with col_body2:
    with st.container(border=True):
        st.markdown("**Tổng điểm hiệu suất tổng hợp**")
        st.caption("Hệ thống tự động tính toán dựa trên trọng số chuẩn của SSI.")
        
        score_cust = min(pct_cust, 100.0)
        score_active = min(pct_active, 100.0)
        score_fee = min(pct_fee, 100.0)
        
        # Trọng số đánh giá năng lực: 30% Khách hàng, 30% Active, 40% Doanh số phí
        total_performance_score = (score_cust * 0.3) + (score_active * 0.3) + (score_fee * 0.4)
        
        if total_performance_score >= 100.0:
            score_color = "#10B981"  # Xanh lá
            status_text = "ĐỦ ĐIỀU KIỆN CHÍNH THỨC"
        elif total_performance_score >= 70.0:
            score_color = "#F59E0B"  # Vàng
            status_text = "ĐẠT CHUẨN THỬ VIỆC"
        else:
            score_color = "#ED1C24"  # Đỏ
            status_text = "CẦN CẢI THIỆN HIỆU SUẤT"
            
        st.markdown(f"<div style='text-align: center; padding: 25px 0px;'>"
                    f"<p style='font-size: 1.1rem; margin-bottom: 5px; color:#6B7280;'>Tỷ lệ hoàn thành tổng hợp</p>"
                    f"<h1 style='color: {score_color}; font-size: 3.5rem; margin: 0;'>{total_performance_score:.1f}%</h1>"
                    f"<p style='color: {score_color}; font-weight: bold; margin-top: 5px;'>{status_text}</p>"
                    f"</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================================
# PHẦN 2: PHÂN TÍCH KHOẢNG CÁCH CHỈ TIÊU (GAP ANALYSIS CHI TIẾT)
# ==========================================================
st.markdown("### II. Phân tích khoảng cách mục tiêu")

my_inactives = [c for c in my_customers if c.get("status") == "inactive"]
my_losses = [c for c in my_customers if float(c.get("profit_margin") or 0.0) < -5.0]

col_gap1, col_gap2 = st.columns([2, 1])

with col_gap1:
    with st.container(border=True):
        st.markdown("**Đánh giá định lượng từ Trợ lý Giám sát**")
        st.markdown(f"**Lỗ hổng danh mục khách hàng:** Bạn đang có <span style='color:#ED1C24; font-weight:bold;'>{len(my_inactives)}</span> tài khoản ngưng giao dịch quá hạn.", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**Đánh giá mục tiêu doanh số phí**")
        if my_fee_m3 < t_fee:
            gap_fee = t_fee - my_fee_m3
            st.info(f"Bạn cần khai thác thêm {gap_fee:,.0f} VNĐ phí môi giới để đạt chỉ tiêu 6 triệu đồng phụ trách.")
        else:
            st.success("Chúc mừng! Bạn đã xuất sắc cán mốc doanh số phí 6,000,000 VNĐ yêu cầu thử việc.")

with col_gap2:
    with st.container(border=True):
        st.markdown("**Kịch bản hành động tối ưu**")
        if my_total_cust < t_cust:
            st.markdown(f"<span style='color: #ED1C24; font-weight: bold;'>Hành động:</span> Tăng cường tìm kiếm và phát triển mạng lưới để bổ sung thêm {t_cust - my_total_cust} khách hàng còn thiếu.", unsafe_allow_html=True)
        elif len(my_inactives) > 0:
            st.markdown(f"<span style='color: #F59E0B; font-weight: bold;'>Hành động:</span> Vào phân hệ 'Advisory Hub' chọn mã tiềm năng để gửi khuyến nghị giao dịch trực tiếp cho nhóm tài khoản Inactive.", unsafe_allow_html=True)
        else:
            st.markdown(f"<span style='color: #10B981; font-weight: bold;'>Hành động:</span> Duy trì chất lượng tư vấn, đẩy mạnh phân phối chéo chứng chỉ quỹ S-FUND.", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================================
# PHẦN 3: BẢNG XẾP HẠNG THI ĐUA NỘI BỘ THEO TIÊU CHÍ
# ==========================================================
st.markdown("### III. Bảng xếp hạng thi đua nội bộ phòng")

with st.container(border=True):
    st.markdown("**Bộ lọc tiêu chí xếp hạng**")
    rank_metric = st.selectbox(
        "Lựa chọn chỉ tiêu để xem thứ hạng thi đua chéo:",
        options=["Doanh số phí giao dịch", "Số lượng khách hàng sở hữu", "Tài khoản hoạt động (Active)"]
    )
    
    st.markdown(f"**Bảng xếp hạng thi đua theo: {rank_metric}**")
    
    if rank_metric == "Doanh số phí giao dịch":
        sorted_brokers = sorted(brokers, key=lambda x: x["fee"]["month3"], reverse=True)
        def get_val(b): return f"{b['fee']['month3']:,.0f} VNĐ"
    elif rank_metric == "Số lượng khách hàng sở hữu":
        sorted_brokers = sorted(brokers, key=lambda x: len([c for c in customers if c["broker_id"] == x["id"]]), reverse=True)
        def get_val(b): return f"{len([c for c in customers if c['broker_id'] == b['id']])} KH"
    else:
        sorted_brokers = sorted(brokers, key=lambda x: len([c for c in customers if c["broker_id"] == x["id"] and c["status"] == "active"]), reverse=True)
        def get_val(b): return f"{len([c for c in customers if c['broker_id'] == b['id'] and c['status'] == 'active'])} TK Active"
        
    rank_table = []
    for rank_idx, b in enumerate(sorted_brokers, 1):
        rank_table.append({
            "Hạng": rank_idx,
            "Thành viên nhóm": b["name"],
            "Kết quả thực hiện": get_val(b),
            "Định vị danh mục": "🟢 Bạn" if b["id"] == current_broker_id else "Đồng nghiệp"
        })
        
    st.dataframe(pd.DataFrame(rank_table), use_container_width=True, hide_index=True)

with st.sidebar:
    st.markdown("---")
    st.markdown("**QUẢN TRỊ NỘI DUNG**")
    st.caption("Dữ liệu chỉ tiêu thử việc được áp dụng đồng bộ cho toàn bộ nhân sự theo quy chế tuyển dụng của SSI năm 2026.")
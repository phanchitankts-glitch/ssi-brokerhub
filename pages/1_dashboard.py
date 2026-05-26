import streamlit as st
import plotly.express as px
import pandas as pd

st.set_page_config(page_title="Dashboard | SSI BrokerHub", page_icon="assets/logo.png", layout="wide")

if "initialized" not in st.session_state:
    st.warning("Vui lòng quay lại trang chủ để hệ thống tải dữ liệu khởi tạo.")
    st.stop()

customers = st.session_state.customers
brokers = st.session_state.brokers
kpi_targets = st.session_state.kpi_targets

st.markdown("<h2 style='color: #000000; margin-bottom: 0px;'>Dashboard Tổng Quan KPI</h2>", unsafe_allow_html=True)
st.markdown("<p style='color: #6B7280; font-size: 1rem;'>Theo dõi tiến độ hoàn thành chỉ tiêu kinh doanh của nhóm môi giới</p>", unsafe_allow_html=True)

total_customers = len(customers)
active_accounts = len([c for c in customers if c["status"] == "active"])
total_fee_month3 = sum([b["fee"]["month3"] for b in brokers])

st.markdown("<br>", unsafe_allow_html=True)
if total_fee_month3 < kpi_targets["monthly_fee"] * 0.8:
    st.error("CẢNH BÁO QUẢN TRỊ: Sắp kết thúc kỳ đánh giá nhưng tổng doanh số phí chưa đạt 80% KPI. Yêu cầu rà soát danh mục khách hàng.")
elif total_fee_month3 < kpi_targets["monthly_fee"]:
    st.warning("THÔNG BÁO: Nhóm đang thiếu doanh số phí. Đề nghị tăng cường các hoạt động chốt lệnh.")
else:
    st.success("XÁC NHẬN: Nhóm đã hoàn thành xuất sắc KPI doanh số kỳ này.")

st.markdown("#### Tiến độ so với mục tiêu")
col1, col2, col3 = st.columns(3)

with col1:
    with st.container(border=True):
        st.metric(label="Tổng khách hàng quản lý", value=f"{total_customers} / {kpi_targets['customers']}")
        st.progress(min(total_customers / kpi_targets['customers'], 1.0))

with col2:
    with st.container(border=True):
        st.metric(label="Tài khoản Active", value=f"{active_accounts} / {kpi_targets['active_accounts']}")
        st.progress(min(active_accounts / kpi_targets['active_accounts'], 1.0))

with col3:
    with st.container(border=True):
        st.metric(label="Doanh số phí (Tháng 3)", value=f"{total_fee_month3:,.0f} VNĐ")
        st.progress(min(total_fee_month3 / kpi_targets['monthly_fee'], 1.0))

st.markdown("<hr style='margin-top: 2rem; margin-bottom: 2rem;'>", unsafe_allow_html=True)

# ==========================================
# PHẦN 4: BIỂU ĐỒ TRỰC QUAN (CỘT & ĐƯỜNG)
# ==========================================
st.markdown("#### Phân tích dữ liệu & Tăng trưởng")
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.markdown("**Phân bổ doanh số phí môi giới**")
    df_brokers = pd.DataFrame(brokers)
    df_brokers['Phí Tháng 3'] = df_brokers['fee'].apply(lambda x: x['month3'])
    fig_bar = px.bar(df_brokers, x="name", y="Phí Tháng 3", text_auto=".2s", labels={"name": "", "Phí Tháng 3": "Doanh số phí (VNĐ)"})
    fig_bar.update_traces(marker_color='#ED1C24', textfont_size=12, textposition="outside", cliponaxis=False)
    fig_bar.update_layout(showlegend=False, margin=dict(t=10, b=20, l=0, r=0), height=320)
    st.plotly_chart(fig_bar, use_container_width=True)

with col_chart2:
    st.markdown("**Tăng trưởng khách hàng mới (4 tuần qua)**")
    trend_data = pd.DataFrame({"Tuần": ["Tuần 1", "Tuần 2", "Tuần 3", "Tuần 4"], "Khách Hàng Mới": [2, 5, 4, 9]})
    fig_line = px.line(trend_data, x="Tuần", y="Khách Hàng Mới", markers=True, labels={"Tuần": "", "Khách Hàng Mới": "Số lượng KH"})
    fig_line.update_traces(line_color='#000000', marker=dict(size=10, color='#ED1C24', line=dict(width=2, color='white')))
    fig_line.update_layout(margin=dict(t=10, b=20, l=0, r=0), height=320)
    st.plotly_chart(fig_line, use_container_width=True)

st.markdown("<hr style='margin-top: 2rem; margin-bottom: 2rem;'>", unsafe_allow_html=True)

st.markdown("#### Mô hình ước tính doanh số chốt lệnh")
missing_fee = max(0, kpi_targets['monthly_fee'] - total_fee_month3)
if missing_fee > 0:
    st.info(f"Phân tích: Nhóm đang thiếu {missing_fee:,.0f} VNĐ để hoàn thành KPI. Sử dụng công cụ dưới đây để lên kế hoạch bù đắp.")

with st.container(border=True):
    col_calc1, col_calc2 = st.columns(2)
    with col_calc1:
        trade_value = st.number_input("Nhập giá trị 1 lệnh dự kiến (VNĐ):", min_value=0, value=100000000, step=10000000)
        fee_rate = st.selectbox("Tỷ lệ phí áp dụng:", [0.0015, 0.0020, 0.0025], format_func=lambda x: f"{x*100}%")
    with col_calc2:
        fee_per_trade = trade_value * fee_rate
        st.metric("Ước tính phí / lệnh:", f"{fee_per_trade:,.0f} VNĐ")
        if missing_fee > 0 and fee_per_trade > 0:
            orders_needed = (missing_fee / fee_per_trade)
            st.markdown(f"<span style='color: #ED1C24; font-weight: bold;'>Yêu cầu hành động: Cần thực hiện thêm tối thiểu {int(orders_needed) + 1} lệnh tương tự để đạt chỉ tiêu.</span>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("**CÔNG CỤ ĐIỀU HÀNH**")
    if st.button("Tải lại Kịch bản Demo", use_container_width=True, type="primary"):
        st.session_state.clear()
        st.rerun()
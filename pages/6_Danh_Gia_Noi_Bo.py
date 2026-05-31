import streamlit as st
import pandas as pd

st.set_page_config(page_title="Đánh giá 360 | SSI BrokerHub", page_icon="assets/logo.png", layout="wide")

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
with menu_cols[0]: st.page_link("pages/1_Khong_Gian_Dieu_Hanh.py", label="Không Gian Điều Hành")
with menu_cols[1]: st.page_link("pages/2_Quan_Tri_Danh_Muc.py", label="Quản Trị Danh Mục")
with menu_cols[2]: st.page_link("pages/3_Khuyen_Nghi_Dau_Tu.py", label="Khuyến Nghị Đầu Tư")
with menu_cols[3]: st.page_link("pages/4_Theo_Doi_KPI.py", label="Theo Dõi KPI")
with menu_cols[4]: st.page_link("pages/5_Nhat_Ky_Van_Hanh.py", label="Nhật Ký Vận Hành")
with menu_cols[5]: st.page_link("pages/6_Danh_Gia_Noi_Bo.py", label="Đánh Giá Nội Bộ")
st.markdown("---")

current_broker_id = st.session_state.current_broker_id
brokers = st.session_state.brokers
current_broker = next(b for b in brokers if b["id"] == current_broker_id)
my_customers = [c for c in st.session_state.customers if c["broker_id"] == current_broker_id]

# KHỞI TẠO DANH SÁCH ĐÁNH GIÁ TRỐNG (Đã xóa dữ liệu thô)
if "cross_evaluations" not in st.session_state:
    st.session_state.cross_evaluations = []

# ==========================================
# HEADER CHUẨN FORM MODULE 3
# ==========================================
st.markdown("<h2 style='color: #000000; margin-bottom: 0px;'>Hệ thống Đánh giá Nội bộ</h2>", unsafe_allow_html=True)
st.markdown(f"<p style='color: #6B7280; font-size: 1rem;'>Đánh giá năng lực định kỳ cho nhân sự: <b>{current_broker['name']}</b></p>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["1. Tự Đánh Giá", "2. Đánh Giá Chéo", "3. Báo Cáo Tổng Hợp"])

# ==========================================
# TAB 1: TỰ ĐÁNH GIÁ
# ==========================================
with tab1:
    my_total = len(my_customers)
    profitable = len([c for c in my_customers if c.get("profit_margin", -1) >= 0])
    win_rate = (profitable / my_total * 100) if my_total > 0 else 0
    auto_ethics = win_rate > 70
    
    with st.container(border=True):
        st.markdown("**Bản thân tự chấm điểm kết quả cuối tháng**")
        col_l, col_r = st.columns(2)
        with col_l:
            s1 = st.slider("Kiến thức thị trường & Sản phẩm", 1, 5, 4, key="self_s1")
            s2 = st.slider("Kỹ năng tư vấn & Khuyến nghị", 1, 5, 3, key="self_s2")
            s3 = st.slider("Chất lượng chăm sóc khách hàng", 1, 5, 4, key="self_s3")
        with col_r:
            s4 = st.slider("Tinh thần làm việc nhóm & Phối hợp", 1, 5, 4, key="self_s4")
            st.divider()
            st.markdown("**Đạo đức nghề nghiệp (SSI Code of Ethics)**")
            if auto_ethics:
                st.markdown(f"Đánh giá hệ thống: <span style='color: #10B981; font-weight: bold;'>5 / 5 Điểm (Tự động)</span>", unsafe_allow_html=True)
                st.caption(f"Tỷ lệ KH có lãi đạt {win_rate:.0f}% (>70%). Ghi nhận điểm tuyệt đối bảo vệ tài sản KH.")
                s5 = 5
            else:
                s5 = st.slider("Mức điểm tự chấm:", 1, 5, 3, key="self_s5")
                st.info(f"Tỷ lệ KH có lãi: {win_rate:.0f}%. (Đạt >70% để tự động Max điểm)")
                
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Xác nhận lưu kết quả tự đánh giá", type="primary"):
            st.session_state.cross_evaluations = [e for e in st.session_state.cross_evaluations if not (e.get("from_name") == "Chính bạn" and e["to_id"] == current_broker_id)]
            st.session_state.cross_evaluations.append({
                "from_name": "Chính bạn", "to_id": current_broker_id, "c1": s1, "c2": s2, "c3": s3, "c4": s4, "c5": s5
            })
            st.success("Đã đồng bộ điểm cá nhân lên hệ thống!")

# ==========================================
# TAB 2: ĐÁNH GIÁ ĐỒNG NGHIỆP
# ==========================================
with tab2:
    with st.container(border=True):
        st.markdown("**Phiếu đánh giá đồng nghiệp**")
        peer_options = {b["id"]: b["name"] for b in brokers if b["id"] != current_broker_id}
        selected_peer_id = st.selectbox("Chọn nhân sự:", options=list(peer_options.keys()), format_func=lambda x: peer_options[x])
        
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            p_c1 = st.slider("Chuyên môn & Phân tích", 1, 5, 4, key="p_s1")
            p_c2 = st.slider("Kỹ năng Giao tiếp KH", 1, 5, 4, key="p_s2")
            p_c3 = st.slider("Mức độ hỗ trợ nhóm", 1, 5, 4, key="p_s3")
        with col_p2:
            p_c4 = st.slider("Ý thức kỷ luật", 1, 5, 4, key="p_s4")
            p_c5 = st.slider("Đạo đức nghề nghiệp", 1, 5, 4, key="p_s5")
            
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Xác nhận gửi phiếu đánh giá"):
            st.session_state.cross_evaluations.append({
                "from_name": current_broker["name"], "to_id": selected_peer_id,
                "c1": p_c1, "c2": p_c2, "c3": p_c3, "c4": p_c4, "c5": p_c5
            })
            st.success("Đã lưu bảng chấm điểm đồng nghiệp thành công!")

# ==========================================
# TAB 3: BẢNG TỔNG HỢP & XUẤT FILE
# ==========================================
with tab3:
    st.markdown("#### Báo cáo Năng lực Trung bình")
    my_evals = [e for e in st.session_state.cross_evaluations if e["to_id"] == current_broker_id]
    
    if my_evals:
        df_evals = pd.DataFrame(my_evals)
        df_display = df_evals.rename(columns={
            "from_name": "Người đánh giá", "c1": "Chuyên môn", "c2": "Tư vấn",
            "c3": "Chăm sóc KH", "c4": "Đội nhóm", "c5": "Đạo đức"
        }).drop(columns=["to_id"])
        
        avg_c1, avg_c2 = df_display["Chuyên môn"].mean(), df_display["Tư vấn"].mean()
        avg_c3, avg_c4 = df_display["Chăm sóc KH"].mean(), df_display["Đội nhóm"].mean()
        avg_c5 = df_display["Đạo đức"].mean()
        total_avg = (avg_c1 + avg_c2 + avg_c3 + avg_c4 + avg_c5) / 5
        
        col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)
        col_m1.metric("Chuyên môn", f"{avg_c1:.1f}")
        col_m2.metric("Tư vấn", f"{avg_c2:.1f}")
        col_m3.metric("Chăm sóc KH", f"{avg_c3:.1f}")
        col_m4.metric("Đội nhóm", f"{avg_c4:.1f}")
        col_m5.metric("Đạo đức", f"{avg_c5:.1f}")
        
        st.markdown(f"**Điểm xét duyệt KPI cuối kỳ:** <span style='color: #ED1C24; font-size: 1.3rem; font-weight: bold;'>{total_avg:.2f} / 5.0</span>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        with st.container(border=True):
            st.markdown("**Chi tiết các phiếu đánh giá**")
            st.dataframe(df_display, use_container_width=True, hide_index=True)
            
            csv_data = df_display.to_csv(index=False).encode('utf-8')
            st.download_button(label="📥 Kết xuất báo cáo (CSV)", data=csv_data, file_name=f"SSI_360_Report_{current_broker['name']}.csv", mime="text/csv")
    else:
        st.info("Hệ thống chưa ghi nhận phiếu đánh giá nào dành cho bạn. Bạn có thể tự đánh giá ở Tab 1 hoặc chờ đồng nghiệp đánh giá từ tài khoản của họ.")

# ==========================================
# FOOTER CHUẨN
# ==========================================
with st.sidebar:
    st.markdown("---")
    st.markdown("**QUẢN TRỊ NỘI DUNG**")
    st.caption("Dữ liệu đánh giá được bảo mật tuyệt đối. Điểm số 360 độ sẽ được sử dụng làm cơ sở để xét thưởng cuối quý theo quy định của SSI.")
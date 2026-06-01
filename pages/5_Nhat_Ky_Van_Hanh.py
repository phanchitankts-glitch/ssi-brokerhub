import streamlit as st
import datetime

st.set_page_config(page_title="Nhật ký | SSI BrokerHub", page_icon="assets/logo.png", layout="wide")

if "initialized" not in st.session_state or not st.session_state.logged_in:
    st.warning("Vui lòng quay lại trang chủ để đăng nhập.")
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
current_broker_id = st.session_state.current_broker_id
st.markdown("<h2 style='color: #111827; margin-bottom: 0;'>Nhật ký Vận hành (Audit Log)</h2>", unsafe_allow_html=True)
st.caption("Ghi nhận mọi hoạt động tương tác với khách hàng của cán bộ môi giới.")

# Form nhập liệu
with st.container(border=True):
    my_customers = [c for c in st.session_state.customers if c["broker_id"] == current_broker_id]
    customer_dict = {c["id"]: c["name"] for c in my_customers}
    
    c1, c2 = st.columns([1, 2])
    with c1:
        label_map = {"call": "Gọi điện thoại", "meet": "Gặp mặt", "report": "Gửi báo cáo", "trade": "Hỗ trợ lệnh", "open": "Mở tài khoản"}
        act_type = st.selectbox("Nghiệp vụ", ["call", "meet", "report", "trade", "open"], format_func=lambda x: label_map[x])
        act_cus = st.selectbox("Khách hàng", options=[None] + list(customer_dict.keys()), format_func=lambda x: customer_dict[x] if x else "Chung")
    with c2:
        act_note = st.text_area("Ghi chú chi tiết kết quả", height=115)
        
    if st.button("Lưu biên bản", type="primary"):
        new_act = {
            "id": max([a["id"] for a in st.session_state.activities]) + 1 if st.session_state.activities else 1,
            "broker_id": current_broker_id, "customer_id": act_cus,
            "type": act_type, "note": act_note,
            "date": datetime.datetime.now().isoformat()[:19]
        }
        st.session_state.activities.append(new_act)
        st.success("Đã ghi nhận dữ liệu vào hệ thống!")
        st.rerun()

st.markdown("##### 🕒 Dòng thời gian gần đây")
my_acts = sorted([a for a in st.session_state.activities if a["broker_id"] == current_broker_id], key=lambda x: x["date"], reverse=True)

if not my_acts:
    st.info("Chưa có hoạt động nào được ghi nhận.")
else:
    for act in my_acts:
        cus_name = next((c["name"] for c in st.session_state.customers if c["id"] == act["customer_id"]), "Khách hàng chung")
        st.markdown(f"""
        <div style='background-color: white; padding: 15px; border-radius: 8px; border-left: 4px solid #ED1C24; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 10px;'>
            <b>{label_map.get(act['type'])}</b> với <b>{cus_name}</b> <span style='color: gray; font-size: 0.8rem;'>({act['date'].replace('T', ' ')})</span><br>
            <span style='color: #4B5563;'>{act['note']}</span>
        </div>
        """, unsafe_allow_html=True)
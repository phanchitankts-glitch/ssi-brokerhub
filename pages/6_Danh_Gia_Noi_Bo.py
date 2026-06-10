import streamlit as st
import pandas as pd
import base64
from streamlit_option_menu import option_menu

st.set_page_config(page_title="Đánh giá 360 | SSI BrokerHub", page_icon="assets/logo.png", layout="wide")

# Kiểm tra xác thực
if "initialized" not in st.session_state or not st.session_state.logged_in:
    st.warning("Yêu cầu xác thực. Vui lòng quay lại trang chủ để đăng nhập hệ thống.")
    st.stop()
# ========================================================
# --- THANH TIỆN ÍCH ĐỘNG (THÔNG BÁO, CHAT, PROFILE) ---
# ========================================================
# 1. Khởi tạo dữ liệu ảo (Session State) cho thông báo và tin nhắn
if "notifications" not in st.session_state:
    st.session_state.notifications = [
        {"id": 1, "text": "Phòng QTRR: Rà soát danh mục margin", "done": False},
        {"id": 2, "text": "Họp giao ban môi giới lúc 15h30", "done": False}
    ]
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

# Lấy thông tin tài khoản đang đăng nhập
current_user_id = st.session_state.current_broker_id
current_user = next((b for b in st.session_state.brokers if b["id"] == current_user_id), {"name": "Cán bộ SSI"})

# 2. Tinh chỉnh CSS để icon trong suốt và ÉP KHOẢNG CÁCH SÁT XUỐNG MENU ĐỎ
st.markdown("""
    <style>
    div[data-testid="stPopover"] > button {
        background-color: transparent !important;
        border: 1px solid rgba(0,0,0,0.15) !important;
        box-shadow: none !important;
        padding: 5px 12px !important;
        color: #4B5563 !important; 
        font-weight: 600;
        font-size: 14px;
        border-radius: 6px;
        height: 38px;
        margin-bottom: -15px; /* Kéo xích nút bấm lại gần thanh menu đỏ */
    }
    div[data-testid="stPopover"] > button:hover {
        color: #ED1C24 !important; 
        border-color: #ED1C24 !important;
        background-color: rgba(237, 28, 36, 0.05) !important;
    }
    </style>
""", unsafe_allow_html=True)

# 3. ĐẾM SỐ LƯỢNG CHƯA ĐỌC ĐỂ HIỂN THỊ BADGE (1), (2)...
unread_notifs = len([n for n in st.session_state.notifications if not n["done"]])
notif_label = f"Thông báo ({unread_notifs})" if unread_notifs > 0 else "Thông báo"

# Đếm số tin nhắn người khác gửi đích danh cho mình
unread_msgs = len([m for m in st.session_state.chat_messages if m["to"] == current_user["name"]])
msg_label = f"Tin nhắn ({unread_msgs})" if unread_msgs > 0 else "Tin nhắn"

# 4. Dàn trang Thanh tiện ích nằm gọn ở góc phải (Căn lề sát nhau)
col_space, col_notif, col_chat, col_profile = st.columns([5.3, 1.7, 1.5, 2.5])

# ---- Ô THÔNG BÁO ----
with col_notif:
    with st.popover(notif_label, icon=":material/notifications_none:"):
        st.markdown("**Thông báo hệ thống**")
        active_notifs = [n for n in st.session_state.notifications if not n["done"]]
        if not active_notifs:
            st.info("Bạn đã xử lý hết công việc. Không có thông báo mới.")
        else:
            for notif in active_notifs:
                if st.checkbox(notif["text"], key=f"notif_{notif['id']}"):
                    notif["done"] = True
                    st.rerun()

# ---- Ô TIN NHẮN ----
with col_chat:
    with st.popover(msg_label, icon=":material/chat_bubble_outline:"):
        st.markdown("**Trao đổi nội bộ**")
        
        other_brokers = [b["name"] for b in st.session_state.brokers if b["id"] != current_user_id]
        chat_target = st.selectbox("Tìm đồng nghiệp:", other_brokers, label_visibility="collapsed")
        
        st.divider()
        
        history = [m for m in st.session_state.chat_messages 
                   if (m["from"] == current_user["name"] and m["to"] == chat_target) 
                   or (m["to"] == current_user["name"] and m["from"] == chat_target)]
        
        chat_container = st.container(height=250)
        with chat_container:
            if not history:
                st.caption(f"Bắt đầu trò chuyện với {chat_target}.")
            for msg in history:
                if msg["from"] == current_user["name"]:
                    st.markdown(f"<div style='text-align:right; margin-bottom: 8px;'><span style='background-color:#ED1C24; color:white; padding:8px 12px; border-radius:15px; display:inline-block; max-width:80%;'>{msg['msg']}</span></div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div style='text-align:left; margin-bottom: 8px;'><span style='background-color:#F3F4F6; color:black; padding:8px 12px; border-radius:15px; display:inline-block; max-width:80%;'><b>{msg['from']}:</b><br>{msg['msg']}</span></div>", unsafe_allow_html=True)
        
        new_msg = st.text_input("Nhập tin...", key="chat_input", label_visibility="collapsed", placeholder="Nhập tin nhắn...")
        if st.button("Gửi tin", use_container_width=True, type="primary"):
            if new_msg:
                st.session_state.chat_messages.append({"from": current_user["name"], "to": chat_target, "msg": new_msg})
                st.rerun()

# ---- Ô TÀI KHOẢN / ĐĂNG XUẤT ----
with col_profile:
    with st.popover(current_user['name'], icon=":material/person_outline:"):
        st.markdown(f"**{current_user['name']}**")
        st.caption("Trạng thái: Đang hoạt động 🟢")
        st.divider()
        
        # Nút xóa lịch sử tin nhắn (để reset số đếm thông báo nếu muốn)
        if st.button("Xóa hộp thư đến", use_container_width=True):
            st.session_state.chat_messages = [m for m in st.session_state.chat_messages if m["to"] != current_user["name"]]
            st.rerun()
            
        if st.button("Đăng xuất", type="primary", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.current_broker_id = None
            st.switch_page("app.py")

# ========================================================
# --- ĐỌC LOGO TỪ FILE LOCAL & MÃ HÓA BASE64 ---
# ========================================================
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception:
        return ""

logo_b64 = get_base64_image("assets/logo.png")
if logo_b64:
    bg_style = f"url('data:image/png;base64,{logo_b64}'), linear-gradient(to right, #8B0000, #ED1C24)"
else:
    bg_style = "linear-gradient(to right, #8B0000, #ED1C24)"

# ========================================================
# --- TẠO MENU NGANG TRÊN CÙNG (TOP NAVIGATION) CHUẨN SSI ---
# ========================================================
st.markdown("""
    <style>
        .block-container { padding-top: 1rem !important; padding-bottom: 0rem !important; }
        [data-testid="collapsedControl"] { display: none; }
        [data-testid='stSidebar'] {display: none !important;}
        header[data-testid="stHeader"] {display: none !important;} 
    </style>
""", unsafe_allow_html=True)

selected = option_menu(
    menu_title=None,
    options=["Tổng Quan", "Quản Trị Danh Mục", "Khuyến Nghị Đầu Tư", "Theo Dõi KPI", "Nhật Ký Vận Hành", "Đánh Giá Nội Bộ"],
    icons=["house", "briefcase", "graph-up-arrow", "bar-chart", "journal-text", "clipboard-check"],
    default_index=5, # <--- Vị trí thứ 6 (Đánh Giá Nội Bộ)
    orientation="horizontal",
    styles={
        "container": {
            "padding": "0px !important", 
            "background-image": bg_style,
            "background-repeat": "no-repeat, no-repeat",
            "background-position": "20px center, center",
            "background-size": "45px, cover", 
            "border-radius": "0px", 
            "max-width": "100%", 
            "margin": "0px",
            "height": "65px",
            "display": "flex",
            "align-items": "center"
        },
        "icon": {
            "color": "white", 
            "font-size": "16px",
            "margin-right": "8px",
            "display": "flex",
            "align-items": "center"
        },
        "nav-link": {
            "font-size": "13px", 
            "text-align": "center", 
            "margin": "0px 2px", 
            "--hover-color": "rgba(255, 255, 255, 0.15)", 
            "color": "white", 
            "font-weight": "bold", 
            "text-transform": "uppercase", 
            "padding": "0px 15px", 
            "height": "45px", 
            "display": "flex", 
            "align-items": "center", 
            "justify-content": "center", 
            "border-radius": "0px",
            "white-space": "nowrap",
            "line-height": "1" 
        },
        "nav-link-selected": {
            "background-color": "rgba(0, 0, 0, 0.25)", 
            "color": "white"
        },
        "nav-pills": {
            "display": "flex",
            "align-items": "center",
            "justify-content": "center", 
            "width": "100%",
            "padding-left": "80px", 
            "margin": "0"
        }
    }
)

pages_dict = {
    "Tổng Quan": "pages/1_Tong_Quan.py",
    "Quản Trị Danh Mục": "pages/2_Quan_Tri_Danh_Muc.py",
    "Khuyến Nghị Đầu Tư": "pages/3_Khuyen_Nghi_Dau_Tu.py",
    "Theo Dõi KPI": "pages/4_Theo_Doi_KPI.py",
    "Nhật Ký Vận Hành": "pages/5_Nhat_Ky_Van_Hanh.py",
    "Đánh Giá Nội Bộ": "pages/6_Danh_Gia_Noi_Bo.py"
}

if pages_dict[selected] != "pages/6_Danh_Gia_Noi_Bo.py":
    st.switch_page(pages_dict[selected])

# ==========================================
# KHU VỰC NGHIỆP VỤ 
# ==========================================
current_broker_id = st.session_state.current_broker_id
brokers = st.session_state.brokers
current_broker = next(b for b in brokers if b["id"] == current_broker_id)
my_customers = [c for c in st.session_state.customers if c["broker_id"] == current_broker_id]

if "cross_evaluations" not in st.session_state:
    st.session_state.cross_evaluations = []

st.markdown("<h2 style='color: #000000; margin-bottom: 0px;'>Hệ thống Đánh giá Nội bộ</h2>", unsafe_allow_html=True)
st.markdown(f"<p style='color: #6B7280; font-size: 1rem;'>Đánh giá năng lực định kỳ cho nhân sự: <b>{current_broker['name']}</b></p>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["1. Tự Đánh Giá", "2. Đánh Giá Chéo", "3. Báo Cáo Tổng Hợp"])

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

with st.sidebar:
    st.markdown("---")
    st.markdown("**QUẢN TRỊ NỘI DUNG**")
    st.caption("Dữ liệu đánh giá được bảo mật tuyệt đối. Điểm số 360 độ sẽ được sử dụng làm cơ sở để xét thưởng cuối quý theo quy định của SSI.")
# Gọi hàm hiển thị chân trang thương hiệu SSI
from data.mock_data import render_footer
render_footer()
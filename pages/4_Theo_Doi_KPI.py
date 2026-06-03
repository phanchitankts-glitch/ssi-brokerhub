import streamlit as st
import pandas as pd
import base64
from streamlit_option_menu import option_menu

st.set_page_config(page_title="KPI Cá Nhân | SSI BrokerHub", page_icon="assets/logo.png", layout="wide")

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
    default_index=3, # <--- Vị trí thứ 4 (Theo dõi KPI)
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

if pages_dict[selected] != "pages/4_Theo_Doi_KPI.py":
    st.switch_page(pages_dict[selected])

# ==========================================
# KHU VỰC NGHIỆP VỤ 
# ==========================================
current_broker_id = st.session_state.current_broker_id
brokers = st.session_state.brokers
customers = st.session_state.customers

current_broker = next(b for b in brokers if b["id"] == current_broker_id)
my_customers = [c for c in customers if c["broker_id"] == current_broker_id]

st.markdown("<h2 style='color: #000000; margin-bottom: 0px;'>KPI Scorecard cá nhân</h2>", unsafe_allow_html=True)
st.markdown("<p style='color: #6B7280; font-size: 1rem;'>Theo dõi tiến độ chỉ tiêu thử việc và xếp hạng thi đua nội bộ phòng</p>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

t_cust = 20          
t_active = 10        
t_fee = 6000000      

my_total_cust = len(my_customers)
my_active_cust = len([c for c in my_customers if c["status"] == "active"])
my_fee_m1 = current_broker["fee"]["month1"]
my_fee_m2 = current_broker["fee"]["month2"]
my_fee_m3 = current_broker["fee"]["month3"]

pct_cust = (my_total_cust / t_cust) * 100
pct_active = (my_active_cust / t_active) * 100
pct_fee = (my_fee_m3 / t_fee) * 100

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
        
        total_performance_score = (score_cust * 0.3) + (score_active * 0.3) + (score_fee * 0.4)
        
        if total_performance_score >= 100.0:
            score_color = "#10B981"  
            status_text = "ĐỦ ĐIỀU KIỆN CHÍNH THỨC"
        elif total_performance_score >= 70.0:
            score_color = "#F59E0B"  
            status_text = "ĐẠT CHUẨN THỬ VIỆC"
        else:
            score_color = "#ED1C24"  
            status_text = "CẦN CẢI THIỆN HIỆU SUẤT"
            
        st.markdown(f"<div style='text-align: center; padding: 25px 0px;'>"
                    f"<p style='font-size: 1.1rem; margin-bottom: 5px; color:#6B7280;'>Tỷ lệ hoàn thành tổng hợp</p>"
                    f"<h1 style='color: {score_color}; font-size: 3.5rem; margin: 0;'>{total_performance_score:.1f}%</h1>"
                    f"<p style='color: {score_color}; font-weight: bold; margin-top: 5px;'>{status_text}</p>"
                    f"</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

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
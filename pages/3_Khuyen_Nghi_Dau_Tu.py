import streamlit as st
import pandas as pd
import yfinance as yf
import base64
from streamlit_option_menu import option_menu
from datetime import datetime  # <--- Khai báo thư viện thời gian

st.set_page_config(page_title="Advisory Hub | SSI BrokerHub", page_icon="assets/logo.png", layout="wide")

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
    default_index=2, # <--- Vị trí thứ 3 (Khuyến Nghị Đầu Tư)
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

if pages_dict[selected] != "pages/3_Khuyen_Nghi_Dau_Tu.py":
    st.switch_page(pages_dict[selected])

# ==========================================
# KHU VỰC NGHIỆP VỤ 
# ==========================================
stocks = st.session_state.stocks
customers = st.session_state.customers
current_broker_id = st.session_state.current_broker_id

st.markdown("<h2 style='color: #000000; margin-bottom: 0px;'>Trung tâm Khuyến nghị đầu tư</h2>", unsafe_allow_html=True)
st.markdown("<p style='color: #6B7280; font-size: 1rem;'>Hỗ trợ môi giới phân tích doanh nghiệp và gửi tín hiệu giao dịch đến khách hàng</p>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

col_select1, col_select2 = st.columns([1, 2])

with col_select1:
    with st.container(border=True):
        st.markdown("**Lựa chọn danh mục phân tích**")
        ticker_list = [s["ticker"] for s in stocks]
        selected_ticker = st.selectbox("Mã cổ phiếu niêm yết:", options=ticker_list)
        
        stock_data = next(s for s in stocks if s["ticker"] == selected_ticker)
        
        # ----------------------------------------------------
        # BỘ XỬ LÝ API GIÁ ĐÃ ĐƯỢC CẬP NHẬT CHỐNG LỖI
        # ----------------------------------------------------
        with st.spinner("Đang đồng bộ API từ sàn HOSE..."):
            try:
                # Đổi chuẩn sang đuôi .VN
                live_data = yf.Ticker(f"{selected_ticker}.VN")
                
                # Phương án 1: Gọi fast_info siêu tốc
                try:
                    real_price = live_data.fast_info['lastPrice']
                except:
                    # Phương án 2: Back-up bằng history nếu fast_info bị lỗi trên máy
                    real_price = live_data.history(period="1d")['Close'].iloc[-1]
                    
                price_display = f"{real_price:,.0f} VNĐ"
            except Exception as e:
                # In chi tiết lỗi ra Terminal để Tech Lead dễ rà soát
                print(f"Lỗi API mã {selected_ticker}: {e}")
                price_display = "Thị trường đóng cửa / Lỗi kết nối API"
        # ----------------------------------------------------
        
        st.markdown(f"**Giá khớp lệnh Real-time:** <span style='color: #10B981; font-size: 1.3rem; font-weight: bold;'>{price_display}</span>", unsafe_allow_html=True)
        
        # 👇 ĐÃ CHỈNH SỬA: Thay thế text cũ và sử dụng thời gian thực
        current_time = datetime.now().strftime("%H:%M - %d/%m/%Y")
        st.caption(f"Dữ liệu cơ bản cập nhật gần nhất: {current_time}")

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

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("#### Hệ thống Push Tín hiệu & Trợ lý Soạn thảo")

auto_draft = f"Kính gửi Quý khách hàng,\n\nHệ thống Phân tích SSI BrokerHub cập nhật tín hiệu kỹ thuật cho mã cổ phiếu {stock_data['ticker']} ({stock_data['company_name']}).\n"
auto_draft += f"- Giá thị trường hiện tại: {price_display}\n"
auto_draft += f"- Vùng giá giải ngân an toàn: {stock_data['buy_zone']}\n"
auto_draft += f"- Định giá mục tiêu: {stock_data['target']} | Ngưỡng cắt lỗ: {stock_data['cutloss']}\n\n"
auto_draft += f"Luận điểm đầu tư: {stock_data['thesis']} Dòng tiền hiện tại đang cho thấy dấu hiệu {stock_data['volume'].lower()}.\n\n"
auto_draft += f"Hành động khuyến nghị: {action}.\n\nTrân trọng,"

message_content = st.text_area("Nội dung kịch bản tư vấn (Được tạo tự động, có thể chỉnh sửa):", value=auto_draft, height=220)
import streamlit as st
import pandas as pd
import base64
from datetime import date
from data.mock_data import calculate_days_since_trade, is_churn_risk
from streamlit_option_menu import option_menu

st.set_page_config(page_title="CRM | SSI BrokerHub", page_icon="assets/logo.png", layout="wide")

if "initialized" not in st.session_state or not st.session_state.logged_in:
    st.warning("Vui lòng quay lại trang chủ để đăng nhập bằng Smart OTP.")
    st.stop()
# ========================================================
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
    default_index=1, # <--- 1 là vị trí thứ 2 (Quản trị danh mục)
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

# Bản đồ điều hướng
pages_dict = {
    "Tổng Quan": "pages/1_Tong_Quan.py",
    "Quản Trị Danh Mục": "pages/2_Quan_Tri_Danh_Muc.py",
    "Khuyến Nghị Đầu Tư": "pages/3_Khuyen_Nghi_Dau_Tu.py",
    "Theo Dõi KPI": "pages/4_Theo_Doi_KPI.py",
    "Nhật Ký Vận Hành": "pages/5_Nhat_Ky_Van_Hanh.py",
    "Đánh Giá Nội Bộ": "pages/6_Danh_Gia_Noi_Bo.py"
}

# <--- SỬA TÊN TRANG HIỆN TẠI ĐỂ KHÔNG BỊ LỖI CHUYỂN HƯỚNG ---
if pages_dict[selected] != "pages/2_Quan_Tri_Danh_Muc.py":
    st.switch_page(pages_dict[selected])

# ==========================================
# KHU VỰC NGHIỆP VỤ CRM
# ==========================================
current_broker_id = st.session_state.current_broker_id

st.markdown("<h2 style='color: #111827; margin-bottom: 0;'>Hệ thống Quản trị Khách hàng (CRM)</h2>", unsafe_allow_html=True)
st.caption("Quản lý danh mục đầu tư, tích hợp cảnh báo rủi ro và theo dõi hệ sinh thái S-Products.")
st.markdown("---")

my_customers = [c for c in st.session_state.customers if c["broker_id"] == current_broker_id]

tab1, tab2 = st.tabs(["Báo cáo Danh mục & S-Products", "Khai báo Khách hàng mới"])

with tab1:
    # --- Khối Metrics Tổng quan ---
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    
    total_cus = len(my_customers)
    total_asset = sum(c.get("trade_value", 0) for c in my_customers)
    churn_count = sum(1 for c in my_customers if calculate_days_since_trade(c["last_trade_date"]) > 14)
    cross_sell_count = sum(1 for c in my_customers if len(c.get("s_products", [])) > 0)
    
    with col_m1:
        st.metric("Tổng Khách hàng", f"{total_cus} KH")
    with col_m2:
        st.metric("Tài sản quản lý (AUM)", f"{total_asset:,.0f} đ")
    with col_m3:
        st.metric("Tỉ lệ Cross-sell (S-Products)", f"{int((cross_sell_count/total_cus)*100) if total_cus > 0 else 0}%", f"{cross_sell_count} KH đang dùng")
    with col_m4:
        st.metric("Cảnh báo Churn (>14 ngày)", f"{churn_count} KH", delta="- Rủi ro cao", delta_color="inverse")
    
    st.markdown("<br>", unsafe_allow_html=True)

    # --- Bộ lọc ---
    with st.container(border=True):
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            filter_status = st.selectbox("Trạng thái", ["Tất cả", "active", "inactive"])
        with col_f2:
            filter_product = st.selectbox("Lọc theo S-Products", ["Tất cả", "Có dùng S-Products", "Chưa dùng S-Products"])
        with col_f3:
            st.markdown("<br>", unsafe_allow_html=True)
            show_churn_only = st.checkbox("Chỉ hiển thị rủi ro Churn")

    # --- Xử lý dữ liệu bảng ---
    filtered_customers = []
    status_map = {"active": "Đang GD", "inactive": "Tạm ngưng"}

    for c in my_customers:
        if filter_status != "Tất cả" and c["status"] != filter_status: continue
        if show_churn_only and not is_churn_risk(c): continue
        has_product = len(c.get("s_products", [])) > 0
        if filter_product == "Có dùng S-Products" and not has_product: continue
        if filter_product == "Chưa dùng S-Products" and has_product: continue
        
        c_display = c.copy()
        c_display["days_inactive"] = calculate_days_since_trade(c["last_trade_date"])
        c_display["status_label"] = status_map.get(c["status"], c["status"])
        
        s_prod_list = c.get("s_products", [])
        c_display["s_products_label"] = " • ".join(s_prod_list) if s_prod_list else "---"
        c_display["profit_margin"] = c.get("profit_margin", 0.0)
        
        filtered_customers.append(c_display)

    if filtered_customers:
        df = pd.DataFrame(filtered_customers)
        df = df.sort_values(by="trade_value", ascending=False)
        
        df = df[["id", "name", "trade_value", "profit_margin", "s_products_label", "days_inactive", "status_label"]]
        df.columns = ["ID", "Khách Hàng", "NAV (VNĐ)", "Lãi/Lỗ (%)", "Hệ sinh thái S-Products", "Số ngày chưa GD", "Trạng Thái"]
        
        def style_dataframe(data):
            def highlight_churn_row(row):
                if row["Số ngày chưa GD"] > 14: return ['background-color: #FEE2E2'] * len(row)
                return [''] * len(row)
            
            def color_profit(val):
                if val > 0: return 'color: #059669; font-weight: bold;'
                elif val < 0: return 'color: #DC2626; font-weight: bold;'
                return 'color: #4B5563;'
            
            def color_products(val):
                if val != "---": return 'color: #2563EB; font-weight: bold;'
                return 'color: #9CA3AF;'

            styler = data.style.apply(highlight_churn_row, axis=1)
            
            try:
                styler = styler.map(color_profit, subset=['Lãi/Lỗ (%)']).map(color_products, subset=['Hệ sinh thái S-Products'])
            except AttributeError:
                styler = styler.applymap(color_profit, subset=['Lãi/Lỗ (%)']).applymap(color_products, subset=['Hệ sinh thái S-Products'])
                
            return styler.format({"NAV (VNĐ)": "{:,.0f}", "Lãi/Lỗ (%)": "{:+.1f}%"})

        st.markdown("##### Chi tiết Danh mục Khách hàng")
        st.dataframe(style_dataframe(df), use_container_width=True, hide_index=True, height=450)
    else:
        st.info("Không tìm thấy dữ liệu khớp với bộ lọc.")

with tab2:
    st.markdown("##### Khai báo Khách hàng mới")
    with st.form("add_customer_form", clear_on_submit=True):
        col_form1, col_form2 = st.columns(2)
        with col_form1:
            c_name = st.text_input("Họ và Tên (*)")
            c_phone = st.text_input("Số điện thoại (*)")
            c_products = st.multiselect("Đăng ký sử dụng dịch vụ chéo (S-Products)", ["S-BOND", "S-FUND", "S-MARGIN"])
        with col_form2:
            c_trade = st.number_input("Giá trị giao dịch dự kiến (VNĐ)", min_value=0, step=10000000, value=50000000)
        
        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("Lưu hồ sơ Khách hàng", type="primary")
        
        if submitted and c_name and c_phone:
            new_id = max([c["id"] for c in st.session_state.customers]) + 1
            new_customer = {
                "id": new_id, "name": c_name, "phone": c_phone,
                "open_date": st.session_state.demo_date.strftime("%Y-%m-%d"),
                "last_trade_date": st.session_state.demo_date.strftime("%Y-%m-%d"),
                "trade_value": c_trade, "profit_margin": 0.0,
                "s_products": c_products,
                "status": "active", "broker_id": current_broker_id
            }
            st.session_state.customers.append(new_customer)
            st.success("Đã lưu hồ sơ thành công! Mời bạn qua Tab Báo cáo để xem.")
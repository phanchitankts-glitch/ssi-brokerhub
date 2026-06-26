import streamlit as st
import datetime
import base64
import pandas as pd
from streamlit_option_menu import option_menu

st.set_page_config(page_title="Nhật ký | SSI BrokerHub", page_icon="assets/logo.png", layout="wide")

if "initialized" not in st.session_state or not st.session_state.logged_in:
    st.warning("Vui lòng quay lại trang chủ để đăng nhập.")
    st.stop()

if "notifications" not in st.session_state:
    st.session_state.notifications = [
        {"id": 1, "text": "Phòng QTRR: Rà soát danh mục margin", "done": False},
        {"id": 2, "text": "Họp giao ban môi giới lúc 15h30", "done": False}
    ]
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

current_user_id = st.session_state.current_broker_id
current_user = next((b for b in st.session_state.brokers if b["id"] == current_user_id), {"name": "Cán bộ SSI", "emp_code": "SSI-UNKNOWN"})

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
        margin-bottom: -15px; 
    }
    div[data-testid="stPopover"] > button:hover {
        color: #ED1C24 !important; 
        border-color: #ED1C24 !important;
        background-color: rgba(237, 28, 36, 0.05) !important;
    }
    </style>
""", unsafe_allow_html=True)

unread_notifs = len([n for n in st.session_state.notifications if not n["done"]])
notif_label = f"Thông báo ({unread_notifs})" if unread_notifs > 0 else "Thông báo"

unread_msgs = len([m for m in st.session_state.chat_messages if m["to"] == current_user["name"]])
msg_label = f"Tin nhắn ({unread_msgs})" if unread_msgs > 0 else "Tin nhắn"

col_space, col_notif, col_chat, col_profile = st.columns([5.3, 1.7, 1.5, 2.5])

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

with col_profile:
    with st.popover(current_user['name'], icon=":material/person_outline:"):
        st.markdown(f"**{current_user['name']}**")
        st.caption("Trạng thái: Đang hoạt động 🟢")
        st.divider()
        
        if st.button("Xóa hộp thư đến", use_container_width=True):
            st.session_state.chat_messages = [m for m in st.session_state.chat_messages if m["to"] != current_user["name"]]
            st.rerun()
            
        if st.button("Đăng xuất", type="primary", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.current_broker_id = None
            st.switch_page("app.py")

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
    default_index=4, 
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

if pages_dict[selected] != "pages/5_Nhat_Ky_Van_Hanh.py":
    st.switch_page(pages_dict[selected])

current_broker_id = st.session_state.current_broker_id
# LƯỢC BỎ TIẾNG ANH: (Audit Log)
st.markdown(f"<h2 style='color: #111827; margin-bottom: 0;'>Nhật ký Vận hành - {current_user.get('emp_code', '')}</h2>", unsafe_allow_html=True)
st.caption("Ghi nhận mọi hoạt động tương tác với khách hàng của cán bộ môi giới. Dữ liệu được dùng làm cơ sở minh bạch hóa KPI.")

label_map = {"call": "Gọi điện thoại", "meet": "Gặp mặt", "report": "Gửi báo cáo", "trade": "Hỗ trợ lệnh", "open": "Mở tài khoản"}

with st.container(border=True):
    my_customers = [c for c in st.session_state.customers if c["broker_id"] == current_broker_id]
    customer_dict = {c["id"]: c["name"] for c in my_customers}
    
    c1, c2 = st.columns([1, 2])
    with c1:
        act_type = st.selectbox("Nghiệp vụ", ["call", "meet", "report", "trade", "open"], format_func=lambda x: label_map[x])
        act_cus = st.selectbox("Khách hàng", options=[None] + list(customer_dict.keys()), format_func=lambda x: customer_dict[x] if x else "Chung (Chưa định danh)")
    with c2:
        act_note = st.text_area("Ghi chú chi tiết kết quả", height=115)
        
    if st.button("Lưu biên bản", type="primary"):
        new_act = {
            "id": max([a["id"] for a in st.session_state.activities]) + 1 if st.session_state.activities else 1,
            "broker_id": current_broker_id, 
            "customer_id": act_cus,
            "type": act_type, 
            "note": act_note,
            "date": datetime.datetime.now().isoformat()[:19]
        }
        st.session_state.activities.append(new_act)
        st.success("Đã ghi nhận dữ liệu vào hệ thống!")
        st.rerun()

st.markdown("##### Bảng dữ liệu Lịch sử tương tác")
my_acts = sorted([a for a in st.session_state.activities if a["broker_id"] == current_broker_id], key=lambda x: x["date"], reverse=True)

if not my_acts:
    st.info("Chưa có hoạt động nào được ghi nhận.")
else:
    table_data = []
    for act in my_acts:
        cus_name = next((c["name"] for c in st.session_state.customers if c["id"] == act["customer_id"]), "Khách hàng chung")
        formatted_date = act["date"].replace("T", " ")
        
        table_data.append({
            "Thời gian": formatted_date,
            "Mã NV Thực hiện": current_user.get("emp_code", "SSI-UNKNOWN"), 
            "Khách hàng": cus_name,
            "Nghiệp vụ": label_map.get(act["type"], "Khác"),
            "Chi tiết công việc": act["note"]
        })
        
    df_activities = pd.DataFrame(table_data)
    
    st.dataframe(
        df_activities,
        column_config={
            "Thời gian": st.column_config.TextColumn("Thời gian", width="medium"),
            "Mã NV Thực hiện": st.column_config.TextColumn("Mã NV Thực hiện", width="small"),
            "Khách hàng": st.column_config.TextColumn("Khách hàng", width="medium"),
            "Nghiệp vụ": st.column_config.TextColumn("Nghiệp vụ", width="small"),
            "Chi tiết công việc": st.column_config.TextColumn("Chi tiết công việc", width="large"),
        },
        use_container_width=True,
        hide_index=True
    )

try:
    from data.mock_data import render_footer
    render_footer()
except Exception:
    pass
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import base64
from datetime import date, timedelta
from sklearn.cluster import KMeans
from sklearn.svm import SVC
from streamlit_option_menu import option_menu

st.set_page_config(page_title="Dashboard | SSI BrokerHub", page_icon="assets/logo.png", layout="wide")

# ========================================================
# KIỂM TRA ĐĂNG NHẬP
# ========================================================
if "initialized" not in st.session_state or getattr(st.session_state, 'logged_in', False) == False:
    st.warning("Vui lòng quay lại trang chủ để đăng nhập.")
    st.stop()

# ========================================================
# LẤY DỮ LIỆU TỪ HỆ THỐNG CHUNG (Có cơ chế chống lỗi)
# ========================================================
customers = st.session_state.get("customers", [])
brokers = st.session_state.get("brokers", [])
kpi_targets = st.session_state.get("kpi_targets", {"customers": 20, "active_accounts": 10, "monthly_fee": 6000000})
fee_rates = st.session_state.get("fee_rates", {"min": 0.0015, "default": 0.0015, "max": 0.0025})
demo_date = st.session_state.get("demo_date", date.today())
current_user_id = st.session_state.current_broker_id
current_user = next((b for b in brokers if b["id"] == current_user_id), {"name": "Cán bộ SSI", "fee": {"month3": 0}})

# ----------------------------------------------------
# BỘ MÁY TÍNH NAV ĐỘNG NGAY TẠI TRANG TỔNG QUAN
# (Fix lỗi NAV = 0 khi broker mới vừa đăng nhập vào)
# ----------------------------------------------------
for c in customers:
    total_cost = 0
    total_nav = 0
    for p in c.get("portfolio", []):
        stock_info = next((s for s in st.session_state.stocks if s["ticker"] == p["ticker"]), None)
        if stock_info and "current_price" in stock_info:
            cur_price = stock_info["current_price"]
        else:
            base_str = stock_info.get("buy_zone", "30.0").split(" - ")[0] if stock_info else "30.0"
            try: cur_price = float(base_str.replace(',', '')) * 1000
            except: cur_price = 30000.0
            
        total_cost += p["volume"] * p["avg_price"]
        total_nav += p["volume"] * cur_price

    if total_cost > 0:
        c["trade_value"] = total_nav
        c["profit_margin"] = ((total_nav - total_cost) / total_cost) * 100
# ----------------------------------------------------

# ========================================================
# --- THANH TIỆN ÍCH ĐỘNG (THÔNG BÁO, CHAT, PROFILE) ---
# ========================================================
if "notifications" not in st.session_state:
    st.session_state.notifications = [
        {"id": 1, "text": "Phòng QTRR: Rà soát danh mục margin", "done": False},
        {"id": 2, "text": "Họp giao ban môi giới lúc 15h30", "done": False}
    ]
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

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
            st.info("Bạn đã xử lý hết công việc.")
        else:
            for notif in active_notifs:
                if st.checkbox(notif["text"], key=f"notif_{notif['id']}"):
                    notif["done"] = True
                    st.rerun()

with col_chat:
    with st.popover(msg_label, icon=":material/chat_bubble_outline:"):
        st.markdown("**Trao đổi nội bộ**")
        other_brokers = [b["name"] for b in brokers if b["id"] != current_user_id]
        chat_target = st.selectbox("Tìm đồng nghiệp:", other_brokers, label_visibility="collapsed")
        st.divider()
        history = [m for m in st.session_state.chat_messages if (m["from"] == current_user["name"] and m["to"] == chat_target) or (m["to"] == current_user["name"] and m["from"] == chat_target)]
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

# ========================================================
# --- TẠO MENU NGANG TRÊN CÙNG (TOP NAVIGATION) ---
# ========================================================
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except: return ""

logo_b64 = get_base64_image("assets/logo.png")
bg_style = f"url('data:image/png;base64,{logo_b64}'), linear-gradient(to right, #8B0000, #ED1C24)" if logo_b64 else "linear-gradient(to right, #8B0000, #ED1C24)"

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
    default_index=0, 
    orientation="horizontal",
    styles={
        "container": {"padding": "0px !important", "background-image": bg_style, "background-repeat": "no-repeat, no-repeat", "background-position": "20px center, center", "background-size": "45px, cover", "border-radius": "0px", "margin": "0px", "height": "65px", "display": "flex", "align-items": "center"},
        "icon": {"color": "white", "font-size": "16px", "margin-right": "8px"},
        "nav-link": {"font-size": "13px", "text-align": "center", "margin": "0px 2px", "--hover-color": "rgba(255, 255, 255, 0.15)", "color": "white", "font-weight": "bold", "text-transform": "uppercase", "padding": "0px 15px", "height": "45px", "display": "flex", "align-items": "center", "justify-content": "center", "border-radius": "0px"},
        "nav-link-selected": {"background-color": "rgba(0, 0, 0, 0.25)", "color": "white"},
        "nav-pills": {"display": "flex", "align-items": "center", "justify-content": "center", "width": "100%", "padding-left": "80px", "margin": "0"}
    }
)

pages_dict = {"Tổng Quan": "pages/1_Tong_Quan.py", "Quản Trị Danh Mục": "pages/2_Quan_Tri_Danh_Muc.py", "Khuyến Nghị Đầu Tư": "pages/3_Khuyen_Nghi_Dau_Tu.py", "Theo Dõi KPI": "pages/4_Theo_Doi_KPI.py", "Nhật Ký Vận Hành": "pages/5_Nhat_Ky_Van_Hanh.py", "Đánh Giá Nội Bộ": "pages/6_Danh_Gia_Noi_Bo.py"}
if pages_dict[selected] != "pages/1_Tong_Quan.py": st.switch_page(pages_dict[selected])

# ==========================================
# KHU VỰC NGHIỆP VỤ - DASHBOARD CÁ NHÂN
# ==========================================
st.markdown("<h2 style='color: #000000; margin-bottom: 0px;'>Dashboard Tổng Quan KPI</h2>", unsafe_allow_html=True)
st.markdown(f"<p style='color: #6B7280; font-size: 1rem;'>Hệ thống quản trị và phân tích dữ liệu đa chiều của Môi giới: <b>{current_user['name']}</b></p>", unsafe_allow_html=True)

with st.expander("Tùy chỉnh cấu hình vùng làm việc", expanded=False):
    col_set1, col_set2, col_set3, col_set4 = st.columns(4)
    with col_set1: show_charts = st.checkbox("Biểu đồ trực quan", value=True)
    with col_set2: show_radar = st.checkbox("Radar năng lực", value=True)
    with col_set3: show_sentiment = st.checkbox("Cảm xúc thị trường", value=True)
    with col_set4: show_calculator = st.checkbox("Mô hình tính phí", value=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- BỘ LỌC DỮ LIỆU CHỈ DÀNH CHO CÁ NHÂN BROKER ĐANG ĐĂNG NHẬP ---
my_customers = [c for c in customers if c["broker_id"] == current_user_id]
my_total_customers = len(my_customers)
my_active_accounts = len([c for c in my_customers if c["status"] == "active"])
my_monthly_fee = current_user.get("fee", {}).get("month3", 0)

# ==========================================
# TRUNG TÂM CẢNH BÁO RỦI RO (Alert Center)
# ==========================================
st.markdown("#### Trung tâm cảnh báo rủi ro danh mục")
risk_customers = [c for c in my_customers if c.get("profit_margin", 0) < -5.0]

if risk_customers:
    for rc in risk_customers:
        st.error(f"Cảnh báo rủi ro: Khách hàng {rc['name']} ghi nhận mức lỗ {rc['profit_margin']:.2f}%. Yêu cầu rà soát danh mục lập tức.")
else:
    st.success("Trạng thái ổn định: Không phát hiện tài khoản nào của bạn vi phạm ngưỡng quản trị rủi ro.")

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# PHẦN KPI CHÍNH (ĐÁNH GIÁ CÁ NHÂN THEO ĐỀ BÀI)
# ==========================================
kpi_cust_passed = my_total_customers >= kpi_targets["customers"]
kpi_active_passed = my_active_accounts >= kpi_targets["active_accounts"]
kpi_fee_passed = my_monthly_fee >= kpi_targets["monthly_fee"]

if kpi_cust_passed and kpi_active_passed and kpi_fee_passed:
    st.success("XÁC NHẬN: Chúc mừng! Bạn đã hoàn thành xuất sắc toàn bộ 3 chỉ tiêu KPI cá nhân kỳ này.")
elif my_monthly_fee < kpi_targets["monthly_fee"] * 0.8:
    st.error("CẢNH BÁO QUẢN TRỊ: Doanh số phí cá nhân chưa đạt 80% KPI. Yêu cầu đẩy mạnh giao dịch.")
else:
    st.warning("THÔNG BÁO: Bạn chưa hoàn thành 100% các chỉ tiêu KPI cá nhân. Hãy kiểm tra các mục còn thiếu bên dưới.")

st.markdown("#### Tiến độ so với mục tiêu cá nhân")
col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
with col_kpi1:
    with st.container(border=True):
        st.metric(label="Tổng khách hàng thu hút", value=f"{my_total_customers} / {kpi_targets['customers']}")
        st.progress(min(my_total_customers / kpi_targets['customers'], 1.0))
with col_kpi2:
    with st.container(border=True):
        st.metric(label="Tài khoản Active (Duy trì GD)", value=f"{my_active_accounts} / {kpi_targets['active_accounts']}")
        st.progress(min(my_active_accounts / kpi_targets['active_accounts'], 1.0))
with col_kpi3:
    with st.container(border=True):
        st.metric(label="Doanh số phí đạt được", value=f"{my_monthly_fee:,.0f} / {kpi_targets['monthly_fee']:,.0f} VNĐ")
        st.progress(min(my_monthly_fee / kpi_targets['monthly_fee'], 1.0))

st.markdown("<hr style='margin-top: 2rem; margin-bottom: 2rem;'>", unsafe_allow_html=True)

# ==========================================
# BIỂU ĐỒ TRỰC QUAN & RADAR NĂNG LỰC
# ==========================================
if show_charts or show_radar:
    col_layout1, col_layout2 = st.columns([1, 1])
    
    with col_layout1:
        if show_charts:
            st.markdown("**So sánh Doanh số phí với Đồng nghiệp**")
            df_brokers = pd.DataFrame(brokers)
            df_brokers['Phí Tháng 3'] = df_brokers['fee'].apply(lambda x: x.get('month3', 0))
            
            colors = ['#ED1C24' if b_id == current_user_id else '#D1D5DB' for b_id in df_brokers['id']]
            
            fig_bar = px.bar(df_brokers, x="name", y="Phí Tháng 3", text_auto=".2s")
            fig_bar.update_traces(marker_color=colors, textfont_size=12, textposition="outside", cliponaxis=False)
            fig_bar.update_layout(showlegend=False, margin=dict(t=10, b=20, l=0, r=0), height=320, xaxis_title="", yaxis_title="VNĐ")
            st.plotly_chart(fig_bar, use_container_width=True)
            
    with col_layout2:
        if show_radar:
            st.markdown("**Mô hình định vị năng lực (Radar Chart)**")
            radar_metrics = ['Doanh số phí', 'Tìm kiếm KH mới', 'Giữ chân khách hàng', 'Hiệu suất tư vấn', 'S-Products']
            fig_radar = go.Figure()
            
            my_radar_scores = [
                min((my_monthly_fee/kpi_targets['monthly_fee'])*100, 100),
                min((my_total_customers/kpi_targets['customers'])*100, 100),
                min((my_active_accounts/kpi_targets['active_accounts'])*100, 100),
                85, 80
            ]
            
            fig_radar.add_trace(go.Scatterpolar(
                r=my_radar_scores, theta=radar_metrics, fill='toself', name=current_user['name'], line_color='#ED1C24'
            ))
            fig_radar.add_trace(go.Scatterpolar(
                r=[70, 70, 70, 70, 70], theta=radar_metrics, fill='toself', name='Trung bình phòng', line_color='#000000'
            ))
            
            fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=True, margin=dict(t=30, b=10, l=10, r=10), height=320)
            st.plotly_chart(fig_radar, use_container_width=True)

    st.markdown("<hr style='margin-top: 1rem; margin-bottom: 2rem;'>", unsafe_allow_html=True)

# ----------------- MODULE AI ENGINE (Chạy ngầm) -----------------
df_ai = pd.DataFrame(customers)
if not df_ai.empty:
    try:
        df_ai['days_inactive'] = df_ai['last_trade_date'].apply(lambda x: (demo_date - date.fromisoformat(x)).days)
        X_cluster = df_ai[['trade_value', 'profit_margin']]
        kmeans = KMeans(n_clusters=3, random_state=42, n_init=10).fit(X_cluster)
        df_ai['cluster'] = kmeans.predict(X_cluster)
        cluster_map = {df_ai.groupby('cluster')['trade_value'].mean().sort_values().index[i]: v for i, v in enumerate(["Passive Account", "Active Trader", "Premium Account"])}
        df_ai['kmeans_segment'] = df_ai['cluster'].map(cluster_map)
        
        y_churn = (df_ai['days_inactive'] > 14).astype(int)
        X_churn = df_ai[['days_inactive', 'profit_margin']]
        if len(y_churn.unique()) > 1:
            svm_model = SVC(probability=True, random_state=42, kernel='linear').fit(X_churn, y_churn)
            df_ai['svm_prob'] = np.round(svm_model.predict_proba(X_churn)[:, 1] * 100, 1)
        else:
            df_ai['svm_prob'] = np.where(df_ai['days_inactive'] > 14, 88.0, 11.0)
            
        ai_results = df_ai.set_index('id').to_dict('index')
    except:
        ai_results = {}
else:
    ai_results = {}
# ---------------------------------------------------------------

# ==========================================
# INTERACTIVE DATA GRID (SIÊU LƯỚI CÁ NHÂN)
# ==========================================
st.markdown("#### Quản lý danh sách khách hàng của bạn (Interactive Grid)")
df_grid = pd.DataFrame(my_customers)

if not df_grid.empty and ai_results:
    # Lấy ngày hiện tại (năm nay 2026)
    today_date = date.today()
    
    df_grid['Phân nhóm AI'] = df_grid['id'].apply(lambda x: ai_results.get(x, {}).get('kmeans_segment', 'N/A'))
    df_grid['Rủi ro Churn'] = df_grid['id'].apply(lambda x: f"{ai_results.get(x, {}).get('svm_prob', 0)}%")
    df_grid['Ngày ngưng GD'] = df_grid['id'].apply(lambda x: ai_results.get(x, {}).get('days_inactive', 0))
    
    # --- CẬP NHẬT: 'last_trade_date' (GD Cuối) sát với thời gian thực tế hiện tại năm 2026 ---
    df_grid['last_trade_date'] = df_grid['Ngày ngưng GD'].apply(lambda x: (today_date - timedelta(days=x)).strftime('%Y-%m-%d'))
    
    st.dataframe(
        df_grid[['name', 'phone', 'last_trade_date', 'Ngày ngưng GD', 'trade_value', 'profit_margin', 'Phân nhóm AI', 'Rủi ro Churn', 'status']],
        column_config={
            "name": "Khách hàng",
            "phone": "Số điện thoại", # CẬP NHẬT: Đổi từ phone thành "Số điện thoại"
            "last_trade_date": "GD Cuối",
            "Ngày ngưng GD": st.column_config.NumberColumn("Ngưng GD", format="%d ngày"),
            "trade_value": st.column_config.NumberColumn("NAV (VNĐ)", format="%d"),
            "profit_margin": st.column_config.ProgressColumn("Hiệu suất", min_value=-20, max_value=20, format="%.1f%%"),
            "Phân nhóm AI": "Nhóm khách hàng",
            "Rủi ro Churn": "Xác suất rời bỏ",
            "status": "Trạng thái"
        },
        use_container_width=True, hide_index=True
    )
    st.download_button(label="Kết xuất báo cáo danh mục (CSV)", data=df_grid.to_csv(index=False).encode('utf-8'), file_name=f"SSI_BrokerHub_CRM_{current_user['name']}.csv", mime="text/csv")
else:
    st.info("Chưa có dữ liệu khách hàng được phân bổ cho bạn.")

st.markdown("<hr style='margin-top: 2rem; margin-bottom: 2rem;'>", unsafe_allow_html=True)

# ==========================================
# SENTIMENT HUB
# ==========================================
if show_sentiment:
    st.markdown("#### Trung tâm cảm xúc thị trường (Sentiment Hub)")
    col_sent1, col_sent2 = st.columns([1, 2])
    with col_sent1:
        with st.container(border=True):
            st.markdown("**Chỉ báo tâm lý dòng tiền**")
            st.markdown("<h2 style='color: #10B981; margin-top: 10px; margin-bottom: 0px;'>TÍCH CỰC (74%)</h2>", unsafe_allow_html=True)
            st.progress(0.74)
            st.caption("Khối ngoại mua ròng mạnh rổ VN30.")
    with col_sent2:
        news_data = pd.DataFrame({
            "Tin tức nổi bật": [
                "Ngân hàng Nhà nước duy trì chính sách nới lỏng hỗ trợ thanh khoản.",
                "Sản lượng thép Hòa Phát (HPG) đạt kỷ lục trong phiên giao dịch tháng 5.",
                "FPT ký kết hợp đồng AI chiến lược trị giá 50 triệu USD.",
                "VN-Index tiếp cận vùng kháng cự tâm lý 1,300 điểm."
            ],
            "Tác động": ["Tích cực", "Rất tích cực", "Tích cực", "Trung lập"]
        })
        st.dataframe(news_data, use_container_width=True, hide_index=True)

st.markdown("<hr style='margin-top: 1rem; margin-bottom: 2rem;'>", unsafe_allow_html=True)

# ==========================================
# MÁY TÍNH PHÍ 
# ==========================================
if show_calculator:
    st.markdown("#### Mô hình ước tính doanh số chốt lệnh")
    missing_fee = max(0, kpi_targets['monthly_fee'] - my_monthly_fee)
    if missing_fee > 0: st.info(f"Phân tích KPI cá nhân: Bạn cần khai thác thêm {missing_fee:,.0f} VNĐ phí môi giới để hoàn thành chỉ tiêu tháng.")
    else: st.success("Tuyệt vời! Bạn đã vượt chỉ tiêu doanh số phí tháng này.")
        
    with st.container(border=True):
        col_calc1, col_calc2 = st.columns(2)
        with col_calc1:
            val = st.number_input("Giá trị lệnh dự kiến (VNĐ):", min_value=0, value=100000000, step=10000000)
            rate = st.selectbox("Tỷ lệ phí:", [fee_rates["min"], fee_rates["default"], fee_rates["max"]], index=1, format_func=lambda x: f"{x*100}%")
        with col_calc2:
            fee = val * rate
            st.metric("Ước tính phí thu về:", f"{fee:,.0f} VNĐ")
            if missing_fee > 0 and fee > 0:
                st.markdown(f"<span style='color: #ED1C24; font-weight: bold;'>Đề xuất: Cần thực hiện tối thiểu {int(missing_fee / fee) + 1} lệnh tương tự để lấp đầy KPI.</span>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("<br><br>---<br>**CÔNG CỤ ĐIỀU HÀNH**", unsafe_allow_html=True)
    if st.button("Tải lại Kịch bản Demo", use_container_width=True, type="primary"):
        st.session_state.clear()
        st.rerun()
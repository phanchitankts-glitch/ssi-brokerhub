import streamlit as st
import pandas as pd
import yfinance as yf
import base64
import time
from datetime import date
from data.mock_data import calculate_days_since_trade, is_churn_risk
from streamlit_option_menu import option_menu

st.set_page_config(page_title="CRM | SSI BrokerHub", page_icon="assets/logo.png", layout="wide")

if "initialized" not in st.session_state or not st.session_state.logged_in:
    st.warning("Vui lòng quay lại trang chủ để đăng nhập bằng Smart OTP.")
    st.stop()

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

current_user_id = st.session_state.current_broker_id
current_user = next((b for b in st.session_state.brokers if b["id"] == current_user_id), {"name": "Cán bộ SSI"})

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
    with st.popover(notif_label):
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
    with st.popover(msg_label):
        st.markdown("**Trao đổi nội bộ**")
        other_brokers = [b["name"] for b in st.session_state.brokers if b["id"] != current_user_id]
        chat_target = st.selectbox("Tìm đồng nghiệp:", other_brokers, label_visibility="collapsed")
        st.divider()
        history = [m for m in st.session_state.chat_messages if (m["from"] == current_user["name"] and m["to"] == chat_target) or (m["to"] == current_user["name"] and m["from"] == chat_target)]
        chat_container = st.container(height=250)
        with chat_container:
            if not history: st.caption(f"Bắt đầu trò chuyện với {chat_target}.")
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
    with st.popover(current_user['name']):
        st.markdown(f"**{current_user['name']}**")
        st.caption("Trạng thái: Đang hoạt động")
        st.divider()
        if st.button("Xóa hộp thư đến", use_container_width=True):
            st.session_state.chat_messages = [m for m in st.session_state.chat_messages if m["to"] != current_user["name"]]
            st.rerun()
        if st.button("Đăng xuất", type="primary", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.current_broker_id = None
            st.switch_page("app.py")

# ========================================================
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except: return ""

logo_b64 = get_base64_image("assets/logo.png")
bg_style = f"url('data:image/png;base64,{logo_b64}'), linear-gradient(to right, #8B0000, #ED1C24)" if logo_b64 else "linear-gradient(to right, #8B0000, #ED1C24)"

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
    default_index=1,
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
if pages_dict[selected] != "pages/2_Quan_Tri_Danh_Muc.py": st.switch_page(pages_dict[selected])

# ==========================================
# TỪ ĐIỂN MÃ CỔ PHIẾU VÀ HÀM LẤY GIÁ LIVE
# ==========================================
VN_STOCKS = {
    "ACB": "Ngân hàng TMCP Á Châu", "BCM": "Tổng CTCP Đầu tư và Phát triển Công nghiệp", "BID": "Ngân hàng TMCP Đầu tư và Phát triển VN", "BVH": "Tập đoàn Bảo Việt", "CTG": "Ngân hàng TMCP Công Thương VN", "FPT": "Công ty Cổ phần FPT", "GAS": "Tổng Công ty Khí Việt Nam", "GVR": "Tập đoàn Công nghiệp Cao su Việt Nam", "HDB": "Ngân hàng TMCP Phát triển TP.HCM", "HPG": "Công ty Cổ phần Tập đoàn Hòa Phát", "MBB": "Ngân hàng TMCP Quân đội", "MSN": "Công ty Cổ phần Tập đoàn Masan", "MWG": "Công ty Cổ phần Đầu tư Thế Giới Di Động", "PLX": "Tập đoàn Xăng dầu Việt Nam", "POW": "Tổng Công ty Điện lực Dầu khí Việt Nam", "SAB": "Tổng CTCP Bia - Rượu - Nước giải khát Sài Gòn", "SHB": "Ngân hàng TMCP Sài Gòn - Hà Nội", "SSB": "Ngân hàng TMCP Đông Nam Á", "SSI": "Công ty Cổ phần Chứng khoán SSI", "STB": "Ngân hàng TMCP Sài Thương Tín", "TCB": "Ngân hàng TMCP Kỹ thương Việt Nam", "TPB": "Ngân hàng TMCP Tiên Phong", "VCB": "Ngân hàng TMCP Ngoại thương Việt Nam", "VHM": "Công ty Cổ phần Vinhomes", "VIB": "Ngân hàng TMCP Quốc tế Việt Nam", "VIC": "Tập đoàn Vingroup", "VJC": "Công ty Cổ phần Hàng không Vietjet", "VNM": "Công ty Cổ phần Sữa Việt Nam", "VPB": "Ngân hàng TMCP Việt Nam Thịnh Vượng", "VRE": "Công ty Cổ phần Vincom Retail",
    "VND": "CTCP Chứng khoán VNDIRECT", "VCI": "CTCP Chứng khoán Vietcap", "HCM": "CTCP Chứng khoán TP.HCM", "KBC": "Tổng Công ty Phát triển Đô thị Kinh Bắc", "DIG": "Tổng CTCP Đầu tư Phát triển Xây dựng", "NVL": "CTCP Tập đoàn Đầu tư Địa ốc No Va", "PVD": "Tổng CTCP Khoan và Dịch vụ Khoan Dầu khí", "PVS": "Tổng CTCP Dịch vụ Kỹ thuật Dầu khí", "DGC": "CTCP Tập đoàn Hóa chất Đức Giang", "DGW": "CTCP Thế Giới Số", "FRT": "CTCP Bán lẻ Kỹ thuật số FPT", "NKG": "CTCP Thép Nam Kim", "HSG": "CTCP Tập đoàn Hoa Sen", "KDH": "CTCP Đầu tư và Kinh doanh Nhà Khang Điền", "NLG": "CTCP Đầu tư Nam Long", "PC1": "CTCP Tập đoàn PC1", "REE": "CTCP Cơ Điện Lạnh", "VHC": "CTCP Vĩnh Hoàn", "ANV": "CTCP Nam Việt", "GEX": "CTCP Tập đoàn GELEX", "DXG": "CTCP Tập đoàn Đất Xanh", "CEO": "CTCP Tập đoàn C.E.O", "CII": "CTCP Đầu tư Hạ tầng Kỹ thuật TP.HCM", "HHV": "CTCP Đầu tư Hạ tầng Giao thông Đèo Cả", "LCG": "CTCP Lizen", "VCG": "Tổng CTCP Xuất nhập khẩu và Xây dựng VN", "KDC": "CTCP Tập đoàn KIDO", "SBT": "CTCP Thành Thành Công - Biên Hòa", "DBC": "CTCP Tập đoàn Dabaco Việt Nam", "HAG": "CTCP Hoàng Anh Gia Lai", "VIX": "CTCP Chứng khoán VIX", "BSI": "CTCP Chứng khoán BIDV", "CTS": "CTCP Chứng khoán VietinBank", "MBS": "CTCP Chứng khoán MB", "SHS": "CTCP Chứng khoán Sài Gòn - Hà Nội", "EIB": "Ngân hàng TMCP Xuất Nhập khẩu VN", "LPB": "Ngân hàng TMCP Lộc Phát VN", "OCB": "Ngân hàng TMCP Phương Đông", "MSB": "Ngân hàng TMCP Hàng Hải VN", "GMD": "CTCP Gemadept", "PVT": "Tổng CTCP Vận tải Dầu khí", "BSR": "CTCP Lọc hóa dầu Bình Sơn", "OIL": "Tổng Công ty Dầu Việt Nam", "NT2": "CTCP Điện lực Dầu khí Nhơn Trạch 2", "TCH": "CTCP Đầu tư Dịch vụ Tài chính Hoàng Huy", "BCG": "CTCP Tập đoàn Bamboo Capital", "PAN": "CTCP Tập đoàn PAN", "IDC": "Tổng công ty IDICO", "DPR": "CTCP Cao su Đồng Phú", "DRC": "CTCP Cao su Đà Nẵng", "BMP": "CTCP Nhựa Bình Minh", "PTB": "CTCP Phú Tài"
}

@st.cache_data(ttl=120)
def get_live_price(ticker):
    try: return yf.Ticker(f"{ticker}.VN").fast_info['lastPrice']
    except: return 30000.0

if "crm_staging_cart" not in st.session_state:
    st.session_state.crm_staging_cart = []

# ==========================================
# KHU VỰC NGHIỆP VỤ CRM
# ==========================================
current_broker_id = st.session_state.current_broker_id

st.markdown("<h2 style='color: #111827; margin-bottom: 0;'>Hệ thống Quản trị Khách hàng (CRM)</h2>", unsafe_allow_html=True)
st.caption("Quản lý danh mục đầu tư, tích hợp cảnh báo rủi ro và theo dõi hệ sinh thái S-Products.")
st.markdown("---")

my_customers = [c for c in st.session_state.customers if c["broker_id"] == current_broker_id]

# ----------------------------------------------------
# CẬP NHẬT NAV TOÀN BỘ KHÁCH HÀNG TRƯỚC KHI HIỂN THỊ
# ----------------------------------------------------
for c in my_customers:
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
        if c["profit_margin"] > 0: c["performance"] = "green"
        elif c["profit_margin"] > -5: c["performance"] = "yellow"
        else: c["performance"] = "red"

tab1, tab2 = st.tabs(["Báo cáo Danh mục & S-Products", "Khai báo Khách hàng mới"])

with tab1:
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    total_cus = len(my_customers)
    total_asset = sum(c.get("trade_value", 0) for c in my_customers)
    churn_count = sum(1 for c in my_customers if calculate_days_since_trade(c["last_trade_date"]) > 14)
    cross_sell_count = sum(1 for c in my_customers if len(c.get("s_products", [])) > 0)
    
    with col_m1: st.metric("Tổng Khách hàng", f"{total_cus} KH")
    with col_m2: st.metric("Tài sản quản lý (AUM)", f"{total_asset:,.0f} đ")
    with col_m3: st.metric("Tỉ lệ Cross-sell", f"{int((cross_sell_count/total_cus)*100) if total_cus > 0 else 0}%", f"{cross_sell_count} KH đang dùng")
    with col_m4: st.metric("Cảnh báo Churn (>14 ngày)", f"{churn_count} KH", delta="Rủi ro cao", delta_color="inverse")
    
    st.markdown("<br>", unsafe_allow_html=True)

    with st.container(border=True):
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1: filter_status = st.selectbox("Trạng thái", ["Tất cả", "active", "inactive"])
        with col_f2: filter_product = st.selectbox("Lọc theo S-Products", ["Tất cả", "Có dùng S-Products", "Chưa dùng S-Products"])
        with col_f3: 
            st.markdown("<br>", unsafe_allow_html=True)
            show_churn_only = st.checkbox("Chỉ hiển thị rủi ro Churn")

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
        
        port = c.get("portfolio", [])
        c_display["portfolio_label"] = ", ".join([f"{p['ticker']} ({p['volume']:,})" for p in port]) if port else "Tiền mặt"
        
        filtered_customers.append(c_display)

    if filtered_customers:
        df = pd.DataFrame(filtered_customers)
        df = df.sort_values(by="trade_value", ascending=False)
        df = df[["id", "name", "trade_value", "profit_margin", "portfolio_label", "s_products_label", "days_inactive", "status_label"]]
        df.columns = ["ID", "Khách Hàng", "NAV (VNĐ)", "Lãi/Lỗ (%)", "Danh Mục Cổ Phiếu", "Hệ Sinh Thái", "Số ngày chưa GD", "Trạng Thái"]
        
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
            try: styler = styler.map(color_profit, subset=['Lãi/Lỗ (%)']).map(color_products, subset=['Hệ Sinh Thái'])
            except AttributeError: styler = styler.applymap(color_profit, subset=['Lãi/Lỗ (%)']).applymap(color_products, subset=['Hệ Sinh Thái'])
            return styler.format({"NAV (VNĐ)": "{:,.0f}", "Lãi/Lỗ (%)": "{:+.1f}%"})

        st.markdown("##### Chi tiết Danh mục Khách hàng")
        st.dataframe(style_dataframe(df), use_container_width=True, hide_index=True, height=450)
    else:
        st.info("Không tìm thấy dữ liệu khớp với bộ lọc.")

# -------------------------------------------------------------------------
# TAB 2 - FORM KHAI BÁO SẠCH SẼ KHÔNG CÓ EMOJI
# -------------------------------------------------------------------------
with tab2:
    st.markdown("##### Khai báo Khách hàng & Cổ phiếu nắm giữ")
    
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        crm_name = st.text_input("1. Họ và Tên khách hàng (*)", placeholder="VD: Nguyễn Văn Linh")
        crm_phone = st.text_input("2. Số điện thoại (*)", placeholder="098xxxxxxx")
    with col_f2:
        crm_s_prod = st.multiselect("3. Đăng ký S-Products", ["S-BOND", "S-FUND", "S-MARGIN"])
        st.caption("Khách hàng sẽ được tự động định giá theo biến động thị trường thực tế.")

    st.markdown("---")
    st.markdown("**Thêm mã cổ phiếu vào giỏ danh mục của khách**")
    
    sc1, sc2, sc3 = st.columns([2, 1.5, 1])
    with sc1:
        sel_crm_ticker = st.selectbox("Chọn mã chứng khoán niêm yết:", options=list(VN_STOCKS.keys()), key="crm_sel_tk")
    with sc2:
        sel_crm_vol = st.number_input("Khối lượng sở hữu:", min_value=100, step=100, value=1000, key="crm_sel_vol")
    with sc3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Thêm vào giỏ", use_container_width=True):
            price_now = get_live_price(sel_crm_ticker)
            st.session_state.crm_staging_cart.append({
                "ticker": sel_crm_ticker,
                "volume": sel_crm_vol,
                "price": price_now,
                "val": price_now * sel_crm_vol
            })
            st.rerun()

    p_now = get_live_price(sel_crm_ticker)
    st.caption(f"Giá khớp lệnh hiện tại của {sel_crm_ticker}: {p_now:,.0f} VNĐ | Định giá lô này: {p_now * sel_crm_vol:,.0f} VNĐ")

    # Hiển thị giỏ hàng dạng bảng doanh nghiệp chuyên nghiệp
    if st.session_state.crm_staging_cart:
        st.markdown("<br>**Các mã cổ phiếu chuẩn bị gán cho khách hàng:**", unsafe_allow_html=True)
        df_staging = pd.DataFrame(st.session_state.crm_staging_cart)
        df_staging.columns = ["Mã CP", "Khối lượng", "Giá thị trường", "Thành tiền (VNĐ)"]
        st.dataframe(df_staging.style.format({"Khối lượng": "{:,.0f}", "Giá thị trường": "{:,.0f}", "Thành tiền (VNĐ)": "{:,.0f}"}), use_container_width=True)

        total_est_nav = sum(x["val"] for x in st.session_state.crm_staging_cart)
        st.markdown(f"**Tổng định giá danh mục ban đầu (AUM):** <span style='color:#059669; font-size:1.2rem; font-weight:bold;'>{total_est_nav:,.0f} VNĐ</span>", unsafe_allow_html=True)

        col_b1, col_b2 = st.columns([1, 4])
        with col_b1:
            if st.button("Xóa giỏ hàng"):
                st.session_state.crm_staging_cart = []
                st.rerun()
        with col_b2:
            if st.button("HOÀN TẤT LƯU HỒ SƠ KHÁCH HÀNG", type="primary", use_container_width=True):
                if not crm_name.strip() or not crm_phone.strip():
                    st.error("Vui lòng điền đủ Họ tên và Số điện thoại!")
                else:
                    try: demo_dt = st.session_state.demo_date.strftime("%Y-%m-%d")
                    except: demo_dt = date.today().strftime("%Y-%m-%d")
                    
                    try: new_crm_id = max([int(str(c["id"]).replace("C_","")) if str(c["id"]).startswith("C_") else int(c["id"]) if isinstance(c["id"], int) else 999 for c in st.session_state.customers]) + 1
                    except: new_crm_id = len(st.session_state.customers) + 101
                    
                    st.session_state.customers.append({
                        "id": new_crm_id,
                        "name": crm_name.strip(),
                        "phone": crm_phone.strip(),
                        "open_date": demo_dt,
                        "last_trade_date": demo_dt,
                        "trade_value": total_est_nav,
                        "profit_margin": 0.0,
                        "s_products": crm_s_prod,
                        "portfolio": [
                            {
                                "ticker": item["ticker"],
                                "volume": item["volume"],
                                "avg_price": item["price"]
                            }
                            for item in st.session_state.crm_staging_cart
                        ],
                        "status": "active",
                        "broker_id": current_broker_id
                    })
                    st.session_state.crm_staging_cart = []
                    st.success("Đã lưu hồ sơ thành công! Vui lòng chuyển sang Tab Báo cáo để kiểm tra.")
                    time.sleep(1.2)
                    st.rerun()

# Gọi hàm hiển thị chân trang thương hiệu SSI
from data.mock_data import render_footer
render_footer()
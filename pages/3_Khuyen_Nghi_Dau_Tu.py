import streamlit as st
import pandas as pd
import yfinance as yf
import base64
import time 
from datetime import datetime, timedelta
from streamlit_option_menu import option_menu
import plotly.graph_objects as go 

st.set_page_config(page_title="Advisory Hub | SSI BrokerHub", page_icon="assets/logo.png", layout="wide")

if "initialized" not in st.session_state or not st.session_state.logged_in:
    st.warning("Yêu cầu xác thực. Vui lòng quay lại trang chủ để đăng nhập hệ thống.")
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
    default_index=2, 
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
if pages_dict[selected] != "pages/3_Khuyen_Nghi_Dau_Tu.py": st.switch_page(pages_dict[selected])

# ==========================================
# KHU VỰC NGHIỆP VỤ - VN100 UNIVERSE & BIỂU ĐỒ
# ==========================================
st.markdown("<h2 style='color: #000000; margin-bottom: 0px;'>Trung tâm Khuyến nghị đầu tư</h2>", unsafe_allow_html=True)
st.markdown("<p style='color: #6B7280; font-size: 1rem;'>Hỗ trợ môi giới phân tích doanh nghiệp và gửi tín hiệu giao dịch đến khách hàng</p>", unsafe_allow_html=True)

st.markdown("---")

@st.cache_data(ttl=60) 
def get_index_realtime(ticker, fallback_value):
    try:
        idx = yf.Ticker(ticker)
        current_price = idx.fast_info['lastPrice']
        prev_close = idx.fast_info['previousClose']
        change = current_price - prev_close
        pct_change = (change / prev_close) * 100
        change_str = f"{change:+.2f} ({pct_change:+.2f}%)"
        return f"{current_price:,.2f}", change_str
    except:
        return fallback_value, "+15.20 (0.85%)"

with st.spinner("Đang cập nhật chỉ số thị trường..."):
    vni_score, vni_change = get_index_realtime("^VNINDEX", "1,825.45")
    vn30_score, vn30_change = get_index_realtime("^VN30", "1,850.10")

col_idx1, col_idx2, col_idx3, col_idx4 = st.columns(4)
with col_idx1: st.metric("VN-INDEX", vni_score, vni_change)
with col_idx2: st.metric("VN30-INDEX", vn30_score, vn30_change)
with col_idx3: st.metric("HNX-INDEX", "240.20", "2.10 (0.88%)") 
with col_idx4: st.metric("Thanh khoản HOSE", "28,500 Tỷ VNĐ", "Tăng 12%")
st.markdown("---")

VN_STOCKS = {
    "ACB": "Ngân hàng TMCP Á Châu", "BCM": "Tổng CTCP Đầu tư và Phát triển Công nghiệp", "BID": "Ngân hàng TMCP Đầu tư và Phát triển VN", "BVH": "Tập đoàn Bảo Việt", "CTG": "Ngân hàng TMCP Công Thương VN", "FPT": "Công ty Cổ phần FPT", "GAS": "Tổng Công ty Khí Việt Nam", "GVR": "Tập đoàn Công nghiệp Cao su Việt Nam", "HDB": "Ngân hàng TMCP Phát triển TP.HCM", "HPG": "Công ty Cổ phần Tập đoàn Hòa Phát", "MBB": "Ngân hàng TMCP Quân đội", "MSN": "Công ty Cổ phần Tập đoàn Masan", "MWG": "Công ty Cổ phần Đầu tư Thế Giới Di Động", "PLX": "Tập đoàn Xăng dầu Việt Nam", "POW": "Tổng Công ty Điện lực Dầu khí Việt Nam", "SAB": "Tổng CTCP Bia - Rượu - Nước giải khát Sài Gòn", "SHB": "Ngân hàng TMCP Sài Gòn - Hà Nội", "SSB": "Ngân hàng TMCP Đông Nam Á", "SSI": "Công ty Cổ phần Chứng khoán SSI", "STB": "Ngân hàng TMCP Sài Thương Tín", "TCB": "Ngân hàng TMCP Kỹ thương Việt Nam", "TPB": "Ngân hàng TMCP Tiên Phong", "VCB": "Ngân hàng TMCP Ngoại thương Việt Nam", "VHM": "Công ty Cổ phần Vinhomes", "VIB": "Ngân hàng TMCP Quốc tế Việt Nam", "VIC": "Tập đoàn Vingroup", "VJC": "Công ty Cổ phần Hàng không Vietjet", "VNM": "Công ty Cổ phần Sữa Việt Nam", "VPB": "Ngân hàng TMCP Việt Nam Thịnh Vượng", "VRE": "Công ty Cổ phần Vincom Retail",
    "VND": "CTCP Chứng khoán VNDIRECT", "VCI": "CTCP Chứng khoán Vietcap", "HCM": "CTCP Chứng khoán TP.HCM", "KBC": "Tổng Công ty Phát triển Đô thị Kinh Bắc", "DIG": "Tổng CTCP Đầu tư Phát triển Xây dựng", "NVL": "CTCP Tập đoàn Đầu tư Địa ốc No Va", "PVD": "Tổng CTCP Khoan và Dịch vụ Khoan Dầu khí", "PVS": "Tổng CTCP Dịch vụ Kỹ thuật Dầu khí", "DGC": "CTCP Tập đoàn Hóa chất Đức Giang", "DGW": "CTCP Thế Giới Số", "FRT": "CTCP Bán lẻ Kỹ thuật số FPT", "NKG": "CTCP Thép Nam Kim", "HSG": "CTCP Tập đoàn Hoa Sen", "KDH": "CTCP Đầu tư và Kinh doanh Nhà Khang Điền", "NLG": "CTCP Đầu tư Nam Long", "PC1": "CTCP Tập đoàn PC1", "REE": "CTCP Cơ Điện Lạnh", "VHC": "CTCP Vĩnh Hoàn", "ANV": "CTCP Nam Việt", "GEX": "CTCP Tập đoàn GELEX", "HDG": "CTCP Tập đoàn Hà Đô", "DXG": "CTCP Tập đoàn Đất Xanh", "CEO": "CTCP Tập đoàn C.E.O", "CII": "CTCP Đầu tư Hạ tầng Kỹ thuật TP.HCM", "HHV": "CTCP Đầu tư Hạ tầng Giao thông Đèo Cả", "LCG": "CTCP Lizen", "VCG": "Tổng CTCP Xuất nhập khẩu và Xây dựng VN", "FCN": "CTCP Fecon", "KDC": "CTCP Tập đoàn KIDO", "SBT": "CTCP Thành Thành Công - Biên Hòa", "DBC": "CTCP Tập đoàn Dabaco Việt Nam", "HAG": "CTCP Hoàng Anh Gia Lai", "ASM": "CTCP Tập đoàn Sao Mai", "IDI": "CTCP Đầu tư và Phát triển Đa Quốc Gia", "VIX": "CTCP Chứng khoán VIX", "BSI": "CTCP Chứng khoán BIDV", "CTS": "CTCP Chứng khoán VietinBank", "MBS": "CTCP Chứng khoán MB", "SHS": "CTCP Chứng khoán Sài Gòn - Hà Nội", "EIB": "Ngân hàng TMCP Xuất Nhập khẩu VN", "LPB": "Ngân hàng TMCP Lộc Phát VN", "OCB": "Ngân hàng TMCP Phương Đông", "MSB": "Ngân hàng TMCP Hàng Hải VN", "NAB": "Ngân hàng TMCP Nam Á", "VSC": "CTCP Tập đoàn Container VN", "HAH": "CTCP Vận tải và Xếp dỡ Hải An", "GMD": "CTCP Gemadept", "PVT": "Tổng CTCP Vận tải Dầu khí", "BSR": "CTCP Lọc hóa dầu Bình Sơn", "OIL": "Tổng Công ty Dầu Việt Nam", "NT2": "CTCP Điện lực Dầu khí Nhơn Trạch 2", "QTP": "CTCP Nhiệt điện Quảng Ninh", "GEG": "CTCP Điện Gia Lai", "TCH": "CTCP Đầu tư Dịch vụ Tài chính Hoàng Huy", "HUT": "CTCP Tasco", "BCG": "CTCP Tập đoàn Bamboo Capital", "PAN": "CTCP Tập đoàn PAN", "LTG": "CTCP Tập đoàn Lộc Trời", "TAR": "CTCP Nông nghiệp Công nghệ cao Trung An", "SZC": "CTCP Sonadezi Châu Đức", "IDC": "Tổng công ty IDICO", "PHR": "CTCP Cao Phương Hòa", "DPR": "CTCP Cao su Đồng Phú", "DRC": "CTCP Cao su Đà Nẵng", "CSM": "CTCP Công nghiệp Cao su Miền Nam", "AAA": "CTCP Nhựa An Phát Xanh", "APH": "CTCP Tập đoàn An Phát Holdings", "BMP": "CTCP Nhựa Bình Minh", "NTP": "CTCP Nhựa Thiếu niên Tiền Phong", "PTB": "CTCP Phú Tài"
}

col_main1, col_main2 = st.columns([1.2, 2])

with col_main1:
    with st.container(border=True):
        st.markdown("**Lựa chọn danh mục phân tích**")
        selected_ticker = st.selectbox("Mã cổ phiếu niêm yết:", options=list(VN_STOCKS.keys()))
        company_name = VN_STOCKS[selected_ticker]
        
        real_price = 0
        df_historical = None
        
        with st.spinner("Đang đồng bộ dữ liệu Real-time & Chart..."):
            try:
                stock = yf.Ticker(f"{selected_ticker}.VN")
                df_historical = stock.history(period="6mo")
                
                try:
                    real_price = stock.fast_info['lastPrice']
                except:
                    if not df_historical.empty:
                        real_price = df_historical['Close'].iloc[-1]
                    else:
                        real_price = 0
                
                price_display = f"{real_price:,.0f} VNĐ" if real_price else "Chờ cập nhật"
                
                # --- ĐẨY GIÁ SANG BỘ NHỚ CHUNG CHO TRANG 2 DÙNG ---
                if real_price:
                    found = False
                    for s in st.session_state.stocks:
                        if s["ticker"] == selected_ticker:
                            s["current_price"] = real_price
                            found = True
                            break
                    if not found:
                        st.session_state.stocks.append({"ticker": selected_ticker, "current_price": real_price})
                # --------------------------------------------------

                info = stock.info
                try:
                    r_roe = info.get('returnOnEquity')
                    real_roe = f"{float(r_roe) * 100:.1f}%" if r_roe else "N/A"
                except: real_roe = "N/A"
                
                try:
                    r_eps = info.get('trailingEps')
                    real_eps = f"{float(r_eps):,.0f} VNĐ" if r_eps else "N/A"
                except: real_eps = "N/A"
                
                try:
                    r_pe = info.get('trailingPE')
                    real_pe = f"{float(r_pe):.1f}x" if r_pe else "N/A"
                except: real_pe = "N/A"
                
                if not df_historical.empty and len(df_historical) >= 15:
                    close_prices = df_historical['Close']
                    delta = close_prices.diff()
                    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                    rs = gain / loss
                    rsi = 100 - (100 / (1 + rs.iloc[-1]))
                    real_rsi = f"{rsi:.1f}"
                else:
                    real_rsi = "N/A"
                    
            except Exception as e:
                print(f"Lỗi API: {e}")
                price_display = "Lỗi API / Đóng cửa"
                real_roe = real_eps = real_pe = real_rsi = "N/A"
                real_price = 0

        st.markdown(f"**Giá khớp lệnh Real-time:** <span style='color: #10B981; font-size: 1.3rem; font-weight: bold;'>{price_display}</span>", unsafe_allow_html=True)
        current_time = datetime.now().strftime("%H:%M:%S - %d/%m/%Y")
        st.caption(f"Dữ liệu cơ bản cập nhật lúc: {current_time}")

with col_main2:
    if df_historical is not None and not df_historical.empty:
        fig = go.Figure(data=[go.Candlestick(
            x=df_historical.index, open=df_historical['Open'], high=df_historical['High'],
            low=df_historical['Low'], close=df_historical['Close'],
            increasing_line_color='#10B981', decreasing_line_color='#ED1C24'
        )])
        fig.update_layout(
            title=f"Biểu đồ biến động giá 6 tháng - {selected_ticker}", yaxis_title="Giá (VNĐ)",
            xaxis_rangeslider_visible=False, height=300, margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Chưa thể tải dữ liệu biểu đồ từ máy chủ vào lúc này.")

if real_rsi != "N/A":
    rsi_val = float(real_rsi)
    if rsi_val > 70:
        mock_volume = "Áp lực chốt lời gia tăng (Quá mua)"
        mock_thesis = f"Cổ phiếu {selected_ticker} đang đi vào vùng quá mua kỹ thuật (RSI > 70). Động lượng tăng có thể suy yếu trong ngắn hạn. Khuyến nghị thận trọng với việc giải ngân mới."
        action_choice = 2 
    elif rsi_val < 30:
        mock_volume = "Tích lũy cạn cung (Quá bán)"
        mock_thesis = f"{selected_ticker} đã chiết khấu sâu về vùng định giá hấp dẫn (RSI < 30). Áp lực bán cạn kiệt, tín hiệu quá bán mở ra cơ hội bắt đáy cho nhịp hồi phục."
        action_choice = 0 
    else:
        mock_volume = "Duy trì mức trung bình 20 phiên"
        mock_thesis = f"{selected_ticker} đang duy trì nền giá ổn định. Dòng tiền luân chuyển tốt. Vùng giá hiện tại phù hợp để gia tăng tỷ trọng theo chiều hướng thị trường chung."
        action_choice = 1 
else:
    mock_volume = "Chờ cập nhật"
    mock_thesis = "Đang thu thập thêm dữ liệu thị trường để đưa ra nhận định..."
    action_choice = 2

if real_price > 0:
    buy_zone = f"{real_price * 0.98:,.0f} - {real_price * 1.02:,.0f}"
    target = f"{real_price * 1.15:,.0f}"   
    cutloss = f"{real_price * 0.93:,.0f}"  
else:
    buy_zone = target = cutloss = "Đang chờ cập nhật"

st.markdown(f"### Phân tích chi tiết: {selected_ticker} - {company_name}")

col_f1, col_f2, col_f3, col_f4 = st.columns(4)
with col_f1: st.metric("Chỉ số ROE", real_roe)
with col_f2: st.metric("EPS (Trượt)", real_eps)
with col_f3: st.metric("P/E Forward", real_pe)
with col_f4: st.metric("Chỉ số RSI (14)", real_rsi)

st.markdown("<br>", unsafe_allow_html=True)

col_body1, col_body2 = st.columns([2, 1])

with col_body1:
    with st.container(border=True):
        st.markdown("**Luận điểm đầu tư (Dựa trên dữ liệu Real-time)**")
        st.write(mock_thesis)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**Trạng thái dòng tiền (Volume Analysis)**")
        st.info(mock_volume)

with col_body2:
    with st.container(border=True):
        st.markdown("**Vùng giá khuyến nghị**")
        st.markdown(f"Vùng mua: <span style='color: #10B981; font-weight: bold;'>{buy_zone}</span>", unsafe_allow_html=True)
        st.markdown(f"Giá mục tiêu: <span style='color: #000000; font-weight: bold;'>{target}</span>", unsafe_allow_html=True)
        st.markdown(f"Giá cắt lỗ: <span style='color: #ED1C24; font-weight: bold;'>{cutloss}</span>", unsafe_allow_html=True)
        
        st.divider()
        st.markdown("**Xác nhận hành động**")
        action = st.radio("Khuyến nghị:", ["MUA TÍCH LŨY", "MUA GIA TĂNG", "THEO DÕI"], index=action_choice, label_visibility="collapsed")

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("#### Hệ thống Push Tín hiệu & Trợ lý Soạn thảo")

auto_draft = f"Kính gửi Quý khách hàng,\n\nHệ thống Phân tích SSI BrokerHub cập nhật tín hiệu kỹ thuật cho mã cổ phiếu {selected_ticker} ({company_name}).\n"
auto_draft += f"- Giá thị trường hiện tại: {price_display}\n"
auto_draft += f"- Vùng giá giải ngân an toàn: {buy_zone}\n"
auto_draft += f"- Định giá mục tiêu: {target} | Ngưỡng cắt lỗ: {cutloss}\n\n"
auto_draft += f"Luận điểm đầu tư: {mock_thesis} Dòng tiền hiện tại đang cho thấy dấu hiệu {mock_volume.lower()}.\n\n"
auto_draft += f"Hành động khuyến nghị: {action}.\n\nTrân trọng,"

message_content = st.text_area("Nội dung kịch bản tư vấn:", value=auto_draft, height=220)

my_customers = [c for c in st.session_state.customers if c["broker_id"] == current_user_id]
df_customers = pd.DataFrame(my_customers)

if not df_customers.empty:
    selected_customers = st.multiselect("Chọn khách hàng nhận thông báo:", options=df_customers["name"].tolist(), default=df_customers["name"].tolist())
    if st.button("Xác nhận gửi tín hiệu Smart OTP", type="primary"):
        if selected_customers: st.success(f"Yêu cầu thành công: Đã gửi thông báo khuyến nghị {selected_ticker} đến {len(selected_customers)} khách hàng qua ứng dụng SSI iBoard Pro.")
        else: st.error("Lỗi: Vui lòng lựa chọn ít nhất một khách hàng.")
else:
    st.info("Hệ thống chưa ghi nhận danh sách khách hàng thuộc quyền quản lý của bạn.")

with st.sidebar:
    st.markdown("---")
    st.markdown("**CÔNG CỤ REAL-TIME**")
    live_mode = st.toggle("🔴 Chế độ Live Bảng Điện (Refresh 15s)", value=False)
    st.markdown("---")
    st.markdown("**QUẢN TRỊ NỘI DUNG**")
    st.caption("Dữ liệu giá Real-time được đồng bộ qua Yahoo Finance. Báo cáo phân tích được cung cấp bởi SSI Research Center.")

if live_mode:
    time.sleep(15)
    st.rerun()
# Gọi hàm hiển thị chân trang thương hiệu SSI
from data.mock_data import render_footer
render_footer()
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import base64
import random
from streamlit_option_menu import option_menu

st.set_page_config(page_title="Đánh giá Nội bộ | SSI BrokerHub", page_icon="assets/logo.png", layout="wide")

if "initialized" not in st.session_state or getattr(st.session_state, 'logged_in', False) == False:
    st.warning("Vui lòng quay lại trang chủ để đăng nhập.")
    st.stop()

current_user_id = st.session_state.current_broker_id
brokers = st.session_state.get("brokers", [])
current_user = next((b for b in brokers if b["id"] == current_user_id), {"name": "Cán bộ SSI"})

if "notifications" not in st.session_state:
    st.session_state.notifications = [
        {"id": 1, "text": "Phòng HR: Mở cổng đánh giá hiệu suất Tháng 6/2026", "done": False}
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
    default_index=5, 
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
if pages_dict[selected] != "pages/6_Danh_Gia_Noi_Bo.py": st.switch_page(pages_dict[selected])

if "evaluations" not in st.session_state:
    evals = []
    past_months = ["Tháng 1/2026", "Tháng 2/2026", "Tháng 3/2026", "Tháng 4/2026", "Tháng 5/2026"]
    
    random.seed(123) 
    
    for m in past_months:
        for target_b in brokers:
            for evaluator_b in brokers:
                eval_type = "Tự đánh giá" if target_b["id"] == evaluator_b["id"] else "Đánh giá chéo"
                evals.append({
                    "Kỳ đánh giá": m,
                    "target_id": target_b["id"],
                    "evaluator_id": evaluator_b["id"],
                    "Loại": eval_type,
                    "Chuyên môn": random.randint(6, 10),
                    "Tư vấn": random.randint(6, 10),
                    "Làm việc nhóm": random.randint(7, 10),
                    "Kỷ luật": random.randint(8, 10)
                })
    st.session_state.evaluations = evals

st.markdown("<h2 style='color: #000000; margin-bottom: 0px;'>Đánh giá Nội bộ</h2>", unsafe_allow_html=True)
st.markdown("<p style='color: #6B7280; font-size: 1rem;'>Phân hệ quản lý và tổng hợp kết quả đánh giá năng lực nhân sự định kỳ.</p>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["Tổng hợp kết quả đánh giá", "Thực hiện đánh giá (Tháng hiện tại)"])

with tab1:
    df_evals = pd.DataFrame(st.session_state.evaluations)
    
    df_evals['Điểm tổng hợp'] = df_evals[['Chuyên môn', 'Tư vấn', 'Làm việc nhóm', 'Kỷ luật']].mean(axis=1)
    
    col_filter1, col_filter2 = st.columns([1, 3])
    with col_filter1:
        month_options = ["Tất cả các tháng"] + list(df_evals["Kỳ đánh giá"].unique())
        selected_month = st.selectbox("Lựa chọn kỳ báo cáo:", month_options, index=len(month_options)-1)
    
    if selected_month != "Tất cả các tháng":
        df_filtered = df_evals[df_evals["Kỳ đánh giá"] == selected_month]
    else:
        df_filtered = df_evals.copy()
        
    df_summary = df_filtered.groupby('target_id').agg(
        Số_phiếu=('evaluator_id', 'count'),
        Chuyên_môn=('Chuyên môn', 'mean'),
        Tư_vấn=('Tư vấn', 'mean'),
        Làm_việc_nhóm=('Làm việc nhóm', 'mean'),
        Kỷ_luật=('Kỷ luật', 'mean'),
        Điểm_tổng_hợp=('Điểm tổng hợp', 'mean')
    ).reset_index()
    
    broker_dict = {b["id"]: b["name"] for b in brokers}
    df_summary['Tên nhân sự'] = df_summary['target_id'].map(broker_dict)
    
    df_display = df_summary[['Tên nhân sự', 'Số_phiếu', 'Chuyên_môn', 'Tư_vấn', 'Làm_việc_nhóm', 'Kỷ_luật', 'Điểm_tổng_hợp']].copy()
    df_display.columns = ['Tên nhân sự', 'Số lượng phiếu', 'Chuyên môn', 'Kỹ năng tư vấn', 'Làm việc nhóm', 'Tuân thủ kỷ luật', 'Điểm tổng hợp']
    df_display = df_display.sort_values(by="Điểm tổng hợp", ascending=False)
    
    st.markdown("#### Bảng điểm hiệu suất nhân sự")
    st.dataframe(
        df_display.style.format({
            "Chuyên môn": "{:.1f}", "Kỹ năng tư vấn": "{:.1f}", 
            "Làm việc nhóm": "{:.1f}", "Tuân thủ kỷ luật": "{:.1f}", "Điểm tổng hợp": "{:.2f}"
        }).background_gradient(subset=["Điểm tổng hợp"], cmap="Reds", vmin=6, vmax=10),
        use_container_width=True, hide_index=True
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### Báo cáo phân tích trực quan")
    
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.markdown("**So sánh hiệu suất phòng (Điểm tổng hợp)**")
        fig_bar = px.bar(df_display, x="Tên nhân sự", y="Điểm tổng hợp", text_auto=".2f")
        colors = ['#ED1C24' if name == current_user['name'] else '#D1D5DB' for name in df_display['Tên nhân sự']]
        fig_bar.update_traces(marker_color=colors, textfont_size=12, textposition="outside", cliponaxis=False)
        fig_bar.update_layout(yaxis=dict(range=[0, 11]), margin=dict(t=20, b=0, l=0, r=0), height=350, xaxis_title="", yaxis_title="Điểm (Thang 10)")
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_chart2:
        # LƯỢC BỎ TIẾNG ANH: (Radar)
        st.markdown("**Định vị năng lực cá nhân**")
        metrics = ['Chuyên môn', 'Kỹ năng tư vấn', 'Làm việc nhóm', 'Tuân thủ kỷ luật']
        
        my_stats = df_display[df_display["Tên nhân sự"] == current_user['name']]
        team_avg = df_display.mean(numeric_only=True)
        
        fig_radar = go.Figure()
        if not my_stats.empty:
            my_scores = my_stats[metrics].values[0].tolist()
            fig_radar.add_trace(go.Scatterpolar(r=my_scores, theta=metrics, fill='toself', name='Điểm của bạn', line_color='#ED1C24'))
        
        team_scores = team_avg[metrics].tolist()
        fig_radar.add_trace(go.Scatterpolar(r=team_scores, theta=metrics, fill='toself', name='Trung bình phòng', line_color='#6B7280'))
        
        fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 10])), showlegend=True, margin=dict(t=20, b=0, l=0, r=0), height=350)
        st.plotly_chart(fig_radar, use_container_width=True)

    st.markdown("**Theo dõi phong độ cá nhân theo thời gian**")
    my_history = df_evals[df_evals["target_id"] == current_user_id].groupby("Kỳ đánh giá")["Điểm tổng hợp"].mean().reset_index()
    my_history['month_num'] = my_history['Kỳ đánh giá'].str.extract(r'(\d+)').astype(int)
    my_history = my_history.sort_values("month_num")
    
    fig_line = px.line(my_history, x="Kỳ đánh giá", y="Điểm tổng hợp", markers=True)
    fig_line.update_traces(line_color='#10B981', marker=dict(size=8, color='#ED1C24'))
    fig_line.update_layout(yaxis=dict(range=[5, 10.5]), margin=dict(t=10, b=0, l=0, r=0), height=250, xaxis_title="", yaxis_title="Điểm trung bình")
    st.plotly_chart(fig_line, use_container_width=True)

with tab2:
    current_period = "Tháng 6/2026"
    st.info(f"Kỳ đánh giá hiện tại: **{current_period}** (Thang điểm chuẩn: 1 - 10)")
    
    already_submitted = any(e for e in st.session_state.evaluations if e["evaluator_id"] == current_user_id and e["Kỳ đánh giá"] == current_period)
    
    if already_submitted:
        st.success("Hệ thống đã ghi nhận phiếu đánh giá của bạn cho kỳ này. Xin cảm ơn!")
    else:
        with st.form("evaluation_form"):
            st.markdown("### I. Tự đánh giá cá nhân")
            st.caption("Đánh giá trung thực về hiệu suất công việc của bản thân trong tháng.")
            col_s1, col_s2, col_s3, col_s4 = st.columns(4)
            self_cm = col_s1.number_input("Chuyên môn nghiệp vụ", 1, 10, 8, key="s_cm")
            self_tv = col_s2.number_input("Kỹ năng tư vấn", 1, 10, 8, key="s_tv")
            self_tw = col_s3.number_input("Tinh thần làm việc nhóm", 1, 10, 8, key="s_tw")
            self_kl = col_s4.number_input("Tuân thủ kỷ luật", 1, 10, 8, key="s_kl")
            
            st.markdown("---")
            
            st.markdown("### II. Đánh giá chéo đồng nghiệp")
            st.caption("Nhận xét mang tính xây dựng cho các thành viên khác trong phòng. Kết quả sẽ được hệ thống tổng hợp ẩn danh.")
            
            peer_results = {}
            other_brokers = [b for b in brokers if b["id"] != current_user_id]
            
            for ob in other_brokers:
                st.markdown(f"**Nhân sự: {ob['name']}**")
                p1, p2, p3, p4 = st.columns(4)
                peer_results[ob["id"]] = {
                    "cm": p1.number_input("Chuyên môn", 1, 10, 8, key=f"p_cm_{ob['id']}"),
                    "tv": p2.number_input("Kỹ năng tư vấn", 1, 10, 8, key=f"p_tv_{ob['id']}"),
                    "tw": p3.number_input("Làm việc nhóm", 1, 10, 8, key=f"p_tw_{ob['id']}"),
                    "kl": p4.number_input("Tuân thủ kỷ luật", 1, 10, 8, key=f"p_kl_{ob['id']}")
                }
                st.markdown("<br>", unsafe_allow_html=True)
            
            submit_btn = st.form_submit_button("Lưu và Gửi đánh giá", type="primary")
            
            if submit_btn:
                new_records = []
                
                new_records.append({
                    "Kỳ đánh giá": current_period, "target_id": current_user_id, "evaluator_id": current_user_id,
                    "Loại": "Tự đánh giá", "Chuyên môn": self_cm, "Tư vấn": self_tv, "Làm việc nhóm": self_tw, "Kỷ luật": self_kl
                })
                
                for target_id, scores in peer_results.items():
                    new_records.append({
                        "Kỳ đánh giá": current_period, "target_id": target_id, "evaluator_id": current_user_id,
                        "Loại": "Đánh giá chéo", "Chuyên môn": scores["cm"], "Tư vấn": scores["tv"], "Làm việc nhóm": scores["tw"], "Kỷ luật": scores["kl"]
                    })
                
                st.session_state.evaluations.extend(new_records)
                st.rerun()

try:
    from data.mock_data import render_footer
    render_footer()
except Exception:
    pass
import streamlit as st
import pandas as pd
from datetime import date
from data.mock_data import calculate_days_since_trade, is_churn_risk

st.set_page_config(page_title="CRM | SSI BrokerHub", page_icon="assets/logo.png", layout="wide")

if "initialized" not in st.session_state or not st.session_state.logged_in:
    st.warning("Vui lòng quay lại trang chủ để đăng nhập bằng Smart OTP.")
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
with menu_cols[0]: st.page_link("pages/1_Khong_Gian_Dieu_Hanh.py", label="Không Gian Điều Hành")
with menu_cols[1]: st.page_link("pages/2_Quan_Tri_Danh_Muc.py", label="Quản Trị Danh Mục")
with menu_cols[2]: st.page_link("pages/3_Khuyen_Nghi_Dau_Tu.py", label="Khuyến Nghị Đầu Tư")
with menu_cols[3]: st.page_link("pages/4_Theo_Doi_KPI.py", label="Theo Dõi KPI")
with menu_cols[4]: st.page_link("pages/5_Nhat_Ky_Van_Hanh.py", label="Nhật Ký Vận Hành")
with menu_cols[5]: st.page_link("pages/6_Danh_Gia_Noi_Bo.py", label="Đánh Giá Nội Bộ")
st.markdown("---")

# --- ĐỊNH NGHĨA BIẾN current_broker_id ĐỂ SỬA LỖI ---
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
    # Đếm số lượng KH có sử dụng ít nhất 1 S-Product
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
        # Lọc Trạng thái
        if filter_status != "Tất cả" and c["status"] != filter_status: continue
        # Lọc Churn
        if show_churn_only and not is_churn_risk(c): continue
        # Lọc S-Products
        has_product = len(c.get("s_products", [])) > 0
        if filter_product == "Có dùng S-Products" and not has_product: continue
        if filter_product == "Chưa dùng S-Products" and has_product: continue
        
        c_display = c.copy()
        c_display["days_inactive"] = calculate_days_since_trade(c["last_trade_date"])
        c_display["status_label"] = status_map.get(c["status"], c["status"])
        
        # Tạo chuỗi hiển thị Tag S-Products
        s_prod_list = c.get("s_products", [])
        c_display["s_products_label"] = " • ".join(s_prod_list) if s_prod_list else "---"
        
        # Đảm bảo có trường profit_margin (nếu data thiếu thì mặc định 0)
        c_display["profit_margin"] = c.get("profit_margin", 0.0)
        
        filtered_customers.append(c_display)

    if filtered_customers:
        df = pd.DataFrame(filtered_customers)
        df = df.sort_values(by="trade_value", ascending=False)
        
        # Chọn các cột cần thiết
        df = df[["id", "name", "trade_value", "profit_margin", "s_products_label", "days_inactive", "status_label"]]
        df.columns = ["ID", "Khách Hàng", "NAV (VNĐ)", "Lãi/Lỗ (%)", "Hệ sinh thái S-Products", "Số ngày chưa GD", "Trạng Thái"]
        
        # --- HÀM TÔ MÀU (PANDAS STYLER) ---
        def style_dataframe(data):
            # Tô màu nền nguyên dòng nếu Churn
            def highlight_churn_row(row):
                if row["Số ngày chưa GD"] > 14: return ['background-color: #FEE2E2'] * len(row)
                return [''] * len(row)
            
            # Tô màu chữ Lãi (Xanh) / Lỗ (Đỏ)
            def color_profit(val):
                if val > 0: return 'color: #059669; font-weight: bold;'
                elif val < 0: return 'color: #DC2626; font-weight: bold;'
                return 'color: #4B5563;'
            
            # Tô màu text cho Tag S-Products
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
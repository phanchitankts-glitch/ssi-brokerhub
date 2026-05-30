# data/mock_data.py
# ============================================================
# mock_data.py — Toàn bộ dữ liệu giả của hệ thống SSI BrokerHub
#
# TV4 phụ trách : phần STOCKS (8 mã cổ phiếu)
# TV5 phụ trách : phần BROKERS + CUSTOMERS (20 khách hàng)
# TV6 phụ trách : file scenario_day25.py riêng (dựa trên file này)
#
# LƯU Ý: Không ai được sửa file này ngoài TV4 và TV5.
# Mọi thay đổi cần thông báo cho TV1 để cập nhật session_state.
# ============================================================

from datetime import date

# ============================================================
# NGÀY DEMO CỐ ĐỊNH — KHÔNG DÙNG date.today()
# ============================================================
DEMO_DATE = date.fromisoformat("2025-05-25")  

# ============================================================
# HẰNG SỐ — Chỉ tiêu KPI và tỷ lệ phí
# ============================================================
KPI_TARGETS = {
    "customers": 20,
    "active_accounts": 10,
    "monthly_fee": 6_000_000
}

FEE_RATES = {
    "min": 0.0015,
    "max": 0.0025,
    "default": 0.0015
}

CHURN_THRESHOLD_DAYS = 14

# ============================================================
# BROKERS — 6 thành viên đóng vai môi giới (Đã nâng cấp)
# ============================================================
brokers = [
    {"id": 1, "name": "Phan Chí Tấn", "avatar": "PT", "fee": {"month1": 5_800_000, "month2": 6_200_000, "month3": 5_000_000}},
    {"id": 2, "name": "Nguyễn Hồ Xuân Thùy", "avatar": "XT", "fee": {"month1": 6_100_000, "month2": 5_900_000, "month3": 5_000_000}},
    {"id": 3, "name": "Cao Tường Vy", "avatar": "TV", "fee": {"month1": 5_500_000, "month2": 6_300_000, "month3": 5_000_000}},
    {"id": 4, "name": "Nguyễn Ngọc Thanh Ngân", "avatar": "TN", "fee": {"month1": 6_000_000, "month2": 5_700_000, "month3": 5_000_000}},
    {"id": 5, "name": "Nguyễn Quang Huy", "avatar": "QH", "fee": {"month1": 5_900_000, "month2": 6_100_000, "month3": 5_000_000}},
    {"id": 6, "name": "Lê Phước Tính", "avatar": "PT", "fee": {"month1": 5_200_000, "month2": 5_500_000, "month3": 5_000_000}}
]

# ============================================================
# CUSTOMERS — 20 khách hàng giả định
# (Đã bổ sung profit_margin và s_products, giữ nguyên trade_value để khớp toán)
# ============================================================
customers = [
    # ── NHÓM ACTIVE (10 khách) ──────────────────────────────
    {"id": 1, "name": "Nguyễn Văn An", "phone": "090xxxxxxx", "open_date": "2025-01-15", "last_trade_date": "2025-05-20", "trade_value": 260_000_000, "performance": "green", "status": "active", "broker_id": 1, "profit_margin": 8.5, "s_products": ["S-BOND"]},
    {"id": 2, "name": "Trần Thị Bích", "phone": "091xxxxxxx", "open_date": "2025-01-20", "last_trade_date": "2025-05-18", "trade_value": 210_000_000, "performance": "green", "status": "active", "broker_id": 1, "profit_margin": 6.2, "s_products": []},
    {"id": 3, "name": "Lê Hoàng Cường", "phone": "093xxxxxxx", "open_date": "2025-02-01", "last_trade_date": "2025-05-22", "trade_value": 360_000_000, "performance": "green", "status": "active", "broker_id": 5, "profit_margin": 12.0, "s_products": ["S-FUND", "S-BOND"]},
    {"id": 4, "name": "Phạm Thị Dung", "phone": "094xxxxxxx", "open_date": "2025-02-10", "last_trade_date": "2025-05-19", "trade_value": 160_000_000, "performance": "yellow", "status": "active", "broker_id": 2, "profit_margin": 1.5, "s_products": []},
    {"id": 5, "name": "Hoàng Văn Em", "phone": "096xxxxxxx", "open_date": "2025-02-15", "last_trade_date": "2025-05-21", "trade_value": 310_000_000, "performance": "green", "status": "active", "broker_id": 2, "profit_margin": 9.3, "s_products": ["S-BOND"]},
    {"id": 6, "name": "Vũ Thị Phương", "phone": "097xxxxxxx", "open_date": "2025-02-20", "last_trade_date": "2025-05-17", "trade_value": 230_000_000, "performance": "green", "status": "active", "broker_id": 6, "profit_margin": 5.5, "s_products": []},
    {"id": 7, "name": "Đặng Minh Quân", "phone": "098xxxxxxx", "open_date": "2025-03-01", "last_trade_date": "2025-05-20", "trade_value": 280_000_000, "performance": "green", "status": "active", "broker_id": 3, "profit_margin": 7.1, "s_products": ["S-FUND"]},
    {"id": 8, "name": "Bùi Thị Hoa", "phone": "099xxxxxxx", "open_date": "2025-03-05", "last_trade_date": "2025-05-16", "trade_value": 175_000_000, "performance": "yellow", "status": "active", "broker_id": 3, "profit_margin": 0.5, "s_products": []},
    {"id": 9, "name": "Ngô Văn Khải", "phone": "086xxxxxxx", "open_date": "2025-03-10", "last_trade_date": "2025-05-23", "trade_value": 330_000_000, "performance": "green", "status": "active", "broker_id": 4, "profit_margin": 14.2, "s_products": ["S-BOND"]},
    {"id": 10, "name": "Đinh Thị Lan", "phone": "085xxxxxxx", "open_date": "2025-03-15", "last_trade_date": "2025-05-19", "trade_value": 195_000_000, "performance": "green", "status": "active", "broker_id": 4, "profit_margin": 6.8, "s_products": []},

    # ── NHÓM INACTIVE (8 khách) ─────────────────────────────
    {"id": 11, "name": "Trương Văn Minh", "phone": "083xxxxxxx", "open_date": "2025-01-25", "last_trade_date": "2025-05-12", "trade_value": 120_000_000, "performance": "red", "status": "inactive", "broker_id": 1, "profit_margin": -5.2, "s_products": ["S-FUND"]},
    {"id": 12, "name": "Lý Thị Ngọc", "phone": "082xxxxxxx", "open_date": "2025-02-05", "last_trade_date": "2025-05-11", "trade_value": 90_000_000, "performance": "red", "status": "inactive", "broker_id": 5, "profit_margin": -8.0, "s_products": []},
    {"id": 13, "name": "Phan Văn Ổn", "phone": "081xxxxxxx", "open_date": "2025-02-12", "last_trade_date": "2025-05-13", "trade_value": 150_000_000, "performance": "yellow", "status": "inactive", "broker_id": 2, "profit_margin": -1.2, "s_products": []},
    {"id": 14, "name": "Cao Thị Phúc", "phone": "070xxxxxxx", "open_date": "2025-02-18", "last_trade_date": "2025-05-12", "trade_value": 100_000_000, "performance": "red", "status": "inactive", "broker_id": 2, "profit_margin": -12.5, "s_products": ["S-BOND"]},
    {"id": 15, "name": "Mai Văn Quý", "phone": "079xxxxxxx", "open_date": "2025-03-02", "last_trade_date": "2025-05-14", "trade_value": 80_000_000, "performance": "yellow", "status": "inactive", "broker_id": 3, "profit_margin": 0.0, "s_products": []},
    {"id": 16, "name": "Lưu Thị Sen", "phone": "077xxxxxxx", "open_date": "2025-03-08", "last_trade_date": "2025-05-11", "trade_value": 70_000_000, "performance": "red", "status": "inactive", "broker_id": 6, "profit_margin": -6.7, "s_products": []},
    {"id": 17, "name": "Tạ Văn Tâm", "phone": "076xxxxxxx", "open_date": "2025-03-12", "last_trade_date": "2025-05-13", "trade_value": 80_000_000, "performance": "green", "status": "inactive", "broker_id": 4, "profit_margin": 5.1, "s_products": ["S-FUND"]},
    {"id": 18, "name": "Đỗ Thị Uyên", "phone": "075xxxxxxx", "open_date": "2025-03-18", "last_trade_date": "2025-05-12", "trade_value": 60_000_000, "performance": "green", "status": "inactive", "broker_id": 4, "profit_margin": 8.8, "s_products": []},

    # ── NHÓM CHURN WARNING (2 khách) ────────────────────────
    {"id": 19, "name": "Hà Văn Vinh", "phone": "074xxxxxxx", "open_date": "2025-01-30", "last_trade_date": "2025-05-09", "trade_value": 40_000_000, "performance": "red", "status": "inactive", "broker_id": 1, "profit_margin": -15.0, "s_products": []},
    {"id": 20, "name": "Nguyễn Thị Xuân", "phone": "073xxxxxxx", "open_date": "2025-02-08", "last_trade_date": "2025-05-10", "trade_value": 40_000_000, "performance": "yellow", "status": "inactive", "broker_id": 5, "profit_margin": -2.5, "s_products": ["S-BOND"]}
]

# ── VERIFY TOÁN (Giữ nguyên từ form gốc) ──
if __name__ == "__main__":
    total_trade = sum(c["trade_value"] for c in customers)
    total_fee = int(total_trade * FEE_RATES["default"])
    print(f"Tổng trade_value : {total_trade:,.0f} VNĐ")
    print(f"Tổng phí (0.15%) : {total_fee:,.0f} VNĐ")
    print(f"Mục tiêu         : 5,000,000 VNĐ")
    print(f"Chênh lệch       : {total_fee - 5_000_000:+,.0f} VNĐ\n")
    for c in customers:
        days = (DEMO_DATE - date.fromisoformat(c["last_trade_date"])).days
        if days > CHURN_THRESHOLD_DAYS:
            print(f"[CHURN] {c['name']} — {days} ngày không GD ✓")

# ============================================================
# STOCKS — 8 mã cổ phiếu dùng trong Advisory Hub (Đã nâng cấp)
# ============================================================
stocks = [
    {
        "ticker": "HPG", "company_name": "Tập đoàn Hòa Phát", "buy_zone": "28.5 - 29.5", "target": 35.0, "cutloss": 27.0, 
        "thesis": "Duy trì vị thế đầu ngành thép, biên lợi nhuận cải thiện nhờ giá HRC phục hồi.", 
        "roe": 15.2, "eps": 2800, "pe": 10.5, "rsi": 45, "volume": "Tích lũy nền", "updated_at": "08:00 - 25/05/2025"
    },
    {
        "ticker": "FPT", "company_name": "Công ty Cổ phần FPT", "buy_zone": "120.0 - 125.0", "target": 140.0, "cutloss": 115.0, 
        "thesis": "Tăng trưởng mảng công nghệ duy trì 2 chữ số, trúng thầu nhiều dự án chuyển đổi số quốc tế.", 
        "roe": 25.4, "eps": 5600, "pe": 22.1, "rsi": 68, "volume": "Duy trì mức cao", "updated_at": "09:15 - 25/05/2025"
    },
    {
        "ticker": "ACB", "company_name": "Ngân hàng TMCP Á Châu", "buy_zone": "27.0 - 28.0", "target": 32.0, "cutloss": 25.5, 
        "thesis": "Chất lượng tài sản top đầu, quản trị rủi ro tốt. Tỷ lệ CASA duy trì ổn định quanh mức 22%.", 
        "roe": 22.1, "eps": 3500, "pe": 8.0, "rsi": 55, "volume": "Dòng tiền lớn tham gia", "updated_at": "10:30 - 25/05/2025"
    },
    {
        "ticker": "MWG", "company_name": "CTCP Đầu tư Thế Giới Di Động", "buy_zone": "55.0 - 58.0", "target": 68.0, "cutloss": 52.0, 
        "thesis": "Bách Hóa Xanh đạt điểm hòa vốn, sức mua bán lẻ dần hồi phục trong nửa cuối năm.", 
        "roe": 12.5, "eps": 1500, "pe": 38.5, "rsi": 72, "volume": "Tăng đột biến", "updated_at": "14:00 - 25/05/2025"
    },
    {
        "ticker": "TCB", "company_name": "Ngân hàng TMCP Kỹ thương Việt Nam", "buy_zone": "45.0 - 47.0", "target": 55.0, "cutloss": 42.0, 
        "thesis": "Lợi thế chi phí vốn rẻ với tỷ lệ CASA dẫn đầu ngành (gần 40%), NIM duy trì ở mức cao trên 4.5%.", 
        "roe": 18.5, "eps": 4500, "pe": 7.5, "rsi": 60, "volume": "Dòng tiền tổ chức mua gom", "updated_at": "14:30 - 25/05/2025"
    },
    {
        "ticker": "HDB", "company_name": "Ngân hàng TMCP Phát triển TP.HCM", "buy_zone": "22.5 - 23.5", "target": 28.0, "cutloss": 21.0, 
        "thesis": "Tốc độ tăng trưởng tín dụng cao, NIM cải thiện tích cực nhờ tệp khách hàng cá nhân và SME. ROE top đầu.", 
        "roe": 23.0, "eps": 3200, "pe": 6.8, "rsi": 50, "volume": "Thanh khoản bùng nổ", "updated_at": "15:00 - 25/05/2025"
    },
    {
        "ticker": "SSI", "company_name": "Công ty Cổ phần Chứng khoán SSI", "buy_zone": "35.0 - 36.5", "target": 42.0, "cutloss": 33.0, 
        "thesis": "Hưởng lợi trực tiếp từ thanh khoản thị trường. Thị phần môi giới và dư nợ margin duy trì top 1.", 
        "roe": 14.5, "eps": 1800, "pe": 18.0, "rsi": 58, "volume": "Bắt đáy vùng hỗ trợ", "updated_at": "15:15 - 25/05/2025"
    },
    {
        "ticker": "VNM", "company_name": "CTCP Sữa Việt Nam", "buy_zone": "65.0 - 67.0", "target": 75.0, "cutloss": 62.0, 
        "thesis": "Dòng tiền kinh doanh ổn định, tỷ suất cổ tức cao. Kỳ vọng phục hồi biên lợi nhuận nhờ giá nguyên liệu giảm.", 
        "roe": 28.0, "eps": 4200, "pe": 16.5, "rsi": 42, "volume": "Tiết cung vùng đáy", "updated_at": "15:45 - 25/05/2025"
    }
]

# ============================================================
# ACTIVITIES — Nhật ký hoạt động mẫu ban đầu
# ============================================================
activities = [
    {"id": 1, "broker_id": 1, "customer_id": 1, "type": "call", "note": "Gọi điện tư vấn về cổ phiếu HPG, khách đồng ý mua 10.000 cổ", "date": "2025-05-25T09:35:00"},
    {"id": 2, "broker_id": 1, "customer_id": 3, "type": "report", "note": "Gửi báo cáo phân tích tuần cho khách hàng", "date": "2025-05-24T14:20:00"},
    {"id": 3, "broker_id": 2, "customer_id": 5, "type": "meet", "note": "Gặp mặt tại văn phòng, tư vấn mở rộng danh mục", "date": "2025-05-23T10:00:00"},
    {"id": 4, "broker_id": 3, "customer_id": 7, "type": "trade", "note": "Chốt lệnh mua FPT giá 135.000đ, khối lượng 5.000 cổ", "date": "2025-05-22T11:15:00"},
    {"id": 5, "broker_id": 4, "customer_id": None, "type": "open", "note": "Hỗ trợ khách hàng mới mở tài khoản trực tuyến qua app SSI", "date": "2025-05-21T15:30:00"}
]

# ============================================================
# HELPER FUNCTIONS
# ============================================================
def get_customer_by_id(customer_id: int) -> dict | None:
    return next((c for c in customers if c["id"] == customer_id), None)

def get_broker_by_id(broker_id: int) -> dict | None:
    return next((b for b in brokers if b["id"] == broker_id), None)

def get_stock_by_ticker(ticker: str) -> dict | None:
    return next((s for s in stocks if s["ticker"] == ticker.upper()), None)

def get_customers_by_broker(broker_id: int) -> list:
    return [c for c in customers if c["broker_id"] == broker_id]

def calculate_fee(trade_value: int, rate: float = FEE_RATES["default"]) -> int:
    return int(trade_value * rate)

def calculate_days_since_trade(last_trade_date: str) -> int:
    last = date.fromisoformat(last_trade_date)
    return (DEMO_DATE - last).days

def is_churn_risk(customer: dict) -> bool:
    return calculate_days_since_trade(customer["last_trade_date"]) > CHURN_THRESHOLD_DAYS
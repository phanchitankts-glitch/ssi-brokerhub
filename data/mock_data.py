# data/mock_data.py
# ============================================================
# mock_data.py — Toàn bộ dữ liệu giả của hệ thống SSI BrokerHub
# ============================================================

from datetime import date, timedelta
import random

# ============================================================
# NGÀY DEMO CỐ ĐỊNH
# ============================================================
DEMO_DATE = date.fromisoformat("2025-05-25")  

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
# BROKERS — 6 thành viên đóng vai môi giới
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
# STOCKS — 8 mã cổ phiếu dùng trong Advisory Hub
# ============================================================
stocks = [
    {"ticker": "HPG", "company_name": "Tập đoàn Hòa Phát", "buy_zone": "28.5 - 29.5", "target": 35.0, "cutloss": 27.0, "thesis": "Duy trì vị thế...", "roe": 15.2, "eps": 2800, "pe": 10.5, "rsi": 45, "volume": "Tích lũy nền", "updated_at": "08:00 - 25/05/2025"},
    {"ticker": "FPT", "company_name": "Công ty Cổ phần FPT", "buy_zone": "120.0 - 125.0", "target": 140.0, "cutloss": 115.0, "thesis": "Tăng trưởng...", "roe": 25.4, "eps": 5600, "pe": 22.1, "rsi": 68, "volume": "Duy trì mức cao", "updated_at": "09:15 - 25/05/2025"},
    {"ticker": "ACB", "company_name": "Ngân hàng TMCP Á Châu", "buy_zone": "27.0 - 28.0", "target": 32.0, "cutloss": 25.5, "thesis": "Chất lượng...", "roe": 22.1, "eps": 3500, "pe": 8.0, "rsi": 55, "volume": "Dòng tiền lớn...", "updated_at": "10:30 - 25/05/2025"},
    {"ticker": "MWG", "company_name": "CTCP Đầu tư Thế Giới Di Động", "buy_zone": "55.0 - 58.0", "target": 68.0, "cutloss": 52.0, "thesis": "Bách Hóa Xanh...", "roe": 12.5, "eps": 1500, "pe": 38.5, "rsi": 72, "volume": "Tăng đột biến", "updated_at": "14:00 - 25/05/2025"},
    {"ticker": "TCB", "company_name": "Ngân hàng TMCP Kỹ thương Việt Nam", "buy_zone": "45.0 - 47.0", "target": 55.0, "cutloss": 42.0, "thesis": "Lợi thế chi phí...", "roe": 18.5, "eps": 4500, "pe": 7.5, "rsi": 60, "volume": "Dòng tiền...", "updated_at": "14:30 - 25/05/2025"},
    {"ticker": "HDB", "company_name": "Ngân hàng TMCP Phát triển TP.HCM", "buy_zone": "22.5 - 23.5", "target": 28.0, "cutloss": 21.0, "thesis": "Tốc độ tăng...", "roe": 23.0, "eps": 3200, "pe": 6.8, "rsi": 50, "volume": "Thanh khoản...", "updated_at": "15:00 - 25/05/2025"},
    {"ticker": "SSI", "company_name": "Công ty Cổ phần Chứng khoán SSI", "buy_zone": "35.0 - 36.5", "target": 42.0, "cutloss": 33.0, "thesis": "Hưởng lợi trực tiếp...", "roe": 14.5, "eps": 1800, "pe": 18.0, "rsi": 58, "volume": "Bắt đáy hỗ trợ", "updated_at": "15:15 - 25/05/2025"},
    {"ticker": "VNM", "company_name": "CTCP Sữa Việt Nam", "buy_zone": "65.0 - 67.0", "target": 75.0, "cutloss": 62.0, "thesis": "Dòng tiền kinh doanh...", "roe": 28.0, "eps": 4200, "pe": 16.5, "rsi": 42, "volume": "Tiết cung đáy", "updated_at": "15:45 - 25/05/2025"}
]

# ============================================================
# CUSTOMERS — Tự động sinh ngẫu nhiên (17-23 khách / Broker)
# ============================================================
customers = []
first_names = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Huỳnh", "Phan", "Vũ", "Võ", "Đặng", "Bùi", "Đỗ", "Ngô"]
middle_names = ["Thị", "Văn", "Hữu", "Minh", "Thanh", "Thành", "Đức", "Ngọc", "Gia", "Bảo", "Tuấn", "Anh", "Xuân"]
last_names = ["An", "Bình", "Cường", "Dũng", "Đạt", "Hải", "Hiếu", "Huy", "Hùng", "Khoa", "Lâm", "Linh", "Long", "Minh", "Nam", "Phúc", "Quân", "Quang", "Sơn", "Tâm", "Thành", "Tiến", "Trí", "Trung"]

random.seed(42) 
customer_id_counter = 1

for broker in brokers:
    num_cust = random.randint(17, 23)
    for _ in range(num_cust):
        name = f"{random.choice(first_names)} {random.choice(middle_names)} {random.choice(last_names)}"
        phone = f"09{random.randint(10000000, 99999999)}"
        
        days_open = random.randint(100, 1000)
        open_date = DEMO_DATE - timedelta(days=days_open)
        
        days_inactive = random.randint(1, 60)
        last_trade_date = DEMO_DATE - timedelta(days=days_inactive)
        
        if days_inactive > 30:
            status = "inactive"
        elif days_inactive > CHURN_THRESHOLD_DAYS:
            status = random.choice(["active", "inactive"])
        else:
            status = "active"
            
        s_products_pool = ["S-BOND", "S-FUND", "S-MARGIN"]
        s_products = random.sample(s_products_pool, k=random.randint(0, len(s_products_pool)))
        
        # Sinh danh mục cổ phiếu ngẫu nhiên cho khách
        portfolio = []
        num_stocks = random.randint(1, 3)
        my_stocks = random.sample(stocks, num_stocks)
        for s in my_stocks:
            base_str = s.get("buy_zone", "30.0").split(" - ")[0]
            try:
                base_price = float(base_str.replace(',', '')) * 1000
            except:
                base_price = 30000.0
            
            avg_price = base_price * random.uniform(0.85, 1.15)
            volume = random.randint(10, 50) * 100
            portfolio.append({
                "ticker": s["ticker"],
                "volume": volume,
                "avg_price": avg_price
            })
            
        customers.append({
            "id": customer_id_counter,
            "name": name,
            "phone": phone,
            "open_date": open_date.isoformat(),
            "last_trade_date": last_trade_date.isoformat(),
            "trade_value": 0,       # Sẽ được tính lại tự động ở trang 2
            "profit_margin": 0.0,   # Sẽ được tính lại tự động ở trang 2
            "performance": "yellow",
            "status": status,
            "broker_id": broker["id"],
            "s_products": s_products,
            "portfolio": portfolio
        })
        customer_id_counter += 1

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
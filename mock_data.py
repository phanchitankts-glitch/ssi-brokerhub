# mock_data.py — Toàn bộ dữ liệu giả của hệ thống SSI BrokerHub
#
# TV4 phụ trách : phần STOCKS (4 mã cổ phiếu)
# TV5 phụ trách : phần BROKERS + CUSTOMERS (20 khách hàng)
# TV6 phụ trách : file scenario_day25.py riêng (dựa trên file này)
#
# LƯU Ý: Không ai được sửa file này ngoài TV4 và TV5.
# Mọi thay đổi cần thông báo cho TV1 để cập nhật session_state.

from datetime import date

# ============================================================
# NGÀY DEMO CỐ ĐỊNH — KHÔNG DÙNG date.today()
# Lý do: date.today() lấy ngày thật của máy tính lúc chạy.
# Nếu ngày thuyết trình khác ngày code thì churn warning
# sẽ tính sai, khách 19+20 sẽ không highlight đỏ nữa.
# ============================================================

DEMO_DATE = date.fromisoformat("2025-05-25")  # Cố định ngày demo

# ============================================================
# HẰNG SỐ — Chỉ tiêu KPI và tỷ lệ phí
# Không cần sửa phần này
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
# BROKERS — 4 thành viên đóng vai môi giới
# TV5 điền tên thật của các thành viên vào đây
# ============================================================

brokers = [
    {
        "id": 1,
        "name": "[Họ tên TV1]",
        "avatar": "T1",
        "fee": {
            "month1": 5_800_000,
            "month2": 6_200_000,
            "month3": 5_000_000
        }
    },
    {
        "id": 2,
        "name": "[Họ tên TV2]",
        "avatar": "T2",
        "fee": {
            "month1": 6_100_000,
            "month2": 5_900_000,
            "month3": 5_000_000
        }
    },
    {
        "id": 3,
        "name": "[Họ tên TV3]",
        "avatar": "T3",
        "fee": {
            "month1": 5_500_000,
            "month2": 6_300_000,
            "month3": 5_000_000
        }
    },
    {
        "id": 4,
        "name": "[Họ tên TV4]",
        "avatar": "T4",
        "fee": {
            "month1": 6_000_000,
            "month2": 5_700_000,
            "month3": 5_000_000
        }
    }
]

# ============================================================
# CUSTOMERS — 20 khách hàng giả định
# TV5 phụ trách toàn bộ phần này
#
# Phân bổ bắt buộc:
#   - 10 khách active   (last_trade_date trong vòng 14 ngày so với DEMO_DATE)
#   - 8  khách inactive (không GD nhưng chưa quá 14 ngày)
#   - 2  khách CHURN WARNING (last_trade_date cách DEMO_DATE 15-16 ngày)
#
# Performance: ~12 green, ~4 yellow, ~4 red → green+yellow > 70%
#
# ⚠️ QUAN TRỌNG VỀ trade_value:
#   Để tổng phí ra ~5.000.000 VNĐ thì tổng trade_value phải ~3.330.000.000 VNĐ
#   Công thức: tổng_phí = tổng_trade_value × 0.0015
#   TV5 verify lại bằng Excel: =SUM(trade_value cột) * 0.0015
# ============================================================

customers = [
    # ── NHÓM ACTIVE (10 khách) ──────────────────────────────
    # Tổng trade_value nhóm này cần ~2.500.000.000 VNĐ
    {
        "id": 1,
        "name": "Nguyễn Văn An",
        "phone": "090xxxxxxx",
        "open_date": "2025-01-15",
        "last_trade_date": "2025-05-20",
        "trade_value": 260_000_000,
        "performance": "green",
        "status": "active",
        "broker_id": 1
    },
    {
        "id": 2,
        "name": "Trần Thị Bích",
        "phone": "091xxxxxxx",
        "open_date": "2025-01-20",
        "last_trade_date": "2025-05-18",
        "trade_value": 210_000_000,
        "performance": "green",
        "status": "active",
        "broker_id": 1
    },
    {
        "id": 3,
        "name": "Lê Hoàng Cường",
        "phone": "093xxxxxxx",
        "open_date": "2025-02-01",
        "last_trade_date": "2025-05-22",
        "trade_value": 360_000_000,
        "performance": "green",
        "status": "active",
        "broker_id": 1
    },
    {
        "id": 4,
        "name": "Phạm Thị Dung",
        "phone": "094xxxxxxx",
        "open_date": "2025-02-10",
        "last_trade_date": "2025-05-19",
        "trade_value": 160_000_000,
        "performance": "yellow",
        "status": "active",
        "broker_id": 2
    },
    {
        "id": 5,
        "name": "Hoàng Văn Em",
        "phone": "096xxxxxxx",
        "open_date": "2025-02-15",
        "last_trade_date": "2025-05-21",
        "trade_value": 310_000_000,
        "performance": "green",
        "status": "active",
        "broker_id": 2
    },
    {
        "id": 6,
        "name": "Vũ Thị Phương",
        "phone": "097xxxxxxx",
        "open_date": "2025-02-20",
        "last_trade_date": "2025-05-17",
        "trade_value": 230_000_000,
        "performance": "green",
        "status": "active",
        "broker_id": 2
    },
    {
        "id": 7,
        "name": "Đặng Minh Quân",
        "phone": "098xxxxxxx",
        "open_date": "2025-03-01",
        "last_trade_date": "2025-05-20",
        "trade_value": 280_000_000,
        "performance": "green",
        "status": "active",
        "broker_id": 3
    },
    {
        "id": 8,
        "name": "Bùi Thị Hoa",
        "phone": "099xxxxxxx",
        "open_date": "2025-03-05",
        "last_trade_date": "2025-05-16",
        "trade_value": 175_000_000,
        "performance": "yellow",
        "status": "active",
        "broker_id": 3
    },
    {
        "id": 9,
        "name": "Ngô Văn Khải",
        "phone": "086xxxxxxx",
        "open_date": "2025-03-10",
        "last_trade_date": "2025-05-23",
        "trade_value": 330_000_000,
        "performance": "green",
        "status": "active",
        "broker_id": 4
    },
    {
        "id": 10,
        "name": "Đinh Thị Lan",
        "phone": "085xxxxxxx",
        "open_date": "2025-03-15",
        "last_trade_date": "2025-05-19",
        "trade_value": 195_000_000,
        "performance": "green",
        "status": "active",
        "broker_id": 4
    },

    # ── NHÓM INACTIVE (8 khách) ─────────────────────────────
    # Tổng trade_value nhóm này cần ~750.000.000 VNĐ
    {
        "id": 11,
        "name": "Trương Văn Minh",
        "phone": "083xxxxxxx",
        "open_date": "2025-01-25",
        "last_trade_date": "2025-05-12",
        "trade_value": 120_000_000,
        "performance": "red",
        "status": "inactive",
        "broker_id": 1
    },
    {
        "id": 12,
        "name": "Lý Thị Ngọc",
        "phone": "082xxxxxxx",
        "open_date": "2025-02-05",
        "last_trade_date": "2025-05-11",
        "trade_value": 90_000_000,
        "performance": "red",
        "status": "inactive",
        "broker_id": 1
    },
    {
        "id": 13,
        "name": "Phan Văn Ổn",
        "phone": "081xxxxxxx",
        "open_date": "2025-02-12",
        "last_trade_date": "2025-05-13",
        "trade_value": 150_000_000,
        "performance": "yellow",
        "status": "inactive",
        "broker_id": 2
    },
    {
        "id": 14,
        "name": "Cao Thị Phúc",
        "phone": "070xxxxxxx",
        "open_date": "2025-02-18",
        "last_trade_date": "2025-05-12",
        "trade_value": 100_000_000,
        "performance": "red",
        "status": "inactive",
        "broker_id": 2
    },
    {
        "id": 15,
        "name": "Mai Văn Quý",
        "phone": "079xxxxxxx",
        "open_date": "2025-03-02",
        "last_trade_date": "2025-05-14",
        "trade_value": 80_000_000,
        "performance": "yellow",
        "status": "inactive",
        "broker_id": 3
    },
    {
        "id": 16,
        "name": "Lưu Thị Sen",
        "phone": "077xxxxxxx",
        "open_date": "2025-03-08",
        "last_trade_date": "2025-05-11",
        "trade_value": 70_000_000,
        "performance": "red",
        "status": "inactive",
        "broker_id": 3
    },
    {
        "id": 17,
        "name": "Tạ Văn Tâm",
        "phone": "076xxxxxxx",
        "open_date": "2025-03-12",
        "last_trade_date": "2025-05-13",
        "trade_value": 80_000_000,
        "performance": "green",
        "status": "inactive",
        "broker_id": 4
    },
    {
        "id": 18,
        "name": "Đỗ Thị Uyên",
        "phone": "075xxxxxxx",
        "open_date": "2025-03-18",
        "last_trade_date": "2025-05-12",
        "trade_value": 60_000_000,
        "performance": "green",
        "status": "inactive",
        "broker_id": 4
    },

    # ── NHÓM CHURN WARNING (2 khách) ────────────────────────
    # last_trade_date phải cách DEMO_DATE (25/05/2025) đúng 15-16 ngày
    # → 25/05 - 16 ngày = 09/05, 25/05 - 15 ngày = 10/05
    # Tổng trade_value nhóm này ~80.000.000 VNĐ
    {
        "id": 19,
        "name": "Hà Văn Vinh",
        "phone": "074xxxxxxx",
        "open_date": "2025-01-30",
        "last_trade_date": "2025-05-09",   # DEMO_DATE - 16 ngày → churn = True
        "trade_value": 40_000_000,
        "performance": "red",
        "status": "inactive",
        "broker_id": 1
    },
    {
        "id": 20,
        "name": "Nguyễn Thị Xuân",
        "phone": "073xxxxxxx",
        "open_date": "2025-02-08",
        "last_trade_date": "2025-05-10",   # DEMO_DATE - 15 ngày → churn = True
        "trade_value": 40_000_000,
        "performance": "yellow",
        "status": "inactive",
        "broker_id": 1
    }
]

# ── VERIFY TOÁN (TV5 chạy đoạn này để kiểm tra trước khi nộp) ──
# Mở terminal, chạy: python mock_data.py
# Kết quả mong đợi: tổng phí xấp xỉ 5.000.000 VNĐ
if __name__ == "__main__":
    total_trade = sum(c["trade_value"] for c in customers)
    total_fee = int(total_trade * FEE_RATES["default"])
    print(f"Tổng trade_value : {total_trade:,.0f} VNĐ")
    print(f"Tổng phí (0.15%) : {total_fee:,.0f} VNĐ")
    print(f"Mục tiêu         : 5,000,000 VNĐ")
    print(f"Chênh lệch       : {total_fee - 5_000_000:+,.0f} VNĐ")
    print()

    # Kiểm tra churn
    for c in customers:
        days = (DEMO_DATE - date.fromisoformat(c["last_trade_date"])).days
        if days > CHURN_THRESHOLD_DAYS:
            print(f"[CHURN] {c['name']} — {days} ngày không GD ✓")

# ============================================================
# STOCKS — 4 mã cổ phiếu dùng trong Advisory Hub
# TV4 phụ trách toàn bộ phần này
# Số liệu PHẢI tra từ CafeF / Vietstock — không được bịa
# ============================================================

stocks = [
    {
        "ticker": "HPG",
        "company_name": "Tập đoàn Hòa Phát",
        "buy_zone": "[TV4 điền]",
        "target": 0.0,
        "cutloss": 0.0,
        "thesis": "[TV4 viết 2-3 câu — gợi ý: sản lượng HRC tháng 3 tăng mạnh, triển vọng xuất khẩu cải thiện, biên lợi nhuận hồi phục]",
        "roe": 0.0,
        "eps": 0,
        "pe": 0.0,
        "rsi": 0,
        "volume": "[TV4 nhận xét]",
        "updated_at": "09:32 - 23/05/2025"
    },
    {
        "ticker": "FPT",
        "company_name": "Công ty Cổ phần FPT",
        "buy_zone": "[TV4 điền]",
        "target": 0.0,
        "cutloss": 0.0,
        "thesis": "[TV4 viết — gợi ý: tăng trưởng mảng CNTT và giáo dục, đơn hàng nước ngoài tích cực, biên lợi nhuận cải thiện]",
        "roe": 0.0,
        "eps": 0,
        "pe": 0.0,
        "rsi": 0,
        "volume": "[TV4 nhận xét]",
        "updated_at": "09:45 - 23/05/2025"
    },
    {
        "ticker": "ACB",
        "company_name": "Ngân hàng TMCP Á Châu",
        "buy_zone": "[TV4 điền]",
        "target": 0.0,
        "cutloss": 0.0,
        "thesis": "[TV4 viết — gợi ý: tỷ lệ CASA dẫn đầu ngành, NIM ổn định, chất lượng tài sản kiểm soát tốt, tỷ lệ nợ xấu thấp]",
        "roe": 0.0,
        "eps": 0,
        "pe": 0.0,
        "rsi": 0,
        "volume": "[TV4 nhận xét]",
        "updated_at": "10:05 - 23/05/2025"
    },
    {
        "ticker": "MWG",
        "company_name": "Công ty Cổ phần Đầu tư Thế Giới Di Động",
        "buy_zone": "[TV4 điền]",
        "target": 0.0,
        "cutloss": 0.0,
        "thesis": "[TV4 viết — gợi ý: chuỗi Bách Hóa Xanh cải thiện biên lợi nhuận, doanh thu phục hồi sau tái cơ cấu, định giá hấp dẫn so với lịch sử]",
        "roe": 0.0,
        "eps": 0,
        "pe": 0.0,
        "rsi": 0,
        "volume": "[TV4 nhận xét]",
        "updated_at": "10:18 - 23/05/2025"
    }
]

# ============================================================
# ACTIVITIES — Nhật ký hoạt động mẫu ban đầu
# ============================================================

activities = [
    {
        "id": 1,
        "broker_id": 1,
        "customer_id": 1,
        "type": "call",
        "note": "Gọi điện tư vấn về cổ phiếu HPG, khách đồng ý mua 10.000 cổ",
        "date": "2025-05-25T09:35:00"
    },
    {
        "id": 2,
        "broker_id": 1,
        "customer_id": 3,
        "type": "report",
        "note": "Gửi báo cáo phân tích tuần cho khách hàng",
        "date": "2025-05-24T14:20:00"
    },
    {
        "id": 3,
        "broker_id": 2,
        "customer_id": 5,
        "type": "meet",
        "note": "Gặp mặt tại văn phòng, tư vấn mở rộng danh mục",
        "date": "2025-05-23T10:00:00"
    },
    {
        "id": 4,
        "broker_id": 3,
        "customer_id": 7,
        "type": "trade",
        "note": "Chốt lệnh mua FPT giá 135.000đ, khối lượng 5.000 cổ",
        "date": "2025-05-22T11:15:00"
    },
    {
        "id": 5,
        "broker_id": 4,
        "customer_id": None,
        "type": "open",
        "note": "Hỗ trợ khách hàng mới mở tài khoản trực tuyến qua app SSI",
        "date": "2025-05-21T15:30:00"
    }
]

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_customer_by_id(customer_id: int) -> dict | None:
    """Tìm khách hàng theo ID."""
    return next((c for c in customers if c["id"] == customer_id), None)


def get_broker_by_id(broker_id: int) -> dict | None:
    """Tìm broker theo ID."""
    return next((b for b in brokers if b["id"] == broker_id), None)


def get_stock_by_ticker(ticker: str) -> dict | None:
    """Tìm cổ phiếu theo mã. Không phân biệt hoa thường."""
    return next((s for s in stocks if s["ticker"] == ticker.upper()), None)


def get_customers_by_broker(broker_id: int) -> list:
    """Lấy danh sách khách hàng của một broker."""
    return [c for c in customers if c["broker_id"] == broker_id]


def calculate_fee(trade_value: int, rate: float = FEE_RATES["default"]) -> int:
    """Tính phí môi giới từ giá trị giao dịch."""
    return int(trade_value * rate)


def calculate_days_since_trade(last_trade_date: str) -> int:
    """
    Tính số ngày kể từ lần giao dịch cuối so với DEMO_DATE.
    Dùng DEMO_DATE cố định thay vì date.today() để tránh lỗi lúc lên bục.
    """
    last = date.fromisoformat(last_trade_date)
    return (DEMO_DATE - last).days


def is_churn_risk(customer: dict) -> bool:
    """Kiểm tra khách hàng có nguy cơ churn không (> 14 ngày không GD)."""
    return calculate_days_since_trade(customer["last_trade_date"]) > CHURN_THRESHOLD_DAYS

# Binance Futures Volume Alert Bot

Bot theo dõi volume đột biến trên các cặp Futures của Binance và gửi cảnh báo qua Telegram khi phát hiện biến động bất thường.

## Tính năng

- Theo dõi tất cả các cặp USDT Futures trên Binance
- Phát hiện nến có volume đột biến (cao hơn trung bình) và giá tăng
- Gửi cảnh báo qua Telegram khi phát hiện bất thường
- Hỗ trợ nhiều khung thời gian (1m, 5m, 15m, 30m, 1h, 4h, 1d)
- Tự động retry khi gặp lỗi kết nối
- Ghi log đầy đủ để theo dõi hoạt động

## Cài đặt

1. Clone repository:
```bash
git clone <repository-url>
cd binance-volume-alert
```

2. Cài đặt các thư viện cần thiết:
```bash
pip install -r requirements.txt
```

3. Cấu hình Telegram Bot:
- Tạo bot mới thông qua [@BotFather](https://t.me/BotFather)
- Lưu lại Token của bot
- Chat với bot và lấy Chat ID

4. Cấu hình trong file `app.py`:
```python
TELEGRAM_TOKEN = "YOUR_BOT_TOKEN"
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID"
TIMEFRAME = "15m"  # Thay đổi theo nhu cầu
```

## Cấu hình

Các thông số có thể điều chỉnh trong class `BinanceVolumeAlert`:

- `volume_threshold`: Ngưỡng volume (mặc định 2.0 = 200% trung bình)
- `price_increase_threshold`: Ngưỡng tăng giá (mặc định 1%)
- `lookback_periods`: Số nến để tính trung bình (mặc định 24 nến)
- `timeframe`: Khung thời gian (1m, 5m, 15m, 30m, 1h, 4h, 1d)

## Chạy bot

```bash
python app.py
```

Bot sẽ:
1. Gửi tin nhắn thông báo khởi động qua Telegram
2. Bắt đầu quét các cặp Futures theo khung thời gian đã cấu hình
3. Gửi cảnh báo khi phát hiện bất thường
4. Ghi log vào file `volume_alert.log`

## Log

Bot ghi log vào 2 nơi:
- Console: Hiển thị trực tiếp khi chạy
- File `volume_alert.log`: Lưu lại để kiểm tra sau

## Xử lý lỗi

Bot có các cơ chế xử lý lỗi:
- Tự động retry khi gặp lỗi gửi tin nhắn Telegram
- Bỏ qua các cặp giao dịch có dữ liệu không hợp lệ
- Chờ và thử lại khi gặp lỗi API
- Ghi log chi tiết để dễ dàng debug

## Đóng góp

Mọi đóng góp đều được hoan nghênh. Vui lòng tạo issue hoặc pull request.

## License

[MIT License](LICENSE)
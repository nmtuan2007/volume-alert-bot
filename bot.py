import ccxt
import pandas as pd
import numpy as np
import asyncio
import random
from telegram.ext import ApplicationBuilder
from datetime import datetime
import logging
import sys
import os

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

# Lấy thông tin từ GitHub secrets
TELEGRAM_TOKEN = "7732399702:AAHHtWhOR-aBusIYLR1jI2GllozuYlBnoJ8"
TELEGRAM_CHAT_ID = 6173457255
TIMEFRAME = "1h"

class BinanceVolumeAlert:
    def __init__(self, telegram_token, telegram_chat_id, timeframe='1h'):
        # Khởi tạo kết nối Binance
        self.exchange = ccxt.binance({
            'enableRateLimit': True,
            'options': {
                'defaultType': 'future'
            }
        })
        
        # Khởi tạo application Telegram
        self.app = ApplicationBuilder().token(telegram_token).build()
        self.chat_id = telegram_chat_id
        
        # Các thông số cấu hình
        self.timeframe = timeframe  # Thêm cấu hình timeframe
        self.volume_threshold = 3.0  # Volume cao hơn trung bình 200% 
        self.price_increase_threshold = 4.0  # Giá tăng 1% trở lên
        self.lookback_periods = 24  # Số nến để tính trung bình
    
    def get_all_futures(self):
        """Lấy danh sách tất cả các cặp giao dịch futures"""
        try:
            markets = self.exchange.load_markets()
            return [symbol for symbol in markets.keys() if '/USDT:USDT' in symbol]
        except Exception as e:
            logging.error(f"Loi khi lay danh sach futures: {str(e)}")
            return []
    
    def get_ohlcv_data(self, symbol):
        """Lấy dữ liệu OHLCV cho một cặp giao dịch"""
        try:
            # Lấy thêm 2 nến để đảm bảo có đủ dữ liệu
            ohlcv = self.exchange.fetch_ohlcv(
                symbol,
                timeframe=self.timeframe,
                limit=self.lookback_periods + 2
            )
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            # Bỏ qua nến cuối cùng (nến đang chạy)
            df = df[:-1]
            
            return df
        except Exception as e:
            logging.error(f"Loi khi lay du lieu {symbol}: {str(e)}")
            return None

    def check_volume_spike(self, df):
        """Kiểm tra volume đột biến và giá tăng"""
        try:
            if len(df) < self.lookback_periods + 1:
                return False, 0, 0
            
            current_candle = df.iloc[-1]
            previous_candles = df.iloc[:-1]
            
            # Kiểm tra giá trị volume hợp lệ
            if current_candle['volume'] <= 0 or current_candle['volume'] is None:
                logging.warning(f"Volume không hợp lệ: {current_candle['volume']}")
                return False, 0, 0
                
            # Tính volume trung bình và kiểm tra
            avg_volume = previous_candles['volume'].mean()
            if avg_volume <= 0 or pd.isna(avg_volume):
                logging.warning(f"Volume trung bình không hợp lệ: {avg_volume}")
                return False, 0, 0
            
            # Tính % tăng giá và kiểm tra
            if current_candle['open'] <= 0 or pd.isna(current_candle['open']):
                logging.warning(f"Giá mở cửa không hợp lệ: {current_candle['open']}")
                return False, 0, 0
                
            price_increase = ((current_candle['close'] - current_candle['open']) / current_candle['open']) * 100
            volume_ratio = current_candle['volume'] / avg_volume
            
            # Kiểm tra kết quả tính toán
            if pd.isna(price_increase) or pd.isna(volume_ratio):
                logging.warning(f"Kết quả tính toán không hợp lệ - Price increase: {price_increase}, Volume ratio: {volume_ratio}")
                return False, 0, 0
            
            is_spike = (volume_ratio > self.volume_threshold and 
                    price_increase > self.price_increase_threshold)
            
            return is_spike, volume_ratio, price_increase
            
        except Exception as e:
            logging.error(f"Lỗi trong check_volume_spike: {str(e)}")
            return False, 0, 0
    
    async def send_telegram_alert(self, symbol, volume_ratio, price_increase):
        """Gửi cảnh báo qua Telegram"""
        max_retries = 3
        retry_delay = 5  # seconds
        
        for attempt in range(max_retries):
            try:
                message = (
                    f"CANH BAO VOLUME DOT BIEN!\n\n"
                    f"Cap: {symbol}\n"
                    f"Volume: {volume_ratio:.2f}x trung binh\n"
                    f"Tang gia: {price_increase:.2f}%\n"
                    f"Thoi gian: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )
                await self.app.bot.send_message(
                    chat_id=self.chat_id,
                    text=message
                )
                logging.info(f"Da gui canh bao cho {symbol}")
                break
            except Exception as e:
                if attempt == max_retries - 1:
                    logging.error(f"Loi khi gui canh bao Telegram: {str(e)}")
                else:
                    logging.warning(f"Lan thu {attempt + 1} gui that bai, thu lai sau {retry_delay} giay")
                    await asyncio.sleep(retry_delay)

    async def scan_single_symbol(self, symbol):
        """Quét một cặp giao dịch"""
        try:
            # Thêm delay ngẫu nhiên từ 0.1 đến 0.5 giây
            await asyncio.sleep(random.uniform(0.1, 0.5))
            
            df = self.get_ohlcv_data(symbol)
            if df is not None and not df.empty:
                is_spike, volume_ratio, price_increase = self.check_volume_spike(df)
                if is_spike:
                    await self.send_telegram_alert(symbol, volume_ratio, price_increase)
        except Exception as e:
            logging.error(f"Loi khi quet {symbol}: {str(e)}")
    
    async def run(self):
        """Chạy vòng lặp chính của chương trình"""
        # Gửi tin nhắn test khi khởi động
        try:
            await self.app.initialize()  # Khởi tạo application
            await self.app.bot.send_message(
                chat_id=self.chat_id,
                text="Bot da khoi dong va bat dau quet..."
            )
        except Exception as e:
            logging.error(f"Khong the gui tin nhan test: {str(e)}")
            return

        while True:
            try:
                symbols = self.get_all_futures()
                logging.info(f"Dang quet {len(symbols)} cap giao dich")
                
                # Chia nhỏ danh sách symbols thành các nhóm
                batch_size = 10
                for i in range(0, len(symbols), batch_size):
                    batch = symbols[i:i + batch_size]
                    tasks = [self.scan_single_symbol(symbol) for symbol in batch]
                    await asyncio.gather(*tasks)
                    await asyncio.sleep(1)  # Delay giữa các batch
                
                logging.info("Hoan thanh quet. Doi 5 phut...")
                await asyncio.sleep(300)
                
            except Exception as e:
                logging.error(f"Loi trong vong lap chinh: {str(e)}")
                await asyncio.sleep(60)

async def main():
    scanner = BinanceVolumeAlert(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, TIMEFRAME)
    await scanner.run()

if __name__ == "__main__":
    asyncio.run(main())
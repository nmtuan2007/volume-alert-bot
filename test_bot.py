import asyncio
import telegram

async def send_test_message():
    # Khởi tạo bot với token
    bot = telegram.Bot(token='7732399702:AAHHtWhOR-aBusIYLR1jI2GllozuYlBnoJ8')
    
    # Gửi tin nhắn test
    await bot.send_message(
        chat_id=6173457255,
        text="🔔 Test thông báo - Bot đang hoạt động!"
    )

# Chạy hàm async
asyncio.run(send_test_message())
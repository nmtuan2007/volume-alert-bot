@echo off
:: Đường dẫn đến thư mục chứa virtual environment
set VENV_PATH=D:\PythonEnv

:: Tên của virtual environment
set VENV_NAME=crypto_signal

:: Đường dẫn đầy đủ của virtual environment
set FULL_VENV_PATH=%VENV_PATH%\%VENV_NAME%

:: Tạo thư mục virtual environment nếu chưa tồn tại
if not exist %VENV_PATH% (
    mkdir %VENV_PATH%
)

:: Tạo virtual environment
echo Creating virtual environment at %FULL_VENV_PATH%...
python -m venv %FULL_VENV_PATH%

:: Kiểm tra nếu virtual environment đã được tạo thành công
if not exist %FULL_VENV_PATH%\Scripts\activate (
    echo Failed to create virtual environment. Exiting...
    exit /b
)

:: Kích hoạt virtual environment
echo Activating virtual environment...
call %FULL_VENV_PATH%\Scripts\activate

:: Chuyển về thư mục C:\Users\admin\Desktop\Python
cd /d C:\Users\admin\Desktop\Python
echo Virtual environment activated and directory changed to %CD%.

:: Giữ cửa sổ console mở
cmd /k

@echo off
echo ============================================
echo   ExamPortal Setup Script
echo ============================================
echo.

echo [1/5] Installing dependencies...
pip install -r requirements.txt

echo.
echo [2/5] Running migrations...
python manage.py migrate

echo.
echo [3/5] Creating superuser (admin)...
echo Run: python manage.py createsuperuser

echo.
echo [4/5] Loading sample data...
python manage.py shell < setup_data.py

echo.
echo ============================================
echo   Setup Complete!
echo ============================================
echo.
echo To run the server:
echo   python manage.py runserver
echo.
echo To access admin:
echo   http://127.0.0.1:8000/admin/
echo.
pause

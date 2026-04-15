@echo off
echo ============================================================
echo Fixing Driver Monitoring System Installation
echo ============================================================
echo.

echo [1/5] Upgrading pip...
python -m pip install --upgrade pip
echo.

echo [2/5] Installing OpenCV...
pip install opencv-python
echo.

echo [3/5] Installing MediaPipe...
pip install mediapipe
echo.

echo [4/5] Installing other packages...
pip install scipy pygame scikit-learn imutils pyttsx3
echo.

echo [5/5] Verifying installation...
python -c "import cv2; print('✅ OpenCV version:', cv2.__version__)"
python -c "import mediapipe; print('✅ MediaPipe installed')"
python -c "import scipy; print('✅ SciPy installed')"
echo.

echo ============================================================
echo Installation Complete!
echo ============================================================
echo.
echo Now run: python check_environment.py
pause
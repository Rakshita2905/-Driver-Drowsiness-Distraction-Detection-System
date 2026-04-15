@echo off
echo ============================================================
echo Installing All Required Packages
echo ============================================================
echo.

echo Upgrading pip...
python -m pip install --upgrade pip
echo.

echo Installing OpenCV...
python -m pip install opencv-python
echo.

echo Installing MediaPipe...
python -m pip install mediapipe
echo.

echo Installing NumPy...
python -m pip install numpy
echo.

echo Installing PyYAML...
python -m pip install pyyaml
echo.

echo ============================================================
echo Verifying installations...
echo ============================================================
echo.

python -c "import cv2; print('✅ OpenCV:', cv2.__version__)"
python -c "import mediapipe; print('✅ MediaPipe:', mediapipe.__version__)"
python -c "import numpy; print('✅ NumPy:', numpy.__version__)"
python -c "import yaml; print('✅ PyYAML installed')"

echo.
echo ============================================================
echo Installation Complete!
echo ============================================================
echo.
echo Now run: python main_fixed.py
pause
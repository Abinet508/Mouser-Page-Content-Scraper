@echo off
echo Installing required Python libraries...
python -m pip install --upgrade pip
pip install -r requirements.txt
echo Installation completed.
./install_playwright.sh
pause
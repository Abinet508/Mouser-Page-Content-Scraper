@echo off
echo Installing required Python libraries...
python -m pip install --upgrade pip
playwright install

echo Installation completed.
pause

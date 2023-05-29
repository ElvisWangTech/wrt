set PY_HOME="C:/Python311"
pyinstaller --clean --noconfirm --add-data "%PY_HOME%/Lib/site-packages/whisper/assets/*.*;whisper/assets" --add-data "WRT.ui;." --add-data "icons/*.*;icons" -w  WRT.py
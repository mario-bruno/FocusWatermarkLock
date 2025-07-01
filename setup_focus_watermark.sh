#!/bin/bash

APPNAME="Focus Watermark Lock"
PYFILE="focus_watermark_lock.py"
LOGO_PNG="logo_focus.png"
REQFILE="requirements.txt"

echo ""
echo "========== Focus Watermark Lock Setup =========="
echo "OS Detected: $(uname)"

# STEP 1: Ambiente virtuale
if [ ! -d "venv" ]; then
    echo "[*] Creo ambiente virtuale..."
    python3 -m venv venv || python -m venv venv
fi

# Attiva virtualenv
if [[ "$OSTYPE" == "darwin"* ]]; then
    source venv/bin/activate
else
    source venv/Scripts/activate
fi

# STEP 2: Dipendenze
echo "[*] Aggiorno pip e installo dipendenze..."
pip install --upgrade pip
pip install PyQt5 PyPDF2 watchdog reportlab pillow pyinstaller

# STEP 3: Icona
if [[ "$OSTYPE" == "darwin"* ]]; then
    # MAC: crea icon.icns se non esiste
    if [ ! -f "icon.icns" ]; then
        echo "[*] Creo icona .icns dal logo..."
        # Richiede logo_focus.png 1024x1024
        if [ ! -f "icon_1024x1024.png" ]; then
            cp "$LOGO_PNG" icon_1024x1024.png
        fi
        mkdir -p icon.iconset
        sips -z 16 16     icon_1024x1024.png --out icon.iconset/icon_16x16.png
        sips -z 32 32     icon_1024x1024.png --out icon.iconset/icon_16x16@2x.png
        sips -z 32 32     icon_1024x1024.png --out icon.iconset/icon_32x32.png
        sips -z 64 64     icon_1024x1024.png --out icon.iconset/icon_32x32@2x.png
        sips -z 128 128   icon_1024x1024.png --out icon.iconset/icon_128x128.png
        sips -z 256 256   icon_1024x1024.png --out icon.iconset/icon_128x128@2x.png
        sips -z 256 256   icon_1024x1024.png --out icon.iconset/icon_256x256.png
        sips -z 512 512   icon_1024x1024.png --out icon.iconset/icon_256x256@2x.png
        sips -z 512 512   icon_1024x1024.png --out icon.iconset/icon_512x512.png
        cp icon_1024x1024.png icon.iconset/icon_512x512@2x.png
        iconutil -c icns icon.iconset
        echo "    -> Creato icon.icns"
    fi
    ICON="--icon=icon.icns"
else
    # WINDOWS: controlla presenza icon.ico
    if [ ! -f "icon.ico" ]; then
        echo "[!] Non hai icon.ico. Creala su icoconvert.com dal logo_focus.png"
        ICON=""
    else
        ICON="--icon=icon.ico"
    fi
fi

# STEP 4: Compilazione con PyInstaller
echo "[*] Compilo l'app con PyInstaller..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    pyinstaller --noconfirm --windowed --name "$APPNAME" $ICON "$PYFILE"
    echo "-> Troverai l'app in dist/$APPNAME.app"
else
    pyinstaller --noconfirm --windowed --name "$APPNAME" $ICON "$PYFILE"
    echo "-> Troverai l'app in dist/$APPNAME.exe"
fi

echo ""
echo "========== Setup completato! =========="
echo "Per avviare in modalità portable: "
echo "    source venv/bin/activate && python $PYFILE"
echo ""

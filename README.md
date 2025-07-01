# Focus Watermark Lock

## Cos’è

Un’applicazione Python/Qt5 che aggiunge watermark ai PDF con logo Focus, blocca copia/modifica (ma non la visualizzazione), salva i file processati in una cartella dedicata, mantiene il conteggio, e funziona su macOS e Windows.

⸻

## Prerequisiti
	•	Python 3.10+ (Scarica qui)
	•	Pip installato (python -m ensurepip)
	•	Internet per installare i pacchetti
	•	(Solo per la compilazione in app/EXE: PyInstaller)

⸻

### 1. Preparazione Cartella di Lavoro
	1.	Crea una cartella chiamata ad esempio FocusWatermarkLock-macOS o FocusWatermarkLock-Windows.
	2.	Scarica/Salva in questa cartella:
	•	focus_watermark_lock.py (lo script principale)
	•	logo_focus.png (il logo ufficiale Focus, PNG, almeno 600x600 pixel consigliato)
	•	(Facoltativo, solo per icona personalizzata: icon.icns per Mac, icon.ico per Windows)
	•	Questo README.txt

⸻

### 2. Installazione automatica tramite script bash

(Consigliato per utenti che sanno usare il terminale/PowerShell/Git Bash)
	1.	Copia il file qui sotto come setup_focus_watermark.sh nella cartella di progetto:

<details>
<summary>Clicca per lo script <code>setup_focus_watermark.sh</code></summary>


#!/bin/bash

APPNAME="Focus Watermark Lock"
PYFILE="focus_watermark_lock.py"
LOGO_PNG="logo_focus.png"

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

</details>


	2.	Rendi eseguibile e lancia lo script:

chmod +x setup_focus_watermark.sh
./setup_focus_watermark.sh



⸻

## 3. Installazione manuale dipendenze (opzionale)

MacOS e Windows

Apri il terminale nella cartella di progetto e lancia:

python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows
pip install --upgrade pip
pip install PyQt5 PyPDF2 watchdog reportlab pillow


⸻

## 4. Creazione Icona

MacOS (.icns)
	•	Ridimensiona il logo a 1024x1024 px e salvalo come icon_1024x1024.png.
	•	Usa i comandi riportati nello script sopra (o nel punto 3 del vecchio README).

Windows (.ico)
	•	Vai su https://icoconvert.com/, carica il PNG e scarica l’icona.

⸻

## 5. Esecuzione diretta dell’app

python focus_watermark_lock.py

	•	Usa l’app in versione “portable”, senza installazione.

⸻

## 6. Creare la versione compilata

macOS:

pyinstaller --noconfirm --windowed --name "Focus Watermark Lock" --icon=icon.icns focus_watermark_lock.py

Troverai l’app pronta in dist/Focus Watermark Lock.app

Windows:

pyinstaller --noconfirm --windowed --name "Focus Watermark Lock" --icon=icon.ico focus_watermark_lock.py

Troverai l’eseguibile in dist/Focus Watermark Lock.exe

⸻

## 7. Uso dell’applicazione
	1.	Scegli la cartella da monitorare tramite il bottone.
	2.	Trascina i tuoi PDF nella cartella:
	•	Verranno watermarkati e salvati nella sottocartella Watermark
	•	Verranno bloccate le funzioni di copia/modifica (ma non la visualizzazione)
	•	Il contatore file è sempre visibile nella GUI.
	3.	Il programma ricorda la cartella scelta e i file processati anche tra riavvii.
	4.	Il pulsante “Ripulisci” svuota la lista a video (ma NON azzera il contatore).

⸻

## 8. FAQ & Risoluzione problemi
	•	Icona non visibile: verifica che sia .icns (Mac) o .ico (Windows) e che sia presente.
	•	Errore “no such file or directory: logo_focus.png”: il logo deve essere nella stessa cartella dello script/app.
	•	Permessi cartelle: assicurati di avere permessi di scrittura nella cartella monitorata.
	•	Dipendenze mancanti:

pip install PyQt5 PyPDF2 watchdog reportlab pillow


	•	Problemi di build PyInstaller: assicurati che tutte le icone e i file siano nella cartella di lavoro; se serve elimina la cartella build e dist e riprova.

⸻

## 9. Struttura della cartella finale

FocusWatermarkLock-OS/
│
├── focus_watermark_lock.py
├── logo_focus.png
├── icon.icns   # (solo Mac)
├── icon.ico    # (solo Windows)
├── requirements.txt  # (facoltativo)
├── README.txt
├── setup_focus_watermark.sh
└── focus_settings.db  # (generato al primo avvio)


⸻

## 10. Note aggiuntive
	•	L’app NON chiede password all’apertura dei PDF watermarkati.
	•	Il blocco di copia/modifica è quello standard dei PDF.
	•	Per modifiche estetiche o funzioni, puoi modificare il file focus_watermark_lock.py.

⸻

Buon lavoro con Focus Watermark Lock!
Per assistenza: contatta Mario!

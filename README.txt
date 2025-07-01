# Focus Watermark Lock

## Cos’è

Un’applicazione Python/Qt5 che aggiunge watermark ai PDF con logo Focus, blocca copia/modifica (ma non la visualizzazione), salva i file processati in una cartella dedicata, mantiene il conteggio, e funziona su macOS e Windows.

⸻

## Prerequisiti
	•	Python 3.10+ (scarica da python.org se non lo hai già)
	•	Pip installato (python -m ensurepip)
	•	Internet per installare i pacchetti
	•	(Solo per la compilazione in app/EXE: PyInstaller)

⸻

## 1. Preparazione Cartella di Lavoro
	1.	Crea una cartella chiamata ad esempio FocusWatermarkLock-macOS o FocusWatermarkLock-Windows.
	2.	Scarica/Salva in questa cartella:
	•	focus_watermark_lock.py (lo script principale)
	•	logo_focus.png (il logo ufficiale Focus in PNG, almeno 600x600 pixel consigliato)
	•	(facoltativo, solo per icona personalizzata: icon.icns per Mac, icon.ico per Windows)
	•	Questo README.txt

⸻

## 2. Installazione Dipendenze

MacOS e Windows

Apri il terminale nella cartella di progetto e lancia:

python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows
pip install --upgrade pip
pip install PyQt5 PyPDF2 watchdog reportlab pillow


⸻

## 3. Creazione dell’Icona

MacOS (.icns)
	1.	Ridimensiona il logo a 1024x1024 px e salvalo come icon_1024x1024.png.
	2.	Esegui:

mkdir icon.iconset
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


	3.	Troverai il file icon.icns nella cartella.

Windows (.ico)
	1.	Vai su https://icoconvert.com/
	2.	Carica il tuo logo PNG quadrato.
	3.	Seleziona dimensione massima (256x256 o più taglie).
	4.	Scarica e rinomina come icon.ico.

⸻

## 4. Esecuzione diretta dell’app

Avvia la GUI da terminale nella cartella:

python focus_watermark_lock.py

	•	Puoi subito usare l’app in versione “portable”, senza installazione.

⸻

## 5. Creare l’app compilata (.app su Mac, .exe su Windows)

MACOS: .app
	1.	Installa PyInstaller:

pip install pyinstaller


	2.	Compila la tua app:

pyinstaller --noconfirm --windowed --name "Focus Watermark Lock" --icon=icon.icns focus_watermark_lock.py


	3.	Trovi l’app pronta in:
dist/Focus Watermark Lock.app
	4.	(Facoltativo) Aggiungi all’avvio:
Preferenze di Sistema → Utenti e Gruppi → Elementi login → + → scegli la tua app.

WINDOWS: .exe
	1.	Installa PyInstaller:

pip install pyinstaller


	2.	Compila:

pyinstaller --noconfirm --windowed --name "Focus Watermark Lock" --icon=icon.ico focus_watermark_lock.py


	3.	Trovi l’eseguibile in:
dist/Focus Watermark Lock.exe
	4.	(Facoltativo) Aggiungi l’exe all’avvio automatico (cartella Esecuzione automatica di Windows o via Task Scheduler).

⸻

## 6. Uso dell’applicazione
	1.	Scegli la cartella da monitorare tramite il bottone.
	2.	Trascina i tuoi PDF nella cartella:
	•	Verranno watermarkati e salvati nella sottocartella Watermark
	•	Verranno bloccate le funzioni di copia/modifica (non la visualizzazione)
	•	Il contatore file è sempre visibile nella GUI.
	3.	Il programma ricorda la cartella scelta e i file processati anche tra riavvii.
	4.	Il pulsante “Ripulisci” svuota la lista dei file processati a video (ma NON azzera il contatore).

⸻

## 7. Risoluzione problemi
	•	Icona non visibile: verifica che sia .icns per Mac e .ico per Windows, e che sia referenziata correttamente.
	•	Dipendenze mancanti:
Installa di nuovo le librerie richieste:

pip install PyQt5 PyPDF2 watchdog reportlab pillow


	•	Permessi cartelle:
Assicurati di avere permessi di scrittura nella cartella monitorata.
	•	Errore “no such file or directory: logo_focus.png”:
Assicurati che il logo sia presente e correttamente nominato nella stessa cartella dello script/app.

⸻

## 8. Struttura della cartella finale

FocusWatermarkLock-OS/
│
├── focus_watermark_lock.py
├── logo_focus.png
├── icon.icns   # (solo Mac)
├── icon.ico    # (solo Windows)
├── requirements.txt  # (facoltativo)
├── README.txt
└── focus_settings.db  # (generato al primo avvio)


⸻

## 9. Dipendenze (requirements.txt esempio)

PyQt5
PyPDF2
watchdog
reportlab
pillow


⸻

## 10. Note aggiuntive
	•	L’app NON chiede password all’apertura dei PDF watermarkati.
	•	Il blocco di copia/modifica è quello standard dei PDF, non è inviolabile per chi usa software avanzati, ma è efficace con Acrobat/Preview.
	•	Per modifiche estetiche o funzioni, puoi modificare il file focus_watermark_lock.py.

⸻

Buon lavoro con Focus Watermark Lock!
Per assistenza: contatta Mario!

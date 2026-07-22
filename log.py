import logging
import os
import zipfile
import shutil
from datetime import datetime

LOG_DIR = "logs/current"
ARCHIVE_DIR = "logs/archive"

os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(ARCHIVE_DIR, exist_ok=True)

def archive_old_logs():
    """
    Zippt alle vorhandenen Logdateien aus logs/current
    und verschiebt sie nach logs/archive.
    """
    for filename in os.listdir(LOG_DIR):
        if filename.endswith(".log"):
            logfile = os.path.join(LOG_DIR, filename)

            zip_name = os.path.join(
                ARCHIVE_DIR,
                filename.replace(".log", ".zip")
            )

            with zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(logfile, arcname=filename)

            os.remove(logfile)


def setup_logging():
    archive_old_logs()

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)-8s - %(name)-10s - %(message)s"
    )

    # Hauptlogger konfigurieren
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    # Konsolenlog
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Für jedes Modul eine eigene Logdatei
    modules = ["server", "client", "network", "game"]

    for module in modules:
        file_handler = logging.FileHandler(
            os.path.join(LOG_DIR, f"{timestamp}_{module}.log"),
            encoding="utf-8"
        )
        file_handler.setFormatter(formatter)

        logger = logging.getLogger(module)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)
        logger.propagate = True   # gleichzeitig auch auf Konsole ausgeben
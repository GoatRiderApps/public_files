from datetime import datetime
from functools import lru_cache
import shutil
import httpx
from loguru import logger
import os
import sys
import subprocess
from tqdm import tqdm
import asyncio

if getattr(sys, "frozen", False):
    base_path = os.path.dirname(sys.executable)
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

EXE_FILE = "JpkXmlReader.exe"
EXE_LATEST = "JpkXmlReader_latest.exe"
templates_path = os.path.join(base_path, "templates")
version_file_path = os.path.join(templates_path, "version")
exe_path = os.path.join(base_path, EXE_FILE)

logger.add("logs.log", rotation="1MiB", level="DEBUG", enqueue=True)

VERSION = "1.0.0"
RELASE_DATE = datetime(2026, 2, 19)


@lru_cache
def get_latest_version_from_repo() -> str:
    r = httpx.get(
        "https://raw.githubusercontent.com/GoatRiderApps/public_files/main/jpk_xml/latest"
    )

    if r.status_code != 200:
        logger.error(
            f"Problem z pobraniem informacji o najnowszej wersji:\n{r.status_code}"
        )
        return ()

    return r.text.strip()


async def get_exe_from_repo():
    kill_old_processes()
    logger.info("Rozpoczynam ściąganie")
    exe_version = get_latest_version_from_repo()
    exe_url = f"https://raw.githubusercontent.com/GoatRiderApps/public_files/main/jpk_xml/{exe_version}/JpkXmlReader_v{exe_version}.exe"

    async with httpx.AsyncClient(timeout=30) as client:
        async with client.stream("GET", exe_url) as response:
            response.raise_for_status()
            total = int(response.headers.get("Content-Length", 0))

            with (
                open(EXE_LATEST, "wb") as ef,
                tqdm(
                    total=total,
                    unit="B",
                    unit_scale=True,
                    unit_divisor=1024,
                    desc="Downloading",
                ) as progress,
            ):
                async for chunk in response.aiter_bytes(chunk_size=8192):
                    if chunk:
                        ef.write(chunk)
                        progress.update(len(chunk))
    logger.info(f"Ściąganie EXE zakończone. Total size: {total}bytes")


def is_new_version():
    web_version = get_latest_version_from_repo()

    if not os.path.exists(version_file_path):
        logger.info("Plik z wersją nie istnieje")
        version_from_file = "0.0.0"
    else:
        logger.info("Plik z wersją znaleziony - pobieram wpis")
        with open(version_file_path, "r") as rf:
            version_from_file = rf.read().strip()

    v1 = tuple(map(int, version_from_file.split(".")))
    v2 = tuple(map(int, web_version.split(".")))

    return v2 > v1


def kill_old_processes():
    result = subprocess.run(
        ["tasklist", "/FI", f"IMAGENAME eq {EXE_FILE}"], capture_output=True, text=True
    )

    if EXE_FILE in result.stdout:
        logger.info(f"{EXE_FILE} działa jako proces - ubijam")
        subprocess.run(["taskkill", "/F", "/IM", EXE_FILE])


def replace_execs():
    kill_old_processes()

    try:
        os.remove(EXE_FILE)
        logger.info(f"{EXE_FILE} usunięty")
    except Exception as e:
        logger.error(f"Nie mogę usunąć pliku: {EXE_FILE}\nBłąd: {e}")

    try:
        shutil.move(EXE_LATEST, EXE_FILE)
        logger.info("Update wersji zakończony")
    except Exception as e:
        logger.error(
            f"Nie mogę zakończyć updatu pliku z {EXE_LATEST} do {EXE_FILE}\nBłąd: {e}"
        )


def run_exe():
    kill_old_processes()
    subprocess.Popen(exe_path, close_fds=True)


def get_answer() -> bool:
    answer = input("Jest dostępna nowa wersja. Pobrać? T/[N] -> ")
    if answer.lower().strip() in ("t", "y"):
        return True
    return False


async def main():
    if not is_new_version():
        run_exe()
        sys.exit(0)

    if not get_answer():
        run_exe()
    else:
        await get_exe_from_repo()
        print("Pobrano plik. Zamieniam")
        replace_execs()
        run_exe()


if __name__ == "__main__":
    asyncio.run(main())
    # kill_old_processes()

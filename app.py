from datetime import datetime
import httpx
from loguru import logger

logger.add("logs.log", roatiotn="1M", level="DEBUG", enqueue=True)

VERSION = "0.1.0"
RELASE_DATE = datetime(2026, 2, 19)


def get_latest_version_from_repo() -> tuple[int, int, int]:
    r = httpx.get('https://github.com/GoatRiderApps/public_files/jpk_xml/latest')

    if r.status_code != 200:
        logger.error(f"Problem z pobraniem informacji o najnowszej wersji:\n{r.status_code}")
        return ()

    print(r.text)

def main():
    print("Hello from repo-with-public-files!")


if __name__ == "__main__":
    main()

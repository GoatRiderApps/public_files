import tomllib
from pathlib import Path
import re
from datetime import datetime

# ścieżki
pyproject = Path("pyproject.toml")
app_file = Path("app.py")

# odczyt wersji z pyproject.toml
data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
version = data["project"]["version"]
release_date = datetime.now()

# podmiana w app.py
content = app_file.read_text(encoding="utf-8")
content = re.sub(r'VERSION\s*=\s*".*?"', f'VERSION = "{version}"', content)
content = re.sub(
    r"RELASE_DATE\s*=\s*datetime\(\s*\d{4}\s*,\s*\d{1,2}\s*,\s*\d{1,2}\s*\)",
    f"RELASE_DATE = datetime({release_date.year}, {release_date.month}, {release_date.day})",
    content,
)
app_file.write_text(content, encoding="utf-8")

with open(".env", "w", encoding="utf-8") as vf:
    vf.write(f'VERSION = "{version}"\n')

with open("releases/latest", "w", encoding="utf8") as wf:
    wf.write(version)

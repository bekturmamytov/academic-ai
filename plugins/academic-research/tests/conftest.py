import shutil
import struct
import sys
import zlib
from pathlib import Path

import pytest

PLUGIN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN / "scripts"))

FIXTURES = Path(__file__).parent / "fixtures"


def png(w: int = 40, h: int = 20) -> bytes:
    raw = b"".join(b"\x00" + b"\xcc\xcc\xcc" * w for _ in range(h))

    def chunk(tag, data):
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))


@pytest.fixture
def workspace(tmp_path: Path) -> Path:
    """Рабочая папка преподавателя: profile.yaml + работа из примера и тестовых глав."""
    (tmp_path / "profile.yaml").write_text(
        'name: "Иванов Иван Иванович"\n'
        'university: "Кыргызский государственный технический университет им. И. Раззакова"\n'
        'faculty: "Энергетический факультет"\ndepartment: "Теплоэнергетика"\ncity: "Бишкек"\nlanguage: ru\n',
        encoding="utf-8")
    work = tmp_path / "work"
    shutil.copytree(FIXTURES / "work", work)
    shutil.copy(PLUGIN / "templates" / "work.example.yaml", work / "work.yaml")
    (work / "figures").mkdir()
    (work / "figures" / "stand.png").write_bytes(png())
    return work


def set_yaml(path: Path, **changes) -> None:
    import yaml
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    data.update(changes)
    path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")

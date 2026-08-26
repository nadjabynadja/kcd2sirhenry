#!/usr/bin/env python3
"""Build the Sir Henry Kobyla Regalia compatibility PAK deterministically."""

from __future__ import annotations

import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "sir_henry_kobyla_regalia"
OUTPUT = ROOT / "sir_henry_kobyla_regalia" / "Data" / "sir_henry_kobyla_regalia.pak"
MEMBERS = {
    SOURCE / "Libs/Tables/item/InventoryPreset__sir_henry_kobyla_regalia.xml":
        "Libs/Tables/item/InventoryPreset__sir_henry_kobyla_regalia.xml",
    SOURCE / "Libs/Tables/item/clothing_preset__sir_henry_kobyla_regalia.xml":
        "Libs/Tables/item/clothing_preset__sir_henry_kobyla_regalia.xml",
}


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(OUTPUT, "w", compression=zipfile.ZIP_STORED) as pak:
        for source, archive_name in sorted(MEMBERS.items(), key=lambda pair: pair[1]):
            info = zipfile.ZipInfo(archive_name, date_time=(2026, 8, 25, 0, 0, 0))
            info.compress_type = zipfile.ZIP_STORED
            info.external_attr = 0o100644 << 16
            pak.writestr(info, source.read_bytes())
    print(f"Built {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

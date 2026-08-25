#!/usr/bin/env python3
"""Validate the recovered Sir Henry of Skalitz release artifacts."""

from __future__ import annotations

import hashlib
import re
import struct
import sys
import zipfile
from collections import Counter
from pathlib import Path, PurePosixPath
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "sir_henry_of_skalitz"
OPTIONAL = ROOT / "sir_henry_quests"
LOCALIZATION = MAIN / "Localization"
TABLES_PAK = OPTIONAL / "Data" / "Tables.pak"
RECOVERED_CHECKSUMS = ROOT / "upstream" / "recovered-release.sha256"

LANGUAGES = (
    "chineses",
    "chineset",
    "czech",
    "english",
    "french",
    "german",
    "italian",
    "japanese",
    "korean",
    "polish",
    "portuguese",
    "russian",
    "spanish",
    "turkish",
    "ukrainian",
    "vietnamese",
)
LOCALIZATION_FILES = (
    "text_ui_dialog.xml",
    "text_ui_misc.xml",
    "text_ui_quest.xml",
    "text_ui_soul.xml",
)
TABLE_FILES = (
    "Libs/Tables/item/clothing_preset__player.xml",
    "Libs/Tables/rpg/buff__sirhenry.xml",
    "Libs/Tables/rpg/perk__sirhenry.xml",
    "Libs/Tables/rpg/perk_buff.xml",
    "Libs/Tables/rpg/reputation_change.xml",
    "Libs/Tables/rpg/rpg_param.xml",
)
EXPECTED_CLIPS = 300
CUSTOM_PERK_ID = "a5117e17-0d1a-4b19-9f00-5127486b0001"
CUSTOM_BUFF_ID = "a5117e17-0d1a-4b19-9f00-5127486b0002"
MODID_RE = re.compile(r"^[a-z][a-z0-9_]*$")


class Audit:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.checks = 0

    def require(self, condition: bool, message: str) -> None:
        self.checks += 1
        if not condition:
            self.errors.append(message)

    def warn(self, condition: bool, message: str) -> None:
        self.checks += 1
        if not condition:
            self.warnings.append(message)


def safe_member(name: str) -> bool:
    path = PurePosixPath(name)
    return not path.is_absolute() and ".." not in path.parts and "\\" not in name


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def open_pak(path: Path, audit: Audit) -> zipfile.ZipFile | None:
    audit.require(path.is_file(), f"missing archive: {path.relative_to(ROOT)}")
    if not path.is_file():
        return None
    try:
        pak = zipfile.ZipFile(path)
    except (OSError, zipfile.BadZipFile) as exc:
        audit.require(False, f"cannot open {path.relative_to(ROOT)}: {exc}")
        return None

    label = path.relative_to(ROOT)
    infos = pak.infolist()
    audit.require(bool(infos), f"empty archive: {label}")
    audit.require(
        all(safe_member(info.filename) for info in infos),
        f"unsafe member path in {label}",
    )
    audit.require(
        all(info.compress_type == zipfile.ZIP_STORED for info in infos),
        f"{label} must use stored/uncompressed ZIP entries",
    )
    bad = pak.testzip()
    audit.require(bad is None, f"CRC failure in {label}: {bad}")
    return pak


def parse_xml(data: bytes, label: str, audit: Audit) -> ET.Element | None:
    try:
        return ET.fromstring(data)
    except ET.ParseError as exc:
        audit.require(False, f"invalid XML in {label}: {exc}")
        return None


def validate_manifests(audit: Audit) -> None:
    versions: set[str] = set()
    expected = ((MAIN, "sir_henry_of_skalitz"), (OPTIONAL, "sir_henry_quests"))
    for directory, expected_modid in expected:
        path = directory / "mod.manifest"
        audit.require(path.is_file(), f"missing manifest: {path.relative_to(ROOT)}")
        if not path.is_file():
            continue
        try:
            root = ET.parse(path).getroot()
        except ET.ParseError as exc:
            audit.require(False, f"invalid manifest XML in {path.relative_to(ROOT)}: {exc}")
            continue
        audit.require(root.tag == "kcd_mod", f"unexpected root in {path.relative_to(ROOT)}")
        info = root.find("info")
        audit.require(info is not None, f"missing info block in {path.relative_to(ROOT)}")
        if info is None:
            continue
        values = {child.tag: (child.text or "").strip() for child in info}
        for field in ("name", "modid", "description", "author", "version", "created_on"):
            audit.require(bool(values.get(field)), f"missing {field} in {path.relative_to(ROOT)}")
        modid = values.get("modid", "")
        audit.require(modid == expected_modid, f"modid mismatch in {path.relative_to(ROOT)}")
        audit.require(bool(MODID_RE.fullmatch(modid)), f"invalid modid in {path.relative_to(ROOT)}")
        audit.require(values.get("modifies_level") == "false", f"unexpected modifies_level in {path.relative_to(ROOT)}")
        if values.get("version"):
            versions.add(values["version"])
    audit.require(len(versions) == 1, f"module versions do not match: {sorted(versions)}")
    audit.require((OPTIONAL / "README.md").is_file(), "optional module README is missing")


def validate_recovered_checksums(audit: Audit) -> None:
    audit.require(RECOVERED_CHECKSUMS.is_file(), "recovered release checksum list is missing")
    if not RECOVERED_CHECKSUMS.is_file():
        return
    for number, line in enumerate(RECOVERED_CHECKSUMS.read_text(encoding="ascii").splitlines(), 1):
        if not line.strip():
            continue
        try:
            expected, relative = line.split(None, 1)
        except ValueError:
            audit.require(False, f"malformed checksum line {number}")
            continue
        path = ROOT / relative.strip()
        audit.require(path.is_file(), f"checksum target is missing: {relative}")
        if path.is_file():
            actual = file_sha256(path)
            audit.require(actual == expected, f"recovered artifact changed: {relative}")


def xml_archive_path(language: str) -> Path:
    # The release uses title case except for the two Chinese identifiers.
    name = language.capitalize() + "_xml.pak"
    return LOCALIZATION / name


def validate_localization(audit: Audit) -> None:
    expected_paks = {xml_archive_path(lang).name for lang in LANGUAGES}
    actual_paks = {path.name for path in LOCALIZATION.glob("*_xml.pak")}
    audit.require(actual_paks == expected_paks, f"localization PAK set differs: expected={sorted(expected_paks)} actual={sorted(actual_paks)}")

    baseline_counts: dict[str, int] | None = None
    baseline_keys: dict[str, set[str]] | None = None
    for language in LANGUAGES:
        path = xml_archive_path(language)
        pak = open_pak(path, audit)
        if pak is None:
            continue
        with pak:
            names = tuple(sorted(pak.namelist()))
            audit.require(names == LOCALIZATION_FILES, f"unexpected members in {path.name}: {names}")
            counts: dict[str, int] = {}
            keys_by_file: dict[str, set[str]] = {}
            for name in LOCALIZATION_FILES:
                if name not in pak.namelist():
                    continue
                root = parse_xml(pak.read(name), f"{path.name}/{name}", audit)
                if root is None:
                    continue
                audit.require(root.tag == "Table", f"unexpected root in {path.name}/{name}")
                rows = root.findall("Row")
                keys: list[str] = []
                bad_shapes = 0
                for row in rows:
                    cells = row.findall("Cell")
                    if len(cells) != 3:
                        bad_shapes += 1
                        continue
                    keys.append(cells[0].text or "")
                counts[name] = len(rows)
                keys_by_file[name] = set(keys)
                audit.require(bad_shapes == 0, f"{bad_shapes} malformed rows in {path.name}/{name}")
                audit.require(len(keys) == len(set(keys)), f"duplicate localization keys in {path.name}/{name}")
                audit.require(all(keys), f"empty localization key in {path.name}/{name}")
            if baseline_counts is None:
                baseline_counts = counts
                baseline_keys = keys_by_file
            else:
                audit.require(counts == baseline_counts, f"row-count drift in {path.name}: {counts}")
                for name in LOCALIZATION_FILES:
                    audit.require(keys_by_file.get(name) == baseline_keys.get(name), f"key-set drift in {path.name}/{name}")


def vorbis_identity(data: bytes) -> tuple[int, int] | None:
    marker = data.find(b"\x01vorbis")
    # identification header: marker, version u32, channels u8, sample rate u32
    if marker < 0 or len(data) < marker + 16:
        return None
    channels = data[marker + 11]
    sample_rate = struct.unpack_from("<I", data, marker + 12)[0]
    return channels, sample_rate


def validate_voice(audit: Audit) -> None:
    expected_paks = {f"{lang}.pak" for lang in LANGUAGES}
    actual_paks = {path.name for path in LOCALIZATION.glob("*.pak") if not path.name.endswith("_xml.pak")}
    audit.require(actual_paks == expected_paks, f"voice PAK set differs: expected={sorted(expected_paks)} actual={sorted(actual_paks)}")

    baseline_paths: tuple[str, ...] | None = None
    for language in LANGUAGES:
        path = LOCALIZATION / f"{language}.pak"
        pak = open_pak(path, audit)
        if pak is None:
            continue
        with pak:
            names = tuple(sorted(pak.namelist()))
            audit.require(len(names) == EXPECTED_CLIPS, f"{path.name} has {len(names)} clips, expected {EXPECTED_CLIPS}")
            audit.require(len(names) == len(set(names)), f"duplicate member paths in {path.name}")
            audit.require(all(name.endswith(".ogg") for name in names), f"non-Ogg member in {path.name}")
            if baseline_paths is None:
                baseline_paths = names
            else:
                audit.require(names == baseline_paths, f"voice-path drift in {path.name}")

            payload_hashes: list[bytes] = []
            bad_headers = 0
            bad_format = 0
            for name in names:
                data = pak.read(name)
                if not data.startswith(b"OggS"):
                    bad_headers += 1
                if vorbis_identity(data) != (1, 48_000):
                    bad_format += 1
                payload_hashes.append(hashlib.sha256(data).digest())
            audit.require(bad_headers == 0, f"{bad_headers} invalid Ogg headers in {path.name}")
            audit.require(bad_format == 0, f"{bad_format} clips are not mono 48 kHz Vorbis in {path.name}")
            audit.warn(len(payload_hashes) == len(set(payload_hashes)), f"duplicate audio payloads in {path.name}")


def duplicate_attribute(rows: list[ET.Element], attribute: str) -> list[str]:
    values = [row.get(attribute, "") for row in rows]
    return sorted(value for value, count in Counter(values).items() if value and count > 1)


def validate_tables(audit: Audit) -> None:
    pak = open_pak(TABLES_PAK, audit)
    if pak is None:
        return
    with pak:
        names = tuple(sorted(pak.namelist()))
        audit.require(names == TABLE_FILES, f"unexpected table members: {names}")
        roots: dict[str, ET.Element] = {}
        for name in TABLE_FILES:
            if name in pak.namelist():
                root = parse_xml(pak.read(name), f"Tables.pak/{name}", audit)
                if root is not None:
                    roots[name] = root
                    audit.require(root.tag == "database", f"unexpected root in Tables.pak/{name}")

        primary_keys = {
            "Libs/Tables/rpg/buff__sirhenry.xml": "buff_id",
            "Libs/Tables/rpg/reputation_change.xml": "reputation_change_id",
            "Libs/Tables/rpg/rpg_param.xml": "rpg_param_key",
            "Libs/Tables/rpg/perk__sirhenry.xml": "perk_id",
            "Libs/Tables/item/clothing_preset__player.xml": "clothing_preset_id",
        }
        for name, attribute in primary_keys.items():
            root = roots.get(name)
            if root is None or not list(root):
                continue
            rows = list(list(root)[0])
            duplicates = duplicate_attribute(rows, attribute)
            audit.require(not duplicates, f"duplicate {attribute} values in {name}: {duplicates}")

        perk_root = roots.get("Libs/Tables/rpg/perk__sirhenry.xml")
        buff_root = roots.get("Libs/Tables/rpg/buff__sirhenry.xml")
        link_root = roots.get("Libs/Tables/rpg/perk_buff.xml")
        perk_ids = {row.get("perk_id") for row in list(list(perk_root)[0])} if perk_root is not None else set()
        buff_ids = {row.get("buff_id") for row in list(list(buff_root)[0])} if buff_root is not None else set()
        links = {(row.get("perk_id"), row.get("buff_id")) for row in list(list(link_root)[0])} if link_root is not None else set()
        audit.require(CUSTOM_PERK_ID in perk_ids, "custom Sir Henry perk is missing")
        audit.require(CUSTOM_BUFF_ID in buff_ids, "custom Sir Henry buff is missing")
        audit.require((CUSTOM_PERK_ID, CUSTOM_BUFF_ID) in links, "custom perk-to-buff link is missing")


def main() -> int:
    audit = Audit()
    print("Validating manifests...")
    validate_manifests(audit)
    print("Validating recovered release checksums...")
    validate_recovered_checksums(audit)
    print("Validating 16 localization archives...")
    validate_localization(audit)
    print("Validating 4,800 voice clips...")
    validate_voice(audit)
    print("Validating gameplay tables...")
    validate_tables(audit)

    for warning in audit.warnings:
        print(f"WARNING: {warning}", file=sys.stderr)
    for error in audit.errors:
        print(f"ERROR: {error}", file=sys.stderr)
    print(f"Completed {audit.checks} checks: {len(audit.errors)} error(s), {len(audit.warnings)} warning(s).")
    return 1 if audit.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())

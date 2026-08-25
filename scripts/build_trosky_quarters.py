#!/usr/bin/env python3
"""Build the Linux-native Trosky quarters level patch deterministically.

The builder consumes a legally installed/extracted vanilla trosecko level.pak.
It deliberately patches exported XML rather than requiring the Windows editor.
"""

from __future__ import annotations

import argparse
import binascii
import hashlib
import struct
import zipfile
import zlib
from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "sir_henry_trosky_quarters" / "Data" / "Levels" / "trosecko" / "level.pak"
DEFAULT_LEVEL_PAK = Path("/run/media/nadja/vol1/Game Mods Dev/KCD 2/tables/Levels/trosecko/level.pak")
EXPECTED_LEVEL_PAK_SHA256 = "39936765768694ec55c457af5d355d62be60812f60f6047d71797094aec3afb9"
EXPECTED_MEMBER_SHA256 = {
    "objects_mission0.xml": "624b51dcc0a04ac21b12e04dced99567bc151c7311ee560d9bc467559199969f",
    "layers/playerstash_7f1869a5-bf84-4a5b-bc82-e40d93f860b9.xml": "fd7ab2f33de6eaf9b74d12d6f6b93898933f39c30678ec864ee6bd9695f836bc",
    "layers/other_a067eb13-56b1-4ceb-ac63-86e03d8e7706.xml": "03d816e7e8ffef84bb475ae40d713024d8d2af4c7099993651b4d725cc618ae5",
    "tables/ai/scheduler.xml": "4099097c8ca3bf8c54e27db85d5858061cd2036338fcee84981235679db0c6fd",
}
MEMBERS = tuple(EXPECTED_MEMBER_SHA256)

# Vanilla entities selected after tracing quest aliases, home links, and souls.
OLD_BED_ID = "42143"
OLD_TRIGGER_ID = "42144"
NEW_BED_ID = "39429"
NEW_TRIGGER_ID = "39430"
NEW_CHEST_ID = "39579"
NEW_CHEST_HOLDER_ID = "39580"
SHARED_GUARD_ARMORY_ID = "39498"
TOUR_TAGPOINT_ID = "38591"
GUARD_ID = "194586"  # ttro_man_26 / char_GENERIC_MAN_GUARD_18
OLD_GUARD_HOME_ID = "17958"
NEW_GUARD_HOME_ID = "32968"

OLD_STASH_POS = "2401.348,2587.609,210.0882"
OLD_STASH_ROTATE = "-0.139173,0,0,0.9902681"
NEW_STASH_POS = "2515.261,2597.491,183.538"
NEW_STASH_ROTATE = "-0.3907312,0,0,0.9205048"
OLD_STASH_LAYER = "Main/ttro_trosky/castle/courtyard2/_common/playerStash"
NEW_STASH_LAYER = "Main/ttro_trosky/lowerCastle/courtyard4/_common/playerStash"
OLD_GUARD_CHEST_LAYER = "Main/ttro_trosky/castle/courtyard2/_common"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_member(pak_path: Path, member: str) -> bytes:
    """Read a member while tolerating retail slash differences.

    Some retail KCD II PAKs use forward slashes in the central directory but
    backslashes in local headers. Python 3.14 rejects that mismatch, so this
    reads and validates the entry from its local-header offset.
    """

    with zipfile.ZipFile(pak_path) as pak:
        info = pak.getinfo(member)
        if info.compress_type not in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED):
            raise ValueError(f"unsupported compression method for {member}: {info.compress_type}")
        with pak_path.open("rb") as stream:
            stream.seek(info.header_offset)
            header = stream.read(30)
            fields = struct.unpack("<IHHHHHIIIHH", header)
            signature, compression, name_length, extra_length = fields[0], fields[3], fields[-2], fields[-1]
            if signature != 0x04034B50 or compression != info.compress_type:
                raise ValueError(f"invalid local ZIP header for {member}")
            stream.seek(name_length + extra_length, 1)
            payload = stream.read(info.compress_size)
        data = payload if compression == zipfile.ZIP_STORED else zlib.decompress(payload, -zlib.MAX_WBITS)
        if len(data) != info.file_size or (binascii.crc32(data) & 0xFFFFFFFF) != info.CRC:
            raise ValueError(f"size/CRC mismatch while reading {member}")
        return data


def replace_once(data: bytes, old: bytes, new: bytes, label: str) -> bytes:
    count = data.count(old)
    if count != 1:
        raise ValueError(f"{label}: expected one match, found {count}")
    return data.replace(old, new, 1)


def entity_block(data: bytes, entity_id: str) -> tuple[int, int, bytes]:
    marker = f'EntityId="{entity_id}"'.encode()
    if data.count(marker) != 1:
        raise ValueError(f"entity {entity_id}: expected one declaration")
    at = data.index(marker)
    start = data.rfind(b"\t<Entity ", 0, at)
    end = data.index(b"\n\t</Entity>", at) + len(b"\n\t</Entity>")
    if start < 0:
        raise ValueError(f"entity {entity_id}: start not found")
    return start, end, data[start:end]


def update_entity(data: bytes, entity_id: str, transform) -> bytes:
    start, end, block = entity_block(data, entity_id)
    changed = transform(block)
    if changed == block:
        raise ValueError(f"entity {entity_id}: transform made no change")
    return data[:start] + changed + data[end:]


def patch_objects(data: bytes) -> bytes:
    # Every quest-facing alias follows Henry to the guard-barracks bed.
    aliases = (
        ("bed_playerRoomTrosky", OLD_BED_ID, NEW_BED_ID),
        ("playersBed", OLD_BED_ID, NEW_BED_ID),
        ("bed_playerRoom", OLD_BED_ID, NEW_BED_ID),
        ("playersBed_interactor", OLD_TRIGGER_ID, NEW_TRIGGER_ID),
    )
    for alias, old, new in aliases:
        data = replace_once(
            data,
            f'<Link TargetId="{old}" TargetGuid="00000000-0000-0000" Name="asset[&apos;{alias}&apos;]" />'.encode(),
            f'<Link TargetId="{new}" TargetGuid="00000000-0000-0000" Name="asset[&apos;{alias}&apos;]" />'.encode(),
            f"quest alias {alias}",
        )

    equipment_lines: list[bytes] = []

    def patch_new_bed(block: bytes) -> bytes:
        nonlocal equipment_lines
        lines = block.splitlines(keepends=True)
        equipment_lines = [line for line in lines if b"#ChangeEquipment[" in line]
        if len(equipment_lines) != 4 or any(f'TargetId="{NEW_CHEST_ID}"'.encode() not in line for line in equipment_lines):
            raise ValueError("new bed: unexpected equipment links")
        block = b"".join(line for line in lines if line not in equipment_lines)
        return replace_once(block, b'esSleepQuality="medium"', b'esSleepQuality="high"', "new bed quality")

    data = update_entity(data, NEW_BED_ID, patch_new_bed)

    # Ten other communal bunks used the selected bedside chest. Preserve their
    # sleep equipment behavior by redirecting them to the existing guard
    # armory chest already used by this guard cohort.
    shared_prefix = f'TargetId="{NEW_CHEST_ID}" TargetGuid="00000000-0000-0000" Name="#ChangeEquipment['.encode()
    armory_prefix = f'TargetId="{SHARED_GUARD_ARMORY_ID}" TargetGuid="00000000-0000-0000" Name="#ChangeEquipment['.encode()
    if data.count(shared_prefix) != 40:
        raise ValueError(f"shared guard beds: expected 40 remaining equipment links, found {data.count(shared_prefix)}")
    data = data.replace(shared_prefix, armory_prefix)

    def patch_old_bed(block: bytes) -> bytes:
        block = replace_once(block, b'esSleepQuality="high"', b'esSleepQuality="medium"', "old bed quality")
        insert = b"".join(equipment_lines)
        return replace_once(block, b"\t\t</EntityLinks>", insert + b"\t\t</EntityLinks>", "old bed equipment links")

    data = update_entity(data, OLD_BED_ID, patch_old_bed)

    def patch_new_trigger(block: bytes) -> bytes:
        return replace_once(
            block,
            b'<Properties InteractorPriorityOverride="1">',
            b'<Properties InteractorPriorityOverride="1" bQuestSystemTrigger="1">',
            "new quest bed trigger",
        )

    def patch_old_trigger(block: bytes) -> bytes:
        return replace_once(block, b' bQuestSystemTrigger="1"', b"", "old quest bed trigger")

    data = update_entity(data, NEW_TRIGGER_ID, patch_new_trigger)
    data = update_entity(data, OLD_TRIGGER_ID, patch_old_trigger)

    # The physical guard chest moves to Henry's former stash position.
    def move_guard_chest(block: bytes) -> bytes:
        block = replace_once(block, f'Pos="{NEW_STASH_POS}"'.encode(), f'Pos="{OLD_STASH_POS}"'.encode(), "guard chest position")
        block = replace_once(block, f'Rotate="{NEW_STASH_ROTATE}"'.encode(), f'Rotate="{OLD_STASH_ROTATE}"'.encode(), "guard chest rotation")
        return replace_once(
            block,
            b'EditorLayer="Main/ttro_trosky/lowerCastle/courtyard4/_common"',
            f'EditorLayer="{OLD_GUARD_CHEST_LAYER}"'.encode(),
            "guard chest layer",
        )

    data = update_entity(data, NEW_CHEST_ID, move_guard_chest)
    data = update_entity(data, NEW_CHEST_HOLDER_ID, move_guard_chest)

    # Keep the chamberlain's room-tour destination aligned with the new room.
    def move_tour_tagpoint(block: bytes) -> bytes:
        block = replace_once(block, b'Pos="2399.947,2591.579,210.022"', b'Pos="2514.44,2597.225,183.5139"', "tour tagpoint position")
        return replace_once(
            block,
            b'Rotate="-0.9956101,5.8349e-08,2.778016e-09,-0.09359193"',
            b'Rotate="0.9335804,0,0,-0.358368"',
            "tour tagpoint rotation",
        )

    data = update_entity(data, TOUR_TAGPOINT_ID, move_tour_tagpoint)
    ET.fromstring(data)
    return data


def patch_player_stash(data: bytes) -> bytes:
    if data.count(f'Pos="{OLD_STASH_POS}"'.encode()) != 2:
        raise ValueError("player stash: expected two entities at the vanilla position")
    if data.count(f'Rotate="{OLD_STASH_ROTATE}"'.encode()) != 2:
        raise ValueError("player stash: expected two vanilla rotations")
    data = data.replace(f'Pos="{OLD_STASH_POS}"'.encode(), f'Pos="{NEW_STASH_POS}"'.encode())
    data = data.replace(f'Rotate="{OLD_STASH_ROTATE}"'.encode(), f'Rotate="{NEW_STASH_ROTATE}"'.encode())
    if data.count(f'EditorLayer="{OLD_STASH_LAYER}"'.encode()) != 2:
        raise ValueError("player stash: unexpected layer count")
    data = data.replace(f'EditorLayer="{OLD_STASH_LAYER}"'.encode(), f'EditorLayer="{NEW_STASH_LAYER}"'.encode())
    ET.fromstring(data)
    return data


def patch_guard_layer(data: bytes) -> bytes:
    start, end, block = entity_block(data, GUARD_ID)
    old = f'<Link TargetId="{OLD_GUARD_HOME_ID}" TargetGuid="00000000-0000-0000" Name="_!home" />'.encode()
    new = f'<Link TargetId="{NEW_GUARD_HOME_ID}" TargetGuid="00000000-0000-0000" Name="_!home" />'.encode()
    block = replace_once(block, old, new, "guard home link")
    data = data[:start] + block + data[end:]
    ET.fromstring(data)
    return data


def guid64_decimal(guid: str) -> str:
    first, second, third = guid.split("-")
    return str(int(third + second + first, 16))


def patch_scheduler(data: bytes) -> bytes:
    source = guid64_decimal("ecf8b1c1-91ac-4135")
    old_home = guid64_decimal("f03c4f32-9c2f-4c4e")
    new_home = guid64_decimal("8601be80-fa9e-4eb9")
    marker = f'<C_SmartHub EntityGuid="{source}"'.encode()
    if data.count(marker) != 1:
        raise ValueError("scheduler: guard hub not found exactly once")
    start = data.index(marker)
    end = data.index(b"\n\t\t</C_SmartHub>", start) + len(b"\n\t\t</C_SmartHub>")
    block = data[start:end]
    if block.count(b'AILinkHome="true"') != 1:
        raise ValueError("scheduler: selected guard does not have exactly one home link")
    old = f'TargetGuid="{old_home}"'.encode()
    new = f'TargetGuid="{new_home}"'.encode()
    block = replace_once(block, old, new, "scheduler guard home")
    data = data[:start] + block + data[end:]
    ET.fromstring(data)
    return data


def build(level_pak: Path, allow_unverified: bool) -> None:
    actual_pak_hash = file_sha256(level_pak)
    if actual_pak_hash != EXPECTED_LEVEL_PAK_SHA256 and not allow_unverified:
        raise ValueError(
            "baseline level.pak differs from the verified KCD II 1.5.5 export; "
            "use a matching source or pass --allow-unverified after reviewing the delta"
        )

    source = {name: read_member(level_pak, name) for name in MEMBERS}
    for name, expected in EXPECTED_MEMBER_SHA256.items():
        actual = sha256(source[name])
        if actual != expected and not allow_unverified:
            raise ValueError(f"baseline member differs: {name} ({actual})")

    generated = {
        "objects_mission0.xml": patch_objects(source["objects_mission0.xml"]),
        "layers/playerstash_7f1869a5-bf84-4a5b-bc82-e40d93f860b9.xml": patch_player_stash(
            source["layers/playerstash_7f1869a5-bf84-4a5b-bc82-e40d93f860b9.xml"]
        ),
        "layers/other_a067eb13-56b1-4ceb-ac63-86e03d8e7706.xml": patch_guard_layer(
            source["layers/other_a067eb13-56b1-4ceb-ac63-86e03d8e7706.xml"]
        ),
        "tables/ai/scheduler.xml": patch_scheduler(source["tables/ai/scheduler.xml"]),
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(OUTPUT, "w", compression=zipfile.ZIP_STORED) as pak:
        for name, payload in sorted(generated.items()):
            info = zipfile.ZipInfo(name, date_time=(2026, 8, 25, 0, 0, 0))
            info.compress_type = zipfile.ZIP_STORED
            info.external_attr = 0o100644 << 16
            pak.writestr(info, payload)
    print(f"Built {OUTPUT.relative_to(ROOT)} from {level_pak}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--level-pak", type=Path, default=DEFAULT_LEVEL_PAK, help="path to vanilla Data/Levels/trosecko/level.pak")
    parser.add_argument("--allow-unverified", action="store_true", help="attempt exact guarded patches on a different baseline")
    args = parser.parse_args()
    if not args.level_pak.is_file():
        parser.error(f"level.pak not found: {args.level_pak}")
    build(args.level_pak, args.allow_unverified)


if __name__ == "__main__":
    main()

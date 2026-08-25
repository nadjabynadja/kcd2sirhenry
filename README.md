# Sir Henry of Skalitz

Sir Henry of Skalitz is a two-part mod for *Kingdom Come: Deliverance II*.
It treats Henry as the newly legitimized, low-ranking knight established by the
end of the first game, and carries that premise through dialogue, subtitles,
voice-over, clothing, reputation, and a small optional perk.

## Included modules

### `sir_henry_of_skalitz`

The main narrative and presentation module:

- revised dialogue and supporting UI text in all 16 shipped languages;
- 300 replacement voice lines per language;
- no level edits or gameplay-table changes.

### `sir_henry_quests`

An optional tables-only companion. It gives Henry a more knightly presentation
at Trosky, modestly adjusts quest pay, makes reputation gains and losses matter
more, raises the social cost of dirty or damaged equipment, and adds a small
Speech-tree perk. See [the module notes](sir_henry_quests/README.md) for the
exact changes and compatibility implications.

## Installation

Copy either or both module directories into the game's `Mods` directory:

```text
KingdomComeDeliverance2/
└── Mods/
    ├── sir_henry_of_skalitz/
    └── sir_henry_quests/       # optional
```

The main module works by itself. The optional module is designed to accompany
it but contains no scripts or level changes and can be removed independently.

## Compatibility

This release was assembled against the KCD II 1.5 patch series. The exact
hotfix used to export the original tables has not yet been independently
recorded; treat 1.5.6 as the current verification target, not as a proven source
baseline. See [COMPATIBILITY.md](docs/COMPATIBILITY.md).

The main compatibility concern is full-file replacement. Localization tables
and three gameplay tables contain complete snapshots of their upstream files.
Another mod or game patch touching the same files may win or lose according to
load order. Do not assume that two such mods merge automatically.

## Validate a release

Python 3.10 or newer is the only requirement:

```sh
python3 scripts/validate.py
```

The validator checks manifests, archive integrity and layout, XML structure,
language symmetry, voice-path symmetry, Ogg/Vorbis headers, duplicate keys,
custom perk/buff linkage, and the uncompressed ZIP method required for KCD II
PAKs.

## Development status

The checked-in PAKs are the recovered release artifacts. The editable source
model and deterministic builder are being reconstructed in stages rather than
committing multi-gigabyte expansions of the same upstream tables. The recovery
plan is documented in [docs/SOURCE_PLAN.md](docs/SOURCE_PLAN.md).

## Attribution and license

This is an unofficial, non-commercial fan mod and is not endorsed by Warhorse
Studios or PLAION. See [PROVENANCE.md](docs/PROVENANCE.md) for the concise asset
and translation record, and [LICENSE](LICENSE) for the repository's licensing
boundary.

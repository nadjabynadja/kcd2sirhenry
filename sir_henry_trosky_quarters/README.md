# Trosky Guest Quarters (optional module)

This module makes Henry a better-treated guest of Trosky Castle without making
him its lord. It does **not** use Otto von Bergow's bed or bedroom.

## The exchange

- Henry receives high single bed `39429` in the lower-castle guard barracks and
  the bedside chest position beside it.
- The shared player stash proxy moves from the courtyard woodshed to that
  bedside position, so it remains the same persistent stash used elsewhere.
- Anonymous guard `ttro_man_26` (`char_GENERIC_MAN_GUARD_18`) moves from the
  guard-house home scheduler to the upper courtyard home scheduler. He keeps
  his normal day/night guard duties but sleeps from that home pool, which now
  includes Henry's released bed.
- The guard's bedside equipment chest moves to Henry's former stash position,
  and the former Henry bed receives the guard sleep-equipment links.
- The other communal bunks that shared the selected bedside chest are
  redirected to the cohort's existing guard armory chest, so no uninvolved
  sleeper loses storage.
- The Trosky room quest aliases, sleep/save trigger, and chamberlain-tour room
  marker follow Henry to the new room.

The new bed is marked high quality and the released bed medium quality. This is
a guest-room promotion, not ownership of a noble suite.

## Installation

Place the complete `sir_henry_trosky_quarters` directory in the game's `Mods`
directory. This is independent of the narrative, Knightly Bearing, and Kobyla
Regalia modules.

Install it before the Trosky room is granted (ideally before beginning the
Trosky quest sequence). Bed ownership is written into saves by the quest
system; installing after that action has already completed may leave the old
ownership cached until a new playthrough or a suitable save from before the
room grant.

## Linux-native rebuild

The checked-in level patch was produced without the official Windows editor.
Python 3 and a legally obtained vanilla `Data/Levels/trosecko/level.pak` are
enough:

```sh
python3 scripts/build_trosky_quarters.py \
  --level-pak "/path/to/KingdomComeDeliverance2/Data/Levels/trosecko/level.pak"
```

The builder accepts the verified 1.5.5 exported baseline, applies guarded
byte-level XML edits, parses every generated XML file, and writes a
stored/uncompressed deterministic PAK named
`Data/Levels/trosecko/sir_henry_trosky_quarters.pak`. The mod-ID filename is
intentional: `level.pak` is reserved for a level's primary archive and must not
be used for a patch to the existing Trosecko level. A different game baseline
fails closed.

## Compatibility and verification status

This module replaces four complete exported level files inside
`Data/Levels/trosecko/level.pak`: the main mission entity list, the player-stash
layer, the layer containing the selected guard, and the scheduler table. It is
therefore incompatible with another mod replacing any of those files unless
the changes are reconciled manually.

Static validation is complete against the local 1.5.5 export. The current
workspace does not contain a runnable game installation, so the remaining
in-game checks are: room-tour pathing, trespass state after the room grant,
sleep/save ownership, shared-stash persistence, and the displaced guard's
overnight pathing. Keep a save from before the room grant for that test.

# Sir Henry of Skalitz - Kobyla Regalia

Optional compatibility module for **Sir Henry of Skalitz** and **House of
Kobyla Arms Armour and Regalia**.

## Requirements

- House of Kobyla Arms Armour and Regalia 1.6.5 or later (required for Henry's
  hood and horse regalia)
- Sir Henry of Skalitz is recommended, but not technically required

Install `sir_henry_kobyla_regalia` beside the other mod directories and load it
after `KobylaArms` and the Sir Henry modules.

## Changes

- Replaces both startup phases (`UC_HenryStart` and `UC_HenryStartStage1`) with
  the base-game Noble cuirass, plate arms, plate legs, red Long Pourpoint, and
  Noble Boots while retaining Henry Base hood.
- Adds the base-game Bascinet with breteche to Henry's inventory instead of
  equipping it in the scene outfit.
- Adds Henry's Kobyla caparison and chanfron to `horse_henry_arrival` while
  preserving the horse's original saddle and bridle.

The compatibility module is intentionally tables-only. An earlier build also
shipped a standalone `Gameplay` document containing always-active
`player_stash` nodes. That graph was not owned by a retail-style quest project
and could stall a new game while the starting world initialized, so it has
been removed from the runtime package.

## Compatibility

The clothing changes use a patched table file. Another mod patching the same
two preset records can still conflict according to load order. This module no
longer adds or replaces quest graphs or directly mutates the shared player
stash.

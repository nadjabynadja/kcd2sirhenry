# Sir Henry of Skalitz - Kobyla Regalia

Optional compatibility module for **Sir Henry of Skalitz** and **House of
Kobyla Arms Armour and Regalia**.

## Requirements

- House of Kobyla Arms Armour and Regalia 1.6.5 or later (hard requirement for
  this compatibility module's item records)
- Sir Henry of Skalitz is recommended, but not technically required

Install `sir_henry_kobyla_regalia` beside the other mod directories and load it
after `KobylaArms` and the Sir Henry modules.

## Changes

- Replaces `UC_HenryStart` with the Kobyla Noble Bastard cuirass, arms, legs,
  and bascinet; Henry Base hood; red-brocade Kobyla Noble Gambeson; and Noble
  Boots.
- Adds Henry's Kobyla caparison and chanfron to `horse_henry_arrival` while
  preserving the horse's original saddle and bridle.
- Adds Henry Base hood, Henry's caparison, and Henry's chanfron to the shared
  player stash.
- Adds the seven-piece starting outfit to the shared player stash after
  `naTroskach.endQuest` (the end of *For Whom the Bell Tolls*).

The stash entries use quality 3, matching the Kobyla Arms merchant presets,
and `DisableRestock=true` so removed or sold rewards are not recreated.

## Compatibility

The clothing changes use a patched table file. Another mod patching the same
two preset records can still conflict according to load order. The quest graph
is additive and does not replace `naTroskach.xml`.

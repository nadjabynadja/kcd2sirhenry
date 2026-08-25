# Knightly Bearing (optional module)

`sir_henry_quests` is the optional mechanical companion to Sir Henry of
Skalitz. It contains data tables only: no scripts, quests, or level edits.

## What it changes

- Replaces Henry's `UC_HenryTrosky` scene outfit with a noble gambeson, hood,
  quilted hose, high boots, knight's spurs, and a Knight's Longsword.
- Changes `QuestMoneyRewardScaleConstant` from `1.025` to `1.10`.
- Changes `ArmorDirtToCharismaCoef` from `0.8` to `1.1`.
- Changes `ArmorStatusToCharismaCoef` from `0.6` to `0.85`.
- Retunes 29 reputation events so deliberate wrongdoing and failed bearing
  cost more while quest deeds and successful social checks count more.
- Adds a level-five Speech perk using the existing Knight in Shining Armour UI
  strings. Its persistent buff grants `Charisma +2` and `Prestige +3`.

The intended balance is not a blanket buff. Henry receives modest advantages
for rank and service but is judged more sharply and must maintain his appearance.

## Installation and removal

Place the complete `sir_henry_quests` directory in the game's `Mods` directory.
It may be installed alongside the main module or omitted entirely.

The module contains no executable code. Removing it stops its table overrides
from loading. As with any data mod, make a normal save before changing the mod
set; a save that learned the custom perk may retain a reference to that perk.

## Compatibility

`Tables.pak` includes full-file overrides of:

- `Libs/Tables/rpg/reputation_change.xml`
- `Libs/Tables/rpg/rpg_param.xml`
- `Libs/Tables/rpg/perk_buff.xml`

It also includes additive custom perk and buff tables and a single-record
clothing-preset override. Mods changing the three full files are load-order
sensitive. Reconcile them manually rather than assuming their values merge.

The release targets the KCD II 1.5 patch series. See
[`docs/COMPATIBILITY.md`](../docs/COMPATIBILITY.md) for baseline status.

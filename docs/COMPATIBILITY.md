# Compatibility and game baseline

## Supported version

The recovered `0.2.0` release was assembled for the *Kingdom Come: Deliverance
II* 1.5 patch series. PLAION's support index lists subsequent 1.5-series hotfixes
through 1.5.6. The exact hotfix from which these full tables were exported has
not yet been proven by checksum.

Until upstream checksums are recorded, use this wording:

> Targets KCD II 1.5.x; verification target 1.5.6. Exact source hotfix pending.

Do not silently change that to an exact 1.5.6 claim. The source-recovery process
must compare the bundled full tables with a clean 1.5.6 installation first.

## Known conflict surfaces

The main module replaces the complete `text_ui_dialog.xml`,
`text_ui_quest.xml`, `text_ui_soul.xml`, and `text_ui_misc.xml` tables for each
language.

The optional module replaces complete `reputation_change.xml`, `rpg_param.xml`,
and `perk_buff.xml` files. It also supplies additive perk/buff files and one
clothing-preset record.

Trosky Guest Quarters replaces four files inside the Trosecko `level.pak`:
`objects_mission0.xml`, `tables/ai/scheduler.xml`, the selected guard's
streaming layer, and the Trosky player-stash layer. It cannot be combined by
load order alone with another mod replacing any of those files. The authored
delta is rebuilt from the verified 1.5.5 level export and intentionally marks
`modifies_level` true.

Any mod or patch touching the same complete file is potentially incompatible.
Load order chooses a winner; it does not merge individual XML rows.

## PAK format

Keep the archives as ordinary ZIP files using the **stored/uncompressed** method.
Official KCD II publishing guidance describes PAKs as uncompressed ZIP archives
and warns that some ZIP writers produce incompatible output. The repository
validator rejects other compression methods.

References:

- [Official KCD II modding overview](https://www.deepsilver.com/games/kingdom-come-deliverance-ii/news/modding-in-kingdom-come-deliverance-2)
- [Official PLAION Patch 1.5 notice](https://playersupport.plaion.com/en/support/solutions/articles/10000012575-patch-1-5)

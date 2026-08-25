# Trosky quarters authored delta

This is the human-reviewable selection record used by
`scripts/build_trosky_quarters.py`. No upstream level XML is committed as
source.

| Role | Entity | GUID | Vanilla location |
|---|---:|---|---|
| Henry's old bed | 42143 | `d8c2dde3-94e1-0d66` | castle courtyard 2 |
| old bed trigger | 42144 | `755327b6-f900-0b8a` | castle courtyard 2 |
| new guard-barracks bed | 39429 | `113ef129-a845-0bb5` | lower castle, courtyard 4 barracks |
| new bed trigger | 39430 | `bcaf0b7c-c5a4-0d59` | lower castle, courtyard 4 barracks |
| exchanged guard chest | 39579 | `0f6b8031-05b1-07b2` | beside bed 39429 |
| guard chest holder | 39580 | `4ec86073-709d-04de` | beside bed 39429 |
| selected guard | 194586 | `ecf8b1c1-91ac-4135` | `ttro_man_26`, generic Guard 18 |
| guard's old home | 17958 | `f03c4f32-9c2f-4c4e` | lower castle courtyard 4 |
| guard's new home | 32968 | `8601be80-fa9e-4eb9` | castle courtyard 2 |

Selection constraints:

- no Bergow, Capon, chamberlain, named knight, or named quest guard;
- a real guard-faction NPC with ordinary day/night guard aliases;
- an interior single high bed with a bedside chest;
- the guard keeps his work schedule and changes only home;
- the ten other communal bunks sharing chest 39579 are redirected to the
  cohort's existing guard armory chest 39498;
- all three Henry-bed quest aliases and the explicit interactor alias move;
- the activated player-stash proxy and the permanent guard chest exchange
  positions rather than creating a second player inventory.

Verified upstream baseline:

- `Data/Levels/trosecko/level.pak`: KCD II release 1.5.5 export,
  SHA-256 `39936765768694ec55c457af5d355d62be60812f60f6047d71797094aec3afb9`.

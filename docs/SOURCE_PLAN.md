# Editable source recovery plan

The current repository began as a release bundle: two manifests and 33 PAK
archives. The goal is to make that release reproducible without treating full
copies of upstream game data as the canonical authored source.

## Source model

Use three distinct layers:

1. **Upstream snapshot metadata** — game version, source archive checksums, and
   per-table checksums. Do not commit redistributed upstream archives.
2. **Authored deltas** — the actual text replacements, table value changes,
   custom records, and voice-file mapping owned by this project.
3. **Generated workspace and release** — expanded XML and PAKs rebuilt from a
   locally installed, checksum-matched copy of the game.

The intended layout is:

```text
src/
├── localization/
│   ├── edits.tsv
│   └── languages/<language>.tsv
├── voice/
│   ├── manifest.tsv
│   └── <language>/...ogg
└── tables/
    ├── additive/
    ├── overrides/
    └── patches.toml
upstream/
├── baseline.json
└── README.md
build/                         # ignored, expanded/generated files
dist/                          # ignored, assembled release
```

## Recovery phases

### Phase 1: inventory and freeze the recovered release

- Record SHA-256 checksums for every current PAK and every member.
- Record the installed game's exact version and upstream PAK checksums.
- Keep the current `0.2.0` artifacts immutable as the recovery reference.
- Run `python3 scripts/validate.py` before and after every recovery step.

### Phase 2: recover the localization deltas

- Obtain clean 1.5-series localization XML from the same game build.
- Match rows by the first `Cell` (localization key), never by row number.
- Compare the release's output column with clean upstream and export only true
  changes to UTF-8 TSV files.
- Store the source text, replacement text, language, review state, and optional
  voice mapping for each edited key.
- Reapply the exported deltas to a clean snapshot and require byte-equivalent
  semantic output: identical keys and cell values, allowing only intentional
  formatting normalization.

### Phase 3: recover voice sources and mapping

- Retain the existing Ogg files in Git LFS initially; they are authored release
  assets and cannot be reconstructed from XML alone.
- Create `src/voice/manifest.tsv` with language, archive path, dialogue/event
  identity, speaker, replacement text key where known, duration, codec settings,
  generator/source record, and review status.
- Rename no in-game paths. Treat the archive path as a stable game identifier.
- If lossless masters exist, keep them outside the release tree and document
  their storage; generate the 48 kHz mono Vorbis outputs deterministically.

### Phase 4: recover gameplay-table intent

- Extract the two additive custom tables as directly authored XML.
- Express the clothing preset as one intentional record.
- Represent the three full-table overrides as keyed patches against a verified
  upstream snapshot. For example, `rpg_param` patches are keyed by
  `rpg_param_key`; reputation patches are keyed by `reputation_change_id`.
- Generate the complete engine-facing files only during the build.
- Fail the build if an upstream checksum changes or a patch target disappears.

### Phase 5: deterministic build and regression test

- Add `scripts/build.py` using only the Python standard library where practical.
- Normalize archive member ordering, timestamps, permissions, and ZIP metadata.
- Use ZIP stored mode: official KCD II publishing guidance requires
  uncompressed ZIP-format PAKs.
- Build into `dist/`, validate it, and compare its semantic contents with the
  frozen `0.2.0` release.
- Add CI for source-only tests. Release assembly may remain local because it
  requires legally obtained upstream game data and large LFS assets.

## Definition of done

Recovery is complete when a clean checkout plus a verified local KCD II
installation can produce both mod directories with one build command, the
validator passes, and every intentional difference from upstream is represented
by a human-reviewable source record.

# Translation Status — {{PROJECT}}
<!-- Written by validate.py. Do not hand-edit; fix the source and re-run. -->

Last run: <!-- pending first validate.py run -->

| File | Arabic mirror | State |
|---|---|---|
| — | — | run `python docs/_meta/validate.py docs` to populate |

## How sync works
Every `*.ar.md` carries `source_sha` in its frontmatter: the SHA-256 of the English body
it was translated from. `validate.py` recomputes that hash and reports:

- `in-sync` — hashes match.
- `STALE` — the English file changed after translation. Retranslate, then update `source_sha`.
- `MISSING` — a mirror-mode file has no Arabic counterpart.
- `ORPHAN` — an Arabic file whose English source is gone.

STALE and MISSING fail the docs check. Bilingual coverage is only real when it is verified.

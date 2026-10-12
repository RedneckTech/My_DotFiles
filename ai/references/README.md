# ai/references/ — authoritative reference docs

Verified reference material the AI should **trust over vendor prose or
manuals**. Each subject gets its own subdirectory with a `README.md` index.

A reference belongs here when it is:

- **Verified** — behaviour confirmed by running/probing the real system, not
  copied from documentation that may be wrong.
- **Authoritative** — the doc the AI should consult first for that subject,
  with any known documentation errors called out explicitly.
- **Stable** — filenames won't churn, so agent prompts can point at them.

## Subjects

| Directory | Subject | Source |
|-----------|---------|--------|
| `timesharing-basic/` | TIMESHARING BASIC/3270BBS v3.0.0 (the 3270 BBS language) | copied from `/media/jpfeiff/BlackBox/3270BBS/basic-learning/` |

### timesharing-basic/

14 docs, every fact verified live against interpreter v3.0.0. Start at
`LANGUAGE_REFERENCE.md`; `MANUAL_ERRATA_FOR_DEV.md` lists every place the
shipped manual (v2.9.2) is wrong. See that directory's `README.md` for the
full index.

## Canonical copy

Like `scripts/`, these are **copies** of a project's doc set — the working
copy lives with the project (here: the `3270BBS` repo, `basic-learning/`).
Edit the project copy, then re-copy it here. Keep the two in sync; if a doc
set outgrows its project, promote this copy to canonical and have the project
point back at it.

## Adding a subject

1. `mkdir references/<subject>/`.
2. Copy the verified doc set in, plus its `README.md` index.
3. Add a row to the table above.

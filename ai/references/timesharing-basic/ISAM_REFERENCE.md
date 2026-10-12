# Indexed Files (ISAM) — Complete Reference (v3.0.0)

Everything below was verified by running it on the live interpreter and by
inspecting the resulting `.dat` files byte-for-byte.

## Basics

```basic
DIM C{}
OPEN "contacts.dat" FOR INDEXED AS #1 KEY = "id"
C{"id"} = "001" : C{"name"} = "Alice" : PUT #1, C{}
...
CLOSE #1
```

- File handles `#1`-`#4` (max 4 open at once, same as sequential files).
- `KEY = "field"` names the field that acts as the primary key.
- The data file is plain `.dat`; **no separate `.idx` file is created** —
  the index is built in memory when the file is opened.

## The four operations

| Operation | Syntax |
|-----------|--------|
| Write (upsert) | `PUT #n, array{}` |
| Read by key | `GET #n, array{}, KEY = expr` |
| Read by record # | `GET #n, array{}, REC = n` |
| Sequential read | `GET #n, array{}, NEXT` |
| Delete by key | `DELETE #n, KEY = expr` |
| Delete by rec # | `DELETE #n, REC = n` |
| Rewind | `RESET #n` |

## Status functions

| Function | Meaning |
|----------|---------|
| `FOUND(n)` | 1 if the last GET found a record |
| `EOF(n)` | 1 at end of file |
| `DELETED(n)` | deleted status — **UNRELIABLE, see below** |

## Critical gotcha: PUT and GET do NOT clear the array

This is the single most important thing to know. The associative array you
PUT from and GET into is **reused** — fields from the previous operation
persist.

Verified failure:

```basic
C{"id"}="1" : C{"name"}="Alice" : C{"age"}=30 : PUT #1, C{}
C{"id"}="2" : C{"city"}="NYC" : PUT #1, C{}      ' only id+city intended
```

The second record in the file ends up as:

```
id=2  name=Alice  age=30  city=NYC
```

— `name` and `age` leaked in from the first record. The same happens on
GET: reading a record that lacks a field returns the *stale* value from the
previous GET, not an empty value.

**Fix: re-DIM the array before each PUT and each GET.** `DIM C{}` clears an
associative array (verified: after re-DIM, missing keys return 0):

```basic
DIM C{}                          ' clear before each PUT
C{"id"}="2" : C{"city"}="NYC" : PUT #1, C{}

DIM R{}                          ' clear before each GET
GET #1, R{}, KEY = "2"
```

With the re-DIM, records are written exactly as intended, and a missing
field correctly returns `0`.

## Records are schemaless

Different records can have different fields. A record with no `name` reads
back `R{"name"}` = `0` (numeric default, not empty string). Design your
code to handle absent fields.

## Semantics (verified)

- **Record numbers are 1-based.** `REC = 1` is the first record; `REC = 0`
  returns `FOUND = 0`.
- **Sequential order is INSERTION order, not key order.** Insert 003, 001,
  002 and a `RESET` + `NEXT` scan returns 003, 001, 002 — the key index is
  for random access only, it does not sort the file.
- **`PUT` is a true upsert.** Writing the same key twice updates the
  existing record in place (the file keeps one record, last write wins).
- **`DELETE` is a soft delete.** The record is marked with a `0x7F` (DEL)
  byte at the start of its line; it is not physically removed.
- **`GET ... NEXT` skips deleted records.**
- **Re-adding a deleted key appends a NEW record** — it does not reuse the
  deleted slot (the old marked line stays in the file).
- **Numeric and string keys both work** (`KEY = 200` and `KEY = "200"`).
- **The index is rebuilt on OPEN**, so CLOSE then re-OPEN (even in a new
  session) reads records by key correctly.
- **GET on an empty file** returns `FOUND = 0`.
- **Multiple indexed files** can be open at once (up to the 4-handle limit).

## The .dat file format

A plain text file, records separated by newlines, fields as
`name=value` pairs separated by TAB (`0x09`):

```
id=1<TAB>name=Alice<TAB>age=30
<0x7F>id=2<TAB>name=Bob            ' 0x7F prefix = deleted
id=3<TAB>name=Carol
```

Field order in a record follows the order the keys were set in the
associative array, not a fixed schema (so `name=...<TAB>id=...` is possible).

## `DELETED(n)` is unreliable

During a sequential scan, `DELETED(1)` reported `1` for a record that was
NOT deleted (the deleted record was the *next* one), and `0` for a
correctly-undeleted record. Do not trust `DELETED()` for correctness —
`GET ... NEXT` already skips deleted records, so a normal scan only yields
live records and `DELETED()` is unnecessary.

## Error messages (verified)

| Error | Cause |
|-------|-------|
| `?FILE NOT OPENED FOR INDEXED` | PUT/GET on a file opened FOR INPUT/OUTPUT/APPEND |
| `?KEY FIELD 'id' NOT SET` | `PUT` without setting the key field |
| `?ARRAY NOT DEFINED` | documented for undimensioned arrays (GET with an undefined array silently returned no record in testing) |

## Working pattern (copy this)

```basic
DIM C{}
OPEN "rolodex.dat" FOR INDEXED AS #1 KEY = "id"
DIM C{} : C{"id"}="001" : C{"name"}="Alice" : C{"phone"}="555-1234" : PUT #1, C{}
DIM C{} : C{"id"}="002" : C{"name"}="Bob"   : C{"phone"}="555-5678" : PUT #1, C{}

DIM R{}
GET #1, R{}, KEY = "002"
IF FOUND(1) THEN PRINT R{"name"}; " "; R{"phone"}

RESET #1
WHILE NOT EOF(1)
    DIM R{}
    GET #1, R{}, NEXT
    IF FOUND(1) THEN PRINT R{"id"}; " "; R{"name"}
WEND
CLOSE #1
```

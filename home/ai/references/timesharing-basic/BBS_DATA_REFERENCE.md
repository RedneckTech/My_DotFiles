# 3270BBS Data Access (v3.0.1)

BASIC programs can read live BBS data through the `$`-sources. Each is
copied into an associative array with a whole-array assignment, e.g.
`U{} = $UserInfo`. The table of keys is from the v3.0.1 manual; the
mechanics (replacement, `""` defaults, case-insensitivity) were verified
live.

## The shared rules

Every `$`-source behaves the same way:

- **The assignment replaces the array** — whatever it held is gone, then it
  holds exactly the keys of the source.
- **A missing key reads as `""`**, even in an array without `$` in its name.
- **All values are strings** — use `VAL()` for arithmetic, compare with
  strings.
- **Key names ignore case** — `U{"USERNAME"}` and `U{"username"}` are the
  same field. (Your own associative arrays and ISAM records are
  case-sensitive; these BBS records are not.)
- `DIM U{}` before the assignment; the array stays a record after setting
  single elements until you `DIM` it again.

## $UserInfo — your profile

```basic
DIM U{} : U{} = $UserInfo
PRINT U{"username"}
```

| Key | Description |
|-----|-------------|
| `username` | your username |
| `country` | your country (may be empty) |

Admin-only fields (email, IP, role, ban status) are never exposed.

**Known bug (still present in 3.0.1):** `$UserInfo{"country"}` returns the
username, not the country. Treat `country` as unreliable.

## $TermInfo — your terminal

```basic
DIM T{} : T{} = $TermInfo
```

| Key | Description |
|-----|-------------|
| `model` | `"Mod2"` (24x80), `"Mod3"` (32x80), `"Mod4"` (43x80) |
| `codepage` | `"310"` (graphics) or `"037"` (standard EBCDIC) |

Use `IF T{"codepage"} = "310"` before drawing `CP310$` graphics.

## $Mail(n) — your mail

`n=0` = most recent, `n=1`/`n=-1` = second most recent.

```basic
DIM M{} : M{} = $Mail(0)
```

| Key | Description |
|-----|-------------|
| `datetime` | ISO 8601 `YYYY-MM-DDTHH:MM:SS` |
| `from` | sender username |
| `body` | full message body |
| `read` | `"1"` read, `"0"` unread |
| `replied` | `"1"` replied, `"0"` not |
| `id` | message id |

Empty values if no mail.

## $ChatMessage(n) — public chat

`n=0` = most recent, `n=1`/`n=-1` = second most recent.

```basic
DIM C{} : C{} = $ChatMessage(0)
```

| Key | Description |
|-----|-------------|
| `datetime` | ISO 8601 `YYYY-MM-DDTHH:MM:SS` |
| `username` | who posted |
| `message` | message content |

Only the public global room, not private rooms. Empty if none.

## $Topic(n) — accessible topics

`n=0` = most recent, `n=1` = second. Only topics the user may access.

```basic
DIM T{} : T{} = $Topic(0)
```

| Key | Description |
|-----|-------------|
| `id` | topic id (use with `$Post`) |
| `title` | title |
| `author` | creator |
| `conference` | conference name |
| `datetime` | ISO 8601 |
| `posts` | post/reply count |
| `views` | view count |
| `likes` | like count |

## $Post(topic_id, n) — posts in a topic

`n=0` = first (oldest) post, `n=1` = second, …

```basic
DIM P{} : P{} = $Post(VAL(T{"id"}), 0)
```

| Key | Description |
|-----|-------------|
| `id` | post id |
| `author` | who wrote it |
| `body` | post content |
| `datetime` | ISO 8601 |
| `likes` | like count |
| `dislikes` | dislike count |

Empty if the topic is not found or access is denied.

## Idiotmatic read loop

```basic
DIM M{} : M{} = $Mail(0)
IF M{"datetime"} = "" THEN PRINT "No mail" ELSE PRINT M{"from"}
```
